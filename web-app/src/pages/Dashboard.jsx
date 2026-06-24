import React from 'react'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { name: 'Active Scam Logs', val: '142', change: '+12% this week' },
          { name: 'Counterfeit Flagged', val: '89', change: '+5% this week' },
          { name: 'Fraud Network Hubs', val: '31', change: '8 unresolved' },
          { name: 'Alert Escaped Density', val: 'High', change: 'Region: New Delhi' }
        ].map((stat, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">{stat.name}</p>
            <p className="text-3xl font-bold mt-2 text-white">{stat.val}</p>
            <p className="text-xs text-blue-400 mt-2">{stat.change}</p>
          </div>
        ))}
      </div>
      
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl h-96 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Dashboard analytical graphs will render here.</p>
      </div>
    </div>
  )
}
