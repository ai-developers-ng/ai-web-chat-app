import { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './hooks/useAuth'
import { ToastProvider } from './hooks/useToast'
import { Navbar } from './components/Layout/Navbar'
import { TabNav } from './components/Layout/TabNav'
import { ChatWindow } from './components/Chat/ChatWindow'
import { CodeWindow } from './components/CodeAssistant/CodeWindow'
import { DocumentAnalyzer } from './components/DocumentAnalyzer/DocumentAnalyzer'
import { ImageGen } from './components/ImageGen/ImageGen'
import { ImageAnalyzer } from './components/ImageAnalyzer/ImageAnalyzer'
import { History } from './components/History/History'
import { Admin } from './components/Admin/Admin'
import { AuthModal } from './components/Auth/AuthModal'
import { api } from './api/client'
import './App.css'

function AppContent() {
  const { user, loading } = useAuth()
  const [activeTab, setActiveTab] = useState('chat')
  const [showAuth, setShowAuth] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [models, setModels] = useState({})
  const [defaultModel, setDefaultModel] = useState('')

  // Load models once authenticated
  useEffect(() => {
    if (!user) { setModels({}); return }
    api.getModels()
      .then(data => {
        setModels(data)
        // Pick first model as default (backend default = claude-sonnet-4-5 if available)
        const keys = Object.keys(data)
        setDefaultModel(data['claude-sonnet-4-5'] ? 'claude-sonnet-4-5' : keys[0] || '')
      })
      .catch(() => {})
  }, [user])

  // Redirect to chat if on restricted tab after logout
  useEffect(() => {
    if (!user && (activeTab === 'history' || activeTab === 'admin')) {
      setActiveTab('chat')
    }
  }, [user, activeTab])

  if (loading) {
    return (
      <div className="app-loading">
        <span className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
      </div>
    )
  }

  const hasModels = Object.keys(models).length > 0

  return (
    <div className="app">
      <Navbar onProfileClick={() => user ? setShowProfile(true) : setShowAuth(true)} />

      {!user ? (
        <div className="auth-gate">
          <div className="auth-gate-content">
            <h1>AI Assistant</h1>
            <p>Sign in to use the AI chatbot, coding assistant, document analyzer, and more.</p>
            <button className="sign-in-btn" onClick={() => setShowAuth(true)}>Sign In</button>
          </div>
        </div>
      ) : (
        <>
          <TabNav activeTab={activeTab} onTabChange={setActiveTab} isAdmin={user.is_admin} />
          <div className="tab-content">
            {activeTab === 'chat' && (
              hasModels
                ? <ChatWindow models={models} defaultModel={defaultModel} />
                : <div className="loading-state"><span className="spinner" /></div>
            )}
            {activeTab === 'code' && (
              hasModels
                ? <CodeWindow models={models} defaultModel={defaultModel} />
                : <div className="loading-state"><span className="spinner" /></div>
            )}
            {activeTab === 'docs' && <DocumentAnalyzer />}
            {activeTab === 'imagegen' && <ImageGen />}
            {activeTab === 'imageanalyze' && <ImageAnalyzer />}
            {activeTab === 'history' && <History />}
            {activeTab === 'admin' && user.is_admin && <Admin />}
          </div>
        </>
      )}

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </div>
  )
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ToastProvider>
  )
}
