import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check } from 'lucide-react'
import { useState } from 'react'
import './StreamingMessage.css'

function CopyButton({ code }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }
  return (
    <button className="copy-btn" onClick={handleCopy} title="Copy code">
      {copied ? <Check size={13} /> : <Copy size={13} />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

function CodeBlock({ node, inline, className, children, ...props }) {
  const lang = /language-(\w+)/.exec(className || '')?.[1] ?? 'text'
  const code = String(children).replace(/\n$/, '')

  if (inline) return <code className="inline-code" {...props}>{children}</code>

  return (
    <div className="code-block">
      <div className="code-header">
        <span className="code-lang">{lang}</span>
        <CopyButton code={code} />
      </div>
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={lang}
        PreTag="div"
        customStyle={{ margin: 0, borderRadius: '0 0 8px 8px', fontSize: '13px' }}
        {...props}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}

export function StreamingMessage({ content, streaming }) {
  return (
    <div className="streaming-message">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{ code: CodeBlock }}
      >
        {content || ''}
      </ReactMarkdown>
      {streaming && <span className="streaming-cursor" />}
    </div>
  )
}
