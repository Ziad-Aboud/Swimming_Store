const urlParams = new URLSearchParams(window.location.search);
const PRODUCT_ID = urlParams.get('id'); // This makes it available to our inline script!
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const productId = parseInt(params.get('id'));
    const container = document.getElementById('productDetail');

    if (!container || !productId) return;

    let currentProduct = null;
    let selectedVariant = null;

    async function fetchProduct() {
        try {
            const response = await fetch(`${API_BASE_URL}/products/${productId}/`);
            if (!response.ok) throw new Error("Not found in database");
            
            currentProduct = await response.json();
            

            if (!currentProduct.variants || currentProduct.variants.length === 0) {
                console.warn("Warning: This product has no variants in the database!");
                currentProduct.variants = [{
                    variant_id: null,
                    size: 'Standard',
                    color: 'Default',
                    price_adjustment: 0,
                    stock: 0 
                }];
            }
            
            selectedVariant = currentProduct.variants[0];
            
            renderProduct();
            renderStaticSections(); 
            
            const loader = document.getElementById('loader');
            if(loader) loader.classList.add('hidden');

        } catch (error) {
            console.error("Crash Details:", error); 
            container.innerHTML = '<div class="empty-state"><h3>Product not found</h3><p>This item may have been removed or is missing data.</p></div>';
            
            const loader = document.getElementById('loader');
            if(loader) loader.classList.add('hidden');
        }
    }
    let currentImageIndex = 0;
    let productGalleryImages = [];
    function renderProduct() {
        const uniqueColors = [...new Set(currentProduct.variants.map(v => v.color))];
        const uniqueSizes = [...new Set(currentProduct.variants.map(v => v.size))];


        const basePrice = parseFloat(currentProduct.base_price) || 0;
        const adjustment = parseFloat(selectedVariant.price_adjustment) || 0;
        const finalPrice = basePrice + adjustment;
        const stockStatus = selectedVariant.stock > 0 
            ? `<span style="color: var(--secondary)">${selectedVariant.stock} in stock</span>` 
            : `<span style="color: #ff4757">Out of Stock</span>`;

        let rawImages = currentProduct.images || [];
        
        productGalleryImages = rawImages.length > 0 
            ? rawImages.map(img => img.image_url) 
            : ['../assets/placeholder.jpg'];
            
        currentImageIndex = 0;

        container.innerHTML = `
        <div class="product-detail-grid">
            
            <div class="product-gallery-container" style="position: relative; display: flex; align-items: center; justify-content: center; background: #f8f9fb; border-radius: 12px; overflow: hidden; height: 450px; width: 100%;">
                <button onclick="prevImage()" style="position: absolute; left: 15px; z-index: 10; background: white; border: 1px solid #eaeaea; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">&#10094;</button>
                
                <img id="mainDetailImage" src="${productGalleryImages[0]}" alt="${currentProduct.name}" style="width: 100%; height: 100%; object-fit: contain; padding: 20px;">
                
                <button onclick="nextImage()" style="position: absolute; right: 15px; z-index: 10; background: white; border: 1px solid #eaeaea; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">&#10095;</button>
            </div>

            <div class="product-info">
                <div class="product-cat">Swimming Gear</div>
                <h1>${currentProduct.name}</h1>
                <div class="price-detail">
                    <span class="price-current">$${finalPrice.toFixed(2)}</span>
                </div>
                <p class="product-desc">${currentProduct.description}</p>

                <div class="product-option">
                    <span class="option-label">Color: <span id="colorName">${selectedVariant.color}</span></span>
                    <div class="size-options">
                        ${uniqueColors.map(c => `
                            <button class="size-btn ${selectedVariant.color === c ? 'active' : ''}" 
                            onclick="selectColor('${c}')">${c}</button>
                        `).join('')}
                    </div>
                </div>

                <div class="product-option">
                    <span class="option-label">Size: <span id="sizeName">${selectedVariant.size}</span></span>
                    <div class="size-options">
                        ${uniqueSizes.map(s => `
                            <button class="size-btn ${selectedVariant.size === s ? 'active' : ''}" 
                            onclick="selectSize('${s}')">${s}</button>
                        `).join('')}
                    </div>
                </div>

                <div class="product-option">
                    <span class="option-label">Availability: ${stockStatus}</span>
                </div>

                <div class="qty-wrapper">
                    <div class="qty-control">
                        <button class="qty-btn" onclick="changeQty(-1)"><i class="fas fa-minus"></i></button>
                        <input type="number" class="qty-input" id="qtyInput" value="1" min="1" max="${selectedVariant.stock}">
                        <button class="qty-btn" onclick="changeQty(1)"><i class="fas fa-plus"></i></button>
                    </div>
                </div>

                <div class="action-btns" style="display: flex; gap: 15px; align-items: center; margin-top: 20px;">
                    <button class="btn btn-primary btn-lg" style="flex: 1;" ${selectedVariant.stock === 0 ? 'disabled' : ''} 
                            onclick="handleAddToCart()">
                        <i class="fas fa-shopping-bag"></i> ${selectedVariant.stock === 0 ? 'Sold Out' : 'Add to Cart'}
                    </button>

                    <button id="wishlistBtn" onclick="toggleProductWishlist()" 
                            style="width: 56px; height: 56px; border-radius: 12px; border: 1.5px solid #eaeaea; background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">
                        <i class="far fa-heart" id="wishlistIcon" style="font-size: 1.5rem; color: #cbd5e1;"></i>
                    </button>
                </div>
            </div>
        </div>`;

        if (typeof updateWishlistUI === 'function') {
            updateWishlistUI();
        }
        
    }
    window.nextImage = function() {
        if (productGalleryImages.length <= 1) return; // Do nothing if there's only 1 image
        
        currentImageIndex++;
        if (currentImageIndex >= productGalleryImages.length) {
            currentImageIndex = 0; // Loop back to the first image
        }
        document.getElementById('mainDetailImage').src = productGalleryImages[currentImageIndex];
    };

    window.prevImage = function() {
        if (productGalleryImages.length <= 1) return; 
        
        currentImageIndex--;
        if (currentImageIndex < 0) {
            currentImageIndex = productGalleryImages.length - 1; // Loop to the last image
        }
        document.getElementById('mainDetailImage').src = productGalleryImages[currentImageIndex];
    };

    // --- Variant Logic ---
    window.selectColor = function(color) {
        // Find a variant with the new color and current size (fallback to first available size in that color)
        selectedVariant = currentProduct.variants.find(v => v.color === color && v.size === selectedVariant.size) 
                       || currentProduct.variants.find(v => v.color === color);
        renderProduct();
    };

    window.selectSize = function(size) {
        selectedVariant = currentProduct.variants.find(v => v.size === size && v.color === selectedVariant.color) 
                       || currentProduct.variants.find(v => v.size === size);
        renderProduct();
    };

    window.changeQty = function(delta) {
        const input = document.getElementById('qtyInput');
        input.value = Math.max(1, Math.min(selectedVariant.stock, parseInt(input.value) + delta));
    };

    // --- Safe Add To Cart Logic ---
    window.handleAddToCart = function() {
        const input = document.getElementById('qtyInput');
        let requestedQty = parseInt(input.value);

        // Check if they typed a crazy high number
        if (requestedQty > selectedVariant.stock) {
            showToast(`Sorry, only ${selectedVariant.stock} left in stock!`, 'error');
            input.value = selectedVariant.stock; 
            return; 
        }

        // Check if they typed a negative number, 0, or gibberish
        if (requestedQty < 1 || isNaN(requestedQty)) {
            showToast('Please enter a valid quantity', 'error');
            input.value = 1;
            return; // Stop the code!
        }

        // If it passes all tests, send it to Django!
        addToCart(selectedVariant.variant_id, requestedQty);
    };

    function renderStaticSections() {
        const reviewsSection = document.getElementById('reviewsSection');
        if (reviewsSection && !reviewsSection.innerHTML.trim()) {
            reviewsSection.innerHTML = `
            <h2>Customer Reviews</h2>
            <div class="no-reviews">
                <i class="fas fa-comment-slash"></i>
                <p>No reviews yet. Check back after users purchase this item!</p>
            </div>`;
        }
    }

    fetchProduct();
});