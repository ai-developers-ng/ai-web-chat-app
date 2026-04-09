import { ChevronDown } from 'lucide-react'
import './ModelSelector.css'

export function ModelSelector({ models, value, onChange, disabled }) {
  return (
    <div className="model-selector">
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
        className="model-select"
      >
        {Object.entries(models).map(([key, m]) => (
          <option key={key} value={key}>{m.name}</option>
        ))}
      </select>
      <ChevronDown size={14} className="model-chevron" />
    </div>
  )
}
