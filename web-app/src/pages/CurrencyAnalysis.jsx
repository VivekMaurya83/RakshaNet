import React, { useState, useRef, useEffect } from 'react'

export default function CurrencyAnalysis() {
  // Image and Scanning State
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  
  // Results State
  const [analysisResult, setAnalysisResult] = useState(null)
  const [isReporting, setIsReporting] = useState(false)
  const [reportId, setReportId] = useState(null)

  const videoRef = useRef(null)
  const streamRef = useRef(null)

  // Clean up camera stream on unmount
  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  // Drag & Drop Handlers
  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0])
    }
  }

  const processFile = (file) => {
    if (!file.type.startsWith('image/')) {
      setErrorMessage('Please upload a valid image file.')
      return
    }
    setErrorMessage('')
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setAnalysisResult(null)
    setReportId(null) // Reset reported state
    stopCamera()
  }

  // Camera Management
  const startCamera = () => {
    setErrorMessage('')
    setSelectedFile(null)
    setPreviewUrl(null)
    setAnalysisResult(null)
    setReportId(null) // Reset reported state
    setIsCameraActive(true)
  }

  const stopCamera = () => {
    setIsCameraActive(false)
  }

  // Handle camera stream toggling with DOM lifecycle alignment
  useEffect(() => {
    let activeStream = null
    
    const enableCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } } 
        })
        activeStream = stream
        streamRef.current = stream
        if (videoRef.current) {
          videoRef.current.srcObject = stream
          videoRef.current.play().catch(e => console.error("Video play failed:", e))
        }
      } catch (err) {
        console.error("Camera access error:", err)
        setErrorMessage('Could not access device camera. Please check permissions.')
        setIsCameraActive(false)
      }
    }

    if (isCameraActive) {
      enableCamera()
    } else {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
    }

    return () => {
      if (activeStream) {
        activeStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [isCameraActive])

  const capturePhoto = () => {
    if (!videoRef.current) return

    const canvas = document.createElement('canvas')
    canvas.width = videoRef.current.videoWidth || 640
    canvas.height = videoRef.current.videoHeight || 480
    const ctx = canvas.getContext('2d')
    
    // Draw current video frame to canvas
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)
    
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'captured_banknote.jpg', { type: 'image/jpeg' })
        processFile(file)
      }
    }, 'image/jpeg', 0.95)
  }

  // API Calls
  const handleAnalyze = async () => {
    if (!selectedFile) {
      setErrorMessage('Please upload or capture a banknote photo first.')
      return
    }

    setIsLoading(true)
    setErrorMessage('')
    setAnalysisResult(null)
    setReportId(null) // Reset reported state

    const formData = new FormData()
    formData.append('image', selectedFile)

    try {
      const response = await fetch('http://localhost:8000/api/v1/currency/analyze', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        const errDetail = await response.json().catch(() => ({}))
        throw new Error(errDetail.detail || `Server error (Status ${response.status})`)
      }
      
      const data = await response.json()
      const mappedData = {
        scanId: data.scanId,
        denomination: 500,
        isCounterfeit: data.prediction === 'Counterfeit',
        confidence: data.confidence,
        anomalies: data.detectedFeatures || [],
        aiExplanation: data.explanation,
        canReport: data.canReport,
        imagePath: data.imagePath
      }
      setAnalysisResult(mappedData)
    } catch (err) {
      setErrorMessage(`Verification request failed: ${err.message}. Make sure the backend service is running.`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReport = async () => {
    if (!analysisResult) return

    setIsReporting(true)
    setErrorMessage('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/currency/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          scanId: analysisResult.scanId,
          imagePath: analysisResult.imagePath,
          prediction: analysisResult.isCounterfeit ? 'Counterfeit' : 'Genuine',
          confidence: analysisResult.confidence
        })
      })

      if (!response.ok) {
        const errDetail = await response.json().catch(() => ({}))
        throw new Error(errDetail.detail || `Server error (Status ${response.status})`)
      }

      const data = await response.json()
      setReportId(data.reportId)
    } catch (err) {
      setErrorMessage(`Failed to save local report: ${err.message}`)
    } finally {
      setIsReporting(false)
    }
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Overview Intro */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-extrabold text-white tracking-wide">Banknote Auditor Workspace</h2>
          <p className="text-slate-400 text-sm mt-1">Audit currency security features using hybrid OpenCV preprocessing, local ONNX neural networks, and Gemini descriptions.</p>
        </div>
        <div className="mt-4 md:mt-0 flex space-x-3">
          <button 
            onClick={isCameraActive ? stopCamera : startCamera}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-all border ${
              isCameraActive 
                ? 'bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20' 
                : 'bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700'
            }`}
          >
            {isCameraActive ? '🔌 Close Viewfinder' : '📷 Use Device Camera'}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-950/30 border border-red-500/20 rounded-xl flex items-center space-x-3 text-red-400 text-sm">
          <span>⚠️ {errorMessage}</span>
        </div>
      )}

      {/* Main Panel grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Upload & Preview Terminal */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 lg:col-span-2 flex flex-col justify-between min-h-[450px]">
          <div className="flex-1 flex flex-col justify-center">
            
            {/* Live Camera Viewfinder */}
            {isCameraActive && (
              <div className="relative rounded-xl overflow-hidden bg-black aspect-video border border-slate-800">
                <video ref={videoRef} className="w-full h-full object-cover" playsInline muted />
                <div className="absolute bottom-4 left-0 right-0 flex justify-center">
                  <button 
                    onClick={capturePhoto}
                    className="w-14 h-14 rounded-full border-4 border-white bg-red-600 active:scale-95 transition-transform flex items-center justify-center shadow-lg"
                  />
                </div>
              </div>
            )}

            {/* Static Image Preview */}
            {previewUrl && !isCameraActive && (
              <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-slate-950 flex items-center justify-center aspect-video">
                <img src={previewUrl} className="max-h-[320px] w-auto object-contain rounded-lg" alt="Scanned bill" />
                <button 
                  onClick={() => { setSelectedFile(null); setPreviewUrl(null); setAnalysisResult(null); }}
                  className="absolute top-3 right-3 bg-black/75 hover:bg-black text-white p-2 rounded-full transition-colors text-xs font-bold"
                >
                  ❌ Remove
                </button>
              </div>
            )}

            {/* Drag and Drop Zone */}
            {!previewUrl && !isCameraActive && (
              <div 
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className="border-2 border-dashed border-slate-800 rounded-2xl p-8 flex flex-col items-center justify-center bg-slate-950/20 hover:bg-slate-950/40 hover:border-slate-700 transition-all cursor-pointer h-72"
              >
                <input 
                  type="file" 
                  id="banknote-upload" 
                  className="hidden" 
                  accept="image/*"
                  onChange={handleFileChange}
                />
                <label htmlFor="banknote-upload" className="flex flex-col items-center cursor-pointer">
                  <div className="w-14 h-14 rounded-full bg-blue-500/5 flex items-center justify-center text-blue-500 border border-blue-500/10 mb-4 shadow-inner">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-sm font-semibold text-slate-200">Drag & Drop banknote photograph</p>
                  <p className="text-xs text-slate-500 mt-1.5">or <span className="text-blue-500 underline">browse local folders</span></p>
                </label>
              </div>
            )}
          </div>

          {/* Action Trigger */}
          {selectedFile && !isCameraActive && (
            <button 
              onClick={handleAnalyze}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-3.5 px-6 rounded-xl text-sm transition-all shadow-xl mt-6 self-end w-full md:w-auto"
            >
              {isLoading ? 'Running Preprocessors...' : 'Verify Banknote Security'}
            </button>
          )}
        </div>

        {/* Audit Results Panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-extrabold text-white border-b border-slate-800 pb-3 uppercase tracking-wider">Live Audit Results</h3>
            
            {!analysisResult && !isLoading && (
              <div className="h-64 flex flex-col items-center justify-center text-center text-slate-500">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor" className="w-12 h-12 mb-3 opacity-30">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5M6 7.5h3v3H6v-3z" />
                </svg>
                <p className="text-xs">Upload or snap a banknote scan to inspect security parameters.</p>
              </div>
            )}

            {/* Spinner state */}
            {isLoading && (
              <div className="h-64 flex flex-col items-center justify-center space-y-4">
                <div className="w-10 h-10 border-4 border-blue-500/25 border-t-blue-500 rounded-full animate-spin" />
                <p className="text-xs text-slate-400 font-semibold uppercase tracking-widest animate-pulse">Pre-processing image...</p>
              </div>
            )}

            {/* Verification Result Display */}
            {analysisResult && !isLoading && (
              <div className="space-y-6 mt-4">
                
                {/* Genuine Counterfeit Header */}
                <div className="flex justify-between items-center p-4 rounded-xl bg-slate-950 border border-slate-800">
                  <div>
                    <p className="text-[10px] text-slate-500 uppercase font-extrabold tracking-wider">Classification Verdict</p>
                    <p className={`text-lg font-black mt-1 ${analysisResult.isCounterfeit ? 'text-red-500' : 'text-emerald-500'}`}>
                      {analysisResult.isCounterfeit ? 'COUNTERFEIT BILL' : 'GENUINE BILL'}
                    </p>
                  </div>
                  <span className={`px-2.5 py-1 text-[10px] font-black rounded border ${
                    analysisResult.isCounterfeit 
                      ? 'text-red-400 bg-red-500/10 border-red-500/20' 
                      : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
                  }`}>
                    ₹{analysisResult.denomination}
                  </span>
                </div>

                {/* Progress bar Confidence indicator */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs font-semibold text-slate-400">
                    <span>Audit Confidence Level</span>
                    <span className={analysisResult.isCounterfeit ? 'text-red-400' : 'text-emerald-400'}>
                      {analysisResult.confidence}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-800">
                    <div 
                      className={`h-full rounded-full transition-all duration-1000 ${
                        analysisResult.isCounterfeit ? 'bg-red-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${analysisResult.confidence}%` }}
                    />
                  </div>
                </div>

                {/* Anomalies listed */}
                {analysisResult.isCounterfeit && (
                  <div className="space-y-2">
                    <p className="text-[10px] text-slate-500 uppercase font-extrabold tracking-wider">Anomalies Detected</p>
                    <div className="space-y-1.5">
                      {analysisResult.anomalies.map((item, i) => (
                        <div key={i} className="flex items-center space-x-2 text-xs text-red-300">
                          <span>•</span>
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI explanations */}
                <div className="space-y-2">
                  <p className="text-[10px] text-slate-500 uppercase font-extrabold tracking-wider">AI Audit Briefing</p>
                  <p className="text-xs text-slate-400 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    {analysisResult.aiExplanation}
                  </p>
                </div>

                {/* Recommendation */}
                <div className="space-y-2">
                  <p className="text-[10px] text-slate-500 uppercase font-extrabold tracking-wider">Officer Action Directive</p>
                  <p className="text-xs text-slate-300 font-medium pb-2">
                    {analysisResult.isCounterfeit ? "Submit to authorities for manual verification." : "No action required. Note verified safe."}
                  </p>
                </div>

                {/* RBI General Guidance (Differentiated from Model Output) */}
                <div className="pt-4 border-t border-slate-800/80 space-y-1.5">
                  <p className="text-[9px] text-blue-400 uppercase font-bold tracking-wider">ℹ️ General RBI Security Guidance</p>
                  <p className="text-[10px] text-slate-500 leading-relaxed font-medium">
                    Genuine ₹500 currency notes always contain specific landmarks: a color-shifting windowed security thread, a Mahatma Gandhi watermark matching the main portrait, and visible micro-lettering. Ensure full manual checks if structural checks fail.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Audit Final Verdict Card */}
          {analysisResult && !isLoading && (
            <div className="mt-8 border-t border-slate-800 pt-6 space-y-4">
              {analysisResult.isCounterfeit ? (
                <>
                  <div className="p-3.5 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-xl text-center font-bold">
                    🚨 Banknote Flagged as Suspicious
                  </div>
                  {analysisResult.canReport && (
                    <div className="flex flex-col space-y-2">
                      {reportId ? (
                        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl text-center font-bold">
                          ✓ Local Incident Report Logged: <br />
                          <span className="font-mono text-[10px] text-emerald-300 select-all">{reportId}</span>
                        </div>
                      ) : (
                        <button
                          onClick={handleReport}
                          disabled={isReporting}
                          className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-bold py-2.5 px-4 rounded-xl text-xs transition-all shadow-md"
                        >
                          {isReporting ? 'Saving Local Incident Log...' : '⚠️ Report Suspicious Note'}
                        </button>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl text-center font-bold">
                  ✓ Banknote Verified Safe
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
