localStorage.removeItem('ss_couponCode');
localStorage.removeItem('ss_discountValue');
localStorage.removeItem('ss_discountType');

if (typeof CURRENT_USER_ID !== 'undefined' && !CURRENT_USER_ID) {
    window.location.href = 'login.html';
}
// 1. We attach renderCart to the global 'window' so main.js can trigger it anytime!
window.renderCart = function() {
    // Grab the UI elements
    const cartContainer = document.getElementById('cartItems');
    const cartSummary   = document.getElementById('cartSummary');
    const emptyCart     = document.getElementById('emptyCart');

    // If we are NOT on the cart page, stop running.
    if (!cartContainer) return;

    // If the cart is empty, show the empty state
    if (cart.length === 0) {
        cartContainer.style.display = 'none';
        if (cartSummary) cartSummary.style.display = 'none';
        if (emptyCart)   emptyCart.style.display   = 'block';
        return;
    }

    // Otherwise, hide the empty state and show the cart!
    if (emptyCart)   emptyCart.style.display   = 'none';
    cartContainer.style.display = 'block';
    if (cartSummary) cartSummary.style.display = 'block';

    // Draw the cart items using Django's database column names
    cartContainer.innerHTML = `
        <div class="cart-header-row">
            <span>Product</span><span>Price</span><span>Qty</span><span>Total</span><span></span>
        </div>
        ${cart.map(item => `
        <div class="cart-item">
            <div class="cart-product">
                <a href="product.html?id=${item.product_id}" style="text-decoration: none;">
                    
                    <div class="cart-product-img" style="background: #f8f9fb; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 1px solid #eaeaea;">
                        <img src="${item.image}" alt="${item.product_name}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    
                </a>
                
                <div class="cart-product-info">
                    <h4>
                        <a href="product.html?id=${item.product_id}" style="text-decoration: none; color: inherit; transition: color 0.3s;">
                            ${item.product_name}
                        </a>
                    </h4>
                    <p>Size: ${item.size} &nbsp;|&nbsp; Color: ${item.color}</p>
                </div>
            </div>
            <div class="cart-price">$${item.unit_price.toFixed(2)}</div>
            <div class="cart-qty">
                <button type="button" onclick="updateCartItemQty(${item.cart_item_id}, ${item.quantity}, -1)"><i class="fas fa-minus"></i></button>
                <span>${item.quantity}</span>
                <button type="button" onclick="updateCartItemQty(${item.cart_item_id}, ${item.quantity}, 1)"><i class="fas fa-plus"></i></button>
            </div>
            <div class="cart-total">$${item.total_item_price.toFixed(2)}</div>
            <button class="cart-remove" onclick="removeFromCart(${item.cart_item_id})"><i class="fas fa-times"></i></button>
        </div>`).join('')}`;

    const subtotal = cart.reduce((s,i) => s + i.total_item_price, 0);

    // Fetch Coupon details
    const storedDiscount = localStorage.getItem('ss_discountValue');
    const storedType = localStorage.getItem('ss_discountType');
    
    let discountAmount = 0;
    let discountLabel = '';

    if (storedDiscount !== null) {
        const val = parseFloat(storedDiscount);
        if (String(storedType) === '1') {
            // It's a Percentage (Type 1)
            discountAmount = subtotal * (val / 100);
            discountLabel = `Discount (${val}%)`;
        } else {
            // It's a Flat Amount (Type 0)
            discountAmount = val;
            discountLabel = `Discount (Flat)`;
        }
    }
    
    // Prevent discount from making the subtotal negative
    if (discountAmount > subtotal) discountAmount = subtotal;

    // Calculate Final Math
    const discountedSubtotal = subtotal - discountAmount;
    const shipping = discountedSubtotal > 100 ? 0 : 9.99;
    const tax      = discountedSubtotal * 0.08; 
    const total    = discountedSubtotal + shipping + tax;

    if (cartSummary) {
        let summaryHTML = `
            <div class="summary-row"><span>Subtotal</span><span>$${subtotal.toFixed(2)}</span></div>`;
        
        if (discountAmount > 0) {
            summaryHTML += `
            <div class="summary-row" style="color: #166534; font-weight: 500;">
                <span>${discountLabel}</span>
                <span>-$${discountAmount.toFixed(2)}</span>
            </div>`;
        }

        summaryHTML += `
            <div class="summary-row"><span>Shipping</span><span>${shipping === 0 ? 'Free' : '$' + shipping.toFixed(2)}</span></div>
            <div class="summary-row"><span>Tax</span><span>$${tax.toFixed(2)}</span></div>
            <div class="summary-row total" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eaeaea;">
                <span style="font-size: 1.2rem; font-weight: bold;">Total</span>
                <span style="font-size: 1.2rem; font-weight: bold; color: var(--primary);">$${total.toFixed(2)}</span>
            </div>`;

        cartSummary.querySelector('.summary-content').innerHTML = summaryHTML;
    }
}; 


