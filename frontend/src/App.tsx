import { useRef, useEffect, useState } from 'react'
import { Niivue } from '@niivue/niivue'
import './App.css'

function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const nvRef = useRef<Niivue | null>(null)
  const [min, setMin] = useState(0)
  const [max, setMax] = useState(1000)
  const [isProcessing, setIsProcessing] = useState(false)

  // Load initial image
useEffect(() => {
  const nv = new Niivue()
  nvRef.current = nv
  nv.attachToCanvas(canvasRef.current!)

  // Use absolute URL in development
  const apiUrl = import.meta.env.DEV 
    ? 'http://localhost:8000/api/image' 
    : '/api/image'

  nv.loadVolumes([{
    url: apiUrl,
    colorMap: "gray",
    opacity: 1
  }]).catch(err => {
    console.error("Failed to load image:", err)
  })
}, [])

  // Apply threshold
  const applyThreshold = async () => {
    setIsProcessing(true)
    try {
      const response = await fetch(`/api/threshold?min_val=${min}&max_val=${max}`)
      const { output } = await response.json()
      
      if (nvRef.current) {
        nvRef.current.loadVolumes([{
          url: output,
          colorMap: "gray",
          opacity: 1,
        }])
      }
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="container">
      <canvas ref={canvasRef} width={800} height={600} />
      
      <div className="controls">
        <h3>Intensity Threshold</h3>
        <div>
          <label>Min: {min}</label>
          <input
            type="range"
            min="0"
            max="2000"
            value={min}
            onChange={(e) => setMin(Number(e.target.value))}
          />
        </div>
        
        <div>
          <label>Max: {max}</label>
          <input
            type="range"
            min="0"
            max="2000"
            value={max}
            onChange={(e) => setMax(Number(e.target.value))}
          />
        </div>
        
        <button 
          onClick={applyThreshold}
          disabled={isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Apply Threshold'}
        </button>
      </div>
    </div>
  )
}

export default App
