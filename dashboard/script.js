// Dashboard JavaScript

const API_BASE = 'http://localhost:5002';
const SECURITY_API = 'http://localhost:5001';
let autoRefreshInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Security Dashboard loaded');
    
    // Setup event listeners
    document.getElementById('refreshBtn').addEventListener('click', refreshData);
    document.getElementById('autoRefreshToggle').addEventListener('change', toggleAutoRefresh);
    
    // Initial data load
    refreshData();
    
    // Start auto-refresh
    toggleAutoRefresh();
    
    // Check server status
    checkServerStatus();
});

// Refresh all data
async function refreshData() {
    console.log('Refreshing dashboard data...');
    
    try {
        await Promise.all([
            updateStats(),
            updateAlerts(),
            updateActivityLog()
        ]);
        
        updateLastUpdatedTime();
        showToast('Data refreshed successfully', 'success');
    } catch (error) {
        console.error('Error refreshing data:', error);
        showToast('Failed to refresh data', 'error');
    }
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        
        document.getElementById('totalRequests').textContent = stats.total_requests || 0;
        document.getElementById('blockedRequests').textContent = stats.blocked || 0;
        document.getElementById('allowedRequests').textContent = stats.allowed || 0;
        document.getElementById('blockRate').textContent = `${stats.block_rate || 0}%`;
        
        // Update severity counts
        if (stats.severity_counts) {
            document.getElementById('criticalCount').textContent = stats.severity_counts.critical || 0;
            document.getElementById('highCount').textContent = stats.severity_counts.high || 0;
            document.getElementById('mediumCount').textContent = stats.severity_counts.medium || 0;
            document.getElementById('lowCount').textContent = stats.severity_counts.low || 0;
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update alerts list
async function updateAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts`);
        const alerts = await response.json();
        
        const alertsList = document.getElementById('alertsList');
        const alertCount = document.getElementById('alertCount');
        
        alertCount.textContent = alerts.length;
        
        if (alerts.length === 0) {
            alertsList.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">🎉</span>
                    <p>No threats detected</p>
                </div>
            `;
            return;
        }
        
        // Show most recent alerts first
        const recentAlerts = alerts.reverse().slice(0, 10);
        
        alertsList.innerHTML = recentAlerts.map(alert => createAlertElement(alert)).join('');
    } catch (error) {
        console.error('Error updating alerts:', error);
    }
}

// Create alert HTML element
function createAlertElement(alert) {
    const time = formatTime(alert.timestamp);
    const sourceIcon = getSourceIcon(alert.source);
    
    return `
        <div class="alert-item severity-${alert.severity}">
            <div class="alert-header">
                <span class="alert-source">${sourceIcon} ${alert.source}</span>
                <span class="alert-time">${time}</span>
            </div>
            <div class="alert-prompt">"${escapeHtml(alert.prompt)}"</div>
            <div class="alert-reason">🚨 ${alert.reason}</div>
        </div>
    `;
}

// Update activity log
async function updateActivityLog() {
    try {
        const response = await fetch(`${API_BASE}/logs/recent`);
        const logs = await response.json();
        
        const activityLog = document.getElementById('activityLog');
        const logCount = document.getElementById('logCount');
        
        logCount.textContent = logs.length;
        
        if (logs.length === 0) {
            activityLog.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">📭</span>
                    <p>No activity yet</p>
                </div>
            `;
            return;
        }
        
        // Show most recent logs first
        const recentLogs = logs.reverse().slice(0, 20);
        
        activityLog.innerHTML = recentLogs.map(log => createLogElement(log)).join('');
    } catch (error) {
        console.error('Error updating activity log:', error);
    }
}

// Create log HTML element
function createLogElement(log) {
    const time = formatTime(log.timestamp);
    const sourceIcon = getSourceIcon(log.source);
    
    return `
        <div class="log-item">
            <div class="log-content">
                <div class="log-header">
                    <span class="log-source">${sourceIcon} ${log.source}</span>
                    <span class="log-action ${log.action}">${log.action}</span>
                </div>
                <div class="log-prompt">${escapeHtml(log.prompt)}</div>
            </div>
            <div class="log-time">${time}</div>
        </div>
    `;
}

// Get icon for source
function getSourceIcon(source) {
    const icons = {
        'ai_agent': '🤖',
        'n8n': '⚡',
        'api': '🔌',
        'webhook': '🪝',
        'unknown': '❓'
    };
    return icons[source] || icons.unknown;
}

// Format timestamp
function formatTime(timestamp) {
    if (!timestamp) return 'Unknown';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    
    return date.toLocaleString();
}

// Update last updated time
function updateLastUpdatedTime() {
    const now = new Date();
    document.getElementById('lastUpdated').textContent = now.toLocaleTimeString();
}

// Toggle auto-refresh
function toggleAutoRefresh() {
    const toggle = document.getElementById('autoRefreshToggle');
    
    if (toggle.checked) {
        // Start auto-refresh every 3 seconds
        autoRefreshInterval = setInterval(refreshData, 3000);
        console.log('Auto-refresh enabled');
    } else {
        // Stop auto-refresh
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
        console.log('Auto-refresh disabled');
    }
}

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch(`${SECURITY_API}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            document.getElementById('serverStatus').innerHTML = `
                <span style="color: var(--color-success)">● Online</span>
            `;
        }
    } catch (error) {
        document.getElementById('serverStatus').innerHTML = `
            <span style="color: var(--color-error)">● Offline</span>
        `;
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle errors gracefully
window.addEventListener('error', (event) => {
    console.error('Dashboard error:', event.error);
});

// Handle API errors
async function fetchWithErrorHandling(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Fetch error for ${url}:`, error);
        throw error;
    }
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatTime,
        getSourceIcon,
        escapeHtml
    };
}
