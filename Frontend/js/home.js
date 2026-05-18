(function initHeroSlider() {
    const slides  = document.querySelectorAll('.hero-slide');
    const dots    = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.hero-prev');
    const nextBtn = document.querySelector('.hero-next');
    if (!slides.length) return;

    let current = 0;

    function goTo(i) {
        slides[current].classList.remove('active');
        dots[current]?.classList.remove('active');
        current = (i + slides.length) % slides.length;
        slides[current].classList.add('active');
        dots[current]?.classList.add('active');
    }

    if (prevBtn) prevBtn.addEventListener('click', () => goTo(current - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goTo(current + 1));
    dots.forEach((d, i) => d.addEventListener('click', () => goTo(i)));
    setInterval(() => goTo(current + 1), 6000);
})();

(function initFeatured() {
    const grid = document.getElementById('featuredGrid');
    if (!grid) return;

    function render(filter) {
        let list = filter === 'all'
            ? PRODUCTS
            : PRODUCTS.filter(p => p.cat === filter || (filter === 'accessories' && ['accessories','fins'].includes(p.cat)));

        grid.innerHTML = list.slice(0, 8).map(createProductCard).join('');

        grid.querySelectorAll('.product-card').forEach((card, i) => {
            card.style.opacity   = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.4s ease';
                card.style.opacity    = '1';
                card.style.transform  = 'translateY(0)';
            }, i * 80);
        });
    }

    render('all');

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            render(btn.dataset.tab);
        });
    });
})();

(function initBestsellers() {
    const scroll = document.getElementById('bestsellerScroll');
    if (!scroll) return;
    const sorted = [...PRODUCTS].sort((a, b) => b.price - a.price);
    scroll.innerHTML = sorted.map(createProductCard).join('');
})();