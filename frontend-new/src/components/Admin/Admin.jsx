import { useState, useEffect } from 'react'
import { Shield, Users, Key, Trash2, Plus } from 'lucide-react'
import { api } from '../../api/client'
import { useToast } from '../../hooks/useToast'
import './Admin.css'

function UserRow({ user, onDelete }) {
  return (
    <div className="admin-row">
      <div className="admin-row-info">
        <span className="admin-username">{user.username}</span>
        <span className="admin-email">{user.email}</span>
        {user.is_admin && <span className="admin-badge-sm">admin</span>}
        {!user.is_active && <span className="inactive-badge">inactive</span>}
      </div>
      <div className="admin-row-actions">
        <span className="admin-date">{new Date(user.created_at).toLocaleDateString()}</span>
        <button className="danger-btn" onClick={() => onDelete(user.id)} title="Delete user">
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  )
}

function SignupCodeRow({ code, onDelete }) {
  return (
    <div className="admin-row">
      <div className="admin-row-info">
        <code className="code-val">{code.code}</code>
        {code.is_used && <span className="used-badge">used</span>}
      </div>
      <div className="admin-row-actions">
        <span className="admin-date">Expires {new Date(code.expires_at).toLocaleDateString()}</span>
        <button className="danger-btn" onClick={() => onDelete(code.id)} title="Delete code">
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  )
}

export function Admin() {
  const [users, setUsers] = useState([])
  const [codes, setCodes] = useState([])
  const [tab, setTab] = useState('users')
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  const reload = async () => {
    setLoading(true)
    try {
      const [u, c] = await Promise.all([api.getAdminUsers(), api.getSignupCodes()])
      setUsers(u.users || [])
      setCodes(c.codes || [])
    } catch (err) { toast(err.message, 'error') }
    finally { setLoading(false) }
  }

  useEffect(() => { reload() }, [])

  const handleDeleteUser = async (id) => {
    if (!confirm('Delete this user?')) return
    try { await api.deleteUser(id); reload(); toast('User deleted', 'success') }
    catch (err) { toast(err.message, 'error') }
  }

  const handleDeleteCode = async (id) => {
    try { await api.deleteSignupCode(id); reload(); toast('Code deleted', 'success') }
    catch (err) { toast(err.message, 'error') }
  }

  const handleCreateCode = async () => {
    try {
      await api.createSignupCode(7)
      reload()
      toast('Code created (7 days)', 'success')
    } catch (err) { toast(err.message, 'error') }
  }

  return (
    <div className="admin-panel">
      <h2 className="tab-heading"><Shield size={18} /> Admin Panel</h2>

      <div className="sub-tabs">
        <button className={`sub-tab ${tab === 'users' ? 'active' : ''}`} onClick={() => setTab('users')}>
          <Users size={13} /> Users ({users.length})
        </button>
        <button className={`sub-tab ${tab === 'codes' ? 'active' : ''}`} onClick={() => setTab('codes')}>
          <Key size={13} /> Signup Codes ({codes.length})
        </button>
      </div>

      {loading ? (
        <div className="loading-state"><span className="spinner" /></div>
      ) : tab === 'users' ? (
        <div className="admin-list">
          {users.map(u => <UserRow key={u.id} user={u} onDelete={handleDeleteUser} />)}
        </div>
      ) : (
        <div className="admin-list">
          <button className="create-code-btn" onClick={handleCreateCode}>
            <Plus size={14} /> Create Signup Code (7 days)
          </button>
          {codes.map(c => <SignupCodeRow key={c.id} code={c} onDelete={handleDeleteCode} />)}
        </div>
      )}
    </div>
  )
}
