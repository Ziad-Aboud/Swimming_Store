document.addEventListener('DOMContentLoaded', () => {
    const grid          = document.getElementById('shopGrid');
    const filterToggle  = document.getElementById('filterToggle');
    const sidebar       = document.querySelector('.shop-sidebar');
    const sidebarClose  = document.getElementById('sidebarClose');
    const sortSelect    = document.getElementById('sortSelect');

    if (!grid) return;

    let currentCat  = 'all';
    let currentSort = 'default';

    const params = new URLSearchParams(window.location.search);
    if (params.get('cat')) {
        currentCat = params.get('cat');
        const cb = document.querySelector(`input[value="${currentCat}"]`);
        if (cb) cb.checked = true;
    }

    function renderProducts() {
        let filtered = currentCat === 'all' ? [...PRODUCTS] : PRODUCTS.filter(p => p.cat === currentCat);

        switch (currentSort) {
            case 'price-low':  filtered.sort((a,b) => a.price - b.price);            break;
            case 'price-high': filtered.sort((a,b) => b.price - a.price);            break;
            case 'name':       filtered.sort((a,b) => a.name.localeCompare(b.name)); break;
        }

        const results = document.getElementById('resultCount');
        if (results) results.textContent = `Showing ${filtered.length} products`;

        if (filtered.length === 0) {
            grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><i class="fas fa-search"></i><h3>No products found</h3><p>Try adjusting your filters.</p></div>';
            return;
        }

        grid.innerHTML = filtered.map(createProductCard).join('');

        grid.querySelectorAll('.product-card').forEach((card, i) => {
            card.style.opacity   = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.4s ease';
                card.style.opacity    = '1';
                card.style.transform  = 'translateY(0)';
            }, i * 60);
        });
    }

    renderProducts();

    document.querySelectorAll('.filter-list input[name="category"]').forEach(cb => {
        cb.addEventListener('change', () => {
            document.querySelectorAll('.filter-list input[name="category"]').forEach(c => { if (c !== cb) c.checked = false; });
            currentCat = cb.checked ? cb.value : 'all';
            renderProducts();
        });
    });

    if (sortSelect) {
        sortSelect.addEventListener('change', () => { currentSort = sortSelect.value; renderProducts(); });
    }

    if (filterToggle) filterToggle.addEventListener('click', () => sidebar?.classList.toggle('active'));
    if (sidebarClose) sidebarClose.addEventListener('click', () => sidebar?.classList.remove('active'));
});