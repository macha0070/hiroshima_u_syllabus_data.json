# ==========================================
# Script Name: NetworkX3D002.py
# Description:
#   [EN] Visualizes the course similarity network in 3D.
#        Nodes are courses, edges represent cosine similarity > threshold (0.2).
#        Colors represent the course field.
#   [JP] 授業の類似度ネットワークを3次元で可視化します。
#        ノードは授業を表し、エッジはコサイン類似度がしきい値（0.2）を超えた場合に結ばれます。
#        色は授業の分野を表します。
#
# Data Flow:
#   Input  : syllabus_vectors.json
#          : course_metadata.json
#   Output : (3D Plot Window / 3Dプロットウィンドウ)
# ==========================================

import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics.pairwise import cosine_similarity
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
    vocab_size = len(vector_data["v"])
    sparse_vectors = vector_data["d"]
    course_ids = vector_data["i"]
    
    num_courses = len(course_ids)
    # Create dense matrix (num_courses x vocab_size)
    dense_matrix = np.zeros((num_courses, vocab_size))
    
    for idx, (indices, values) in enumerate(sparse_vectors):
        for col, val in zip(indices, values):
            dense_matrix[idx, col] = val
            
    # 3. Compute Similarity
    print("Computing similarity matrix...")
    sim_matrix = cosine_similarity(dense_matrix)
    
    # 4. Build Graph
    print("Building graph...")
    G = nx.Graph()
    
    # Add nodes with metadata
    for idx, cid in enumerate(course_ids):
        info = metadata.get(cid, {})
        title = info.get("n", cid)
        field = info.get("f", "Unknown")
        G.add_node(cid, title=title, field=field)
        
    # Add edges
    threshold = 0.2
    for i in range(num_courses):
        for j in range(i + 1, num_courses):
            sim = sim_matrix[i, j]
            if sim >= threshold:
                G.add_edge(course_ids[i], course_ids[j], weight=sim)
                
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    
    # Remove isolates (optional, but good for visualization)
    G.remove_nodes_from(list(nx.isolates(G)))
    print(f"Nodes after removing isolates: {G.number_of_nodes()}")

    # 5. Visualize
    print("Visualizing...")
    # Spring layout in 3D
    pos = nx.spring_layout(G, dim=3, k=0.5, seed=42)
    
    # Extract coordinates
    x_nodes = [pos[n][0] for n in G.nodes()]
    y_nodes = [pos[n][1] for n in G.nodes()]
    z_nodes = [pos[n][2] for n in G.nodes()]
    
    # Color mapping by field
    fields = [G.nodes[n]["field"] for n in G.nodes()]
    unique_fields = list(set(fields))
    field_to_color = {f: plt.cm.jet(i / len(unique_fields)) for i, f in enumerate(unique_fields)}
    node_colors = [field_to_color[f] for f in fields]
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Draw nodes
    ax.scatter(x_nodes, y_nodes, z_nodes, c=node_colors, s=50, edgecolors='k')
    
    # Draw edges
    for u, v in G.edges():
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        z = [pos[u][2], pos[v][2]]
        ax.plot(x, y, z, color='gray', alpha=0.3, linewidth=0.5)
        
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=f,
                              markerfacecolor=c, markersize=10) for f, c in field_to_color.items()]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1))
    
    ax.set_title("Syllabus Network Visualization (3D)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
