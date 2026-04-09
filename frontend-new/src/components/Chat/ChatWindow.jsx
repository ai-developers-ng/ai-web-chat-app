import { useState, useRef, useEffect, useCallback } from 'react'
import { Bot, User, Download, FileText, Printer } from 'lucide-react'
import { useStream } from '../../hooks/useStream'
import { useToast } from '../../hooks/useToast'
import { ModelSelector } from '../shared/ModelSelector'
import { StreamingMessage } from '../shared/StreamingMessage'
import { ChatInput } from './ChatInput'
import { exportMessagesAsMarkdown, exportMessagesAsPDF } from '../../utils/exportChat'
import './ChatWindow.css'

export function ChatWindow({ models, defaultModel }) {
  const [messages, setMessages] = useState([])
  const [selectedModel, setSelectedModel] = useState(defaultModel || Object.keys(models)[0])
  const [isStreaming, setIsStreaming] = useState(false)
  const [showExport, setShowExport] = useState(false)
  const bottomRef = useRef(null)
  const { stream } = useStream()
  const toast = useToast()

  // Keep default model in sync when models load
  useEffect(() => {
    if (defaultModel && models[defaultModel]) setSelectedModel(defaultModel)
  }, [defaultModel, models])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isStreaming) return

    const userMsg = { role: 'user', content: text, id: Date.now() }
    const aiId = Date.now() + 1
    const aiMsg = { role: 'ai', content: '', streaming: true, id: aiId }

    setMessages(prev => [...prev, userMsg, aiMsg])
    setIsStreaming(true)

    await stream({
      endpoint: '/api/chat',
      body: { message: text, model: selectedModel },
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
  }, [isStreaming, selectedModel, stream, toast])

  return (
    <div className="chat-window">
      <div className="chat-toolbar">
        <span className="chat-title">AI Chatbot</span>
        <div className="toolbar-right">
          <ModelSelector
            models={models}
            value={selectedModel}
            onChange={setSelectedModel}
            disabled={isStreaming}
          />
          {messages.length > 0 && (
            <div className="export-dropdown">
              <button className="export-trigger" onClick={() => setShowExport(v => !v)} title="Export chat">
                <Download size={15} />
              </button>
              {showExport && (
                <div className="export-menu" onMouseLeave={() => setShowExport(false)}>
                  <button onClick={() => { exportMessagesAsMarkdown(messages, 'Chat', selectedModel); setShowExport(false) }}>
                    <FileText size={13} /> Export as Markdown
                  </button>
                  <button onClick={() => { exportMessagesAsPDF(messages, 'Chat', selectedModel); setShowExport(false) }}>
                    <Printer size={13} /> Export as PDF
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <Bot size={40} strokeWidth={1.2} />
            <p>Ask me anything</p>
          </div>
        )}
        {messages.map(msg => (
          <div key={msg.id} className={`message-row ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className="message-bubble">
              {msg.role === 'ai'
                ? <StreamingMessage content={msg.content} streaming={msg.streaming} />
                : <span>{msg.content}</span>
              }
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <ChatInput onSend={sendMessage} disabled={isStreaming} placeholder="Ask anything… (Enter to send)" />
    </div>
  )
}
