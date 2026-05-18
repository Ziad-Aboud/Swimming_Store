// This will hold the real data from Django
let PRODUCTS = [];

// The base URL of your Django server
const API_BASE_URL = 'http://127.0.0.1:8000/api'
// const API_BASE_URL = 'https://railway.com/project/fbb7e551-7b08-4331-bf1c-bc639ca6e970/service/3025b434-659d-4e74-a518-7bbb62ed293c?id=f683a51c-baac-4b1f-8e0f-918bbfbd987b&'

// Fetch products from the backend as soon as the page loads
async function fetchProductsFromBackend() {
    try {
        // 1. Fetch the data FIRST
        const response = await fetch(`${API_BASE_URL}/products/`);
        if (!response.ok) throw new Error('Failed to fetch products');
        
        const data = await response.json();
        
        // 2. Format the data ONCE
        PRODUCTS = data.products.map(dbItem => {
            let rawImages = dbItem.images || [];
            rawImages.sort((a, b) => (b.is_primary ? 1 : 0) - (a.is_primary ? 1 : 0));
            let imageUrls = rawImages.map(img => img.image_url);
            
            if (imageUrls.length === 0) {
                imageUrls = ['../assets/placeholder.jpg']; 
            }

            return {
                id: dbItem.product_id,
                name: dbItem.name,
                desc: dbItem.description,
                price: parseFloat(dbItem.base_price),
                images: imageUrls, 
                primaryImage: imageUrls[0], 
                cat: "swimsuits", 
                colors: ["#0066ff"],
                sizes: ["M"]
            };
        });

        // 3. Draw the screens
        if (typeof initFeatured === 'function') initFeatured();
        if (typeof initBestsellers === 'function') initBestsellers();
        if (typeof renderProducts === 'function') renderProducts();

    } catch (error) {
        console.error("Error loading products:", error);
    }
}

// Start the fetch process immediately
fetchProductsFromBackend();


let cart = [];
// Check if a user is saved in the browser from a previous login
let currentUser = JSON.parse(localStorage.getItem('ssUser')) || null;
// If logged in, use their real ID. If not, set it to null.
let CURRENT_USER_ID = currentUser ? currentUser.id : null;

// 1. Fetch the Cart from Django
async function fetchCart() {
    if (!CURRENT_USER_ID) return;
    try {
        const response = await fetch(`${API_BASE_URL}/cart/${CURRENT_USER_ID}/`);
        if (response.ok) {
            const data = await response.json();
            cart = data.items || []; 
            updateBadges();
            
            // If the user is currently on the cart.html page, tell it to redraw!
            if (typeof renderCart === 'function') renderCart(); 
        }
    } catch (error) {
        console.error("Error fetching cart:", error);
    }
}

// 2. Add an Item to Django
async function addToCart(productId, qty = 1) {
    // 2. Add an Item to Django
        if (!CURRENT_USER_ID) {
            // Check if they are on the homepage or inside the pages folder to get the right link
            const isPages = window.location.pathname.includes('/pages/');
            window.location.href = isPages ? 'login.html' : 'pages/login.html';
            return; // Stop the function here!
        }

    try {
        const response = await fetch(`${API_BASE_URL}/cart/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: CURRENT_USER_ID,
                variant_id: productId,
                quantity: qty
            })
        });

        const data = await response.json();
        if (response.ok) {
            showToast('Added to cart successfully!', 'success');
            fetchCart(); 
        } else {
            showToast(data.error || 'Failed to add item', 'error');
        }
    } catch (error) {
        console.error("Error adding to cart:", error);
    }
}

// 3. Remove an Item from Django
async function removeFromCart(cartItemId) {
    try {
        const response = await fetch(`${API_BASE_URL}/cart/items/${cartItemId}/`, {
            method: 'DELETE'
        });
        if (response.ok) {
            showToast('Item removed from cart', 'error');
            fetchCart(); 
        }
    } catch (error) {
        console.error("Error removing item:", error);
    }
}
window.updateCartItemQty = async function(cartItemId, currentQty, delta) {
    const newQty = parseInt(currentQty) + parseInt(delta);

    // If the user clicks minus and the quantity hits 0, remove the item.
    if (newQty <= 0) {
        removeFromCart(cartItemId);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/cart/items/${cartItemId}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: newQty })
        });

        const data = await response.json();
        
        if (response.ok) {
            fetchCart(); 
        } else {
            showToast(data.error || 'Failed to update quantity', 'error');
        }
    } catch (error) {
        console.error("Error updating quantity:", error);
    }
};

function updateBadges() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.querySelectorAll('#cartBadge').forEach(b => { b.textContent = totalItems; });

}

fetchCart();

function saveWish() { localStorage.setItem('ssWish', JSON.stringify(wishlist)); updateBadges(); }




function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) { container = document.createElement('div'); container.className = 'toast-container'; document.body.appendChild(container); }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}

function createProductCard(product) {
    const isWished = wishlist.includes(product.id);
    const isPages  = window.location.pathname.includes('/pages/');
    const base     = isPages ? '' : 'pages/';
    let badgeHTML  = '';
    if (product.badge === 'new')  badgeHTML = '<span class="product-badge badge-new">New</span>';
    if (product.badge === 'sale') badgeHTML = '<span class="product-badge badge-sale">Sale</span>';
    if (product.badge === 'hot')  badgeHTML = '<span class="product-badge badge-hot">Hot</span>';

    return `
    <div class="product-card" data-cat="${product.cat}">
        <div class="product-card-img">
            ${badgeHTML}
            <div class="product-actions">
                <button class="product-action-btn ${isWished ? 'wishlisted' : ''}" data-wish-id="${product.id}" onclick="toggleWishlist(${product.id})">
                    <i class="fas fa-heart"></i>
                </button>
                <a href="${base}product.html?id=${product.id}" class="product-action-btn">
                    <i class="fas fa-eye"></i>
                </a>
            </div>
            <a href="${base}product.html?id=${product.id}" style="display:flex; align-items:center; justify-content:center; width:100%; height:100%; text-decoration:none; overflow:hidden;">
                <img src="${product.primaryImage}" alt="${product.name}" style="width:100%; height:100%; object-fit:cover;">
            </a>
        </div>
        <div class="product-card-info">
            <div class="product-card-cat">${product.cat}</div>
            <h3 class="product-card-title">
                <a href="${base}product.html?id=${product.id}">${product.name}</a>
            </h3>
            <div class="product-card-price">
                <span class="current-price">$${product.price.toFixed(2)}</span>
                ${product.oldPrice ? `<span class="old-price">$${product.oldPrice.toFixed(2)}</span>` : ''}
            </div>
        </div>
        </div>`;
}

function initTheme() {
    const saved = localStorage.getItem('ssTheme');
    if (saved === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    document.querySelectorAll('#theme-toggle').forEach(btn => {
        const icon = btn.querySelector('i');
        if (document.documentElement.getAttribute('data-theme') === 'dark') icon.className = 'fas fa-sun';
        btn.addEventListener('click', () => {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
            localStorage.setItem('ssTheme', isDark ? 'light' : 'dark');
            icon.className = isDark ? 'fas fa-moon' : 'fas fa-sun';
        });
    });
}

function initNavbar() {
    const navbar       = document.getElementById('navbar');
    const hamburger    = document.getElementById('hamburger');
    const navLinks     = document.getElementById('navLinks');
    const searchToggle = document.querySelector('.search-toggle');
    const searchOverlay = document.getElementById('searchOverlay');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
    }

    if (searchToggle && searchOverlay) {
        searchToggle.addEventListener('click', () => searchOverlay.classList.toggle('active'));
        const closeBtn = searchOverlay.querySelector('.search-close');
        if (closeBtn) closeBtn.addEventListener('click', () => searchOverlay.classList.remove('active'));
    }

    window.addEventListener('scroll', () => {
        if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 50);
        const btt = document.getElementById('backToTop');
        if (btt) btt.classList.toggle('visible', window.scrollY > 400);
    });

    const btt = document.getElementById('backToTop');
    if (btt) btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

    const userIcons = document.querySelectorAll('.fa-user, .fa-user-circle');
    
    userIcons.forEach(icon => {
        const link = icon.closest('a'); 
        if (link) {
            const isPages = window.location.pathname.includes('/pages/');
            const basePath = isPages ? '' : 'pages/';
            
            link.href = CURRENT_USER_ID ? (basePath + 'profile.html') : (basePath + 'login.html');
        }
    });
}

function initLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        window.addEventListener('load', () => { setTimeout(() => loader.classList.add('hidden'), 600); });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initLoader();
    initTheme();
    initNavbar();
    updateBadges();

    // --- NEW: AUTHENTICATION LOGIC ---
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // 1. Handle Login
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const response = await fetch(`${API_BASE_URL}/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, password: password })
                });
                
                const data = await response.json();

                if (response.ok) {
                    // Success! Save the user object to localStorage
                    localStorage.setItem('ssUser', JSON.stringify(data.user));
                    showToast('Login successful! Redirecting...', 'success');
                    // Send them to the homepage after 1 second
                    setTimeout(() => window.location.href = '../index.html', 1000); 
                } else {
                    showToast(data.error || 'Invalid credentials', 'error');
                }
            } catch (error) {
                console.error("Login error:", error);
            }
        });
    }

    // 2. Handle Registration
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fName = document.getElementById('regFirstName').value;
            const lName = document.getElementById('regLastName').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            
            const confirmPasswordInput = document.getElementById('regConfirmPassword');
            
            if (confirmPasswordInput && password !== confirmPasswordInput.value) {
                showToast('Passwords do not match!', 'error');
                return; 
            }

            try {
                const response = await fetch(`${API_BASE_URL}/users/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        first_name: fName,
                        last_name: lName,
                        email: email,
                        password_hash: password 
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('Registration successful! Please log in.', 'success');
                    // Clear the form fields
                    document.getElementById('regEmail').value = '';
                    document.getElementById('regPassword').value = '';
                    if (confirmPasswordInput) confirmPasswordInput.value = '';
                } else {
                    showToast(data.error || 'Registration failed', 'error');
                }
            } catch (error) {
                console.error("Registration error:", error);
            }
        });
    }
});

// 3. Handle Logout 
window.logoutUser = function() {
    localStorage.removeItem('ssUser'); 
    
    const isPages = window.location.pathname.includes('/pages/');
    window.location.href = isPages ? '../index.html' : 'index.html';
};

// --- GLOBAL NAV BADGE UPDATES ---
window.updateWishlistBadge = async function() {
    // 1. Make sure the user is logged in
    if (typeof CURRENT_USER_ID === 'undefined' || !CURRENT_USER_ID) return;
    
    // 2. Find the badge in the navbar
    const badge = document.getElementById('wishBadge');
    if (!badge) return;

    try {
        // 3. Ask Django how many items are in the wishlist
        const timestamp = new Date().getTime();
        const res = await fetch(`${API_BASE_URL}/wishlist/${CURRENT_USER_ID}/?t=${timestamp}`, { cache: 'no-store' });
        if (res.ok) {
            const data = await res.json();
            
            // 4. Update the number on the screen!
            const count = data.wishlist_ids ? data.wishlist_ids.length : 0;
            badge.textContent = count;
        }
    } catch (e) { 
        console.error("Badge Error:", e); 
    }
};

window.addEventListener('pageshow', () => {
    updateWishlistBadge();
    
    if (typeof fetchCart === 'function') {
        fetchCart(); 
    }
});


document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch(`${API_BASE_URL}/categories/`);
        const data = await res.json();
        
        // 1. Pathing Check: Are we on the homepage or inside the /pages/ folder?
        const isHomePage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('swim-store/');
        const shopPath = isHomePage ? 'pages/shop.html' : 'shop.html';

        // 2. Update Navbar Dropdown
        const navDropdown = document.querySelector('.nav-links .dropdown-menu');
        if (navDropdown) {
            navDropdown.innerHTML = data.categories.map(cat => 
                `<li><a href="${shopPath}?category=${cat.category_id}">${cat.name}</a></li>`
            ).join('');
        }

        // 3. Update Footer Categories
        const footerHeaders = document.querySelectorAll('.footer-col h4');
        let footerList = null;
        
        footerHeaders.forEach(h4 => {
            if (h4.textContent.trim() === 'Categories') {
                footerList = h4.nextElementSibling; 
            }
        });

        if (footerList) {
            const footerCats = data.categories.slice(0, 5); 
            footerList.innerHTML = footerCats.map(cat => 
                `<li><a href="${shopPath}?category=${cat.category_id}">${cat.name}</a></li>`
            ).join('');
        }

    } catch (error) {
        console.error("Error loading global categories:", error);
    }
});