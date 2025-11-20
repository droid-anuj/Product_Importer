/**
 * Webhooks Management Module
 */

document.addEventListener('DOMContentLoaded', () => {
    const createBtn = document.getElementById('create-webhook-btn');
    if (createBtn) {
        createBtn.addEventListener('click', () => openWebhookModal());
    }

    const webhookForm = document.getElementById('webhook-form');
    if (webhookForm) {
        webhookForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveWebhook();
        });
    }
});

async function loadWebhooks() {
    try {
        const list = document.getElementById('webhooks-list');
        if (!list) return;

        list.innerHTML = '<p class="text-center py-8 text-gray-500"><i class="fas fa-spinner fa-spin mr-2"></i>Loading webhooks...</p>';

        const webhooks = await API.webhooks.list();

        if (!webhooks || webhooks.length === 0) {
            list.innerHTML = `
                <div class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                    <i class="fas fa-webhook text-5xl text-gray-300 mb-4"></i>
                    <p class="text-gray-500 font-medium">No webhooks configured yet</p>
                    <p class="text-gray-400 text-sm">Click "New Webhook" to create your first webhook</p>
                </div>
            `;
            updateDashboardStats();
            return;
        }

        list.innerHTML = webhooks.map(webhook => `
            <div class="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition bg-white">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-2">
                            <i class="fas fa-link text-blue-600"></i>
                            <p class="font-mono text-sm text-blue-600 break-all">${escapeHtml(webhook.url)}</p>
                        </div>
                        <div class="flex items-center gap-4 mt-3">
                            <span class="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                                ${webhook.event_type}
                            </span>
                            <span class="inline-block px-3 py-1 ${webhook.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} rounded-full text-xs font-medium">
                                ${webhook.enabled ? '✓ Enabled' : '✗ Disabled'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <div class="flex gap-2 mt-4 pt-4 border-t border-gray-200">
                    <button class="btn-primary btn-small" onclick="testWebhook(${webhook.id})">
                        <i class="fas fa-flask mr-1"></i>Test
                    </button>
                    <button class="btn-warning btn-small" onclick="openWebhookModal(${webhook.id})">
                        <i class="fas fa-edit mr-1"></i>Edit
                    </button>
                    <button class="btn-danger btn-small" onclick="deleteWebhook(${webhook.id})">
                        <i class="fas fa-trash mr-1"></i>Delete
                    </button>
                </div>
            </div>
        `).join('');

        updateDashboardStats();
    } catch (error) {
        console.error('Error loading webhooks:', error);
        const list = document.getElementById('webhooks-list');
        if (list) {
            list.innerHTML = `<div class="text-center py-8 text-red-600"><i class="fas fa-exclamation-circle mr-2"></i>Error loading webhooks: ${error.message}</div>`;
        }
    }
}

function openWebhookModal(webhookId = null) {
    const modal = document.getElementById('webhook-modal');
    const form = document.getElementById('webhook-form');
    const title = document.getElementById('webhook-modal-title');

    if (!modal || !form) return;

    form.reset();
    document.getElementById('webhook-id').value = '';
    document.getElementById('webhook-enabled').checked = true;

    if (webhookId) {
        title.textContent = 'Edit Webhook';
        loadWebhookForEdit(webhookId);
    } else {
        title.textContent = 'Create New Webhook';
    }

    modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
}

function closeWebhookModal() {
    const modal = document.getElementById('webhook-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('modal-open');
    }
}

async function loadWebhookForEdit(webhookId) {
    try {
        const webhook = await API.webhooks.get(webhookId);

        document.getElementById('webhook-id').value = webhook.id;
        document.getElementById('webhook-url').value = webhook.url;
        document.getElementById('webhook-event').value = webhook.event_type;
        document.getElementById('webhook-enabled').checked = webhook.enabled;
    } catch (error) {
        console.error('Error loading webhook:', error);
        alert(`❌ Error loading webhook: ${error.message}`);
        closeWebhookModal();
    }
}

async function saveWebhook() {
    try {
        const webhookId = document.getElementById('webhook-id').value;
        const data = {
            url: document.getElementById('webhook-url').value,
            event_type: document.getElementById('webhook-event').value,
            enabled: document.getElementById('webhook-enabled').checked,
        };

        if (webhookId) {
            await API.webhooks.update(webhookId, data);
            alert('✓ Webhook updated successfully!');
        } else {
            await API.webhooks.create(data);
            alert('✓ Webhook created successfully!');
        }

        closeWebhookModal();
        loadWebhooks();
    } catch (error) {
        console.error('Error saving webhook:', error);
        alert(`❌ Error saving webhook: ${error.message}`);
    }
}

async function testWebhook(webhookId) {
    try {
        const result = await API.webhooks.test(webhookId);

        if (result.success) {
            alert(`✓ Webhook test successful!\n\nStatus: ${result.status_code}\nResponse: ${result.response_body || 'OK'}`);
        } else {
            alert(`⚠️  Webhook test failed.\n\nStatus: ${result.status_code}\nError: ${result.error_message || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error testing webhook:', error);
        alert(`❌ Error testing webhook: ${error.message}`);
    }
}

async function deleteWebhook(webhookId) {
    if (!confirm('Are you sure you want to delete this webhook?')) return;

    try {
        await API.webhooks.delete(webhookId);
        alert('✓ Webhook deleted successfully!');
        loadWebhooks();
    } catch (error) {
        console.error('Error deleting webhook:', error);
        alert(`❌ Error deleting webhook: ${error.message}`);
    }
}

// Utility
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}
