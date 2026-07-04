import React, { useEffect, useState } from 'react'
import { Link2, AlertTriangle, Send, Shield, Smartphone, Globe, Landmark, Users } from 'lucide-react'

export default function PatternLinker() {
  const [syndicates, setSyndicates] = useState([])
  const [selectedSyn, setSelectedSyn] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [alertSuccess, setAlertSuccess] = useState(null)
  const [sendingAlert, setSendingAlert] = useState(false)

  // Fetch linked syndicates
  useEffect(() => {
    setLoading(true)
    fetch('http://localhost:8000/api/v1/network/cross-state-linkages')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch cross-state linkages')
        return res.json()
      })
      .then(data => {
        setSyndicates(data)
        if (data.length > 0) {
          setSelectedSyn(data[0])
        }
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Issue inter-state alert directive
  const handleIssueAlert = () => {
    if (!selectedSyn) return
    setSendingAlert(true)
    setAlertSuccess(null)

    const payload = {
      syndicate_name: selectedSyn.name,
      states: selectedSyn.incidents.map(inc => inc.state)
    }

    fetch('http://localhost:8000/api/v1/network/issue-interstate-alert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to issue inter-state alert')
        return res.json()
      })
      .then(data => {
        setAlertSuccess(data.message)
        setSendingAlert(false)
        // Auto clear success message after 4s
        setTimeout(() => setAlertSuccess(null), 4000)
      })
      .catch(err => {
        alert(err.message)
        setSendingAlert(false)
      })
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-200px)] bg-slate-950">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-semibold text-slate-300 mt-4">Running pattern correlation algorithms...</p>
        <p className="text-xs text-slate-500 mt-1">Checking cross-state complaint databases and device signatures</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-200px)] bg-slate-950 p-6 text-center">
        <p className="text-red-400 font-bold text-sm">Failed to connect to pattern linker backend</p>
        <p className="text-xs text-slate-500 mt-2">Make sure the web-backend server is running at http://localhost:8000</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)] overflow-hidden">
      
      {/* Left Column: Active Syndicates List */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col justify-between overflow-hidden">
        <div className="space-y-4 flex-1 overflow-y-auto pr-1">
          <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            <Link2 className="h-5 w-5 text-blue-500" />
            <span>Cross-State Scam Rings</span>
          </h2>
          <p className="text-xs text-slate-400">
            INCIDENT CORRELATOR: Gangs linked by matching device identifiers, VoIP voiceprints, and ATM coordinates across state borders.
          </p>

          <div className="space-y-3 mt-4">
            {syndicates.map(syn => {
              const totalVolume = syn.incidents.reduce((sum, inc) => sum + inc.complaints, 0)
              const isSelected = selectedSyn && selectedSyn.id === syn.id

              return (
                <div
                  key={syn.id}
                  onClick={() => {
                    setSelectedSyn(syn)
                    setAlertSuccess(null)
                  }}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-blue-600/10 border-blue-500/80 shadow-[0_0_15px_rgba(37,99,235,0.1)]'
                      : 'bg-slate-950 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-bold text-white truncate max-w-[180px]">{syn.name}</h3>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      syn.confidence >= 90
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                    }`}>
                      {syn.confidence}% Confidence
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mb-3">{syn.modus_operandi}</p>
                  
                  <div className="flex justify-between items-center text-[10px] text-slate-500 font-semibold border-t border-slate-800/40 pt-2.5">
                    <span>States: {syn.incidents.map(i => i.state).join(', ')}</span>
                    <span className="text-blue-400">{totalVolume} complaints</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="mt-4 border-t border-slate-800 pt-4 text-xs text-slate-500 flex items-center gap-2">
          <Shield className="h-4 w-4 text-blue-500/70" />
          <span>Real-time inter-state intelligence sharing active.</span>
        </div>
      </div>

      {/* Right Area (2 columns): Incident Correlation & Topology */}
      {selectedSyn && (
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 h-full flex flex-col justify-between overflow-hidden">
          <div className="flex-1 overflow-y-auto pr-1 space-y-6">
            
            {/* Header Details */}
            <div className="flex justify-between items-start border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-xl font-bold text-white">{selectedSyn.name}</h3>
                <p className="text-xs text-blue-400 mt-1 font-semibold uppercase tracking-wider">{selectedSyn.modus_operandi}</p>
              </div>
              <button
                onClick={handleIssueAlert}
                disabled={sendingAlert}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all shadow-md"
              >
                {sendingAlert ? (
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <Send className="h-3.5 w-3.5" />
                )}
                <span>Issue Inter-State Alert</span>
              </button>
            </div>

            {/* Alert success banner */}
            {alertSuccess && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs px-4 py-3 rounded-lg flex items-center gap-2.5 animate-fadeIn">
                <Shield className="h-4.5 w-4.5 shrink-0" />
                <span>{alertSuccess}</span>
              </div>
            )}

            {/* Shared Fingerprints Section */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Shared Digital Fingerprints</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {selectedSyn.indicators.map((ind, idx) => (
                  <div key={idx} className="p-3.5 bg-slate-950 border border-slate-850 rounded-xl flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
                      {idx === 0 ? <Smartphone className="h-4.5 w-4.5" /> : idx === 1 ? <Landmark className="h-4.5 w-4.5" /> : <Globe className="h-4.5 w-4.5" />}
                    </div>
                    <span className="text-[11px] text-slate-300 font-medium leading-tight">{ind}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* State Comparison Table */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">State Incident Comparison Table</h4>
              <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-900/50">
                      <th className="p-3 text-slate-400 font-bold">State</th>
                      <th className="p-3 text-slate-400 font-bold">Active Date</th>
                      <th className="p-3 text-slate-400 font-bold">Laundering Volume</th>
                      <th className="p-3 text-slate-400 font-bold">Complaints</th>
                      <th className="p-3 text-slate-400 font-bold">IP Subnet</th>
                      <th className="p-3 text-slate-400 font-bold">Device Signature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedSyn.incidents.map((inc, index) => (
                      <tr key={index} className="border-b border-slate-800/50 last:border-0 hover:bg-slate-900/20">
                        <td className="p-3 font-bold text-white">{inc.state}</td>
                        <td className="p-3 text-slate-300">{inc.date}</td>
                        <td className="p-3 text-red-400 font-bold">{inc.volume}</td>
                        <td className="p-3 text-slate-300">{inc.complaints}</td>
                        <td className="p-3 font-mono text-blue-400">{inc.main_ip}</td>
                        <td className="p-3 text-slate-400 font-mono text-[11px]">{inc.device_signature}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Shared Infrastructure Diagram Mockup */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Correlation Topology (Shared Infrastructure)</h4>
              <div className="h-[180px] bg-slate-950 border border-slate-800 rounded-xl p-6 relative overflow-hidden flex items-center justify-center bg-[url('/grid-dark.svg')] bg-center">
                
                {/* Visual Flow diagram of matching nodes */}
                <div className="flex justify-between items-center w-full max-w-lg z-10 relative">
                  
                  {/* Left Side: States */}
                  <div className="flex flex-col gap-8">
                    {selectedSyn.incidents.map((inc, i) => (
                      <div key={i} className="flex items-center gap-2 p-2 bg-slate-900/80 border border-slate-800 rounded-lg text-[10px] font-bold text-white shadow">
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                        {inc.state} Case
                      </div>
                    ))}
                  </div>

                  {/* Middle Node: Correlator Signature Link */}
                  <div className="relative flex flex-col items-center">
                    {/* Glowing outer rings */}
                    <div className="absolute inset-0 rounded-full bg-red-500/10 scale-150 animate-ping"></div>
                    <div className="w-14 h-14 rounded-full bg-slate-900 border-2 border-red-500 flex flex-col items-center justify-center shadow-lg relative z-10">
                      <Link2 className="h-6 w-6 text-red-400" />
                      <span className="text-[8px] text-red-400 font-bold uppercase mt-0.5">Match</span>
                    </div>
                    <span className="text-[9px] text-slate-400 font-mono mt-2 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                      IMEI: 35928...
                    </span>
                  </div>

                  {/* Right Side: Shared Assets */}
                  <div className="flex flex-col gap-8 text-right">
                    <div className="flex items-center gap-2 p-2 bg-slate-900/80 border border-slate-800 rounded-lg text-[10px] font-bold text-white shadow justify-end">
                      <Landmark className="h-3.5 w-3.5 text-purple-400" />
                      <span>Rented SBI Mule</span>
                    </div>
                    <div className="flex items-center gap-2 p-2 bg-slate-900/80 border border-slate-800 rounded-lg text-[10px] font-bold text-white shadow justify-end">
                      <Smartphone className="h-3.5 w-3.5 text-cyan-400" />
                      <span>Virtual SIM Gateway</span>
                    </div>
                  </div>
                  
                  {/* Dotted Connections background */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" style={{ minHeight: '130px' }}>
                    <line x1="15%" y1="20%" x2="50%" y2="50%" stroke="rgba(239, 68, 68, 0.4)" strokeWidth="1.5" strokeDasharray="4 4" />
                    <line x1="15%" y1="80%" x2="50%" y2="50%" stroke="rgba(239, 68, 68, 0.4)" strokeWidth="1.5" strokeDasharray="4 4" />
                    <line x1="85%" y1="20%" x2="50%" y2="50%" stroke="rgba(239, 68, 68, 0.4)" strokeWidth="1.5" strokeDasharray="4 4" />
                    <line x1="85%" y1="80%" x2="50%" y2="50%" stroke="rgba(239, 68, 68, 0.4)" strokeWidth="1.5" strokeDasharray="4 4" />
                  </svg>

                </div>

              </div>
            </div>

          </div>

          <div className="mt-4 border-t border-slate-800 pt-4 flex items-center gap-2 text-xs text-slate-500 bg-slate-900/30">
            <AlertTriangle className="h-4.5 w-4.5 text-amber-500" />
            <span>Verification matches NCRB state patterns & standard device profiles.</span>
          </div>
        </div>
      )}
    </div>
  )
}
