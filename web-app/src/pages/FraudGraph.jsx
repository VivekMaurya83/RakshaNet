import React, { useEffect, useRef, useState } from 'react'
import Graph from 'graphology'
import Sigma from 'sigma'

export default function FraudGraph() {
  const containerRef = useRef(null)
  const sigmaRef = useRef(null)
  const overlayCanvasRef = useRef(null)
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Stats
  const [stats, setStats] = useState({
    totalNodes: 0,
    fraudNodes: 0,
    suspiciousNodes: 0,
    anomalyRate: 0,
  })

  // Selected Node for Inspector
  const [selectedNode, setSelectedNode] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showNormal, setShowNormal] = useState(true)
  const [showMerchant, setShowMerchant] = useState(true)
  const [topHubs, setTopHubs] = useState([])
  const [nodeLimit, setNodeLimit] = useState(10000)
  const [minAmount, setMinAmount] = useState(0)
  const [categoryFilter, setCategoryFilter] = useState('all')

  // Fetch graph data
  useEffect(() => {
    setLoading(true)
    fetch('http://localhost:8000/api/v1/network/sigma-graph')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch graph data')
        return res.json()
      })
      .then(data => {
        setGraphData(data)
        
        // Compute stats
        let fraudCount = 0
        let suspiciousCount = 0
        data.nodes.forEach(n => {
          if (n.attributes.is_fraud === 1) fraudCount++
          if (n.attributes.is_suspicious === 1) suspiciousCount++
        })

        setStats({
          totalNodes: data.nodes.length,
          fraudNodes: fraudCount,
          suspiciousNodes: suspiciousCount,
          anomalyRate: ((fraudCount / data.nodes.length) * 100).toFixed(2)
        })

        // Compute top laundering hubs
        const hubs = {}
        data.edges.forEach(e => {
          if (e.attributes.is_fraud === 1) {
            const dest = e.target
            if (!hubs[dest]) {
              hubs[dest] = { id: dest, count: 0, amount: 0.0 }
            }
            hubs[dest].count += 1
            hubs[dest].amount += e.attributes.amount
          }
        })
        const sortedHubs = Object.values(hubs)
          .sort((a, b) => b.amount - a.amount)
          .slice(0, 5)
        setTopHubs(sortedHubs)

        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Initialize Sigma
  useEffect(() => {
    if (!graphData || !containerRef.current) return

    // Create a new graphology graph instance
    const graph = new Graph({ type: 'directed', allowSelfLoops: true })
    
    // Import nodes limited by nodeLimit (with dynamic filters applied)
    const nodesToImport = graphData.nodes.slice(0, nodeLimit);
    nodesToImport.forEach(n => {
      const attrs = n.attributes
      
      // Filter by category tab
      if (categoryFilter === 'fraud' && attrs.is_fraud !== 1) return;
      if (categoryFilter === 'mule' && attrs.is_suspicious !== 1) return;
      if (categoryFilter === 'normal' && (attrs.is_fraud === 1 || attrs.is_suspicious === 1 || attrs.node_type === 'Merchant')) return;
      if (categoryFilter === 'merchant' && attrs.node_type !== 'Merchant') return;

      // Base sizes and colors (adjusted for high-contrast visibility on dark backgrounds)
      let color = '#00f5ff' // High contrast Electric Cyan for normal users
      let size = 6          // Larger size to prevent microscopic rendering

      if (attrs.is_fraud === 1) {
        color = '#ef4444' // Neon red for fraud
        size = 15
      } else if (attrs.is_suspicious === 1) {
        color = '#fbbf24' // High contrast Amber/Gold for mules
        size = 10
      } else if (attrs.node_type === 'Merchant') {
        color = '#a855f7' // High contrast Neon Purple for merchants
        size = 5.5
      }

      graph.addNode(n.key, {
        label: attrs.label,
        x: attrs.x,
        y: attrs.y,
        color: color,
        size: size,
        is_fraud: attrs.is_fraud,
        is_suspicious: attrs.is_suspicious,
        node_type: attrs.node_type,
        total_incoming: attrs.total_incoming,
        total_outgoing: attrs.total_outgoing,
        trans_count: attrs.trans_count,
        avg_trans: attrs.avg_trans
      })
    })

    // Import edges
    graphData.edges.forEach(e => {
      // Filter by minimum transaction amount
      if (minAmount > 0 && e.attributes.amount < minAmount) {
        return
      }

      // Connect only if both nodes are present in the filtered view
      if (graph.hasNode(e.source) && graph.hasNode(e.target)) {
        const is_fraud = e.attributes.is_fraud
        graph.addEdge(e.source, e.target, {
          amount: e.attributes.amount,
          transaction_type: e.attributes.type,
          type: "arrow", // Sigma uses this for rendering, map to arrow
          is_fraud: is_fraud,
          color: is_fraud === 1 ? '#ef4444' : '#1e293b', // Red edges vs Dark slate
          size: is_fraud === 1 ? 1.5 : 0.3
        })
      }
    })

    const sigmaInstance = new Sigma(graph, containerRef.current, {
      allowSelfLoops: true,
      renderLabels: false, // Turn off labels for best raw WebGL performance
      allowInvalidContainer: true, // Suppress zero-width errors on mount
    })

    sigmaRef.current = sigmaInstance

    // Interactive Hover and Selection Styles
    let hoveredNode = null
    
    sigmaInstance.setSetting("nodeReducer", (node, data) => {
      const res = { ...data }
      
      // Node selection state styles
      if (selectedNode) {
        if (node === selectedNode.id) {
          res.highlighted = true
          res.size = Math.max(res.size * 1.8, 16)
          res.label = graph.getNodeAttribute(node, "label")
        } else if (graph.areNeighbors(node, selectedNode.id)) {
          // Keep original color, scale up neighbors, and show their labels
          res.size = res.size * 1.4
          res.label = graph.getNodeAttribute(node, "label")
        } else {
          // Fade everything else out to blend into the background (preserves dark theme, no blue tint)
          res.color = '#0f172a'
          res.label = ''
        }
      } 
      // Node hover state styles
      else if (hoveredNode) {
        if (node === hoveredNode) {
          res.highlighted = true
          res.size = Math.max(res.size * 1.5, 12)
          res.label = graph.getNodeAttribute(node, "label")
        } else if (graph.areNeighbors(node, hoveredNode)) {
          res.size = res.size * 1.2
          res.label = graph.getNodeAttribute(node, "label")
        } else {
          // Fade everything else out to blend into the background
          res.color = '#0f172a'
          res.label = ''
        }
      }
      return res
    })

    sigmaInstance.setSetting("edgeReducer", (edge, data) => {
      const res = { ...data }
      if (selectedNode) {
        const extremes = graph.extremities(edge)
        if (extremes.includes(selectedNode.id)) {
          const isFraudEdge = graph.getEdgeAttribute(edge, "is_fraud") === 1
          res.color = isFraudEdge ? '#ef4444' : '#38bdf8' // Red for fraud, Sky blue for normal transactions
          res.size = isFraudEdge ? 2.5 : 1.5
        } else {
          res.color = 'rgba(15, 23, 42, 0.01)'
          res.size = 0.1
        }
      } else if (hoveredNode) {
        const extremes = graph.extremities(edge)
        if (extremes.includes(hoveredNode)) {
          const isFraudEdge = graph.getEdgeAttribute(edge, "is_fraud") === 1
          res.color = isFraudEdge ? '#ef4444' : '#38bdf8'
          res.size = isFraudEdge ? 1.8 : 1.0
        } else {
          res.color = 'rgba(15, 23, 42, 0.03)'
          res.size = 0.1
        }
      }
      return res
    })

    // Bind event listeners
    sigmaInstance.on('enterNode', (e) => {
      hoveredNode = e.node
      sigmaInstance.refresh()
    })

    sigmaInstance.on('leaveNode', () => {
      hoveredNode = null
      sigmaInstance.refresh()
    })

    sigmaInstance.on('clickNode', (e) => {
      const attrs = graph.getNodeAttributes(e.node)
      setSelectedNode({
        id: e.node,
        ...attrs
      })
    })

    sigmaInstance.on('clickStage', () => {
      setSelectedNode(null)
    })

    // Clean up
    return () => {
      sigmaInstance.kill()
    }
  }, [graphData, showNormal, showMerchant, nodeLimit, minAmount, categoryFilter])

  // Canvas Overlay Animation for selected node (blur everything else out and draw glowing moving dots / trail boxes)
  useEffect(() => {
    if (!selectedNode || !sigmaRef.current || !overlayCanvasRef.current || !graphData) return

    const canvas = overlayCanvasRef.current
    const ctx = canvas.getContext('2d')
    let animationFrameId
    const sigmaInstance = sigmaRef.current
    const graph = sigmaInstance.getGraph()

    // Setup canvas size
    const resizeCanvas = () => {
      if (!canvas) return
      const rect = canvas.parentElement.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = rect.height
    }
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Get ordered transactions connected to the selected node
    const connectedEdges = graphData.edges
      .filter(e => e.source === selectedNode.id || e.target === selectedNode.id)
      // Sort by step ascending (chronological order)
      .sort((a, b) => (a.attributes.step || 0) - (b.attributes.step || 0))
      .slice(0, 15) // Limit to top 15 for high quality visuals

    const draw = () => {
      if (!canvas || !ctx) return
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // 1. Draw a dark semi-transparent backdrop to fade out the background WebGL nodes
      ctx.fillStyle = 'rgba(2, 6, 23, 0.75)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // 2. Draw connections and particles
      connectedEdges.forEach((e, idx) => {
        if (!graph.hasNode(e.source) || !graph.hasNode(e.target)) return

        const srcAttrs = graph.getNodeAttributes(e.source)
        const tgtAttrs = graph.getNodeAttributes(e.target)

        const srcCoords = sigmaInstance.graphToViewport({ x: srcAttrs.x, y: srcAttrs.y })
        const tgtCoords = sigmaInstance.graphToViewport({ x: tgtAttrs.x, y: tgtAttrs.y })

        if (srcCoords && tgtCoords) {
          const isFraud = e.attributes.is_fraud === 1

          // Draw transaction line
          ctx.beginPath()
          ctx.moveTo(srcCoords.x, srcCoords.y)
          ctx.lineTo(tgtCoords.x, tgtCoords.y)
          ctx.strokeStyle = isFraud ? 'rgba(239, 68, 68, 0.4)' : 'rgba(56, 189, 248, 0.4)'
          ctx.lineWidth = isFraud ? 2.5 : 1.5
          ctx.setLineDash([4, 4])
          ctx.stroke()
          ctx.setLineDash([])

          // Draw moving particle (dot)
          const time = Date.now() / 1500
          const t = (time + idx * 0.25) % 1
          const px = srcCoords.x + (tgtCoords.x - srcCoords.x) * t
          const py = srcCoords.y + (tgtCoords.y - srcCoords.y) * t

          ctx.beginPath()
          ctx.arc(px, py, isFraud ? 5 : 4, 0, Math.PI * 2)
          ctx.fillStyle = isFraud ? '#ef4444' : '#38bdf8'
          // Add drop shadow glow
          ctx.shadowBlur = 10
          ctx.shadowColor = isFraud ? '#ef4444' : '#38bdf8'
          ctx.fill()
          ctx.shadowBlur = 0 // Reset shadow

          // Draw transaction label box in the middle of the line
          const mx = (srcCoords.x + tgtCoords.x) / 2
          const my = (srcCoords.y + tgtCoords.y) / 2
          
          const labelText = `#${idx + 1} (${e.attributes.amount >= 1000 ? (e.attributes.amount/1000).toFixed(1) + 'K' : e.attributes.amount})`
          ctx.font = 'bold 9px monospace'
          const textWidth = ctx.measureText(labelText).width
          
          ctx.fillStyle = isFraud ? '#ef4444' : '#0f172a'
          ctx.strokeStyle = isFraud ? '#ef4444' : '#38bdf8'
          ctx.lineWidth = 1
          
          // Draw small trail box background
          ctx.beginPath()
          const paddingX = 4
          const paddingY = 2
          const boxW = textWidth + paddingX * 2
          const boxH = 12 + paddingY * 2
          ctx.roundRect(mx - boxW/2, my - boxH/2, boxW, boxH, 3)
          ctx.fill()
          ctx.stroke()

          // Draw text
          ctx.fillStyle = isFraud ? '#ffffff' : '#e2e8f0'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillText(labelText, mx, my)
        }
      })

      // 3. Redraw the nodes in the foreground so they stand out clearly
      connectedEdges.forEach((e) => {
        const nodesToDraw = [e.source, e.target]
        nodesToDraw.forEach(nodeId => {
          if (!graph.hasNode(nodeId)) return
          
          const nodeAttrs = graph.getNodeAttributes(nodeId)
          const screenCoords = sigmaInstance.graphToViewport({ x: nodeAttrs.x, y: nodeAttrs.y })
          const displayData = sigmaInstance.getNodeDisplayData(nodeId)
          const nodeSize = displayData ? displayData.size : 5

          if (screenCoords) {
            const isSelected = nodeId === selectedNode.id
            const isFraud = graph.getNodeAttribute(nodeId, "is_fraud") === 1
            const isSuspicious = graph.getNodeAttribute(nodeId, "is_suspicious") === 1
            const nodeType = graph.getNodeAttribute(nodeId, "node_type")
            
            // Draw outer halo for selected node
            if (isSelected) {
              const pulse = 10 + Math.sin(Date.now() / 200) * 4
              ctx.beginPath()
              ctx.arc(screenCoords.x, screenCoords.y, nodeSize + pulse, 0, Math.PI * 2)
              ctx.fillStyle = isFraud ? 'rgba(239, 68, 68, 0.15)' : 'rgba(56, 189, 248, 0.15)'
              ctx.fill()
            }

            // Draw node circle
            ctx.beginPath()
            ctx.arc(screenCoords.x, screenCoords.y, nodeSize, 0, Math.PI * 2)
            
            let nodeColor = '#00f5ff' // Default normal user cyan
            if (isFraud) nodeColor = '#ef4444'
            else if (isSuspicious) nodeColor = '#fbbf24'
            else if (nodeType === 'Merchant') nodeColor = '#a855f7'
            
            ctx.fillStyle = nodeColor
            ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.2)'
            ctx.lineWidth = isSelected ? 2 : 1
            ctx.fill()
            ctx.stroke()

            // Draw node ID label text
            const labelText = graph.getNodeAttribute(nodeId, "label")
            ctx.fillStyle = isSelected ? '#ffffff' : '#94a3b8'
            ctx.font = isSelected ? 'bold 10px sans-serif' : '9px sans-serif'
            ctx.textAlign = 'center'
            ctx.textBaseline = 'top'
            ctx.fillText(labelText, screenCoords.x, screenCoords.y + nodeSize + 4)
          }
        })
      })

      animationFrameId = requestAnimationFrame(draw)
    }

    draw()

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('resize', resizeCanvas)
    }
  }, [selectedNode, graphData])

  // Camera action: animate and center view on requested node
  const centerOnNode = (nodeId) => {
    if (!sigmaRef.current) return
    const graph = sigmaRef.current.getGraph()
    if (!graph.hasNode(nodeId)) return

    const nodeDisplayData = sigmaRef.current.getNodeDisplayData(nodeId)
    if (!nodeDisplayData) return

    const attrs = graph.getNodeAttributes(nodeId)
    setSelectedNode({
      id: nodeId,
      ...attrs
    })

    const camera = sigmaRef.current.getCamera()
    camera.animate(
      { x: nodeDisplayData.x, y: nodeDisplayData.y, ratio: 0.12 },
      { duration: 800 }
    )
  }

  // Handle account lookup
  const handleSearch = (e) => {
    e.preventDefault()
    if (!searchQuery.trim() || !graphData) return
    
    // Support searching either exact match or partial end of ID
    const found = graphData.nodes.find(
      n => n.key.toLowerCase() === searchQuery.trim().toLowerCase() ||
           n.key.toLowerCase().endsWith(searchQuery.trim().toLowerCase())
    )
    
    if (found) {
      centerOnNode(found.key)
    } else {
      alert('Account ID not found')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)] overflow-hidden">
      {/* Network visualization container */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 lg:col-span-3 h-full relative overflow-hidden flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>🛑 WebGL Fraud Network Canvas</span>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-red-500/10 text-red-400 border border-red-500/20 rounded animate-pulse">Sigma.js GPU Render</span>
            </h2>
            
            <div className="flex gap-4 items-center bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
              <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={showNormal} 
                  onChange={(e) => setShowNormal(e.target.checked)}
                  className="rounded border-slate-800 bg-slate-950 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-900 w-3.5 h-3.5"
                />
                Show Normal
              </label>

              <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={showMerchant} 
                  onChange={(e) => setShowMerchant(e.target.checked)}
                  className="rounded border-slate-800 bg-slate-950 text-blue-600 focus:ring-blue-500 focus:ring-offset-slate-900 w-3.5 h-3.5"
                />
                Show Merchants
              </label>

              <div className="h-4 w-px bg-slate-800" />

              <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
                <span>Scale:</span>
                <select
                  value={nodeLimit}
                  onChange={(e) => setNodeLimit(Number(e.target.value))}
                  className="bg-slate-950 border border-slate-800 rounded px-2 py-0.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500 cursor-pointer font-semibold"
                >
                  <option value={10000}>10K Nodes</option>
                  <option value={20000}>20K Nodes</option>
                  <option value={40000}>40K Nodes</option>
                  <option value={58169}>All (58K)</option>
                </select>
              </label>
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-4">
            GPU-accelerated rendering of the complete fraud network. Precomputed layout using Louvain Community partition. Hover over nodes to trace links, and click to inspect cash flows.
          </p>
        </div>

        {/* Node Canvas Area */}
        <div className="flex-1 bg-slate-950 border border-slate-800/80 rounded-xl relative overflow-hidden">
          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 z-20">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-sm font-semibold text-slate-300 mt-4">Loading 58,169 nodes & 50,000 edges...</p>
              <p className="text-xs text-slate-500 mt-1">Applying WebGL GPU network rendering pipeline</p>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 z-20 p-6 text-center">
              <p className="text-red-400 font-bold text-sm">Failed to connect to backend service</p>
              <p className="text-xs text-slate-500 mt-2">Make sure the web-backend server is running at http://localhost:8000</p>
            </div>
          )}

          {/* Sigma container */}
          <div ref={containerRef} className="w-full h-full" style={{ position: 'relative' }} />

          {/* Canvas Overlay for high-risk node animations (particle flows, chronological ordering, and blurs) */}
          {selectedNode && (
            <canvas 
              ref={overlayCanvasRef} 
              className="absolute inset-0 z-10 pointer-events-none backdrop-blur-[2px]"
            />
          )}
        </div>

        {/* Legend */}
        <div className="flex justify-between items-center text-xs text-slate-500 mt-4">
          <span>Scroll wheel to zoom | Left-click + drag to pan network</span>
          <div className="flex space-x-4">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#ef4444] rounded-full"></span><span className="text-[10px] text-slate-300">Fraud Node</span></span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#fbbf24] rounded-full"></span><span className="text-[10px] text-slate-300">Mule Candidate</span></span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#00f5ff] rounded-full"></span><span className="text-[10px] text-slate-300">Normal User</span></span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#a855f7] rounded-full"></span><span className="text-[10px] text-slate-300">Merchant</span></span>
          </div>
        </div>
      </div>

      {/* Inspector / Search Sidebar Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between h-full overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-1 space-y-6 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
          <h3 className="text-base font-bold text-white border-b border-slate-800 pb-3">Network Inspector</h3>

          {/* Search form */}
          <form onSubmit={handleSearch} className="space-y-2">
            <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Search Account ID</label>
            <div className="relative">
              <input 
                type="text" 
                placeholder="e.g. C1998372" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
              <button 
                type="submit" 
                className="absolute right-2.5 top-2 text-blue-500 hover:text-blue-400 text-xs font-bold"
              >
                Find
              </button>
            </div>
          </form>

          {/* Dynamic Network Filters Tab */}
          <div className="space-y-4 border-t border-slate-800 pt-4">
            <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Network Filters</label>
            
            {/* Category Filter Grid */}
            <div className="grid grid-cols-3 gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
              {[
                { id: 'all', name: 'All' },
                { id: 'fraud', name: 'Fraud' },
                { id: 'mule', name: 'Mules' },
                { id: 'normal', name: 'Normal' },
                { id: 'merchant', name: 'Merchants' }
              ].map(tab => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setCategoryFilter(tab.id)}
                  className={`text-[9px] py-1 px-1.5 rounded font-semibold text-center truncate transition-all ${
                    categoryFilter === tab.id
                      ? 'bg-blue-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  } ${tab.id === 'merchant' ? 'col-span-2' : ''}`}
                >
                  {tab.name}
                </button>
              ))}
            </div>

            {/* Min Amount Slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px]">
                <span className="text-slate-400">Min Amount:</span>
                <span className="text-blue-400 font-bold font-mono">${minAmount.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="0"
                max="500000"
                step="5000"
                value={minAmount}
                onChange={(e) => setMinAmount(Number(e.target.value))}
                className="w-full h-1 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-blue-500 border border-slate-800"
              />
              <div className="flex justify-between text-[9px] text-slate-500 font-mono">
                <span>$0</span>
                <span>$500K</span>
              </div>
            </div>
          </div>

          {/* Node metadata info / Connected Transactions */}
          <div className="space-y-5">
            {selectedNode ? (
              <div className="space-y-4 animate-fadeIn">
                <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg relative">
                  <button 
                    onClick={() => setSelectedNode(null)}
                    className="absolute top-2 right-2 text-slate-500 hover:text-slate-300 text-xs"
                    title="Clear selection"
                  >
                    ✕
                  </button>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Selected Account</p>
                  <p className="text-sm font-bold text-white mt-1 break-all font-mono">{selectedNode.id}</p>
                  <span className={`inline-block text-[9px] px-2 py-0.5 rounded font-bold mt-2 ${
                    selectedNode.is_fraud === 1 
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                      : (selectedNode.is_suspicious === 1
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-blue-500/20 text-blue-400 border border-blue-500/30')
                  }`}>
                    {selectedNode.is_fraud === 1 ? 'FRAUD NODE' : (selectedNode.is_suspicious === 1 ? 'SUSPICIOUS MULE' : 'NORMAL USER')}
                  </span>
                </div>

                <div className="space-y-2 bg-slate-950 border border-slate-800 rounded-lg p-4 text-xs">
                  <div className="flex justify-between py-1 text-slate-400 border-b border-slate-800/40">
                    <span>Node Type</span>
                    <span className="font-semibold text-slate-200">{selectedNode.node_type}</span>
                  </div>
                  <div className="flex justify-between py-1 text-slate-400 border-b border-slate-800/40">
                    <span>Transactions</span>
                    <span className="font-semibold text-slate-200">{selectedNode.trans_count}</span>
                  </div>
                  <div className="flex justify-between py-1 text-slate-400 border-b border-slate-800/40">
                    <span>Total Sent</span>
                    <span className="font-semibold text-red-400">${selectedNode.total_outgoing.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-1 text-slate-400 border-b border-slate-800/40">
                    <span>Total Received</span>
                    <span className="font-semibold text-emerald-400">${selectedNode.total_incoming.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between py-1 text-slate-400">
                    <span>Avg Transaction</span>
                    <span className="font-semibold text-slate-200">${selectedNode.avg_trans.toLocaleString()}</span>
                  </div>
                </div>

                {/* Connected Transactions Table */}
                <div className="space-y-2">
                  <p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Connected Transactions Trail</p>
                  <div className="space-y-1.5 max-h-[220px] overflow-y-auto pr-1">
                    {graphData.edges
                      .filter(e => e.source === selectedNode.id || e.target === selectedNode.id)
                      .slice(0, 10)
                      .map((e, idx) => {
                        const isOutgoing = e.source === selectedNode.id;
                        const peer = isOutgoing ? e.target : e.source;
                        const isFraudTx = e.attributes.is_fraud === 1;
                        return (
                          <div 
                            key={idx}
                            onClick={() => centerOnNode(peer)}
                            className={`p-2.5 rounded border text-[11px] cursor-pointer transition-all flex flex-col gap-1 ${
                              isFraudTx 
                                ? 'bg-red-950/20 border-red-500/20 hover:border-red-500/50' 
                                : 'bg-slate-950 border-slate-800/60 hover:border-blue-500/30'
                            }`}
                          >
                            <div className="flex justify-between font-mono">
                              <span className={isOutgoing ? 'text-amber-500' : 'text-emerald-500'}>
                                {isOutgoing ? '➔ Sent To' : '➔ Recv From'}
                              </span>
                              <span className="text-slate-400">{peer.slice(-5)}</span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-slate-500 text-[10px] uppercase font-semibold">{e.attributes.transaction_type || 'TRANSFER'}</span>
                              <span className={`font-bold ${isFraudTx ? 'text-red-400' : 'text-slate-200'}`}>
                                ${e.attributes.amount.toLocaleString()}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-5">
                <div className="text-center py-6 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-500">
                  Click a node in the graph to inspect its fraud details and trace connected transactions.
                </div>

                {/* Top Laundering Hubs List */}
                <div className="space-y-2">
                  <p className="text-xs text-slate-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                    <span>Top Laundering Hubs</span>
                  </p>
                  <p className="text-[11px] text-slate-500">Destination accounts receiving the highest volume of mule/fraud transfers:</p>
                  <div className="space-y-2">
                    {topHubs.map((hub, idx) => (
                      <div 
                        key={hub.id} 
                        onClick={() => centerOnNode(hub.id)}
                        className="flex justify-between items-center p-2.5 rounded bg-slate-950 hover:bg-red-950/10 border border-slate-800/80 hover:border-red-500/30 cursor-pointer transition-all"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-slate-500 font-bold w-4">#{idx+1}</span>
                          <span className="text-[11px] font-mono text-slate-300">{hub.id}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-[11px] text-red-400 font-bold">${Math.round(hub.amount).toLocaleString()}</div>
                          <div className="text-[9px] text-slate-500">{hub.count} transactions</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Dataset Stats */}
        <div className="space-y-3 border-t border-slate-800 pt-4 mt-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Dataset Stats</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-950 border border-slate-800 p-2.5 rounded text-center">
              <div className="text-slate-400 text-[10px]">Total Nodes</div>
              <div className="font-bold text-white mt-0.5">{stats.totalNodes.toLocaleString()}</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-2.5 rounded text-center">
              <div className="text-red-400 text-[10px]">Fraud Nodes</div>
              <div className="font-bold text-red-400 mt-0.5">{stats.fraudNodes.toLocaleString()}</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-2.5 rounded text-center">
              <div className="text-amber-400 text-[10px]">Suspicious Mules</div>
              <div className="font-bold text-amber-400 mt-0.5">{stats.suspiciousNodes.toLocaleString()}</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 p-2.5 rounded text-center">
              <div className="text-slate-400 text-[10px]">Anomaly Rate</div>
              <div className="font-bold text-white mt-0.5">{stats.anomalyRate}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
