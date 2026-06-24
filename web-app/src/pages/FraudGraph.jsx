import React from 'react'

export default function FraudGraph() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* React Flow Canvas Mock */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 lg:col-span-3 h-[550px] relative overflow-hidden flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-white">Interactive Fraud Network Canvas</h2>
            <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">React Flow Engine</span>
          </div>
          <p className="text-slate-400 text-sm mb-6">Visualizing correlation paths between suspects, fake police IDs, target bank details, and VoIP phone nodes stored in Firestore collections.</p>
        </div>
        
        {/* Node Canvas Area */}
        <div className="flex-1 bg-slate-950 border border-slate-800/80 rounded-xl relative p-4 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:24px_24px]">
          {/* Suspect Node */}
          <div className="absolute top-1/4 left-1/4 bg-red-950/80 border border-red-500 text-red-200 px-4 py-2.5 rounded-lg shadow-lg w-48 text-center">
            <p className="text-[10px] uppercase font-bold text-red-400">Suspect Identity</p>
            <p className="text-xs font-bold mt-1">CBI Officer Kumar</p>
            <span className="text-[9px] bg-red-500/20 px-1.5 py-0.5 rounded text-red-300 font-semibold block mt-1.5 mx-auto w-12">Risk 95</span>
          </div>

          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            <line x1="35%" y1="35%" x2="55%" y2="55%" stroke="#ef4444" strokeWidth="2" strokeDasharray="5" />
            <line x1="55%" y1="55%" x2="75%" y2="25%" stroke="#3b82f6" strokeWidth="2" />
          </svg>

          {/* Phone Node */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 bg-blue-950/80 border border-blue-500 text-blue-200 px-4 py-2.5 rounded-lg shadow-lg w-48 text-center">
            <p className="text-[10px] uppercase font-bold text-blue-400">VoIP Call Node</p>
            <p className="text-xs font-bold mt-1">+91 98765 43210</p>
            <span className="text-[9px] bg-blue-500/20 px-1.5 py-0.5 rounded text-blue-300 font-semibold block mt-1.5 mx-auto w-12">Risk 90</span>
          </div>

          {/* Bank Account Node */}
          <div className="absolute top-1/4 right-1/4 bg-emerald-950/80 border border-emerald-500 text-emerald-200 px-4 py-2.5 rounded-lg shadow-lg w-48 text-center">
            <p className="text-[10px] uppercase font-bold text-emerald-400">Mule Bank Account</p>
            <p className="text-xs font-bold mt-1">SBI Acc: ...56789</p>
            <span className="text-[9px] bg-emerald-500/20 px-1.5 py-0.5 rounded text-emerald-300 font-semibold block mt-1.5 mx-auto w-12">Risk 98</span>
          </div>
        </div>

        <div className="flex justify-between items-center text-xs text-slate-500 mt-4">
          <span>Scroll to zoom | Drag to pan canvas</span>
          <div className="flex space-x-2">
            <span className="w-3 h-3 bg-red-500 rounded-full inline-block"></span><span className="text-[10px]">Critical Suspect</span>
            <span className="w-3 h-3 bg-blue-500 rounded-full inline-block"></span><span className="text-[10px]">Caller ID</span>
            <span className="w-3 h-3 bg-emerald-500 rounded-full inline-block"></span><span className="text-[10px]">Mule Account</span>
          </div>
        </div>
      </div>

      {/* Node Inspector Side Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
        <h3 className="text-base font-bold text-white border-b border-slate-800 pb-3">Node Inspector</h3>
        <div className="space-y-4">
          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
            <p className="text-xs text-slate-500 font-semibold uppercase">Extracted Entity</p>
            <p className="text-sm font-bold text-slate-200 mt-1">CBI Officer Kumar</p>
            <p className="text-xs text-slate-400 mt-2">Source: scam_reports/REPORT_98765</p>
          </div>
          <div className="space-y-2">
            <p className="text-xs text-slate-500 font-bold uppercase">Associated Links</p>
            <div className="flex justify-between text-xs py-1 text-slate-300">
              <span>calls</span>
              <span className="font-semibold text-slate-400">+91 98765 43210</span>
            </div>
            <div className="flex justify-between text-xs py-1 text-slate-300">
              <span>instructs_payment_to</span>
              <span className="font-semibold text-slate-400">SBI Acc: ...56789</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
