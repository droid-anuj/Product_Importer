/**
 * Main App Controller
 * Handles tab switching, dashboard, and general app logic
 */

const APP = {
    currentTab: 'dashboard',
};

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeDashboard();
    checkAPIHealth();
});

// ===== TAB SWITCHING =====

function initializeTabs() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = tab.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Load dashboard on startup
    setTimeout(() => {
        updateDashboardStats();
    }, 500);
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabName + '-tab');
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
    }

    // Update nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active', 'border-b-2', 'border-blue-600', 'text-blue-600', 'bg-blue-100');
        tab.classList.add('border-transparent', 'text-gray-600');
    });

    const activeTab = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
    if (activeTab) {
        activeTab.classList.add('active', 'border-b-2', 'border-blue-600', 'text-blue-600', 'bg-blue-100');
        activeTab.classList.remove('border-transparent', 'text-gray-600');
    }

    APP.currentTab = tabName;

    // Load tab-specific data
    if (tabName === 'products') {
        loadProducts();
    } else if (tabName === 'webhooks') {
        loadWebhooks();
    } else if (tabName === 'dashboard') {
        updateDashboardStats();
    }
}

// ===== DASHBOARD =====

async function initializeDashboard() {
    updateDashboardStats();
    
    // Refresh dashboard every 30 seconds
    setInterval(() => {
        if (APP.currentTab === 'dashboard') {
            updateDashboardStats();
        }
    }, 30000);
}

async function updateDashboardStats() {
    try {
        const response = await API.products.list(1, 1000);
        const webhooks = await API.webhooks.list();

        const stats = {
            total: response.total || 0,
            active: response.items?.filter(p => p.active).length || 0,
            value: response.items?.reduce((sum, p) => sum + ((p.price || 0) * (p.quantity || 0)), 0) || 0,
            webhooks: webhooks?.length || 0,
        };

        // Update dashboard cards
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-active').textContent = stats.active;
        document.getElementById('stat-value').textContent = '$' + stats.value.toFixed(2);
        document.getElementById('stat-webhooks').textContent = stats.webhooks;

        // Update header
        document.querySelector('#total-products span').textContent = stats.total;
        document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// ===== API HEALTH CHECK =====

async function checkAPIHealth() {
    try {
        const health = await API.health();
        console.log('✓ API is healthy:', health);
    } catch (error) {
        console.error('❌ API health check failed:', error);
        showNotification('⚠️  API connection issue. Some features may not work.', 'warning');
    }
}

// ===== NOTIFICATIONS =====

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-4 rounded-lg text-white font-medium shadow-lg z-50 ${
        type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'
    }`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ===== CLOSE MODALS =====

window.addEventListener('click', (e) => {
    const productModal = document.getElementById('product-modal');
    const webhookModal = document.getElementById('webhook-modal');

    if (productModal && e.target === productModal) {
        closeProductModal();
    }

    if (webhookModal && e.target === webhookModal) {
        closeWebhookModal();
    }
});

// ===== KEYBOARD SHORTCUTS =====

document.addEventListener('keydown', (e) => {
    // Close modals with Escape
    if (e.key === 'Escape') {
        closeProductModal();
        closeWebhookModal();
    }

    // Quick nav with Alt+number
    if (e.altKey) {
        if (e.key === '1') switchTab('dashboard');
        if (e.key === '2') switchTab('upload');
        if (e.key === '3') switchTab('products');
        if (e.key === '4') switchTab('webhooks');
        if (e.key === '5') switchTab('settings');
    }
});

// ===== SETTINGS =====

document.addEventListener('DOMContentLoaded', () => {
    // Load saved settings
    const savedApiUrl = localStorage.getItem('apiBaseURL');
    const savedPageSize = localStorage.getItem('pageSize');

    if (savedApiUrl) {
        API.setBaseURL(savedApiUrl);
        document.getElementById('setting-api-url').value = savedApiUrl;
    }

    if (savedPageSize) {
        productsPageSize = parseInt(savedPageSize);
        document.getElementById('setting-page-size').value = savedPageSize;
    }

    // Save settings button
    const saveSettingsBtn = document.querySelector('button[class*="btn-primary"][class*="Save Settings"]');
    if (saveSettingsBtn) {
        saveSettingsBtn.parentElement.querySelector('button').addEventListener('click', () => {
            const apiUrl = document.getElementById('setting-api-url').value;
            const pageSize = document.getElementById('setting-page-size').value;

            localStorage.setItem('apiBaseURL', apiUrl);
            localStorage.setItem('pageSize', pageSize);

            API.setBaseURL(apiUrl);
            productsPageSize = parseInt(pageSize);

            showNotification('✓ Settings saved successfully!', 'success');
        });
    }
});
