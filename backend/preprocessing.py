import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from io import BytesIO

def load_data(file_content: bytes) -> pd.DataFrame:
    """
    Load CSV data from bytes content.
    """
    try:
        df = pd.read_csv(BytesIO(file_content))
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {str(e)}")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataframe by handling missing values.
    """
    # drop rows with missing values for simplicity as per requirements
    # or fill with mean/median
    # Let's drop for now to ensure robustness unless too many are lost
    if df.isnull().values.any():
        df = df.dropna()
    return df

def preprocess_data(df: pd.DataFrame):
    """
    Preprocess data for clustering:
    - Select numerical features
    - Scale features
    Returns tuple: (scaled_features, scaler, numerical_cols, original_df_with_numerical_only)
    """
    # Identify numerical columns automatically or use specific ones if present
    # The prompt mentions specific columns: Age, Annual Income, Spending Score, etc.
    # We should look for these or similar numerical columns.
    
    # Heuristic: select all numeric columns except 'CustomerID' if it exists
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'CustomerID' in numeric_cols:
        numeric_cols.remove('CustomerID')
    
    if not numeric_cols:
        raise ValueError("No numerical columns found for clustering")

    data_to_scale = df[numeric_cols]
    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data_to_scale)
    
    return scaled_features, scaler, numeric_cols, df
