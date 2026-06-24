import React from 'react'

export default function CurrencyAnalysis() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Scanner Widget */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl md:col-span-2 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white mb-2">Visual Security Verification</h2>
            <p className="text-slate-400 text-sm mb-6">Upload a high-resolution photograph of the banknote to inspect security threads, microtext, and watermarks.</p>
            
            <div className="border-2 border-dashed border-slate-800 rounded-xl p-8 flex flex-col items-center justify-center bg-slate-950/50 hover:bg-slate-900/50 cursor-pointer transition-colors h-64">
              <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-slate-200">Upload banknote image</p>
              <p className="text-xs text-slate-500 mt-1">Supports PNG, JPEG up to 10MB</p>
            </div>
          </div>

          <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg text-sm transition-all shadow-lg mt-6 w-full md:w-auto self-end">
            Execute OpenCV & Model Audit
          </button>
        </div>

        {/* Analysis Indicators */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-6">
          <h3 className="text-base font-bold text-white">Live Audit Analysis</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div>
                <p className="text-xs text-slate-500 font-semibold uppercase">Verification Status</p>
                <p className="text-sm font-semibold text-slate-200 mt-1">Waiting for upload...</p>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-slate-700 animate-pulse"></span>
            </div>
            <div className="flex justify-between items-center p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div>
                <p className="text-xs text-slate-500 font-semibold uppercase">Flagged Anomalies</p>
                <p className="text-sm font-semibold text-slate-200 mt-1">0 Items</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">SAFE</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
