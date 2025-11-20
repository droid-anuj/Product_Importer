/**
 * Products Management Module
 */

let productsCurrentPage = 1;
let productsPageSize = 20;
let productsFilters = {};
let productsTotal = 0;

// Initialize products tab
document.addEventListener('DOMContentLoaded', () => {
    // Create product button
    const createBtn = document.getElementById('create-product-btn');
    if (createBtn) createBtn.addEventListener('click', () => openProductModal());

    // Refresh button
    const refreshBtn = document.getElementById('refresh-products-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', () => loadProducts());

    // Bulk delete button
    const bulkDeleteBtn = document.getElementById('bulk-delete-btn');
    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener('click', () => {
            if (confirm('⚠️  Delete ALL products? This cannot be undone.')) {
                deleteAllProducts();
            }
        });
    }

    // Filter buttons
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', () => {
            productsCurrentPage = 1;
            productsFilters = {
                sku: document.getElementById('filter-sku')?.value || '',
                name: document.getElementById('filter-name')?.value || '',
                active: document.getElementById('filter-active')?.value || '',
            };
            loadProducts();
        });
    }

    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            document.getElementById('filter-sku').value = '';
            document.getElementById('filter-name').value = '';
            document.getElementById('filter-active').value = '';
            productsFilters = {};
            productsCurrentPage = 1;
            loadProducts();
        });
    }

    // Pagination buttons
    const prevBtn = document.getElementById('prev-page-btn');
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (productsCurrentPage > 1) {
                productsCurrentPage--;
                loadProducts();
            }
        });
    }

    const nextBtn = document.getElementById('next-page-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            productsCurrentPage++;
            loadProducts();
        });
    }

    // Product form submit
    const productForm = document.getElementById('product-form');
    if (productForm) {
        productForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveProduct();
        });
    }
});

async function loadProducts() {
    try {
        const tbody = document.getElementById('products-table');
        if (!tbody) return;

        tbody.innerHTML = '<tr class="text-center"><td colspan="7"><div class="flex justify-center py-8"><div class="loading-spinner"></div></div></td></tr>';

        const filters = {};
        if (productsFilters.sku) filters.sku = productsFilters.sku;
        if (productsFilters.name) filters.name = productsFilters.name;
        if (productsFilters.active) filters.active = productsFilters.active === 'true';

        const response = await API.products.list(productsCurrentPage, productsPageSize, filters);

        productsTotal = response.total;

        if (!response.items || response.items.length === 0) {
            tbody.innerHTML = '<tr class="text-center"><td colspan="7" class="py-8 text-gray-500">No products found</td></tr>';
            updatePagination(response);
            return;
        }

        tbody.innerHTML = response.items.map(product => `
            <tr class="hover:bg-gray-50 transition">
                <td class="px-4 py-3 font-mono text-sm font-bold text-blue-600">${escapeHtml(product.sku)}</td>
                <td class="px-4 py-3">
                    <div class="font-medium text-gray-800">${escapeHtml(product.name)}</div>
                    <div class="text-xs text-gray-500">${escapeHtml(product.description || '-')}</div>
                </td>
                <td class="px-4 py-3 font-bold text-green-600">$${(product.price || 0).toFixed(2)}</td>
                <td class="px-4 py-3 text-center font-medium">${product.quantity}</td>
                <td class="px-4 py-3">
                    <span class="px-3 py-1 rounded-full text-xs font-bold ${
                        product.active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                    }">
                        ${product.active ? '✓ Active' : '✗ Inactive'}
                    </span>
                </td>
                <td class="px-4 py-3 text-xs text-gray-600">${formatDate(product.created_at)}</td>
                <td class="px-4 py-3 text-center space-x-1">
                    <button class="btn-primary btn-small" onclick="openProductModal(${product.id})">
                        <i class="fas fa-edit mr-1"></i>Edit
                    </button>
                    <button class="btn-danger btn-small" onclick="deleteProduct(${product.id})">
                        <i class="fas fa-trash mr-1"></i>Delete
                    </button>
                </td>
            </tr>
        `).join('');

        updatePagination(response);
        updateDashboardStats();
    } catch (error) {
        console.error('Error loading products:', error);
        alert(`❌ Error loading products: ${error.message}`);
    }
}

function updatePagination(response) {
    const paginationInfo = document.getElementById('pagination-info');
    if (paginationInfo) {
        paginationInfo.textContent = `Page ${response.page} of ${response.total_pages} (${response.total} total products)`;
    }

    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');

    if (prevBtn) prevBtn.disabled = response.page <= 1;
    if (nextBtn) nextBtn.disabled = response.page >= response.total_pages;
}

function openProductModal(productId = null) {
    const modal = document.getElementById('product-modal');
    const form = document.getElementById('product-form');
    const title = document.getElementById('product-modal-title');

    if (!modal || !form) return;

    form.reset();
    document.getElementById('product-id').value = '';
    document.getElementById('product-active').value = 'true';

    if (productId) {
        title.textContent = 'Edit Product';
        loadProductForEdit(productId);
    } else {
        title.textContent = 'Create New Product';
    }

    modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
}

function closeProductModal() {
    const modal = document.getElementById('product-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('modal-open');
    }
}

async function loadProductForEdit(productId) {
    try {
        const product = await API.products.get(productId);

        document.getElementById('product-id').value = product.id;
        document.getElementById('product-sku').value = product.sku;
        document.getElementById('product-name').value = product.name;
        document.getElementById('product-description').value = product.description || '';
        document.getElementById('product-price').value = product.price || '';
        document.getElementById('product-quantity').value = product.quantity || 0;
        document.getElementById('product-active').value = product.active ? 'true' : 'false';
    } catch (error) {
        console.error('Error loading product:', error);
        alert(`❌ Error loading product: ${error.message}`);
        closeProductModal();
    }
}

async function saveProduct() {
    try {
        const productId = document.getElementById('product-id').value;
        const data = {
            sku: document.getElementById('product-sku').value,
            name: document.getElementById('product-name').value,
            description: document.getElementById('product-description').value || null,
            price: document.getElementById('product-price').value ? parseFloat(document.getElementById('product-price').value) : null,
            quantity: document.getElementById('product-quantity').value ? parseInt(document.getElementById('product-quantity').value) : 0,
            active: document.getElementById('product-active').value === 'true',
        };

        if (productId) {
            await API.products.update(productId, data);
            alert('✓ Product updated successfully!');
        } else {
            await API.products.create(data);
            alert('✓ Product created successfully!');
        }

        closeProductModal();
        loadProducts();
    } catch (error) {
        console.error('Error saving product:', error);
        alert(`❌ Error saving product: ${error.message}`);
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) return;

    try {
        await API.products.delete(productId);
        alert('✓ Product deleted successfully!');
        loadProducts();
    } catch (error) {
        console.error('Error deleting product:', error);
        alert(`❌ Error deleting product: ${error.message}`);
    }
}

async function deleteAllProducts() {
    try {
        const result = await API.products.deleteAll();
        alert(`✓ ${result.message}`);
        loadProducts();
    } catch (error) {
        console.error('Error deleting all products:', error);
        alert(`❌ Error deleting products: ${error.message}`);
    }
}

// Utility functions
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

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
        return dateString;
    }
}
