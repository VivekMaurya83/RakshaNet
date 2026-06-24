import React from 'react'

export default function Settings() {
  return (
    <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl h-96 flex flex-col justify-between">
      <div>
        <h2 className="text-lg font-bold text-white mb-2">Platform Settings</h2>
        <p className="text-slate-400 text-sm">Configure system parameters, Firebase endpoints, and local ONNX model path settings.</p>
      </div>
      <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 my-4 flex items-center justify-center">
        <p className="text-slate-500 text-sm">System credentials & model bindings will display here.</p>
      </div>
    </div>
  )
}
