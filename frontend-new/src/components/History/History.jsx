import { useState, useEffect } from 'react'
import { History as HistoryIcon, Download, MessageSquare, Code2, FileText, Image } from 'lucide-react'
import { api } from '../../api/client'
import { useToast } from '../../hooks/useToast'
import './History.css'

const TYPE_ICONS = {
  chat: <MessageSquare size={13} />,
  code: <Code2 size={13} />,
  document: <FileText size={13} />,
  image_gen: <Image size={13} />,
  image_analyze: <Image size={13} />,
}

function SearchEntry({ item }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="history-entry" onClick={() => setExpanded(e => !e)}>
      <div className="entry-header">
        <span className={`entry-type type-${item.search_type}`}>
          {TYPE_ICONS[item.search_type] || null}
          {item.search_type}
        </span>
        {item.model_id && <span className="entry-model">{item.model_id}</span>}
        <span className="entry-time">{new Date(item.timestamp).toLocaleString()}</span>
        {item.response_time && (
          <span className="entry-time">{item.response_time.toFixed(1)}s</span>
        )}
      </div>
      <p className="entry-query">{item.query.slice(0, 120)}{item.query.length > 120 ? '…' : ''}</p>
      {expanded && item.response && (
        <p className="entry-response">{item.response.slice(0, 500)}{item.response.length > 500 ? '…' : ''}</p>
      )}
    </div>
  )
}

export function History() {
  const [searches, setSearches] = useState([])
  const [stats, setStats] = useState(null)
  const [tab, setTab] = useState('searches')
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.getSearchLogs({ per_page: 50 }),
      api.getStats(),
    ])
      .then(([s, st]) => { setSearches(s.searches || []); setStats(st) })
      .catch(err => toast(err.message, 'error'))
      .finally(() => setLoading(false))
  }, [])

  const handleExport = async () => {
    try {
      const data = await api.exportData('all')
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = 'my-ai-data.json'; a.click()
      URL.revokeObjectURL(url)
    } catch (err) { toast(err.message, 'error') }
  }

  return (
    <div className="history-tab">
      <div className="history-header">
        <h2 className="tab-heading"><HistoryIcon size={18} /> Activity History</h2>
        <button className="export-btn" onClick={handleExport}>
          <Download size={14} /> Export Data
        </button>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-num">{stats.search_stats.total}</span>
            <span className="stat-label">Total Queries</span>
          </div>
          {stats.search_stats.by_type.map(s => (
            <div key={s.type} className="stat-card">
              <span className="stat-num">{s.count}</span>
              <span className="stat-label">{s.type}</span>
            </div>
          ))}
        </div>
      )}

      <div className="sub-tabs">
        <button className={`sub-tab ${tab === 'searches' ? 'active' : ''}`} onClick={() => setTab('searches')}>Searches</button>
      </div>

      {loading ? (
        <div className="loading-state"><span className="spinner" /></div>
      ) : (
        <div className="history-list">
          {searches.length === 0
            ? <p className="empty-msg">No search history yet.</p>
            : searches.map(s => <SearchEntry key={s.id} item={s} />)
          }
        </div>
      )}
    </div>
  )
}
