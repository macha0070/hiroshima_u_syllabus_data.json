# ==========================================
# Script Name: ClusterViz.py
# Description:
#   [EN] Advanced visualization using K-Means clustering and t-SNE projection.
#        Groups courses into semantic clusters and projects them into 3D space.
#        Prints top keywords for each cluster to console.
#   [JP] K-Meansクラスタリングとt-SNE射影を使用した高度な可視化スクリプト。
#        授業を意味的なクラスタにグループ化し、3次元空間に射影します。
#        各クラスタの上位キーワードをコンソールに出力します。
#
# Data Flow:
#   Input  : syllabus_vectors.json
#          : course_metadata.json
#   Output : (3D Plot Window / 3Dプロットウィンドウ)
#          : (Console Output / コンソール出力) - Cluster Keywords
# ==========================================

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import sys

def main():
    # 1. Load Data
    print("Loading data...")
    try:
        with open("syllabus_vectors.json", "r", encoding="utf-8") as f:
            vector_data = json.load(f)
        with open("course_metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    # 2. Reconstruct Vectors
    print("Reconstructing vectors...")
    vocab = vector_data["v"]
    # Reverse vocab for keyword lookup: index -> word
    # vocab is essentially a list where index matches the vector index, OR a dict word->index.
    # Checking structure... usually "v" is a dict {word: index}.
    # Let's handle both just in case, or assume dict based on previous knowledge.
    # Previous viewing showed "v": vocabulary (likely dict).
    index_to_word = {v: k for k, v in vocab.items()}
    
    sparse_vectors = vector_data["d"]
    course_ids = vector_data["i"]
    vocab_size = len(vocab)
    
    num_courses = len(course_ids)
    dense_matrix = np.zeros((num_courses, vocab_size))
    
    for idx, (indices, values) in enumerate(sparse_vectors):
        for col, val in zip(indices, values):
            dense_matrix[idx, col] = val
            
    # 3. K-Means Clustering
    k = 12  # Adjustable number of clusters
    print(f"Applying K-Means Clustering (k={k})...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(dense_matrix)
    
    # Analyze Clusters (Top Keywords)
    print("\n--- Cluster Interpretations ---")
    centers = kmeans.cluster_centers_
    for i in range(k):
        # Get indices of top 10 features for this cluster centroid
        top_features_ind = centers[i].argsort()[-10:][::-1]
        top_words = [index_to_word.get(ind, f"word_{ind}") for ind in top_features_ind]
        print(f"Cluster {i}: {', '.join(top_words)}")

    # 4. t-SNE Projection (High Dim -> 3D)
    print("\nApplying t-SNE (3D projection)... this may take a moment.")
    tsne = TSNE(n_components=3, random_state=42, perplexity=30, learning_rate=200, init='pca')
    projections = tsne.fit_transform(dense_matrix)
    
    # 5. Visualize
    print("Visualizing...")
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot
    # Use a colormap generated from the cluster IDs
    scatter = ax.scatter(
        projections[:, 0], 
        projections[:, 1], 
        projections[:, 2], 
        c=clusters, 
        cmap='tab20', 
        s=40, 
        edgecolors='k', 
        alpha=0.8
    )
    
    # Add labels for a few points (optional, maybe too cluttered)
    # Let's label the centroid-closest point of each cluster maybe?
    # For now, just the points.
    
    # Create legend
    # We can't easily show all course names, but we can show Cluster IDs
    legend1 = ax.legend(*scatter.legend_elements(), title="Clusters", loc="upper right", bbox_to_anchor=(1.1, 1))
    ax.add_artist(legend1)
    
    ax.set_title(f"Syllabus Clusters (t-SNE + K-Means k={k})")
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    ax.set_zlabel("t-SNE 3")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
