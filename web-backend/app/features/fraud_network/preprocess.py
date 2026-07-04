import os
import pandas as pd
import numpy as np
import random

def inject_mule_chains(df: pd.DataFrame, num_chains=200, min_hops=6, max_hops=10) -> pd.DataFrame:
    """
    Injects realistic multi-hop money mule transaction chains (lengths min_hops to max_hops).
    Also injects normal transaction clutter (isFraud=0) on these nodes to prevent overfitting.
    """
    print(f"[*] Injecting {num_chains} multi-hop mule chains (lengths {min_hops}-{max_hops})...")
    new_rows = []
    
    # Get range of steps and amounts from existing data to make them realistic
    min_step, max_step = int(df['step'].min()), int(df['step'].max())
    
    # Get existing accounts to simulate normal interactions (clutter)
    existing_accounts = df['nameOrig'].sample(n=1000, random_state=42).tolist()
    
    for c in range(num_chains):
        hops = np.random.randint(min_hops, max_hops + 1)
        
        # Generate realistic account IDs (C + 10 digits) using random.randint to avoid np.int32 overflow
        victim = f"C{random.randint(1000000000, 9999999999)}"
        mules = [f"C{random.randint(1000000000, 9999999999)}" for _ in range(hops)]
        destination = f"C{random.randint(1000000000, 9999999999)}"
        
        path = [victim] + mules + [destination]
        
        current_step = np.random.randint(min_step, max_step - hops * 2 - 5)
        current_amount = float(np.random.randint(50000, 1000000)) # 50k to 1M INR
        
        for h in range(hops + 1):
            sender = path[h]
            receiver = path[h+1]
            
            # Commission fee: each mule takes a small cut (e.g. 1% to 5%)
            commission = np.random.uniform(0.01, 0.05)
            next_amount = current_amount * (1 - commission)
            
            # 1. Main fraud transaction
            row = {
                'step': current_step,
                'type': 'TRANSFER' if h < hops else 'CASH_OUT',
                'amount': current_amount,
                'nameOrig': sender,
                'oldbalanceOrg': current_amount * 1.2,
                'newbalanceOrig': current_amount * 0.2,
                'nameDest': receiver,
                'oldbalanceDest': 100.0,
                'newbalanceDest': 100.0 + current_amount,
                'isFraud': 1,
                'isFlaggedFraud': 0
            }
            new_rows.append(row)
            
            # 2. Clutter/Noise Injection (to prevent model overfitting on node degrees/chains)
            # 30% chance to generate a normal, non-fraud transaction for this node
            if np.random.random() < 0.3:
                clutter_partner = np.random.choice(existing_accounts)
                clutter_amount = float(np.random.randint(100, 5000))
                clutter_row = {
                    'step': current_step,
                    'type': 'PAYMENT',
                    'amount': clutter_amount,
                    'nameOrig': sender,
                    'oldbalanceOrg': 10000.0,
                    'newbalanceOrig': 10000.0 - clutter_amount,
                    'nameDest': clutter_partner,
                    'oldbalanceDest': 20000.0,
                    'newbalanceDest': 20000.0 + clutter_amount,
                    'isFraud': 0,
                    'isFlaggedFraud': 0
                }
                new_rows.append(clutter_row)
            
            # Advance step and decrease amount for next hop
            current_step += np.random.randint(1, 3) # 1 to 2 step delay
            current_amount = next_amount
            
    injected_df = pd.DataFrame(new_rows)
    df_combined = pd.concat([df, injected_df], ignore_index=True)
    print(f"[+] Injected {len(injected_df)} transactions across {num_chains} fraud chains.")
    return df_combined

def preprocess_dataset(csv_path: str, output_dir: str):
    """
    Preprocesses the PaySim dataset to extract a highly relevant fraud subgraph.
    This keeps the graph size computationally manageable while preserving all fraud chains.
    """
    print(f"[*] Loading PaySim dataset from: {csv_path} ...")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    # Load the dataset
    df = pd.read_csv(csv_path)
    print(f"[+] Loaded {len(df):,} transactions.")
    
    # Inject multi-hop money mule paths
    df = inject_mule_chains(df)

    # 1. Identify core fraud transactions
    fraud_df = df[df['isFraud'] == 1]
    print(f"[+] Found {len(fraud_df):,} fraud transactions.")

    # 2. Extract core fraud accounts (senders and receivers)
    fraud_nodes = set(fraud_df['nameOrig'].unique()).union(set(fraud_df['nameDest'].unique()))
    print(f"[+] Identified {len(fraud_nodes):,} unique accounts directly involved in fraud.")

    # 3. 1-Hop Expansion: Get all transactions connected to these fraud accounts
    # This helps trace the money trail (mule accounts that receive/send money to/from fraud accounts)
    print("[*] Performing 1-hop expansion to trace money trails...")
    connected_df = df[df['nameOrig'].isin(fraud_nodes) | df['nameDest'].isin(fraud_nodes)]
    print(f"[+] Found {len(connected_df):,} transactions in the 1-hop neighborhood.")

    # To ensure the visualization and graph algorithms run instantly, we can cap the size
    # while prioritizing actual fraud transactions
    max_edges = 50000
    if len(connected_df) > max_edges:
        print(f"[!] Downsampling 1-hop neighborhood to {max_edges} transactions for performance...")
        # Keep all fraud transactions, and sample the rest
        fraud_edges = connected_df[connected_df['isFraud'] == 1]
        non_fraud_edges = connected_df[connected_df['isFraud'] == 0].sample(n=max_edges - len(fraud_edges), random_state=42)
        subgraph_df = pd.concat([fraud_edges, non_fraud_edges]).sort_values(by='step')
    else:
        subgraph_df = connected_df

    # 4. Extract all unique nodes in our subgraph
    subgraph_nodes = set(subgraph_df['nameOrig'].unique()).union(set(subgraph_df['nameDest'].unique()))
    print(f"[+] Subgraph contains {len(subgraph_nodes):,} nodes and {len(subgraph_df):,} edges.")

    # 5. Compute Node Features (Phase 2 preparation)
    print("[*] Computing node features...")
    
    # Initialize node feature dict
    node_features = {node: {
        'id': node,
        'total_incoming_val': 0.0,
        'total_outgoing_val': 0.0,
        'trans_count': 0,
        'is_fraud_node': 1 if node in fraud_nodes else 0,
        'node_type': 'Mule' if node.startswith('C') and node in fraud_nodes else ('Merchant' if node.startswith('M') else 'User')
    } for node in subgraph_nodes}

    # Aggregate incoming transactions
    incoming = subgraph_df.groupby('nameDest')['amount'].agg(['sum', 'count'])
    for node, row in incoming.iterrows():
        if node in node_features:
            node_features[node]['total_incoming_val'] = row['sum']
            node_features[node]['trans_count'] += row['count']

    # Aggregate outgoing transactions
    outgoing = subgraph_df.groupby('nameOrig')['amount'].agg(['sum', 'count'])
    for node, row in outgoing.iterrows():
        if node in node_features:
            node_features[node]['total_outgoing_val'] = row['sum']
            node_features[node]['trans_count'] += row['count']

    # Convert to DataFrame
    nodes_df = pd.DataFrame(node_features.values())
    nodes_df['avg_trans_val'] = (nodes_df['total_incoming_val'] + nodes_df['total_outgoing_val']) / np.maximum(nodes_df['trans_count'], 1)
    
    # 6. Save preprocessed files
    os.makedirs(output_dir, exist_ok=True)
    nodes_path = os.path.join(output_dir, 'preprocessed_nodes.csv')
    edges_path = os.path.join(output_dir, 'preprocessed_edges.csv')

    nodes_df.to_csv(nodes_path, index=False)
    subgraph_df.to_csv(edges_path, index=False)

    print(f"[+] Preprocessing complete!")
    print(f"    - Nodes saved to: {nodes_path}")
    print(f"    - Edges saved to: {edges_path}")

if __name__ == '__main__':
    dataset_path = r"D:\HACKATHON_PROJECTS\ET-Hackathon\RakshaNet\web-backend\app\api\v1\dataset\Paysim-graph-dataset.csv"
    output_directory = r"D:\HACKATHON_PROJECTS\ET-Hackathon\RakshaNet\web-backend\app\features\fraud_network\processed"
    preprocess_dataset(dataset_path, output_directory)
