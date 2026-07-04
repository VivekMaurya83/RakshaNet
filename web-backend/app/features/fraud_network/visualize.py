import os
import pandas as pd
import networkx as nx
from pyvis.network import Network

def find_mule_chains(G, fraud_nodes, max_depth=5):
    """
    Traces directed money flows starting from known fraud nodes to find laundering chains.
    Returns a list of paths (node lists).
    """
    chains = []
    # Start DFS from nodes that have outgoing transactions and are involved in fraud
    start_nodes = [n for n in fraud_nodes if G.out_degree(n) > 0]
    
    for start in start_nodes[:50]:  # Limit to top 50 starting nodes to avoid path explosion
        for target in G.nodes():
            if start == target:
                continue
            # Find simple paths of length between 3 and max_depth
            try:
                paths = list(nx.all_simple_paths(G, source=start, target=target, cutoff=max_depth))
                for path in paths:
                    if len(path) >= 3:
                        chains.append(path)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
                
    # Sort chains by length descending and remove duplicates
    chains = sorted(chains, key=len, reverse=True)
    unique_chains = []
    seen = set()
    for c in chains:
        c_tuple = tuple(c)
        if c_tuple not in seen:
            seen.add(c_tuple)
            unique_chains.append(c)
            if len(unique_chains) >= 10:  # Keep top 10 longest/most relevant chains
                break
    return unique_chains

def generate_interactive_graph(processed_dir: str, output_html_path: str):
    """
    Loads preprocessed nodes and edges, builds a NetworkX graph,
    detects money mule chains, and generates a highly interactive, professional PyVis HTML map.
    """
    print("[*] Loading preprocessed data...")
    full_nodes_df = pd.read_csv(os.path.join(processed_dir, 'preprocessed_nodes.csv'))
    full_edges_df = pd.read_csv(os.path.join(processed_dir, 'preprocessed_edges.csv'))

    # DOWNSAMPLING FOR VISUALIZATION
    # Vis.js (HTML Canvas) will freeze if given 50,000 edges. 
    # We prioritize rendering all actual fraud transactions and a tiny sample of context edges.
    print("[!] Downsampling graph specifically for HTML rendering (targeting < 3000 edges)...")
    fraud_edges = full_edges_df[full_edges_df['isFraud'] == 1]
    non_fraud_edges = full_edges_df[full_edges_df['isFraud'] == 0]
    
    if len(fraud_edges) > 1000:
        fraud_edges = fraud_edges.sample(n=1000, random_state=42)
        
    if len(non_fraud_edges) > 500:
        non_fraud_edges = non_fraud_edges.sample(n=500, random_state=42)
        
    edges_df = pd.concat([fraud_edges, non_fraud_edges])
    
    # Only keep nodes that belong to these sampled edges
    render_node_ids = set(edges_df['nameOrig']).union(set(edges_df['nameDest']))
    nodes_df = full_nodes_df[full_nodes_df['id'].isin(render_node_ids)]

    # Build NetworkX Directed Graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for _, row in nodes_df.iterrows():
        G.add_node(
            row['id'],
            label=row['id'],
            is_fraud=int(row['is_fraud_node']),
            total_incoming=float(row['total_incoming_val']),
            total_outgoing=float(row['total_outgoing_val']),
            trans_count=int(row['trans_count']),
            avg_trans=float(row['avg_trans_val']),
            node_type=row['node_type']
        )
        
    # Add edges with attributes
    for _, row in edges_df.iterrows():
        G.add_edge(
            row['nameOrig'],
            row['nameDest'],
            amount=float(row['amount']),
            step=int(row['step']),
            type=row['type'],
            is_fraud=int(row['isFraud'])
        )

    print(f"[+] Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

    # Detect Mule Chains
    fraud_nodes = [n for n, attr in G.nodes(data=True) if attr.get('is_fraud') == 1]
    print(f"[*] Tracing money flow chains starting from {len(fraud_nodes)} fraud nodes...")
    mule_chains = find_mule_chains(G, fraud_nodes, max_depth=4)
    print(f"[+] Detected {len(mule_chains)} distinct multi-hop money laundering chains.")

    # Calculate some summary analytics for the dashboard overlay
    total_volume = edges_df['amount'].sum()
    fraud_volume = edges_df[edges_df['isFraud'] == 1]['amount'].sum()
    anomaly_rate = (len(fraud_nodes) / len(G.nodes)) * 100 if len(G.nodes) > 0 else 0.0

    # Initialize PyVis Network
    # We use a dark background and configure physics
    net = Network(height="800px", width="100%", bgcolor="#0f172a", font_color="#f8fafc", directed=True)
    
    # Configure PyVis options for smooth dragging and professional layout
    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.01,
        spring_length=100,
        spring_strength=0.08,
        damping=0.4,
        overlap=1
    )

    # Add nodes to PyVis with custom styling
    for node, attr in G.nodes(data=True):
        is_fraud = attr.get('is_fraud', 0)
        node_type = attr.get('node_type', 'User')
        
        # Color palette
        if is_fraud == 1:
            color = "#ef4444"  # Neon Red for Fraud
            size = 25
            border_color = "#fca5a5"
        elif node_type == 'Merchant':
            color = "#64748b"  # Slate Gray for Merchants
            size = 12
            border_color = "#94a3b8"
        else:
            # Check if this node is connected to fraud (possible mule)
            has_fraud_neighbor = any(G.has_edge(node, fn) or G.has_edge(fn, node) for fn in fraud_nodes)
            if has_fraud_neighbor:
                color = "#f59e0b"  # Amber/Orange for Suspicious Mules
                size = 18
                border_color = "#fcd34d"
            else:
                color = "#0ea5e9"  # Sky Blue for Normal Users
                size = 15
                border_color = "#38bdf8"

        # Create detailed HTML tooltip
        title_html = f"""
        <div style="font-family: sans-serif; padding: 8px; background: #1e293b; color: #f8fafc; border-radius: 6px; border: 1px solid #475569;">
            <b style="color: {color};">Account: {node}</b><br/>
            <b>Type:</b> {node_type}<br/>
            <hr style="border-color: #475569; margin: 4px 0;"/>
            <b>Total Received:</b> ${attr.get('total_incoming', 0.0):,.2f}<br/>
            <b>Total Sent:</b> ${attr.get('total_outgoing', 0.0):,.2f}<br/>
            <b>Avg Transaction:</b> ${attr.get('avg_trans', 0.0):,.2f}<br/>
            <b>Transactions:</b> {attr.get('trans_count', 0)}<br/>
            <b>Status:</b> <span style="color: {color}; font-weight: bold;">{'FRAUDULENT' if is_fraud == 1 else ('SUSPICIOUS' if color == "#f59e0b" else 'NORMAL')}</span>
        </div>
        """
        
        net.add_node(
            node,
            label=node[-5:],  # Show last 5 chars of account ID for cleaner view
            title=title_html,
            color=color,
            size=size,
            borderWidth=2,
            borderWidthSelected=4,
            shape="dot"
        )

    # Add edges to PyVis with custom styling
    for source, target, attr in G.edges(data=True):
        is_fraud = attr.get('is_fraud', 0)
        color = "#f87171" if is_fraud == 1 else "#334155"  # Red for fraud transfers, dark slate for normal
        width = 3 if is_fraud == 1 else 1
        
        edge_title = f"""
        <div style="font-family: sans-serif; padding: 6px; background: #1e293b; color: #f8fafc; border-radius: 4px; border: 1px solid #475569;">
            <b>Amount:</b> ${attr.get('amount', 0.0):,.2f}<br/>
            <b>Type:</b> {attr.get('type')}<br/>
            <b>Step (Hour):</b> {attr.get('step')}<br/>
            <b>Status:</b> <span style="color: {'#ef4444' if is_fraud == 1 else '#38bdf8'};">{'FRAUDULENT' if is_fraud == 1 else 'NORMAL'}</span>
        </div>
        """
        
        net.add_edge(
            source,
            target,
            title=edge_title,
            color=color,
            width=width,
            arrowStrikethrough=False
        )

    # Save initial pyvis graph
    net.save_graph(output_html_path)
    print(f"[+] Initial graph HTML saved to {output_html_path}")

    # 5. Inject Custom Dashboard and JavaScript for interactivity
    print("[*] Injecting professional dashboard overlay and interactive controls...")
    with open(output_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Create the HTML/CSS for the dashboard and the chain highlighter
    dashboard_style = """
    <style>
        body { margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        #mynetwork { background-color: #0f172a !important; }
        
        /* Dashboard Container */
        .dashboard-container {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 340px;
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            color: #f8fafc;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            z-index: 1000;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .dashboard-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 4px;
            color: #ef4444;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .dashboard-subtitle {
            font-size: 0.8rem;
            color: #94a3b8;
            margin-bottom: 16px;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f8fafc;
        }
        
        .stat-label {
            font-size: 0.65rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 2px;
        }
        
        /* Legend */
        .legend-section {
            margin-bottom: 20px;
            border-top: 1px solid #334155;
            padding-top: 12px;
        }
        
        .section-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: #cbd5e1;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
            font-size: 0.8rem;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        /* Chain List */
        .chain-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .chain-item {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chain-item:hover {
            border-color: #ef4444;
            background: #27272a;
        }
        
        .chain-length {
            background: #ef4444;
            color: #fff;
            padding: 2px 6px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.65rem;
        }
        
        /* Controls */
        .reset-btn {
            width: 100%;
            background: #ef4444;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 16px;
            font-size: 0.8rem;
            transition: background 0.2s;
        }
        
        .reset-btn:hover {
            background: #dc2626;
        }
    </style>
    """

    # Build the HTML for the dashboard panel
    dashboard_html = f"""
    <div class="dashboard-container">
        <div class="dashboard-title">
            🛑 RakshaNet MuleMapper
        </div>
        <div class="dashboard-subtitle">
            Money Laundering Trail Analysis (Phase 1)
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{G.number_of_nodes()}</div>
                <div class="stat-label">Total Accounts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #ef4444;">{len(fraud_nodes)}</div>
                <div class="stat-label">Fraud Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #f59e0b;">${total_volume:,.0f}</div>
                <div class="stat-label">Traced Vol</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #ef4444;">{anomaly_rate:.1f}%</div>
                <div class="stat-label">Anomaly Rate</div>
            </div>
        </div>
        
        <div class="legend-section">
            <div class="section-title">Legend</div>
            <div class="legend-item">
                <span class="legend-color" style="background: #ef4444;"></span>
                <span>Fraudulent Account (Flagged/isFraud)</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #f59e0b;"></span>
                <span>Suspicious Account (Mule Candidate)</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #0ea5e9;"></span>
                <span>Normal Account (Transacting Node)</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #64748b;"></span>
                <span>Merchant Account (Sink Node)</span>
            </div>
        </div>
        
        <div class="legend-section">
            <div class="section-title">Detected Money Trails (Chains)</div>
            <div class="chain-list">
    """

    # Add detected chains to the dashboard
    for idx, chain in enumerate(mule_chains):
        chain_label = " → ".join([c[-4:] for c in chain])
        chain_js_array = str(chain)
        dashboard_html += f"""
        <div class="chain-item" onclick="highlightChain({chain_js_array})">
            <span>#{idx+1} {chain_label}</span>
            <span class="chain-length">{len(chain)} Hops</span>
        </div>
        """

    if not mule_chains:
        dashboard_html += "<div style='font-size: 0.75rem; color: #94a3b8;'>No long laundering chains detected in this sample.</div>"

    dashboard_html += """
            </div>
        </div>
        
        <button class="reset-btn" onclick="resetHighlight()">Clear Highlights</button>
    </div>
    """

    # Interactive JavaScript to inject
    interactive_js = """
    <script type="text/javascript">
        // Keep track of original node colors and sizes to reset later
        var originalNodesData = {};
        
        function getNetworkData() {
            if (typeof network !== 'undefined') {
                // Store original styles on first run
                if (Object.keys(originalNodesData).length === 0) {
                    var nodeIds = nodes.getIds();
                    nodeIds.forEach(function(id) {
                        var node = nodes.get(id);
                        originalNodesData[id] = {
                            color: node.color,
                            size: node.size
                        };
                    });
                }
            }
        }

        function highlightChain(nodeIds) {
            getNetworkData();
            
            // Highlight nodes in the chain, dim others
            var allNodeIds = nodes.getIds();
            allNodeIds.forEach(function(id) {
                var node = nodes.get(id);
                if (nodeIds.includes(id)) {
                    // Make chain nodes bigger and keep original color
                    nodes.update({
                        id: id,
                        color: originalNodesData[id].color,
                        size: originalNodesData[id].size * 1.5
                    });
                } else {
                    // Dim non-chain nodes
                    nodes.update({
                        id: id,
                        color: "rgba(100, 116, 139, 0.15)",
                        size: originalNodesData[id].size * 0.8
                    });
                }
            });

            // Highlight edges between nodes in the chain
            var edgeIds = edges.getIds();
            edgeIds.forEach(function(id) {
                var edge = edges.get(id);
                var isChainEdge = false;
                for (var i = 0; i < nodeIds.length - 1; i++) {
                    if (edge.from === nodeIds[i] && edge.to === nodeIds[i+1]) {
                        isChainEdge = true;
                        break;
                    }
                }
                
                if (isChainEdge) {
                    edges.update({
                        id: id,
                        color: "#ef4444",
                        width: 4
                    });
                } else {
                    edges.update({
                        id: id,
                        color: "rgba(51, 65, 85, 0.1)",
                        width: 1
                    });
                }
            });

            // Zoom into the highlighted chain
            network.fit({
                nodes: nodeIds,
                animation: {
                    duration: 1000,
                    easingFunction: "easeInOutQuad"
                }
            });
        }

        function resetHighlight() {
            getNetworkData();
            
            // Restore all nodes to original color and size
            var allNodeIds = nodes.getIds();
            allNodeIds.forEach(function(id) {
                nodes.update({
                    id: id,
                    color: originalNodesData[id].color,
                    size: originalNodesData[id].size
                });
            });

            // Restore all edges to original styling
            var edgeIds = edges.getIds();
            edgeIds.forEach(function(id) {
                var edge = edges.get(id);
                var isFraud = edge.title.includes("FRAUDULENT");
                edges.update({
                    id: id,
                    color: isFraud ? "#f87171" : "#334155",
                    width: isFraud ? 3 : 1
                });
            });

            // Reset zoom
            network.fit({
                animation: {
                    duration: 1000,
                    easingFunction: "easeInOutQuad"
                }
            });
        }
        
        // Initialize original data once network loads
        setTimeout(getNetworkData, 2000);
    </script>
    """

    # Inject CSS, Dashboard HTML, and JS
    html_content = html_content.replace("</head>", f"{dashboard_style}</head>")
    html_content = html_content.replace("<body>", f"<body>{dashboard_html}")
    html_content = html_content.replace("</body>", f"{interactive_js}</body>")

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[+] Custom dashboard overlay successfully injected into {output_html_path}!")

if __name__ == '__main__':
    processed_directory = r"D:\HACKATHON_PROJECTS\ET-Hackathon\RakshaNet\web-backend\app\features\fraud_network\processed"
    output_file = r"D:\HACKATHON_PROJECTS\ET-Hackathon\RakshaNet\web-backend\app\features\fraud_network\mule_map.html"
    generate_interactive_graph(processed_directory, output_file)
