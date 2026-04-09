import { useState, useRef } from 'react'
import { Send } from 'lucide-react'
import './CodeInput.css'

export function CodeInput({ onSend, disabled }) {
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
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleSubmit()
    }
  }

  const autoResize = (e) => {
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 240) + 'px'
  }

  return (
    <div className="code-input-bar">
      <textarea
        ref={ref}
        className="code-textarea"
        value={text}
        onChange={e => { setText(e.target.value); autoResize(e) }}
        onKeyDown={handleKey}
        placeholder="Describe what you need… (Ctrl+Enter to send)"
        disabled={disabled}
        rows={3}
        spellCheck={false}
      />
      <button
        className="send-btn"
        onClick={handleSubmit}
        disabled={disabled || !text.trim()}
        title="Send (Ctrl+Enter)"
      >
        {disabled ? <span className="spinner-white" /> : <Send size={16} />}
      </button>
    </div>
  )
}
