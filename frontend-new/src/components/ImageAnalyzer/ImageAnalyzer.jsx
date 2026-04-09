import { useState, useRef } from 'react'
import { ScanSearch, Upload, X } from 'lucide-react'
import { api } from '../../api/client'
import { useToast } from '../../hooks/useToast'
import { StreamingMessage } from '../shared/StreamingMessage'
import './ImageAnalyzer.css'

export function ImageAnalyzer() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef(null)
  const toast = useToast()

  const handleFile = (f) => {
    if (!f) return
    setFile(f)
    setResult(null)
    const reader = new FileReader()
    reader.onload = e => setPreview(e.target.result)
    reader.readAsDataURL(f)
  }

  const handleRemove = (e) => {
    e.stopPropagation()
    setFile(null)
    setPreview(null)
    setResult(null)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    handleFile(e.dataTransfer.files[0])
  }

  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true)
    setResult(null)
    try {
      const data = await api.analyzeImage(file)
      if (data.error) throw new Error(data.error)
      setResult(data.response)
    } catch (err) {
      toast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="image-analyzer">
      <h2 className="tab-heading"><ScanSearch size={18} /> Image Analyzer</h2>

      <div
        className={`drop-zone ${file ? 'has-file' : ''}`}
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        onClick={() => !file && inputRef.current.click()}
      >
        {preview ? (
          <div className="image-preview-wrap">
            <img src={preview} alt="Preview" className="image-preview" />
            <button className="remove-file" onClick={handleRemove}><X size={14} /></button>
          </div>
        ) : (
          <>
            <Upload size={32} strokeWidth={1.2} />
            <p>Drop an image here or click to browse</p>
            <p className="drop-hint">Supports PNG, JPG, JPEG, GIF</p>
          </>
        )}
        <input ref={inputRef} type="file" accept="image/*" hidden onChange={e => handleFile(e.target.files[0])} />
      </div>

      <button className="analyze-btn" onClick={handleAnalyze} disabled={!file || loading}>
        {loading ? <><span className="spinner-white" /> Analyzing…</> : 'Analyze Image'}
      </button>

      {result && (
        <div className="doc-result">
          <StreamingMessage content={result} streaming={false} />
        </div>
      )}
    </div>
  )
}
