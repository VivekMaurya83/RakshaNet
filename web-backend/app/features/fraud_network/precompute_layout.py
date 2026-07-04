import os
import json
import pandas as pd
import networkx as nx
import numpy as np
import community as community_louvain

def main():
    print("[*] Starting layout precomputation...")
    processed_dir = r"D:\HACKATHON_PROJECTS\ET-Hackathon\RakshaNet\web-backend\app\features\fraud_network\processed"
    output_json = os.path.join(processed_dir, "sigma_graph.json")

    # 1. Load Preprocessed Datasets
    print("[*] Loading CSV datasets...")
    nodes_df = pd.read_csv(os.path.join(processed_dir, 'preprocessed_nodes.csv'))
    edges_df = pd.read_csv(os.path.join(processed_dir, 'preprocessed_edges.csv'))

    # Replace NaN values with appropriate defaults
    nodes_df = nodes_df.fillna({
        'is_fraud_node': 0,
        'total_incoming_val': 0.0,
        'total_outgoing_val': 0.0,
        'trans_count': 0,
        'avg_trans_val': 0.0,
        'node_type': 'User'
    })
    edges_df = edges_df.fillna({
        'amount': 0.0,
        'step': 0,
        'type': 'PAYMENT',
        'isFraud': 0
    })

    print(f"[+] Loaded {len(nodes_df)} nodes and {len(edges_df)} edges.")

    # 2. Build Undirected Graph for Louvain Community Detection
    print("[*] Partitioning graph into communities...")
    G_undirected = nx.Graph()
    edges_list = list(zip(edges_df['nameOrig'], edges_df['nameDest']))
    G_undirected.add_edges_from(edges_list)
    G_undirected.add_nodes_from(nodes_df['id'])

    partition = community_louvain.best_partition(G_undirected)
    
    # Group nodes by community
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = []
        communities[comm_id].append(node)

    # Sort communities by size descending
    sorted_comm_ids = sorted(communities.keys(), key=lambda k: len(communities[k]), reverse=True)
    print(f"[+] Found {len(sorted_comm_ids)} distinct communities.")

    # 3. Position Communities using Fermat Spiral Layout
    # Large communities (size > 2) are placed on a spiral near the center.
    # Small/noise communities (size <= 2) are placed on a outer grid.
    print("[*] Computing clustered layout coordinates...")
    community_centers = {}
    
    large_comms = [c for c in sorted_comm_ids if len(communities[c]) > 2]
    small_comms = [c for c in sorted_comm_ids if len(communities[c]) <= 2]

    # Golden angle in radians for Fermat Spiral
    golden_angle = 137.5 * (np.pi / 180.0)
    spacing_spiral = 400.0  # spacing multiplier

    # Place large communities on a Fermat Spiral
    for idx, comm_id in enumerate(large_comms):
        r = spacing_spiral * np.sqrt(idx + 1)
        theta = idx * golden_angle
        community_centers[comm_id] = (r * np.cos(theta), r * np.sin(theta))

    # Place small communities in an outer grid pattern
    # Start the grid far away from the spiral center (max_r + safety margin)
    max_spiral_r = spacing_spiral * np.sqrt(len(large_comms) + 1) if large_comms else 0.0
    start_grid_radius = max_spiral_r + 1000.0
    
    # Layout small communities in a square grid outside the center
    grid_cols = int(np.ceil(np.sqrt(len(small_comms)))) if small_comms else 1
    spacing_grid = 150.0

    for idx, comm_id in enumerate(small_comms):
        col = idx % grid_cols
        row = idx // grid_cols
        # Offset grid to start outside the central spiral
        x = (col - grid_cols / 2) * spacing_grid
        y = (row - len(small_comms) / grid_cols / 2) * spacing_grid
        
        # Project outwards if too close to center
        dist = np.sqrt(x*x + y*y)
        if dist < start_grid_radius:
            if dist == 0:
                x = start_grid_radius
                y = 0.0
            else:
                x = (x / dist) * start_grid_radius
                y = (y / dist) * start_grid_radius
                
        community_centers[comm_id] = (x, y)

    # 4. Position individual nodes in concentric rings around community center
    node_positions = {}
    for comm_id, nodes in communities.items():
        cx, cy = community_centers[comm_id]
        
        # If community has 1 node, put it exactly at center
        if len(nodes) == 1:
            node_positions[nodes[0]] = (cx, cy)
        else:
            for idx, node in enumerate(nodes):
                # concentric rings: 12 nodes per ring
                ring = idx // 12
                ring_idx = idx % 12
                
                # Orbit distance increases per ring
                dist = 40.0 + ring * 25.0
                # Angle around the center
                angle = ring_idx * (2.0 * np.pi / 12.0) + (ring * 0.3)
                
                x = cx + dist * np.cos(angle)
                y = cy + dist * np.sin(angle)
                node_positions[node] = (x, y)

    # 5. Build Graphology JSON structure
    print("[*] Generating optimized JSON structure...")
    sigma_nodes = []
    
    # Convert nodes dataframe to quick lookup map
    nodes_meta = nodes_df.set_index('id').to_dict('index')

    # Identify fraud nodes to style neighbors as suspicious
    fraud_nodes_set = set(nodes_df[nodes_df['is_fraud_node'] == 1]['id'])
    
    # Build a lookup of neighbors from the edges dataframe
    connected_to_fraud = set()
    for _, row in edges_df.iterrows():
        orig = row['nameOrig']
        dest = row['nameDest']
        if orig in fraud_nodes_set or dest in fraud_nodes_set:
            connected_to_fraud.add(orig)
            connected_to_fraud.add(dest)

    for _, row in nodes_df.iterrows():
        node_id = row['id']
        is_fraud = int(row['is_fraud_node'])
        node_type = row['node_type']
        
        # Determine coordinates (default to 0 if not positioned)
        x, y = node_positions.get(node_id, (0.0, 0.0))
        
        is_suspicious = 1 if (node_id in connected_to_fraud and is_fraud == 0) else 0

        sigma_nodes.append({
            "key": node_id,
            "attributes": {
                "label": node_id[-5:],  # Last 5 digits for clean UI
                "x": round(float(x), 1),
                "y": round(float(y), 1),
                "node_type": node_type,
                "is_fraud": is_fraud,
                "is_suspicious": is_suspicious,
                "total_incoming": round(float(row['total_incoming_val']), 1),
                "total_outgoing": round(float(row['total_outgoing_val']), 1),
                "trans_count": int(row['trans_count']),
                "avg_trans": round(float(row['avg_trans_val']), 1)
            }
        })

    sigma_edges = []
    for idx, row in edges_df.iterrows():
        is_fraud = int(row['isFraud'])
        
        sigma_edges.append({
            "key": f"e_{idx}",
            "source": row['nameOrig'],
            "target": row['nameDest'],
            "attributes": {
                "amount": round(float(row['amount']), 1),
                "type": row['type'],
                "is_fraud": is_fraud
            }
        })

    graph_data = {
        "attributes": {},
        "options": {
            "type": "directed",
            "multi": False,
            "allowSelfLoops": True
        },
        "nodes": sigma_nodes,
        "edges": sigma_edges
    }

    # Save to JSON file
    print(f"[*] Saving optimized graph to {output_json}...")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False)
        
    print(f"[+] Successfully generated and saved layout to {output_json}!")

if __name__ == '__main__':
    main()
