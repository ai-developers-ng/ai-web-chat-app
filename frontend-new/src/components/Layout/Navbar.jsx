import { Bot, LogOut, User, Shield } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import './Navbar.css'

export function Navbar({ onProfileClick }) {
  const { user, logout } = useAuth()
  const toast = useToast()

  const handleLogout = async () => {
    try {
      await logout()
      toast('Logged out', 'info')
    } catch {
      toast('Logout failed', 'error')
    }
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Bot size={22} />
        <span>AI Assistant</span>
      </div>
      {user && (
        <div className="navbar-right">
          {user.is_admin && (
            <span className="admin-badge">
              <Shield size={12} /> Admin
            </span>
          )}
          <button className="nav-btn" onClick={onProfileClick} title="Profile">
            <User size={16} />
            <span className="nav-username">{user.username}</span>
          </button>
          <button className="nav-btn icon-only" onClick={handleLogout} title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      )}
    </nav>
  )
}
