from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import pickle
import os

# Check environment for writable path
if os.environ.get("VERCEL"):
    MODEL_PATH = "/tmp/kmeans_model.pkl"
else:
    MODEL_PATH = "kmeans_model.pkl"

def find_optimal_k(scaled_data, max_k=10):
    """
    Determine optimal K using the Elbow Method and Silhouette Score.
    We will use a simple heuristic for the elbow point based on inertia.
    """
    inertias = []
    silhouette_scores = []
    K_range = range(2, max_k + 1)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled_data)
        inertias.append(kmeans.inertia_)
        if len(scaled_data) > k:
            score = silhouette_score(scaled_data, kmeans.labels_)
            silhouette_scores.append(score)
        else:
            silhouette_scores.append(-1)
            
    # Simple elbow method: find the point with the maximum curvature
    # Or simply use the highest silhouette score which is often better for validation
    # Let's use a combination or default to silhouette for robustness
    
    # Calculate the slopes of inertia
    diffs = np.diff(inertias)
    diffs_r = diffs[1:] / diffs[:-1]
    
    # Heuristic: if valid silhouette, pick peak silhouette
    if any(s > 0 for s in silhouette_scores):
        best_k = K_range[np.argmax(silhouette_scores)]
    else:
        # Fallback to 4 if silhouette fails or data is weird
        best_k = 4
        
    return best_k, inertias, silhouette_scores

def train_model(scaled_data, n_clusters=None):
    """
    Train KMeans model.
    """
    if n_clusters is None:
        n_clusters, _, _ = find_optimal_k(scaled_data)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)
    
    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(kmeans, f)
        
    return clusters, kmeans, n_clusters
