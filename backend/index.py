from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import sqlite3
import os
import json
from preprocessing import load_data, clean_data, preprocess_data
from model import train_model, find_optimal_k
from insights import generate_cluster_insights

# Supabase imports
from supabase import create_client, Client

app = FastAPI(title="Customer Segmentation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
USE_SUPABASE = SUPABASE_URL and SUPABASE_KEY

# Determine DB Path for SQLite fallback
if os.environ.get("VERCEL"):
    SQLITE_DB_PATH = "/tmp/customers.db"
else:
    SQLITE_DB_PATH = "customers.db"

# --- HELPER FUNCTIONS ---

def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB_PATH)

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_data(df: pd.DataFrame):
    """Saves dataframe to either Supabase or SQLite."""
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            
            # 1. Truncate existing data (simulate replace)
            # optimized: delete all rows where id is not null (assuming id column exists)
            # Note: For this to work efficiently, we just delete everything.
            # Only way to 'delete all' without Where clause in some SDKs is tricky, 
            # but usually .neq('id', 0) works if IDs are positive.
            supabase.table('customers').delete().neq('id', 0).execute()

            # 2. Convert to records
            records = df.to_dict(orient='records')
            
            # 3. Store in 'data' JSONB column to handle dynamic CSV schema
            # We wrap each record: { "data": record_content }
            rows_to_insert = [{"data": record} for record in records]
            
            # 4. Insert in chunks (Supabase has payload limits)
            chunk_size = 1000
            for i in range(0, len(rows_to_insert), chunk_size):
                chunk = rows_to_insert[i:i + chunk_size]
                supabase.table('customers').insert(chunk).execute()
                
        except Exception as e:
            print(f"Supabase Error: {e}")
            raise HTTPException(status_code=500, detail=f"Supabase Save Error: {str(e)}")
    else:
        # SQLite Fallback
        conn = get_sqlite_connection()
        df.to_sql('customers', conn, if_exists='replace', index=False)
        conn.close()

def load_data_from_db() -> pd.DataFrame:
    """Loads data from either Supabase or SQLite."""
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client()
            # Fetch all data (limit is usually 1000 by default, need to paginate if huge)
            # For simplicity in this demo, we fetch max 10000 or use automatic pagination if supported
            # The python client handles some pagination but explicitness is safer.
            response = supabase.table('customers').select('data').execute()
            
            if not response.data:
                return pd.DataFrame()
            
            # Extract the 'data' field from each row
            records = [row['data'] for row in response.data]
            return pd.DataFrame(records)
            
        except Exception as e:
            print(f"Supabase Read Error: {e}")
            raise HTTPException(status_code=500, detail=f"Supabase Read Error: {str(e)}")
    else:
        # SQLite Fallback
        conn = get_sqlite_connection()
        try:
            df = pd.read_sql("SELECT * FROM customers", conn)
        except:
            df = pd.DataFrame()
        conn.close()
        return df

# --- API ENDPOINTS ---

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        content = await file.read()
        df = load_data(content)
        df = clean_data(df)
        
        # Preprocess
        scaled_features, scaler, numeric_cols, processed_df = preprocess_data(df)
        
        # Train model
        best_k, inertias, scores = find_optimal_k(scaled_features)
        clusters, kmeans, n_clusters = train_model(scaled_features, n_clusters=best_k)
        
        # Add Cluster column
        processed_df['Cluster'] = clusters
        
        # Generate Insights to get labels
        insights = generate_cluster_insights(processed_df, 'Cluster')
        
        # Add Segment label to dataframe
        processed_df['CustomerSegment'] = processed_df['Cluster'].apply(lambda c: insights[c]['label'])
        
        # Save to DB (Supabase or SQLite)
        save_data(processed_df)
        
        return {
            "message": "File processed successfully",
            "n_clusters": int(n_clusters),
            "rows": len(processed_df),
            "columns": list(processed_df.columns),
            "model_metrics": {
                "inertias": [float(i) for i in inertias],
                "silhouette_scores": [float(s) for s in scores],
                "optimal_k": int(best_k)
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clusters")
def get_clusters():
    try:
        df = load_data_from_db()
        data = df.to_dict(orient="records")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insights")
def get_insights():
    try:
        df = load_data_from_db()
        
        if df.empty:
            return {"message": "No data available"}
            
        insights = generate_cluster_insights(df, 'Cluster')
        
        # Convert numpy types to native Python types for JSON serialization
        for k, v in insights.items():
            if 'stats' in v:
                v['stats'] = {str(sk): float(sv) for sk, sv in v['stats'].items()}
                
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
def download_results():
    try:
        df = load_data_from_db()
        
        output_file = "segmented_customers.csv"
        df.to_csv(output_file, index=False)
        
        return FileResponse(path=output_file, filename=output_file, media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
