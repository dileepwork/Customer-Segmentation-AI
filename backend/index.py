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

app = FastAPI(title="Customer Segmentation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine DB Path based on environment
# Vercel filesystem is read-only except for /tmp
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/customers.db"
else:
    DB_PATH = "customers.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

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
        
        # Save to SQLite
        conn = get_db_connection()
        processed_df.to_sql('customers', conn, if_exists='replace', index=False)
        conn.close()
        
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
        conn = get_db_connection()
        # Read from DB
        df = pd.read_sql("SELECT * FROM customers", conn)
        conn.close()
        
        # Convert to records
        data = df.to_dict(orient="records")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insights")
def get_insights():
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM customers", conn)
        conn.close()
        
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
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM customers", conn)
        conn.close()
        
        output_file = "segmented_customers.csv"
        df.to_csv(output_file, index=False)
        
        return FileResponse(path=output_file, filename=output_file, media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
