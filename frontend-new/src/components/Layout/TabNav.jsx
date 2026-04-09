import { MessageSquare, Code2, FileText, Image, ScanSearch, History, Shield } from 'lucide-react'
import './TabNav.css'

const TABS = [
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'code', label: 'Code', icon: Code2 },
  { id: 'docs', label: 'Documents', icon: FileText },
  { id: 'imagegen', label: 'Image Gen', icon: Image },
  { id: 'imageanalyze', label: 'Image Analyze', icon: ScanSearch },
  { id: 'history', label: 'History', icon: History, authRequired: true },
  { id: 'admin', label: 'Admin', icon: Shield, adminRequired: true },
]

export function TabNav({ activeTab, onTabChange, isAdmin }) {
  return (
    <div className="tab-nav">
      {TABS.filter(t => {
        if (t.adminRequired) return isAdmin
        return true
      }).map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          className={`tab-btn ${activeTab === id ? 'active' : ''}`}
          onClick={() => onTabChange(id)}
        >
          <Icon size={15} />
          <span>{label}</span>
        </button>
      ))}
    </div>
  )
}
