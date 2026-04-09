import { useState, useRef } from 'react'
import { Send } from 'lucide-react'
import './ChatInput.css'

export function ChatInput({ onSend, disabled, placeholder, multiline = false }) {
  const [text, setText] = useState('')
  const ref = useRef(null)

  const handleSubmit = () => {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
    if (ref.current) ref.current.style.height = 'auto'
  }

  const handleKey = (e) => {
    if (multiline) {
      // Ctrl+Enter or Cmd+Enter to submit in multiline mode
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); handleSubmit() }
    } else {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit() }
    }
  }

  const autoResize = (e) => {
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px'
  }

  return (
    <div className="chat-input-bar">
      <textarea
        ref={ref}
        className="chat-textarea"
        value={text}
        onChange={e => { setText(e.target.value); if (multiline) autoResize(e) }}
        onKeyDown={handleKey}
        placeholder={placeholder || 'Type a message…'}
        disabled={disabled}
        rows={multiline ? 3 : 1}
      />
      <button
        className="send-btn"
        onClick={handleSubmit}
        disabled={disabled || !text.trim()}
        title={multiline ? 'Send (Ctrl+Enter)' : 'Send (Enter)'}
      >
        {disabled ? <span className="spinner-white" /> : <Send size={16} />}
      </button>
    </div>
  )
}
