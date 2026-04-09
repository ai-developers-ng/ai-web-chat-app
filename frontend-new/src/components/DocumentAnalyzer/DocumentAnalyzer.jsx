import { useState, useRef } from 'react'
import { FileText, Upload, X, Download, Printer, ChevronDown, ChevronUp } from 'lucide-react'
import { api } from '../../api/client'
import { useToast } from '../../hooks/useToast'
import { StreamingMessage } from '../shared/StreamingMessage'
import { exportTextAsMarkdown, exportTextAsPDF } from '../../utils/exportChat'
import './DocumentAnalyzer.css'

const ACCEPT = '.txt,.md,.pdf,.doc,.docx,.png,.jpg,.jpeg'

function ResultCard({ item, index }) {
  const [collapsed, setCollapsed] = useState(false)
  return (
    <div className="doc-result">
      <div className="doc-result-header">
        <div className="doc-result-meta">
          <span className="doc-result-label">
            {index != null ? `${index + 1}. ` : ''}{item.filename}
          </span>
        </div>
        <div className="doc-result-actions">
          <div className="doc-export-btns">
            <button className="doc-export-btn" onClick={() => exportTextAsMarkdown(item.response, `Analysis — ${item.filename}`, `doc-analysis-${Date.now()}.md`)}>
              <Download size={13} /> Markdown
            </button>
            <button className="doc-export-btn" onClick={() => exportTextAsPDF(item.response, `Analysis — ${item.filename}`)}>
              <Printer size={13} /> PDF
            </button>
          </div>
          <button className="collapse-btn" onClick={() => setCollapsed(v => !v)}>
            {collapsed ? <ChevronDown size={15} /> : <ChevronUp size={15} />}
          </button>
        </div>
      </div>
      {!collapsed && <StreamingMessage content={item.response} streaming={false} />}
    </div>
  )
}

export function DocumentAnalyzer() {
  const [files, setFiles] = useState([])       // File[]
  const [results, setResults] = useState([])   // {filename, response}[]
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(null) // "2 / 5"
  const inputRef = useRef(null)
  const toast = useToast()

  const addFiles = (incoming) => {
    const list = Array.from(incoming)
    setFiles(prev => {
      const existing = new Set(prev.map(f => f.name))
      const fresh = list.filter(f => !existing.has(f.name))
      return [...prev, ...fresh]
    })
    setResults([])
  }

  const removeFile = (name) => {
    setFiles(prev => prev.filter(f => f.name !== name))
    setResults([])
  }

  const handleDrop = (e) => {
    e.preventDefault()
    addFiles(e.dataTransfer.files)
  }

  const handleAnalyze = async () => {
    if (!files.length) return
    setLoading(true)
    setResults([])
    const out = []
    for (let i = 0; i < files.length; i++) {
      setProgress(`${i + 1} / ${files.length}`)
      try {
        const data = await api.analyzeDocument(files[i])
        if (data.error) throw new Error(data.error)
        out.push({ filename: files[i].name, response: data.response })
      } catch (err) {
        out.push({ filename: files[i].name, response: `Error: ${err.message}` })
        toast(`${files[i].name}: ${err.message}`, 'error')
      }
    }
    setResults(out)
    setProgress(null)
    setLoading(false)
  }

  const exportAll = (format) => {
    const combined = results.map(r => `## ${r.filename}\n\n${r.response}`).join('\n\n---\n\n')
    if (format === 'md') exportTextAsMarkdown(combined, 'Document Analysis', `doc-analysis-all-${Date.now()}.md`)
    else exportTextAsPDF(combined, 'Document Analysis — All Files')
  }

  return (
    <div className="doc-analyzer">
      <h2 className="tab-heading"><FileText size={18} /> Document Analyzer</h2>

      <div
        className={`drop-zone ${files.length ? 'has-file' : ''}`}
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        onClick={() => !files.length && inputRef.current.click()}
      >
        {files.length === 0 ? (
          <>
            <Upload size={32} strokeWidth={1.2} />
            <p>Drop files here or click to browse</p>
            <p className="drop-hint">Supports TXT, MD, PDF, DOC, DOCX, PNG, JPG · Multiple files allowed</p>
          </>
        ) : (
          <div className="file-list">
            {files.map(f => (
              <div key={f.name} className="file-chip">
                <FileText size={13} />
                <span className="file-chip-name">{f.name}</span>
                <button
                  className="remove-file"
                  onClick={e => { e.stopPropagation(); removeFile(f.name) }}
                  disabled={loading}
                >
                  <X size={12} />
                </button>
              </div>
            ))}
            <button
              className="add-more-btn"
              onClick={e => { e.stopPropagation(); inputRef.current.click() }}
              disabled={loading}
            >
              + Add more
            </button>
          </div>
        )}
        <input ref={inputRef} type="file" accept={ACCEPT} hidden multiple onChange={e => addFiles(e.target.files)} />
      </div>

      <div className="analyze-row">
        <button className="analyze-btn" onClick={handleAnalyze} disabled={!files.length || loading}>
          {loading
            ? <><span className="spinner-white" /> Analyzing {progress}…</>
            : `Analyze ${files.length > 1 ? `${files.length} Documents` : 'Document'}`}
        </button>
        {results.length > 1 && !loading && (
          <div className="doc-export-btns">
            <button className="doc-export-btn" onClick={() => exportAll('md')}>
              <Download size={13} /> Export All (MD)
            </button>
            <button className="doc-export-btn" onClick={() => exportAll('pdf')}>
              <Printer size={13} /> Export All (PDF)
            </button>
          </div>
        )}
      </div>

      {results.map((r, i) => (
        <ResultCard key={r.filename + i} item={r} index={results.length > 1 ? i : null} />
      ))}
    </div>
  )
}
