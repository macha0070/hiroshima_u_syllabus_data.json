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
import matplotlib

# Set Japanese font for Windows
plt.rcParams['font.family'] = 'MS Gothic'


def main():
    # 1. Load Data
    print("Loading data...")
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        vector_path = os.path.join(base_dir, "syllabus_vectors.json")
        metadata_path = os.path.join(base_dir, "course_metadata.json")

        with open(vector_path, "r", encoding="utf-8") as f:
            vector_data = json.load(f)
        with open(metadata_path, "r", encoding="utf-8") as f:
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
    # Create cluster labels for legend
    cluster_labels = {}
    for i in range(k):
        top_features_ind = centers[i].argsort()[-3:][::-1] # Top 3 words
        top_words = [index_to_word.get(ind, f"word_{ind}") for ind in top_features_ind]
        cluster_labels[i] = f"{i}: {', '.join(top_words)}"

    # Add labels for legend
    handles, _ = scatter.legend_elements()
    legend_labels = [cluster_labels[int(h.get_label().split("$\\mathdefault{")[1].split("}$")[0])] if "mathdefault" in h.get_label() else cluster_labels[i] for i, h in enumerate(handles)]
    
    # Simpler approach for legend labels since scatter.legend_elements returns handles in order of unique sorted values
    # We can just map indices
    sorted_unique_clusters = np.sort(np.unique(clusters))
    legend_labels = [cluster_labels[cluster_id] for cluster_id in sorted_unique_clusters]
    
    legend1 = ax.legend(handles, legend_labels, title="Clusters", loc="upper right", bbox_to_anchor=(1.1, 1))
    ax.add_artist(legend1)
    
    ax.set_title(f"Syllabus Clusters (t-SNE + K-Means k={k})\nTip: Hover to see Course Name")
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    ax.set_zlabel("t-SNE 3")
    
    # --- Interaction: Hover to show Course Name ---
    # Retrieve course titles for annotations
    course_titles = []
    for cid in course_ids:
        info = metadata.get(cid, {})
        course_titles.append(info.get("n", cid))
    
    annotation = ax.text2D(0.05, 0.95, "", transform=ax.transAxes, color='black', fontsize=12, fontweight='bold', bbox=dict(boxstyle="round", fc="white", alpha=0.9))
    
    def on_mouse_move(event):
        if event.inaxes != ax:
            return
        
        # Project 3D points to 2D
        # This is a bit complex in Matplotlib 3D but standard pick_event is easier
        pass

    # Using 'pick_event' is more reliable for 3D scatter
    scatter.set_picker(True) # Enable picking with default tolerance
    
    def on_pick(event):
        if event.artist != scatter:
            return
        
        # Get index of the picked point
        ind = event.ind[0]
        
        # Get coordinates
        x, y, z = projections[ind]
        
        # Update annotation content
        title = course_titles[ind]
        cluster_id = clusters[ind]
        label = cluster_labels[cluster_id]
        
        annotation.set_text(f"Course: {title}\nCluster: {label}")
        # Redraw
        fig.canvas.draw_idle()

    # fig.canvas.mpl_connect('motion_notify_event', on_mouse_move) # Hover is hard in 3D
    # Use click/pick instead? Or attempt hover with pick?
    # mpl_connect('motion_notify_event') can trigger pick if we manually check, but performant 3D hover is tricky.
    # Let's stick to 'on_pick' which works on CLICK usually, but can work on hover if we use 'motion_notify_event' + self-check or if backend supports it.
    # Actually, standard scatter picking is on click. Let's make it click-based for reliability as requested "hover/click".
    
    fig.canvas.mpl_connect('pick_event', on_pick)
    print("Interaction enabled: Click on points to see Course Name.")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
