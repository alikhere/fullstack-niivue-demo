import { useRef, useEffect, useState, useCallback } from 'react'
import { Niivue } from '@niivue/niivue'
import './App.css'

function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const nvRef = useRef<Niivue | null>(null)
  const [threshold, setThreshold] = useState(0) // Default to 0 (full visibility)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Calculate min/max with reversed logic
  const calculateRange = (value: number) => {
    return {
      min: value,  // Now using value as minimum threshold
      max: 1000    // Keeping max fixed at high value
    }
  }

  // Apply threshold to image
  const applyThreshold = useCallback(async (value: number) => {
    setIsProcessing(true)
    setError(null)
    try {
      const {min, max} = calculateRange(value)
      const response = await fetch(
        `http://localhost:8000/api/threshold?min_val=${min}&max_val=${max}`
      )
      
      if (!response.ok) throw new Error(`API error: ${response.status}`)
      
      const { output } = await response.json()
      
      if (nvRef.current) {
        await nvRef.current.loadVolumes([{
          url: `http://localhost:8000${output}`,
          colorMap: "gray",
          opacity: 1,
        }])
      }
    } catch (err) {
      console.error("Threshold error:", err)
      setError(err instanceof Error ? err.message : 'Threshold failed')
    } finally {
      setIsProcessing(false)
    }
  }, [])

  // Initialize Niivue
  useEffect(() => {
    const nv = new Niivue({
      isResizeCanvas: true,
      isRadiologicalConvention: false,
    })
    nvRef.current = nv
    nv.attachToCanvas(canvasRef.current!)

    const loadInitial = async () => {
      try {
        // First load the base image (full visibility at threshold 0)
        await nv.loadVolumes([{
          url: 'http://localhost:8000/api/image',
          colorMap: "gray",
          opacity: 1
        }])
        
        // Apply initial threshold (0 = full visibility)
        await applyThreshold(0)
      } catch (err) {
        console.error("Initial load error:", err)
        setError(err instanceof Error ? err.message : 'Load failed')
      }
    }

    loadInitial()

    return () => { nvRef.current = null }
  }, [applyThreshold])

  // Handle slider changes
  useEffect(() => {
    const timer = setTimeout(() => {
      applyThreshold(threshold)
    }, 300)
    return () => clearTimeout(timer)
  }, [threshold, applyThreshold])

  return (
    <div className="container">
      <canvas ref={canvasRef} width={800} height={600} />
      
      <div className="controls">
        <h3>Intensity Threshold</h3>
        <div>
          <label>Darken: {threshold}</label>
          <input
            type="range"
            min="0"
            max="100"
            step="2"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
          />
        </div>
        {isProcessing && <div className="processing">Processing...</div>}
        {error && <div className="error">{error}</div>}
      </div>
    </div>
  )
}

export default App