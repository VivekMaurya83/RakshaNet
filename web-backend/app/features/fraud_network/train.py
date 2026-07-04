import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv, GATConv
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score

# 1. Define the Graph Neural Network Model (GraphSAGE)
class FraudSAGE(nn.Module):
    def __init__(self, in_feats, h_feats, out_feats):
        super(FraudSAGE, self).__init__()
        # GraphSAGE layers
        self.conv1 = SAGEConv(in_feats, h_feats)
        self.conv2 = SAGEConv(h_feats, h_feats)
        # Final classification layer
        self.fc = nn.Linear(h_feats, out_feats)

    def forward(self, x, edge_index):
        # First layer with ReLU activation and dropout
        h = self.conv1(x, edge_index)
        h = F.relu(h)
        h = F.dropout(h, p=0.3, training=self.training)
        
        # Second layer
        h = self.conv2(h, edge_index)
        h = F.relu(h)
        
        # Output classification
        out = self.fc(h)
        return out, h  # Return logits and embeddings for visualization/clustering

# 2. Define the Graph Attention Network (GAT) Model as an upgrade option
class FraudGAT(nn.Module):
    def __init__(self, in_feats, h_feats, out_feats, heads=2):
        super(FraudGAT, self).__init__()
        self.conv1 = GATConv(in_feats, h_feats, heads=heads)
        self.conv2 = GATConv(h_feats * heads, h_feats, heads=1)
        self.fc = nn.Linear(h_feats, out_feats)

    def forward(self, x, edge_index):
        h = self.conv1(x, edge_index)
        h = F.elu(h)
        h = F.dropout(h, p=0.3, training=self.training)
        h = self.conv2(h, edge_index)
        h = F.elu(h)
        out = self.fc(h)
        return out, h

def load_graph_data(processed_dir: str):
    """
    Loads preprocessed node and edge CSV files and converts them into
    a PyTorch Geometric Data object with normalized features.
    """
    print("[*] Loading processed CSV files...")
    nodes_df = pd.read_csv(os.path.join(processed_dir, 'preprocessed_nodes.csv'))
    edges_df = pd.read_csv(os.path.join(processed_dir, 'preprocessed_edges.csv'))

    # Map account string IDs to sequential integers [0, num_nodes - 1]
    node_ids = nodes_df['id'].tolist()
    node_to_idx = {nid: idx for idx, nid in enumerate(node_ids)}

    # 1. Build Edge Index
    src_idx = [node_to_idx[src] for src in edges_df['nameOrig']]
    dst_idx = [node_to_idx[dst] for dst in edges_df['nameDest']]
    edge_index = torch.tensor([src_idx, dst_idx], dtype=torch.long)

    # 2. Prepare Node Features
    # Feature columns: total_incoming_val, total_outgoing_val, trans_count, avg_trans_val
    feature_cols = ['total_incoming_val', 'total_outgoing_val', 'trans_count', 'avg_trans_val']
    features = nodes_df[feature_cols].values
    
    # Standardize features (GNNs are sensitive to feature scales)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    x = torch.tensor(features_scaled, dtype=torch.float)

    # 3. Prepare Labels (is_fraud_node)
    y = torch.tensor(nodes_df['is_fraud_node'].values, dtype=torch.long)

    # 4. Create Train/Val/Test Masks
    num_nodes = len(nodes_df)
    indices = np.arange(num_nodes)
    
    # Split: 70% Train, 15% Val, 15% Test
    train_idx, test_idx = train_test_split(indices, test_size=0.3, stratify=nodes_df['is_fraud_node'].values, random_state=42)
    val_idx, test_idx = train_test_split(test_idx, test_size=0.5, stratify=nodes_df.iloc[test_idx]['is_fraud_node'].values, random_state=42)

    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)

    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True

    # Build PyG Data Object
    data = Data(x=x, edge_index=edge_index, y=y)
    data.train_mask = train_mask
    data.val_mask = val_mask
    data.test_mask = test_mask

    print(f"[+] Graph data loaded successfully:")
    print(f"    - Nodes: {data.num_nodes:,}")
    print(f"    - Edges: {data.num_edges:,}")
    print(f"    - Features: {data.num_features}")
    print(f"    - Fraud Nodes in Train: {data.y[train_mask].sum().item()}/{train_mask.sum().item()}")
    
    return data, node_ids

def train_model(processed_dir: str, model_save_path: str):
    # Load data
    data, node_ids = load_graph_data(processed_dir)
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[*] Training on device: {device}")
    
    data = data.to(device)
    
    # Calculate class weights to handle heavy imbalance
    num_fraud = data.y.sum().item()
    num_normal = len(data.y) - num_fraud
    class_weights = torch.tensor([1.0, num_normal / num_fraud], dtype=torch.float).to(device)
    print(f"[*] Class weights (Normal, Fraud): {class_weights.tolist()}")

    # Instantiate GraphSAGE model
    model = FraudSAGE(in_feats=data.num_features, h_feats=64, out_feats=2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    best_val_f1 = 0.0

    print("\n[*] Starting training loop...")
    for epoch in range(1, 101):
        model.train()
        optimizer.zero_grad()
        
        logits, _ = model(data.x, data.edge_index)
        loss = criterion(logits[data.train_mask], data.y[data.train_mask])
        
        loss.backward()
        optimizer.step()

        # Evaluate
        model.eval()
        with torch.no_grad():
            eval_logits, _ = model(data.x, data.edge_index)
            preds = eval_logits.argmax(dim=-1)
            
            # Train metrics
            train_f1 = f1_score(data.y[data.train_mask].cpu(), preds[data.train_mask].cpu(), zero_division=0)
            
            # Val metrics
            val_loss = criterion(eval_logits[data.val_mask], data.y[data.val_mask]).item()
            val_f1 = f1_score(data.y[data.val_mask].cpu(), preds[data.val_mask].cpu(), zero_division=0)

        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:03d} | Train Loss: {loss.item():.4f} | Train F1: {train_f1:.4f} | Val Loss: {val_loss:.4f} | Val F1: {val_f1:.4f}")

        # Save best model
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            torch.save(model.state_dict(), model_save_path)
            
            # Extract and save embeddings
            with torch.no_grad():
                _, embeddings = model(data.x, data.edge_index)
                np.save(os.path.join(processed_dir, 'node_embeddings.npy'), embeddings.cpu().numpy())

    print(f"\n[+] Training completed! Best Validation F1: {best_val_f1:.4f}")
    print(f"[+] Best model checkpoint saved to: {model_save_path}")
    print(f"[+] Node embeddings saved to: {os.path.join(processed_dir, 'node_embeddings.npy')}")

    # Final Test Set Evaluation
    print("\n[*] Running final evaluation on Test Set...")
    model.load_state_dict(torch.load(model_save_path))
    model.eval()
    with torch.no_grad():
        logits, _ = model(data.x, data.edge_index)
        preds = logits.argmax(dim=-1)
        
        test_y = data.y[data.test_mask].cpu().numpy()
        test_preds = preds[data.test_mask].cpu().numpy()
        
        print("\n=== Classification Report (Test Set) ===")
        print(classification_report(test_y, test_preds, target_names=['Normal', 'Fraud']))

if __name__ == '__main__':
    processed_directory = r"D:\HACKATHON_PROJECTS\ET-Hackathon\RakshaNet\web-backend\app\features\fraud_network\processed"
    model_checkpoint = r"D:\HACKATHON_PROJECTS\ET-Hackathon\RakshaNet\web-backend\app\features\fraud_network\mule_sage_model.pt"
    
    # Check if preprocessed files exist
    if not os.path.exists(os.path.join(processed_directory, 'preprocessed_nodes.csv')):
        print("[!] Preprocessed data not found. Please run preprocess.py first!")
    else:
        train_model(processed_directory, model_checkpoint)
