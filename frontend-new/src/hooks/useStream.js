import { useCallback } from 'react'

export function useStream() {
  const stream = useCallback(async ({ endpoint, body, onChunk, onDone, onError }) => {
    let res
    try {
      res = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
    } catch (err) {
      onError(err.message || 'Network error')
      return
    }

    if (!res.ok) {
      try {
        const data = await res.json()
        onError(data.error || `HTTP ${res.status}`)
      } catch {
        onError(`HTTP ${res.status}`)
      }
      return
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      let done, value
      try {
        ;({ done, value } = await reader.read())
      } catch {
        break
      }
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''  // keep incomplete last line

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6).trim()
        if (payload === '[DONE]') {
          onDone()
          return
        }
        try {
          const parsed = JSON.parse(payload)
          if (parsed.error) {
            onError(parsed.error)
            return
          }
          if (parsed.text) onChunk(parsed.text)
        } catch {
          // ignore malformed chunk
        }
      }
    }
    onDone()
  }, [])

  return { stream }
}
