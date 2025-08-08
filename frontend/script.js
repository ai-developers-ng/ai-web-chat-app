// Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// Global state
let currentUser = null;
let isAuthenticated = false;

// DOM Elements
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const loadingOverlay = document.getElementById('loading-overlay');
const toastContainer = document.getElementById('toast-container');

// Authentication elements
const authButtons = document.getElementById('auth-buttons');
const userSection = document.getElementById('user-section');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');
const logoutBtn = document.getElementById('logout-btn');
const profileBtn = document.getElementById('profile-btn');
const historyBtn = document.getElementById('history-btn');
const historyTab = document.getElementById('history-tab');
const adminTab = document.getElementById('admin-tab');

// Modal elements
const authModal = document.getElementById('auth-modal');
const profileModal = document.getElementById('profile-modal');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

// Chat elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');

// Code chat elements
const codeMessages = document.getElementById('code-messages');
const codeInput = document.getElementById('code-input');
const codeSend = document.getElementById('code-send');

// Document analyzer elements
const documentFile = document.getElementById('document-file');
const documentResult = document.getElementById('document-result');
const documentUploadArea = document.getElementById('document-upload-area');

// Image generator elements
const imagePrompt = document.getElementById('image-prompt');
const generateBtn = document.getElementById('generate-btn');
const generatedImage = document.getElementById('generated-image');

// Image analyzer elements
const imageFile = document.getElementById('image-file');
const imageAnalysisResult = document.getElementById('image-analysis-result');
const imageUploadArea = document.getElementById('image-upload-area');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeAuthentication();
    initializeChat();
    initializeCodeChat();
    initializeDocumentAnalyzer();
    initializeImageGenerator();
    initializeImageAnalyzer();
    initializeHistory();
    initializeAdmin();
    checkAuthStatus();
    checkBackendHealth();
});

// Tab functionality
function initializeTabs() {
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    // Check if user is authenticated for protected tabs
    if (!isAuthenticated && ['chat', 'document', 'code', 'image-gen', 'image-analyze', 'history'].includes(tabId)) {
        showAuthModal('login');
        return;
    }
    
    // Remove active class from all tabs and contents
    tabButtons.forEach(btn => btn.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

// Authentication functionality
function initializeAuthentication() {
    // Login button
    loginBtn.addEventListener('click', () => showAuthModal('login'));
    
    // Register button
    registerBtn.addEventListener('click', () => showAuthModal('register'));
    
    // Logout button
    logoutBtn.addEventListener('click', logout);
    
    // Profile button
    profileBtn.addEventListener('click', showProfileModal);
    
    // History button
    historyBtn.addEventListener('click', () => switchTab('history'));
    
    // Modal close buttons
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', closeModals);
    });
    
    // Modal background click
    window.addEventListener('click', (e) => {
        if (e.target === authModal || e.target === profileModal) {
            closeModals();
        }
    });
    
    // Form switch links
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterForm();
    });
    
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginForm();
    });
    
    // Form submissions
    document.getElementById('login-form-element').addEventListener('submit', handleLogin);
    document.getElementById('register-form-element').addEventListener('submit', handleRegister);
    
    // Profile actions
    document.getElementById('export-data-btn').addEventListener('click', exportUserData);
    document.getElementById('change-password-btn').addEventListener('click', () => {
        document.getElementById('change-password-form').style.display = 'block';
    });
    document.getElementById('cancel-change-password').addEventListener('click', () => {
        document.getElementById('change-password-form').style.display = 'none';
        document.getElementById('change-password-form-element').reset();
    });
    document.getElementById('change-password-form-element').addEventListener('submit', handleChangePassword);
}

function showAuthModal(type = 'login') {
    authModal.style.display = 'block';
    if (type === 'login') {
        showLoginForm();
    } else {
        showRegisterForm();
    }
}

function showLoginForm() {
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
}

function showRegisterForm() {
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
}

function showProfileModal() {
    if (!isAuthenticated) return;
    
    // Populate profile information
    document.getElementById('profile-username').textContent = currentUser.username;
    document.getElementById('profile-email').textContent = currentUser.email;
    document.getElementById('profile-created').textContent = new Date(currentUser.created_at).toLocaleDateString();
    document.getElementById('profile-last-login').textContent = currentUser.last_login ? 
        new Date(currentUser.last_login).toLocaleDateString() : 'Never';
    
    profileModal.style.display = 'block';
}

function closeModals() {
    authModal.style.display = 'none';
    profileModal.style.display = 'none';
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            isAuthenticated = true;
            updateAuthUI();
            closeModals();
            showToast('Login successful!', 'success');
            
            // Clear form
            document.getElementById('login-form-element').reset();
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
        const username = document.getElementById('register-username').value.trim();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;
        const signupCode = document.getElementById('register-signup-code').value.trim();
        
        if (!username || !email || !password || !confirmPassword || !signupCode) {
            showToast('Please fill in all fields', 'error');
            return;
        }
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, email, password, signup_code: signupCode })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            showLoginForm();
            
            // Clear form
            document.getElementById('register-form-element').reset();
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Registration failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleChangePassword(e) {
    e.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password-profile').value;
    const confirmNewPassword = document.getElementById('confirm-new-password').value;

    if (!currentPassword || !newPassword || !confirmNewPassword) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    if (newPassword !== confirmNewPassword) {
        showToast('New passwords do not match', 'error');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ 
                current_password: currentPassword,
                new_password: newPassword 
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Password changed successfully!', 'success');
            document.getElementById('change-password-form').style.display = 'none';
            document.getElementById('change-password-form-element').reset();
        } else {
            showToast(data.error || 'Failed to change password', 'error');
        }
    } catch (error) {
        console.error('Change password error:', error);
        showToast('Failed to change password. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function logout() {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            currentUser = null;
            isAuthenticated = false;
            updateAuthUI();
            showToast('Logout successful!', 'success');
            
            // Switch to first tab if on protected tab
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab && ['chat', 'document', 'code', 'image-gen', 'image-analyze', 'history'].includes(activeTab.id)) {
                // Find first non-protected tab or just go to chat (which will show login)
                switchTab('chat');
            }
        } else {
            showToast('Logout failed', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showToast('Logout failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function checkAuthStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/check`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            isAuthenticated = true;
            updateAuthUI();
        } else {
            currentUser = null;
            isAuthenticated = false;
            updateAuthUI();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        currentUser = null;
        isAuthenticated = false;
        updateAuthUI();
    }
}

function updateAuthUI() {
    if (isAuthenticated && currentUser) {
        authButtons.style.display = 'none';
        userSection.style.display = 'flex';
        historyTab.style.display = 'block';
        document.getElementById('username-display').textContent = currentUser.username;
        
        // Show admin tab only for admin users
        if (currentUser.is_admin) {
            adminTab.style.display = 'block';
        } else {
            adminTab.style.display = 'none';
        }
    } else {
        authButtons.style.display = 'flex';
        userSection.style.display = 'none';
        historyTab.style.display = 'none';
        adminTab.style.display = 'none';
    }
}

async function exportUserData() {
    if (!isAuthenticated) return;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/logs/export`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Create and download file
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `user-data-${currentUser.username}-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            showToast('Data exported successfully!', 'success');
        } else {
            const errorData = await response.json();
            showToast(errorData.error || 'Export failed', 'error');
        }
    } catch (error) {
        console.error('Export error:', error);
        showToast('Export failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Utility functions
function showLoading() {
    loadingOverlay.classList.add('show');
}

function hideLoading() {
    loadingOverlay.classList.remove('show');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function formatMessage(text) {
    // Basic markdown-like formatting
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Chat functionality
function initializeChat() {
    chatSend.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
}

async function sendChatMessage() {
    if (!isAuthenticated) {
        showAuthModal('login');
        return;
    }
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user', chatMessages);
    chatInput.value = '';
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Add AI response to chat
        addMessageToChat(data.response, 'ai', chatMessages);
        
    } catch (error) {
        console.error('Chat error:', error);
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'ai', chatMessages);
        showToast('Error sending message: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Code chat functionality
function initializeCodeChat() {
    codeSend.addEventListener('click', sendCodeMessage);
    codeInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            sendCodeMessage();
        }
    });
}

async function sendCodeMessage() {
    if (!isAuthenticated) {
        showAuthModal('login');
        return;
    }
    
    const message = codeInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user', codeMessages);
    codeInput.value = '';
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/code-chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Add AI response to chat
        addMessageToChat(data.response, 'ai', codeMessages);
        
    } catch (error) {
        console.error('Code chat error:', error);
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'ai', codeMessages);
        showToast('Error sending message: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function addMessageToChat(message, sender, container) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = formatMessage(message);
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

// Document analyzer functionality
function initializeDocumentAnalyzer() {
    documentFile.addEventListener('change', handleDocumentUpload);
    
    // Drag and drop functionality
    documentUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        documentUploadArea.style.borderColor = '#5a6fd8';
    });
    
    documentUploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        documentUploadArea.style.borderColor = '#667eea';
    });
    
    documentUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        documentUploadArea.style.borderColor = '#667eea';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            documentFile.files = files;
            handleDocumentUpload();
        }
    });
}

async function handleDocumentUpload() {
    if (!isAuthenticated) {
        showAuthModal('login');
        return;
    }
    
    const file = documentFile.files[0];
    if (!file) return;
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/document-analyze`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayDocumentResult(data.response, file.name);
        showToast('Document analyzed successfully!', 'success');
        
    } catch (error) {
        console.error('Document analysis error:', error);
        showToast('Error analyzing document: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displayDocumentResult(analysis, filename) {
    documentResult.innerHTML = `
        <h3>Analysis of "${filename}"</h3>
        <div>${formatMessage(analysis)}</div>
    `;
}

// Image generator functionality
function initializeImageGenerator() {
    generateBtn.addEventListener('click', generateImage);
    imagePrompt.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            generateImage();
        }
    });
}

async function generateImage() {
    if (!isAuthenticated) {
        showAuthModal('login');
        return;
    }
    
    const prompt = imagePrompt.value.trim();
    if (!prompt) {
        showToast('Please enter a prompt for image generation', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayGeneratedImage(data.image, prompt);
        showToast('Image generated successfully!', 'success');
        
    } catch (error) {
        console.error('Image generation error:', error);
        showToast('Error generating image: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displayGeneratedImage(imageData, prompt) {
    generatedImage.innerHTML = `
        <h3>Generated Image</h3>
        <p><strong>Prompt:</strong> ${prompt}</p>
        <img src="data:image/png;base64,${imageData}" alt="Generated image" />
        <br><br>
        <button class="btn-secondary" onclick="downloadImage('${imageData}', '${prompt}')">
            <i class="fas fa-download"></i> Download Image
        </button>
    `;
}

function downloadImage(imageData, prompt) {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${imageData}`;
    link.download = `generated-image-${Date.now()}.png`;
    link.click();
}

// Image analyzer functionality
function initializeImageAnalyzer() {
    imageFile.addEventListener('change', handleImageUpload);
    
    // Drag and drop functionality
    imageUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#5a6fd8';
    });
    
    imageUploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#667eea';
    });
    
    imageUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        imageUploadArea.style.borderColor = '#667eea';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            imageFile.files = files;
            handleImageUpload();
        }
    });
}

async function handleImageUpload() {
    if (!isAuthenticated) {
        showAuthModal('login');
        return;
    }
    
    const file = imageFile.files[0];
    if (!file) return;
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze-image`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayImageAnalysis(data.response, file);
        showToast('Image analyzed successfully!', 'success');
        
    } catch (error) {
        console.error('Image analysis error:', error);
        showToast('Error analyzing image: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displayImageAnalysis(analysis, file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        imageAnalysisResult.innerHTML = `
            <h3>Analysis of "${file.name}"</h3>
            <div style="text-align: center; margin-bottom: 1rem;">
                <img src="${e.target.result}" alt="Uploaded image" style="max-width: 300px; border-radius: 10px;">
            </div>
            <div>${formatMessage(analysis)}</div>
        `;
    };
    reader.readAsDataURL(file);
}

// History functionality
function initializeHistory() {
    // History tab buttons
    document.querySelectorAll('.history-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-history-tab');
            switchHistoryTab(tabId);
        });
    });
    
    // Load buttons
    document.getElementById('load-searches').addEventListener('click', loadSearchHistory);
    document.getElementById('load-actions').addEventListener('click', loadActionHistory);
    document.getElementById('load-logins').addEventListener('click', loadLoginHistory);
    document.getElementById('load-stats').addEventListener('click', loadUserStats);
}

function switchHistoryTab(tabId) {
    // Remove active class from all history tabs and contents
    document.querySelectorAll('.history-tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.history-tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    document.querySelector(`[data-history-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`${tabId}-history`).classList.add('active');
}

async function loadSearchHistory() {
    if (!isAuthenticated) return;
    
    const searchType = document.getElementById('search-type-filter').value;
    const searchesList = document.getElementById('searches-list');
    
    showLoading();
    
    try {
        let url = `${API_BASE_URL}/logs/searches?per_page=50`;
        if (searchType) {
            url += `&type=${searchType}`;
        }
        
        const response = await fetch(url, {
            credentials: 'include'
        });
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            displaySearchHistory(data.searches, searchesList);
        } else {
            showToast(data.error || 'Failed to load search history', 'error');
        }
    } catch (error) {
        console.error('Load search history error:', error);
        showToast('Failed to load search history', 'error');
    } finally {
        hideLoading();
    }
}

async function loadActionHistory() {
    if (!isAuthenticated) return;
    
    const actionsList = document.getElementById('actions-list');
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/logs/actions?per_page=50`, {
            credentials: 'include'
        });
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            displayActionHistory(data.actions, actionsList);
        } else {
            showToast(data.error || 'Failed to load action history', 'error');
        }
    } catch (error) {
        console.error('Load action history error:', error);
        showToast('Failed to load action history', 'error');
    } finally {
        hideLoading();
    }
}

async function loadLoginHistory() {
    if (!isAuthenticated) return;
    
    const loginsList = document.getElementById('logins-list');
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/logs/logins?per_page=50`, {
            credentials: 'include'
        });
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            displayLoginHistory(data.logins, loginsList);
        } else {
            showToast(data.error || 'Failed to load login history', 'error');
        }
    } catch (error) {
        console.error('Load login history error:', error);
        showToast('Failed to load login history', 'error');
    } finally {
        hideLoading();
    }
}

async function loadUserStats() {
    if (!isAuthenticated) return;
    
    const period = document.getElementById('stats-period').value;
    const statsContent = document.getElementById('stats-content');
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/logs/stats?days=${period}`, {
            credentials: 'include'
        });
        
        if (response.status === 401) {
            showAuthModal('login');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            displayUserStats(data, statsContent);
        } else {
            showToast(data.error || 'Failed to load statistics', 'error');
        }
    } catch (error) {
        console.error('Load stats error:', error);
        showToast('Failed to load statistics', 'error');
    } finally {
        hideLoading();
    }
}

function displaySearchHistory(searches, container) {
    if (searches.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">No search history found.</p>';
        return;
    }
    
    container.innerHTML = searches.map(search => `
        <div class="history-item">
            <div class="history-item-header">
                <span class="history-item-type">${search.search_type}</span>
                <span class="history-item-time">${new Date(search.timestamp).toLocaleString()}</span>
            </div>
            <div class="history-item-content">
                <div class="history-item-query"><strong>Query:</strong> ${search.query}</div>
                ${search.response ? `<div class="history-item-response"><strong>Response:</strong> ${search.response.substring(0, 200)}${search.response.length > 200 ? '...' : ''}</div>` : ''}
                ${search.response_time ? `<div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">Response time: ${search.response_time.toFixed(2)}s</div>` : ''}
            </div>
        </div>
    `).join('');
}

function displayActionHistory(actions, container) {
    if (actions.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">No action history found.</p>';
        return;
    }
    
    container.innerHTML = actions.map(action => `
        <div class="history-item">
            <div class="history-item-header">
                <span class="history-item-type">${action.action_type}</span>
                <span class="history-item-time">${new Date(action.timestamp).toLocaleString()}</span>
            </div>
            <div class="history-item-content">
                ${Object.keys(action.details).length > 0 ? `<div><strong>Details:</strong> ${JSON.stringify(action.details, null, 2)}</div>` : ''}
            </div>
        </div>
    `).join('');
}

function displayLoginHistory(logins, container) {
    if (logins.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">No login history found.</p>';
        return;
    }
    
    container.innerHTML = logins.map(login => `
        <div class="history-item">
            <div class="history-item-header">
                <span class="history-item-type ${login.success ? 'success' : 'failed'}" style="background: ${login.success ? '#27ae60' : '#e74c3c'}">${login.success ? 'Success' : 'Failed'}</span>
                <span class="history-item-time">${new Date(login.login_time).toLocaleString()}</span>
            </div>
            <div class="history-item-content">
                <div><strong>Username:</strong> ${login.username_attempted}</div>
                <div><strong>IP Address:</strong> ${login.ip_address}</div>
                ${!login.success && login.failure_reason ? `<div><strong>Failure Reason:</strong> ${login.failure_reason}</div>` : ''}
            </div>
        </div>
    `).join('');
}

function displayUserStats(stats, container) {
    container.innerHTML = `
        <div class="stats-card">
            <h3>Search Statistics</h3>
            <div class="stats-number">${stats.search_stats.total}</div>
            <div class="stats-label">Total Searches (${stats.period_days} days)</div>
            <ul class="stats-list">
                ${stats.search_stats.by_type.map(item => `
                    <li>
                        <span>${item.type}</span>
                        <span>${item.count}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
        
        <div class="stats-card">
            <h3>Action Statistics</h3>
            <div class="stats-number">${stats.action_stats.total}</div>
            <div class="stats-label">Total Actions (${stats.period_days} days)</div>
            <ul class="stats-list">
                ${stats.action_stats.by_type.map(item => `
                    <li>
                        <span>${item.type}</span>
                        <span>${item.count}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
        
        <div class="stats-card">
            <h3>Login Statistics</h3>
            <div class="stats-number">${stats.login_stats.total_logins}</div>
            <div class="stats-label">Total Logins (${stats.period_days} days)</div>
            <ul class="stats-list">
                <li>
                    <span>Successful</span>
                    <span>${stats.login_stats.successful_logins}</span>
                </li>
                <li>
                    <span>Failed</span>
                    <span>${stats.login_stats.failed_logins}</span>
                </li>
            </ul>
        </div>
    `;
}

// Admin functionality
function initializeAdmin() {
    // Admin tab buttons
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-admin-tab');
            switchAdminTab(tabId);
        });
    });
    
    // Admin action buttons
    document.getElementById('generate-code-btn').addEventListener('click', generateSignupCode);
    document.getElementById('refresh-codes-btn').addEventListener('click', loadSignupCodes);
    
    // User management buttons
    document.getElementById('refresh-users-btn').addEventListener('click', loadUsers);
    document.getElementById('search-users-btn').addEventListener('click', searchUsers);
    document.getElementById('user-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchUsers();
        }
    });
    
    // Modal form submissions
    document.getElementById('edit-user-form').addEventListener('submit', handleEditUser);
    document.getElementById('reset-password-form').addEventListener('submit', handleResetPassword);
    
    // Modal close functionality
    initializeUserModals();
}

function switchAdminTab(tabId) {
    // Remove active class from all admin tabs and contents
    document.querySelectorAll('.admin-tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.admin-tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    document.querySelector(`[data-admin-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`${tabId}-admin`).classList.add('active');
}

async function generateSignupCode() {
    if (!isAuthenticated || !currentUser.is_admin) {
        showToast('Admin access required', 'error');
        return;
    }
    
    const expiryDays = document.getElementById('code-expiry-days').value;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/signup-codes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ expires_in_days: parseInt(expiryDays) })
        });
        
        const data = await response.json();
        
        if (response.status === 401 || response.status === 403) {
            showToast('Admin access required', 'error');
            return;
        }
        
        if (response.ok) {
            showToast('Signup code generated successfully!', 'success');
            
            // Show the generated code in a modal or alert
            const code = data.code.code;
            const expiresAt = new Date(data.code.expires_at).toLocaleString();
            
            showToast(`New signup code: ${code} (expires: ${expiresAt})`, 'success');
            
            // Refresh the codes list
            loadSignupCodes();
        } else {
            showToast(data.error || 'Failed to generate signup code', 'error');
        }
    } catch (error) {
        console.error('Generate code error:', error);
        showToast('Failed to generate signup code', 'error');
    } finally {
        hideLoading();
    }
}

async function loadSignupCodes() {
    if (!isAuthenticated || !currentUser.is_admin) {
        showToast('Admin access required', 'error');
        return;
    }
    
    const codesList = document.getElementById('signup-codes-list');
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/signup-codes`, {
            credentials: 'include'
        });
        
        if (response.status === 401 || response.status === 403) {
            showToast('Admin access required', 'error');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            displaySignupCodes(data.codes, codesList);
        } else {
            showToast(data.error || 'Failed to load signup codes', 'error');
        }
    } catch (error) {
        console.error('Load codes error:', error);
        showToast('Failed to load signup codes', 'error');
    } finally {
        hideLoading();
    }
}

function displaySignupCodes(codes, container) {
    if (codes.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">No signup codes found.</p>';
        return;
    }
    
    container.innerHTML = codes.map(code => {
        const isExpired = new Date(code.expires_at) < new Date();
        const statusClass = code.is_used ? 'used' : (isExpired ? 'expired' : 'active');
        const statusText = code.is_used ? 'Used' : (isExpired ? 'Expired' : 'Active');
        
        return `
            <div class="code-item ${statusClass}">
                <div class="code-header">
                    <div class="code-value">
                        <strong>${code.code}</strong>
                        <button class="copy-btn" onclick="copyToClipboard('${code.code}')" title="Copy code">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                    <span class="code-status ${statusClass}">${statusText}</span>
                </div>
                <div class="code-details">
                    <div><strong>Created:</strong> ${new Date(code.created_at).toLocaleString()}</div>
                    <div><strong>Expires:</strong> ${new Date(code.expires_at).toLocaleString()}</div>
                    ${code.is_used ? `<div><strong>Used by User ID:</strong> ${code.used_by_user_id}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Code copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showToast('Failed to copy code', 'error');
    });
}

// User Management Functions
async function loadUsers() {
    if (!isAuthenticated || !currentUser.is_admin) {
        showToast('Admin access required', 'error');
        return;
    }
    
    const usersList = document.getElementById('users-list');
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            credentials: 'include'
        });
        
        if (response.status === 401 || response.status === 403) {
            showToast('Admin access required', 'error');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            displayUsers(data.users, usersList);
        } else {
            showToast(data.error || 'Failed to load users', 'error');
        }
    } catch (error) {
        console.error('Load users error:', error);
        showToast('Failed to load users', 'error');
    } finally {
        hideLoading();
    }
}

function searchUsers() {
    const searchTerm = document.getElementById('user-search').value.trim().toLowerCase();
    const userItems = document.querySelectorAll('.user-item');
    
    userItems.forEach(item => {
        const username = item.querySelector('.user-name').textContent.toLowerCase();
        const email = item.querySelector('.user-email').textContent.toLowerCase();
        
        if (username.includes(searchTerm) || email.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function displayUsers(users, container) {
    if (users.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">No users found.</p>';
        return;
    }
    
    container.innerHTML = users.map(user => {
        const isCurrentUser = user.id === currentUser.id;
        // Ensure is_active is properly handled (default to true if undefined)
        const isActive = user.is_active !== undefined ? user.is_active : true;
        const statusClass = isActive ? 'active' : 'inactive';
        
        return `
            <div class="user-item ${statusClass}" data-user-id="${user.id}">
                <div class="user-header">
                    <div class="user-info">
                        <div class="user-name">${user.username}</div>
                        <div class="user-email">${user.email}</div>
                        <div class="user-badges">
                            ${user.is_admin ? '<span class="user-badge admin">Admin</span>' : ''}
                            <span class="user-badge ${statusClass}">${isActive ? 'Active' : 'Inactive'}</span>
                        </div>
                    </div>
                    <div class="user-actions">
                        <button class="btn-sm btn-edit" onclick="editUser(${user.id})" title="Edit User">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn-sm btn-reset" onclick="resetUserPassword(${user.id})" title="Reset Password">
                            <i class="fas fa-key"></i> Reset
                        </button>
                        ${!isCurrentUser ? `
                            <button class="btn-sm ${isActive ? 'btn-block' : 'btn-unblock'}" 
                                    onclick="${isActive ? 'blockUser' : 'unblockUser'}(${user.id})" 
                                    title="${isActive ? 'Block User' : 'Unblock User'}">
                                <i class="fas fa-${isActive ? 'ban' : 'check'}"></i> 
                                ${isActive ? 'Block' : 'Unblock'}
                            </button>
                            ${!user.is_admin ? `
                                <button class="btn-sm btn-make-admin" onclick="makeAdmin(${user.id})" title="Make Admin">
                                    <i class="fas fa-user-shield"></i> Admin
                                </button>
                            ` : `
                                <button class="btn-sm btn-remove-admin" onclick="removeAdmin(${user.id})" title="Remove Admin">
                                    <i class="fas fa-user-minus"></i> Remove
                                </button>
                            `}
                            <button class="btn-sm btn-delete" onclick="deleteUser(${user.id})" title="Delete User">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        ` : ''}
                    </div>
                </div>
                <div class="user-details">
                    <div><strong>Created:</strong> ${new Date(user.created_at).toLocaleString()}</div>
                    <div><strong>Last Login:</strong> ${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</div>
                    <div><strong>User ID:</strong> ${user.id}</div>
                    <div><strong>Status:</strong> ${isActive ? 'Active' : 'Inactive'}</div>
                </div>
            </div>
        `;
    }).join('');
}

function editUser(userId) {
    const userItem = document.querySelector(`[data-user-id="${userId}"]`);
    if (!userItem) {
        showToast('User not found', 'error');
        return;
    }
    
    const username = userItem.querySelector('.user-name').textContent;
    const email = userItem.querySelector('.user-email').textContent;
    const isActive = userItem.classList.contains('active');
    const isAdmin = userItem.querySelector('.user-badge.admin') !== null;
    
    // Populate form
    document.getElementById('edit-user-id').value = userId;
    document.getElementById('edit-username').value = username;
    document.getElementById('edit-email').value = email;
    document.getElementById('edit-is-active').checked = isActive;
    document.getElementById('edit-is-admin').checked = isAdmin;
    
    // Show modal
    document.getElementById('edit-user-modal').style.display = 'block';
}

function resetUserPassword(userId) {
    const userItem = document.querySelector(`.user-item .user-actions button[onclick="resetUserPassword(${userId})"]`).closest('.user-item');
    const username = userItem.querySelector('.user-name').textContent;
    
    // Populate form
    document.getElementById('reset-user-id').value = userId;
    document.getElementById('reset-username-display').textContent = username;
    document.getElementById('new-password').value = '';
    
    // Show modal
    document.getElementById('reset-password-modal').style.display = 'block';
}

function blockUser(userId) {
    confirmAction(`Are you sure you want to block this user?`, () => {
        updateUserStatus(userId, true);
    });
}

function unblockUser(userId) {
    confirmAction(`Are you sure you want to unblock this user?`, () => {
        updateUserStatus(userId, false);
    });
}

function makeAdmin(userId) {
    confirmAction(`Are you sure you want to make this user an admin?`, () => {
        updateAdminStatus(userId, true);
    });
}

function removeAdmin(userId) {
    confirmAction(`Are you sure you want to remove admin privileges from this user?`, () => {
        updateAdminStatus(userId, false);
    });
}

function deleteUser(userId) {
    confirmAction(`Are you sure you want to permanently delete this user? This action cannot be undone.`, () => {
        performDeleteUser(userId);
    });
}

function confirmAction(message, callback) {
    document.getElementById('confirm-message').textContent = message;
    document.getElementById('confirm-yes').onclick = () => {
        closeModal('confirm-action-modal');
        callback();
    };
    document.getElementById('confirm-action-modal').style.display = 'block';
}

async function handleEditUser(e) {
    e.preventDefault();
    
    const userId = document.getElementById('edit-user-id').value;
    const username = document.getElementById('edit-username').value.trim();
    const email = document.getElementById('edit-email').value.trim();
    const isActive = document.getElementById('edit-is-active').checked;
    const isAdmin = document.getElementById('edit-is-admin').checked;
    
    if (!username || !email) {
        showToast('Username and email are required', 'error');
        return;
    }
    
    if (username.length < 3) {
        showToast('Username must be at least 3 characters long', 'error');
        return;
    }
    
    // Basic email validation
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                username,
                email,
                is_active: isActive,
                is_admin: isAdmin
            })
        });
        
        const data = await response.json();
        
        if (response.status === 401 || response.status === 403) {
            showToast('Admin access required', 'error');
            return;
        }
        
        if (response.ok) {
            showToast('User updated successfully!', 'success');
            closeModal('edit-user-modal');
            
            // Update current user info if editing own profile
            if (parseInt(userId) === currentUser.id) {
                currentUser = data.user;
                updateAuthUI();
            }
            
            loadUsers(); // Refresh the list
        } else {
            showToast(data.error || 'Failed to update user', 'error');
        }
    } catch (error) {
        console.error('Edit user error:', error);
        showToast('Network error: Failed to update user', 'error');
    } finally {
        hideLoading();
    }
}

async function handleResetPassword(e) {
    e.preventDefault();
    
    const userId = document.getElementById('reset-user-id').value;
    const newPassword = document.getElementById('new-password').value.trim();
    
    showLoading();
    
    try {
        const body = newPassword ? { new_password: newPassword } : {};
        
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Password reset successfully!', 'success');
            
            // Show the new password
            const passwordDisplay = document.createElement('div');
            passwordDisplay.className = 'password-display';
            passwordDisplay.innerHTML = `
                <strong>New Password:</strong> ${data.new_password}
                <button class="copy-password-btn" onclick="copyToClipboard('${data.new_password}')">
                    <i class="fas fa-copy"></i>
                </button>
            `;
            
            const form = document.getElementById('reset-password-form');
            form.appendChild(passwordDisplay);
            
            // Hide the form and show close button
            form.querySelector('.form-actions').style.display = 'none';
            
            setTimeout(() => {
                closeModal('reset-password-modal');
                passwordDisplay.remove();
                form.querySelector('.form-actions').style.display = 'flex';
                form.reset();
            }, 10000); // Auto-close after 10 seconds
            
        } else {
            showToast(data.error || 'Failed to reset password', 'error');
        }
    } catch (error) {
        console.error('Reset password error:', error);
        showToast('Failed to reset password', 'error');
    } finally {
        hideLoading();
    }
}

async function updateUserStatus(userId, block) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/block`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ block })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            loadUsers(); // Refresh the list
        } else {
            showToast(data.error || 'Failed to update user status', 'error');
        }
    } catch (error) {
        console.error('Update user status error:', error);
        showToast('Failed to update user status', 'error');
    } finally {
        hideLoading();
    }
}

async function updateAdminStatus(userId, makeAdmin) {
    showLoading();
    
    try {
        const endpoint = makeAdmin ? 'make-admin' : 'remove-admin';
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/${endpoint}`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            loadUsers(); // Refresh the list
        } else {
            showToast(data.error || 'Failed to update admin status', 'error');
        }
    } catch (error) {
        console.error('Update admin status error:', error);
        showToast('Failed to update admin status', 'error');
    } finally {
        hideLoading();
    }
}

async function performDeleteUser(userId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            loadUsers(); // Refresh the list
        } else {
            showToast(data.error || 'Failed to delete user', 'error');
        }
    } catch (error) {
        console.error('Delete user error:', error);
        showToast('Failed to delete user', 'error');
    } finally {
        hideLoading();
    }
}

function initializeUserModals() {
    // Close modal functionality
    document.querySelectorAll('.modal .close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            closeModal(modal.id);
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
    });
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    
    // Reset forms
    if (modalId === 'edit-user-modal') {
        document.getElementById('edit-user-form').reset();
    } else if (modalId === 'reset-password-modal') {
        document.getElementById('reset-password-form').reset();
        // Remove any password display
        const passwordDisplay = document.querySelector('.password-display');
        if (passwordDisplay) {
            passwordDisplay.remove();
        }
        // Show form actions
        const formActions = document.querySelector('#reset-password-form .form-actions');
        if (formActions) {
            formActions.style.display = 'flex';
        }
    }
}

async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            if (data.bedrock_available) {
                showToast('Connected to AWS Bedrock successfully!', 'success');
            } else {
                showToast('Backend is running but AWS Bedrock is not available. Please check your AWS configuration.', 'error');
            }
        }
    } catch (error) {
        console.error('Health check failed:', error);
        showToast('Cannot connect to backend. Please make sure the Flask server is running.', 'error');
    }
}
