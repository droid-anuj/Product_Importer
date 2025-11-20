/**
 * API Client for Product Importer
 * Handles all API communication
 */

const API = {
    baseURL: '/api',

    // Set custom base URL if needed
    setBaseURL(url) {
        this.baseURL = url;
    },

    // Helper method for fetch requests
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`API Error ${response.status}: ${error}`);
        }

        // Return empty object for 204 No Content
        if (response.status === 204) {
            return {};
        }

        return await response.json();
    },

    // ===== PRODUCTS API =====

    products: {
        list: async (page = 1, pageSize = 20, filters = {}) => {
            // Ensure page_size doesn't exceed backend limit of 100
            const limitedPageSize = Math.min(pageSize, 100);
            const params = new URLSearchParams({
                page,
                page_size: limitedPageSize,
                ...filters,
            });
            return API.request(`/products/?${params}`);
        },

        get: async (id) => {
            return API.request(`/products/${id}`);
        },

        create: async (data) => {
            return API.request('/products/', {
                method: 'POST',
                body: JSON.stringify(data),
            });
        },

        update: async (id, data) => {
            return API.request(`/products/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data),
            });
        },

        delete: async (id) => {
            return API.request(`/products/${id}`, {
                method: 'DELETE',
            });
        },

        deleteAll: async () => {
            return API.request('/products/', {
                method: 'DELETE',
            });
        },
    },

    // ===== WEBHOOKS API =====

    webhooks: {
        list: async () => {
            return API.request('/webhooks/');
        },

        get: async (id) => {
            return API.request(`/webhooks/${id}`);
        },

        create: async (data) => {
            return API.request('/webhooks/', {
                method: 'POST',
                body: JSON.stringify(data),
            });
        },

        update: async (id, data) => {
            return API.request(`/webhooks/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data),
            });
        },

        delete: async (id) => {
            return API.request(`/webhooks/${id}`, {
                method: 'DELETE',
            });
        },

        test: async (id, eventType = 'test') => {
            return API.request(`/webhooks/${id}/test`, {
                method: 'POST',
                body: JSON.stringify({ event_type: eventType }),
            });
        },
    },

    // ===== UPLOAD API =====

    upload: {
        csv: async (file, onProgress) => {
            const formData = new FormData();
            formData.append('file', file);

            const xhr = new XMLHttpRequest();

            return new Promise((resolve, reject) => {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percent = Math.round((e.loaded / e.total) * 100);
                        if (onProgress) onProgress(percent);
                    }
                });

                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(JSON.parse(xhr.responseText));
                    } else {
                        reject(new Error(`Upload failed: ${xhr.status}`));
                    }
                });

                xhr.addEventListener('error', () => {
                    reject(new Error('Upload error'));
                });

                xhr.open('POST', `${API.baseURL}/upload/`);
                xhr.send(formData);
            });
        },

        progress: async (taskId) => {
            return API.request(`/upload/progress/${taskId}`);
        },
    },

    // ===== HEALTH CHECK =====

    health: async () => {
        try {
            const response = await fetch(`${API.baseURL}/health`);
            if (response.ok) {
                return await response.json();
            }
            return { status: 'ok' }; // Fallback if endpoint doesn't exist
        } catch (error) {
            return { status: 'ok' }; // Return ok even if check fails
        }
    },
};
