# ==========================================
# Script Name: NetworkX2D002.py
# Description:
#   [EN] Visualizes the course similarity network in 2D with attached Skill/Tag nodes.
#        Nodes are courses and Skills (e.g., "Experiment", "Seminar").
#   [JP] 授業の類似度ネットワークを2次元で可視化し、スキル/タグノードを付加します。
#
# Data Flow:
#   Input  : syllabus_vectors.json
#          : course_metadata.json
#   Output : (2D Plot Window)
# ==========================================


# ==========================================
# Script Name: NetworkX2D002.py
# Description:
#   [EN] Visualizes the course similarity network in 2D with attached Skill/Tag nodes.
#        **Interactive**: Hover to see details, Click legend to toggle groups.
#   [JP] 授業の類似度ネットワークを2次元で可視化し、スキル/タグノードを付加します。
#        **インタラクティブ機能**: カーソルを合わせると詳細表示、凡例クリックで表示/非表示切り替え。
#
# Data Flow:
#   Input  : syllabus_vectors.json
#          : course_metadata.json
#   Output : (Interactive 2D Plot Window)
# ==========================================

import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import os

# Global references for interactivity
scatters = {}
legend_map = {}
annot = None

def main():
    global annot, scatters, legend_map
    
    # 1. Load Data
    print("Loading data...")
    try:
        # Resolve paths relative to this script file
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
    vocab_size = len(vector_data["v"])
    sparse_vectors = vector_data["d"]
    course_ids = vector_data["i"]
    skills_data = vector_data.get("skills", [])
    
    num_courses = len(course_ids)
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
    
    # Add Course Nodes
    for idx, cid in enumerate(course_ids):
        info = metadata.get(cid, {})
        title = info.get("n", cid)
        field = info.get("f", "Unknown")
        G.add_node(cid, title=title, field=field, node_type="course")
        
    # Add Similarity Edges
    threshold = 0.2
    for i in range(num_courses):
        for j in range(i + 1, num_courses):
            sim = sim_matrix[i, j]
            if sim >= threshold:
                G.add_edge(course_ids[i], course_ids[j], weight=sim, edge_type="similarity")

    # Add Skill Nodes
    print("Adding skill nodes...")
    INTERESTING_PREFIXES = ["tag_", "kw_", "lang_english"]
    added_skills = set()
    
    for idx, cid in enumerate(course_ids):
        if idx >= len(skills_data): break
        course_skills = skills_data[idx]
        for skill in course_skills:
            is_interesting = any(skill.startswith(p) for p in INTERESTING_PREFIXES)
            if is_interesting:
                if skill not in added_skills:
                    G.add_node(skill, title=skill, field="Tag", node_type="skill")
                    added_skills.add(skill)
                G.add_edge(cid, skill, weight=0.5, edge_type="tag_link")

    G.remove_nodes_from(list(nx.isolates(G)))
    print(f"Nodes: {G.number_of_nodes()}")

    # 5. Visualize (Interactive)
    print("Visualizing...")
    plt.rcParams['font.family'] = 'MS Gothic'
    
    pos = nx.spring_layout(G, k=0.15, seed=42)
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Separate nodes by group/field for separate scattering (enables toggling)
    groups = {}
    
    # Group Course Nodes by Field
    course_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "course"]
    for n in course_nodes:
        f = G.nodes[n]["field"]
        if f not in groups: groups[f] = []
        groups[f].append(n)
        
    # Group Skill Nodes
    skill_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "skill"]
    groups["Tag"] = skill_nodes

    # Generate Colors
    unique_fields = sorted(groups.keys())
    # Ensure "Tag" is red, others are jet
    field_to_color = {}
    for i, f in enumerate(unique_fields):
        if f == "Tag":
            field_to_color[f] = "red"
        else:
            field_to_color[f] = plt.cm.jet(i / len(unique_fields))

    # Draw Edges (Static background)
    sim_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "similarity"]
    nx.draw_networkx_edges(G, pos, edgelist=sim_edges, alpha=0.1, edge_color="gray", ax=ax)
    tag_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "tag_link"]
    nx.draw_networkx_edges(G, pos, edgelist=tag_edges, alpha=0.3, edge_color="orange", style="dashed", ax=ax)

    # Draw Nodes Group by Group
    for group_name, nodes in groups.items():
        if not nodes: continue
        
        xy = np.array([pos[n] for n in nodes])
        c = field_to_color[group_name]
        marker = "^" if group_name == "Tag" else "o"
        size = 150 if group_name == "Tag" else 50
        
        # Plot and store artist
        sc = ax.scatter(xy[:, 0], xy[:, 1], c=[c], s=size, marker=marker, label=group_name, edgecolors='w', alpha=0.9)
        scatters[group_name] = sc
        
        # Attach data to the artist for hover lookup
        sc.custom_node_list = nodes
        sc.custom_node_data = [G.nodes[n] for n in nodes]
        sc.custom_node_ids = nodes

    # Labels for Skills (Static)
    skill_labels = {n: n for n in skill_nodes}
    nx.draw_networkx_labels(G, pos, labels=skill_labels, font_size=8, font_color="darkred", font_family='MS Gothic', ax=ax)
    
    # Legend with Picking
    leg = ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1), fancybox=True, shadow=True)
    leg.set_title("Click to Toggle")
    
    # Map legend entries to scatter plots
    for legline, text in zip(leg.get_lines(), leg.get_texts()):
        legline.set_picker(5)  # 5 pts tolerance
        text.set_picker(5)
    # Scatter points in legend are getting handles from scatter
    # We need to map legend handles to the scatter collections
    for handle, text in zip(leg.legend_handles, leg.get_texts()):
        handle.set_picker(5)
        text.set_picker(5)
        lbl = text.get_text()
        if lbl in scatters:
            legend_map[handle] = scatters[lbl]
            legend_map[text] = scatters[lbl]

    # --- Interaction Logic ---
    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(sc, ind):
        # ind["ind"] contains indices of points under cursor
        idx = ind["ind"][0]
        pos_xy = sc.get_offsets()[idx]
        annot.xy = pos_xy
        
        # Get data
        node_title = sc.custom_node_data[idx]['title']
        node_field = sc.custom_node_data[idx]['field']
        
        text = f"{node_title}\n({node_field})"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.9)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            found = False
            for name, sc in scatters.items():
                if not sc.get_visible(): continue # Skip hidden
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(sc, ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    found = True
                    break
            if not found and vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

    def on_pick(event):
        # Event for legend click
        artist = event.artist
        if artist in legend_map:
            sc = legend_map[artist]
            vis = not sc.get_visible()
            sc.set_visible(vis)
            
            # Dim the legend items to show status
            # This is tricky with simple handles, so we leave as is for now
            # or update alpha of the handle
            artist.set_alpha(1.0 if vis else 0.2)
            
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    fig.canvas.mpl_connect("pick_event", on_pick)

    plt.title("Syllabus Network (Interactive)\nHover for Info, Click Legend to Toggle")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

