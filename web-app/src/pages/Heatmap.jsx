import React, { useState, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip as ChartTooltip, Cell } from 'recharts'
import 'leaflet/dist/leaflet.css'

// Helper component to control map panning/zooming programmatically
function MapController({ center, zoom }) {
  const map = useMap()
  if (center) {
    map.setView(center, zoom, { animate: true, duration: 1 })
  }
  return null
}

const hotspots = [
  {
    id: 1,
    name: "Jamtara, Jharkhand",
    coords: [24.1167, 86.8000],
    crimeType: "Vishing & UPI Phishing",
    muleAccounts: 450,
    volume: 12500000,
    risk: "Critical",
    color: "#ef4444",
    details: "Known hotspot for phishing calls and fake KYC updates. Money is routed to multiple layers of rented accounts (mules) across Eastern India."
  },
  {
    id: 2,
    name: "Noida Sector-62, UP",
    coords: [28.6219, 77.3639],
    crimeType: "Digital Arrest & Call Centers",
    muleAccounts: 380,
    volume: 9800000,
    risk: "Critical",
    color: "#ef4444",
    details: "Impersonation scams claiming victim's Aadhaar card/mobile number is involved in money laundering. Money is immediately structured and cashed out."
  },
  {
    id: 3,
    name: "Mewat Region, HR/RJ",
    coords: [27.8860, 76.9930],
    crimeType: "Sextortion & OLX Fraud",
    muleAccounts: 310,
    volume: 7200000,
    risk: "High",
    color: "#f97316",
    details: "High concentration of fake listing scams and blackmail. Relies heavily on regional cash-out mules withdrawing funds at local CSP kiosks."
  },
  {
    id: 4,
    name: "Dwarka, New Delhi",
    coords: [28.5859, 77.0607],
    crimeType: "Bank Account Renting",
    muleAccounts: 290,
    volume: 6100000,
    risk: "High",
    color: "#f97316",
    details: "Hub for opening and selling corporate or personal accounts to cybercriminals. Operates as the initial entry point for fraud proceeds."
  },
  {
    id: 5,
    name: "Gurugram, Haryana",
    coords: [28.4595, 77.0266],
    crimeType: "Corporate Investment Scams",
    muleAccounts: 180,
    volume: 4800000,
    risk: "Medium",
    color: "#eab308",
    details: "Fake WhatsApp/Telegram groups promising high stock trading profits. Uses shell company accounts to launder larger transaction tranches."
  },
  {
    id: 6,
    name: "Bengaluru, Karnataka",
    coords: [12.9716, 77.5946],
    crimeType: "Crypto Investment Scams",
    muleAccounts: 150,
    volume: 3500000,
    risk: "Medium",
    color: "#eab308",
    details: "Tech-savvy fraud networks converting stolen fiat currency into crypto assets on P2P exchanges to bypass local bank freezes."
  }
]

// Mock live alert feed
const initialAlerts = [
  { time: "Just now", msg: "Digital Arrest call originating from Jamtara traced to SBI mule in Dwarka", type: "critical" },
  { time: "2m ago", msg: "Bulk cash-out signature detected in Mewat (4 ATM transactions under Rs. 10k)", type: "high" },
  { time: "10m ago", msg: "Noida Sector-62 server IP communicating with payment gateway api", type: "medium" },
]

export default function Heatmap() {
  const [selectedHotspot, setSelectedHotspot] = useState(hotspots[0])
  const [mapCenter, setMapCenter] = useState([24.1167, 86.8000])
  const [mapZoom, setMapZoom] = useState(6)
  const [alerts, setAlerts] = useState(initialAlerts)

  const handleSelectCity = (hotspot) => {
    setSelectedHotspot(hotspot)
    setMapCenter(hotspot.coords)
    setMapZoom(9)
  }

  // Format volume to readable string
  const formatVol = (val) => {
    return `₹${(val / 10000000).toFixed(2)} Cr`
  }

  const chartData = hotspots.map(h => ({
    name: h.name.split(',')[0],
    volume: h.volume / 100000, // Show in Lakhs
    color: h.color
  }))

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)] overflow-hidden">
      {/* Interactive Map Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 lg:col-span-3 h-full flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>📍 Indian Cybercrime Hotspots & Mule Dens</span>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">Leaflet.js Live Layers</span>
            </h2>
            <span className="text-xs text-slate-500 font-medium">Click on markers to view regional laundering pathways</span>
          </div>
          <p className="text-slate-400 text-sm mb-4">
            Geospatial tracking of mule account density and money mule hubs. Map overlay scales according to total transaction volume.
          </p>
        </div>

        {/* Leaflet Map Area */}
        <div className="flex-1 bg-slate-950 border border-slate-800 rounded-xl relative overflow-hidden z-10">
          <MapContainer 
            center={mapCenter} 
            zoom={mapZoom} 
            style={{ height: '100%', width: '100%' }}
            zoomControl={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            
            <MapController center={mapCenter} zoom={mapZoom} />

            {hotspots.map((hotspot) => (
              <CircleMarker
                key={hotspot.id}
                center={hotspot.coords}
                radius={8 + hotspot.muleAccounts / 35}
                fillColor={hotspot.color}
                color={hotspot.color}
                weight={1.5}
                opacity={0.8}
                fillOpacity={0.35}
                eventHandlers={{
                  click: () => {
                    setSelectedHotspot(hotspot)
                    setMapCenter(hotspot.coords)
                    setMapZoom(9)
                  }
                }}
              >
                <Popup className="leaflet-popup-dark">
                  <div className="p-2 text-slate-100 min-w-[200px]">
                    <h3 className="font-bold text-sm text-white border-b border-slate-800 pb-1.5 mb-1.5 flex justify-between">
                      <span>{hotspot.name}</span>
                      <span style={{ color: hotspot.color }} className="text-[10px] uppercase font-bold">{hotspot.risk}</span>
                    </h3>
                    <p className="text-[11px] text-slate-300 mb-1"><strong>Primary Threat:</strong> {hotspot.crimeType}</p>
                    <p className="text-[11px] text-slate-300 mb-1"><strong>Mule Accounts:</strong> {hotspot.muleAccounts}</p>
                    <p className="text-[11px] text-slate-300"><strong>Fraud Volume:</strong> {formatVol(hotspot.volume)}</p>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        {/* Legend / Tip */}
        <div className="flex justify-between items-center text-xs text-slate-500 mt-4">
          <span>Map rendering powered by CartoDB Dark Matter layer</span>
          <div className="flex space-x-4">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#ef4444] rounded-full"></span><span className="text-[10px] text-slate-300">Critical Threat (Red)</span></span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#f97316] rounded-full"></span><span className="text-[10px] text-slate-300">High Threat (Orange)</span></span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-[#eab308] rounded-full"></span><span className="text-[10px] text-slate-300">Medium Threat (Yellow)</span></span>
          </div>
        </div>
      </div>

      {/* Geospatial Analytics Sidebar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between h-full overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-1 space-y-6 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
          <h3 className="text-base font-bold text-white border-b border-slate-800 pb-3">Geospatial Analytics</h3>

          {/* Hotspot details card */}
          {selectedHotspot && (
            <div className="space-y-4">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <p className="text-xs text-slate-500 font-semibold uppercase">Selected Hotspot</p>
                <p className="text-sm font-bold text-white mt-1">{selectedHotspot.name}</p>
                <div className="flex gap-2 items-center mt-2">
                  <span className={`text-[9px] px-2 py-0.5 rounded font-bold ${
                    selectedHotspot.risk === 'Critical' 
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                      : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                  }`}>
                    {selectedHotspot.risk.toUpperCase()} RISK
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono font-semibold">{selectedHotspot.crimeType}</span>
                </div>
              </div>

              <div className="space-y-2 bg-slate-950 border border-slate-800 rounded-lg p-4 text-xs">
                <div className="flex justify-between py-1 text-slate-400 border-b border-slate-800/40">
                  <span>Mule Nodes</span>
                  <span className="font-semibold text-slate-200">{selectedHotspot.muleAccounts} accounts</span>
                </div>
                <div className="flex justify-between py-1 text-slate-400 border-b border-slate-800/40">
                  <span>Est. Crime Value</span>
                  <span className="font-semibold text-red-400">{formatVol(selectedHotspot.volume)}</span>
                </div>
                <div className="py-1 text-slate-400">
                  <span className="block mb-1 text-slate-500 font-bold uppercase tracking-wider text-[10px]">Modus Operandi</span>
                  <p className="text-slate-300 leading-relaxed text-[11px] font-normal">{selectedHotspot.details}</p>
                </div>
              </div>
            </div>
          )}

          {/* Region selector pills */}
          <div className="space-y-2">
            <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Hotspot Registry</label>
            <div className="grid grid-cols-2 gap-2">
              {hotspots.map(h => (
                <button
                  key={h.id}
                  onClick={() => handleSelectCity(h)}
                  className={`px-3 py-2 rounded-lg text-left text-xs font-semibold border transition-all ${
                    selectedHotspot.id === h.id
                      ? 'bg-blue-600/10 text-blue-400 border-blue-500'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <span className="block truncate">{h.name.split(',')[0]}</span>
                  <span className="block text-[10px] text-slate-500 mt-0.5">{formatVol(h.volume)}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Chart Section */}
          <div className="space-y-2">
            <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Laundering Value (₹ in Lakhs)</label>
            <div className="h-[140px] bg-slate-950 border border-slate-800 rounded-lg p-2 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: -10, right: 10, top: 5, bottom: 5 }}>
                  <XAxis type="number" stroke="#475569" fontSize={9} />
                  <YAxis dataKey="name" type="category" stroke="#475569" fontSize={9} width={50} />
                  <ChartTooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }}
                    labelStyle={{ color: '#f1f5f9', fontWeight: 'bold', fontSize: 10 }}
                    itemStyle={{ color: '#ef4444', fontSize: 10 }}
                  />
                  <Bar dataKey="volume" radius={3}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Live Alert Feed */}
          <div className="space-y-2.5">
            <label className="text-xs text-slate-400 font-bold uppercase tracking-wider block flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span>Live Hotspot Traces</span>
            </label>
            <div className="space-y-2">
              {alerts.map((alert, idx) => (
                <div key={idx} className="p-2.5 bg-slate-950 border border-slate-800/80 rounded text-[11px] leading-relaxed">
                  <div className="flex justify-between text-slate-500 font-mono text-[9px] mb-0.5">
                    <span>{alert.time}</span>
                    <span className={`uppercase font-bold ${
                      alert.type === 'critical' ? 'text-red-400' : (alert.type === 'high' ? 'text-orange-400' : 'text-yellow-400')
                    }`}>{alert.type}</span>
                  </div>
                  <p className="text-slate-300 font-normal">{alert.msg}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
