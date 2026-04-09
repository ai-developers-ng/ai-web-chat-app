import { useState } from 'react'
import { Image, Wand2 } from 'lucide-react'
import { api } from '../../api/client'
import { useToast } from '../../hooks/useToast'
import './ImageGen.css'

export function ImageGen() {
  const [prompt, setPrompt] = useState('')
  const [imageData, setImageData] = useState(null)
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setImageData(null)
    try {
      const data = await api.generateImage(prompt)
      if (data.error) throw new Error(data.error)
      setImageData(data.image)
    } catch (err) {
      toast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    const a = document.createElement('a')
    a.href = `data:image/png;base64,${imageData}`
    a.download = 'generated-image.png'
    a.click()
  }

  return (
    <div className="image-gen">
      <h2 className="tab-heading"><Image size={18} /> Image Generator</h2>

      <div className="image-gen-form">
        <textarea
          className="prompt-textarea"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Describe the image you want to generate… (Ctrl+Enter to generate)"
          rows={6}
          onKeyDown={e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleGenerate() }}
        />
        <button className="generate-btn" onClick={handleGenerate} disabled={!prompt.trim() || loading}>
          {loading ? <><span className="spinner-white" /> Generating…</> : <><Wand2 size={16} /> Generate</>}
        </button>
      </div>

      {imageData && (
        <div className="image-result">
          <img src={`data:image/png;base64,${imageData}`} alt="Generated" className="gen-image" />
          <button className="download-btn" onClick={handleDownload}>Download PNG</button>
        </div>
      )}
    </div>
  )
}
