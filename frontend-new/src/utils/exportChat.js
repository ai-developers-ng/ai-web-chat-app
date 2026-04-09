export function exportMessagesAsMarkdown(messages, title, modelKey) {
  const now = new Date().toLocaleString()
  const lines = [`# ${title} Export\n\n**Date:** ${now}  \n**Model:** ${modelKey}\n\n---\n`]
  for (const m of messages) {
    const role = m.role === 'user' ? '**You**' : '**Assistant**'
    lines.push(`${role}\n\n${m.content}\n\n---\n`)
  }
  downloadText(lines.join('\n'), `${slugify(title)}-${Date.now()}.md`, 'text/markdown')
}

export function exportMessagesAsPDF(messages, title, modelKey) {
  const now = new Date().toLocaleString()
  const rows = messages.map(m => {
    const role = m.role === 'user' ? 'You' : 'Assistant'
    const bg = m.role === 'user' ? '#e8eaff' : '#f4f6fb'
    const content = escapeHtml(m.content).replace(/\n/g, '<br>')
    return `<div style="margin:12px 0;padding:12px 16px;border-radius:8px;background:${bg}">
      <div style="font-size:11px;font-weight:700;color:#5b6ef5;margin-bottom:6px">${role}</div>
      <div style="font-size:13px;line-height:1.6;white-space:pre-wrap">${content}</div>
    </div>`
  }).join('')
  openPrintWindow(title, now, modelKey, rows)
}

export function exportTextAsMarkdown(text, title, filename) {
  const now = new Date().toLocaleString()
  const content = `# ${title}\n\n**Date:** ${now}\n\n---\n\n${text}`
  downloadText(content, filename || `${slugify(title)}-${Date.now()}.md`, 'text/markdown')
}

export function exportTextAsPDF(text, title) {
  const now = new Date().toLocaleString()
  const content = escapeHtml(text).replace(/\n/g, '<br>')
  const rows = `<div style="font-size:13px;line-height:1.8;white-space:pre-wrap">${content}</div>`
  openPrintWindow(title, now, '', rows)
}

// ── helpers ──────────────────────────────────────────────────────────────────

function downloadText(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

function openPrintWindow(title, date, model, bodyHtml) {
  const subtitle = [date, model].filter(Boolean).join(' · ')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${title}</title>
    <style>
      body{font-family:system-ui,sans-serif;max-width:800px;margin:40px auto;color:#1e2340}
      h1{font-size:20px;margin-bottom:4px}
      p.sub{font-size:12px;color:#6b7498;margin-bottom:20px}
      @media print{body{margin:20px}}
    </style></head><body>
    <h1>${escapeHtml(title)}</h1>
    <p class="sub">${escapeHtml(subtitle)}</p>
    ${bodyHtml}
    <script>window.onload=()=>window.print()<\/script>
  </body></html>`
  const w = window.open('', '_blank')
  if (w) { w.document.write(html); w.document.close() }
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
}
