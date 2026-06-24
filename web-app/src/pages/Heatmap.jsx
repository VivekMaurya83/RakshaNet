import React from 'react'

export default function Heatmap() {
  return (
    <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl h-[500px] flex flex-col justify-between">
      <div>
        <h2 className="text-lg font-bold text-white mb-2">Geospatial Crime Hotspots</h2>
        <p className="text-slate-400 text-sm">Visual density map of reported digital arrest calls and counterfeit currency transactions logged via GPS tracking.</p>
      </div>
      <div className="flex-1 bg-slate-950 rounded-xl border border-slate-800 my-4 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Interactive Leaflet.js map layer displaying geofenced hot-zones will load here.</p>
      </div>
      <div className="text-xs text-slate-500">
        Active coordinates logged: Noida, New Delhi, Gurugram, Noida Sector-62.
      </div>
    </div>
  )
}
