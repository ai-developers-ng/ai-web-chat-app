import { useState, useRef, useEffect, useCallback } from 'react'
import { Terminal, User, Code2, Download, FileText, Printer } from 'lucide-react'
import { useStream } from '../../hooks/useStream'
import { useToast } from '../../hooks/useToast'
import { ModelSelector } from '../shared/ModelSelector'
import { StreamingMessage } from '../shared/StreamingMessage'
import { CodeInput } from './CodeInput'
import { exportMessagesAsMarkdown, exportMessagesAsPDF } from '../../utils/exportChat'
import './CodeWindow.css'

const LANGUAGES = [
  { value: '', label: 'Auto-detect' },
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'react', label: 'React / JSX' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'java', label: 'Java' },
  { value: 'csharp', label: 'C#' },
  { value: 'cpp', label: 'C++' },
  { value: 'sql', label: 'SQL' },
  { value: 'bash', label: 'Bash / Shell' },
]

export function CodeWindow({ models, defaultModel }) {
  const [messages, setMessages] = useState([])
  const [selectedModel, setSelectedModel] = useState(defaultModel || Object.keys(models)[0])
  const [language, setLanguage] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [showExport, setShowExport] = useState(false)
  const bottomRef = useRef(null)
  const { stream } = useStream()
  const toast = useToast()

  useEffect(() => {
    if (defaultModel && models[defaultModel]) setSelectedModel(defaultModel)
  }, [defaultModel, models])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isStreaming) return

    const fullMessage = language ? `[Language: ${language}]\n\n${text}` : text
    const userMsg = { role: 'user', content: text, id: Date.now() }
    const aiId = Date.now() + 1
    const aiMsg = { role: 'ai', content: '', streaming: true, id: aiId }

    setMessages(prev => [...prev, userMsg, aiMsg])
    setIsStreaming(true)

    await stream({
      endpoint: '/api/code-chat',
      body: { message: fullMessage, model: selectedModel },
      onChunk: (chunk) => {
        setMessages(prev =>
          prev.map(m => m.id === aiId ? { ...m, content: m.content + chunk } : m)
        )
      },
      onDone: () => {
        setMessages(prev =>
          prev.map(m => m.id === aiId ? { ...m, streaming: false } : m)
        )
        setIsStreaming(false)
      },
      onError: (err) => {
        setMessages(prev =>
          prev.map(m => m.id === aiId ? { ...m, content: `Error: ${err}`, streaming: false } : m)
        )
        setIsStreaming(false)
        toast(err, 'error')
      },
    })
  }, [isStreaming, selectedModel, language, stream, toast])

  return (
    <div className="code-window">
      <div className="code-toolbar">
        <div className="flex items-center gap-2">
          <Code2 size={16} />
          <span className="code-title">Coding Assistant</span>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
            className="lang-select"
            title="Hint the language for better responses"
          >
            {LANGUAGES.map(l => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
          <ModelSelector
            models={models}
            value={selectedModel}
            onChange={setSelectedModel}
            disabled={isStreaming}
          />
          {messages.length > 0 && (
            <div className="export-dropdown">
              <button className="export-trigger" onClick={() => setShowExport(v => !v)} title="Export session">
                <Download size={15} />
              </button>
              {showExport && (
                <div className="export-menu" onMouseLeave={() => setShowExport(false)}>
                  <button onClick={() => { exportMessagesAsMarkdown(messages, 'Coding Session', selectedModel); setShowExport(false) }}>
                    <FileText size={13} /> Export as Markdown
                  </button>
                  <button onClick={() => { exportMessagesAsPDF(messages, 'Coding Session', selectedModel); setShowExport(false) }}>
                    <Printer size={13} /> Export as PDF
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="code-messages">
        {messages.length === 0 && (
          <div className="code-empty">
            <Terminal size={40} strokeWidth={1.2} />
            <p>Ask a coding question</p>
            <p className="code-empty-hint">Ctrl+Enter to send · Select a language for better responses</p>
          </div>
        )}
        {messages.map(msg => (
          <div key={msg.id} className={`message-row ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? <User size={16} /> : <Terminal size={16} />}
            </div>
            <div className="message-bubble">
              {msg.role === 'ai'
                ? <StreamingMessage content={msg.content} streaming={msg.streaming} />
                : <span className="user-code-text">{msg.content}</span>
              }
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <CodeInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  )
}
