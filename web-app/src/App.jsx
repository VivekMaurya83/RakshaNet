import React, { useState } from 'react'
import Dashboard from './pages/Dashboard'
import FraudGraph from './pages/FraudGraph'
import Heatmap from './pages/Heatmap'
import CurrencyAnalysis from './pages/CurrencyAnalysis'
import EvidenceCenter from './pages/EvidenceCenter'
import Settings from './pages/Settings'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between">
        <div>
          <div className="h-20 flex items-center px-6 border-b border-slate-800">
            <span className="text-xl font-bold text-blue-500 tracking-wider">RAKSHANET</span>
          </div>
          <nav className="p-4 space-y-2">
            {[
              { id: 'dashboard', name: 'Dashboard' },
              { id: 'currency', name: 'Counterfeit Currency' },
              { id: 'network', name: 'Fraud Network Graph' },
              { id: 'heatmap', name: 'Geospatial Heatmap' },
              { id: 'evidence', name: 'Evidence Packages' },
              { id: 'settings', name: 'Settings' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
          RakshaNet v2.0.0 (MVP)
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-20 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900">
          <h1 className="text-lg font-semibold uppercase tracking-wider text-slate-300">
            {activeTab.replace('-', ' ')}
          </h1>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-slate-200">Officer Ramesh Sharma</p>
              <p className="text-xs text-slate-500">Super Admin / Analyst</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold">
              RS
            </div>
          </div>
        </header>

        {/* Render Page Components dynamically */}
        <section className="flex-1 p-8 overflow-y-auto bg-slate-950">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'currency' && <CurrencyAnalysis />}
          {activeTab === 'network' && <FraudGraph />}
          {activeTab === 'heatmap' && <Heatmap />}
          {activeTab === 'evidence' && <EvidenceCenter />}
          {activeTab === 'settings' && <Settings />}
        </section>
      </main>
    </div>
  )
}
