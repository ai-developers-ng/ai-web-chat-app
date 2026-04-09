import { useState } from 'react'
import { X, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import './AuthModal.css'

export function AuthModal({ onClose }) {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [form, setForm] = useState({ username: '', email: '', password: '', signupCode: '' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()
  const toast = useToast()

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(form.username, form.password)
        toast('Welcome back!', 'success')
      } else {
        await register(form.username, form.email, form.password, form.signupCode)
        toast('Account created!', 'success')
      }
      onClose()
    } catch (err) {
      toast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2>{mode === 'login' ? 'Sign In' : 'Create Account'}</h2>
          <button className="modal-close" onClick={onClose}><X size={18} /></button>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={form.username}
              onChange={set('username')}
              placeholder="your_username"
              required
              autoFocus
            />
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={form.email}
                onChange={set('email')}
                placeholder="you@example.com"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Password</label>
            <div className="input-with-icon">
              <input
                type={showPw ? 'text' : 'password'}
                value={form.password}
                onChange={set('password')}
                placeholder="••••••••"
                required
              />
              <button type="button" className="input-icon-btn" onClick={() => setShowPw(v => !v)}>
                {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label>Signup Code</label>
              <input
                type="text"
                value={form.signupCode}
                onChange={set('signupCode')}
                placeholder="Enter signup code"
                required
              />
            </div>
          )}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? <span className="spinner-white" /> : (mode === 'login' ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="modal-footer">
          {mode === 'login' ? (
            <span>No account? <button className="link-btn" onClick={() => setMode('register')}>Register</button></span>
          ) : (
            <span>Have an account? <button className="link-btn" onClick={() => setMode('login')}>Sign in</button></span>
          )}
        </div>
      </div>
    </div>
  )
}
