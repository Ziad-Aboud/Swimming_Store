-- ============================================================
-- THE ULTIMATE E-COMMERCE DATABASE SCHEMA (Clean Version)
-- ============================================================

-- 1. Turn off Foreign Key checks so we can safely wipe the database clean
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS used_coupons;
DROP TABLE IF EXISTS payment_methods;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS wishlists;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS product_images;
DROP TABLE IF EXISTS product_variants;
DROP TABLE IF EXISTS product_categories;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS coupons;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS cities;
DROP TABLE IF EXISTS states;
DROP TABLE IF EXISTS phone_numbers;
DROP TABLE IF EXISTS users;

-- Turn them back on to enforce the rules
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- INDEPENDENT TABLES (No Parent Dependencies)
-- ============================================================

CREATE TABLE users (
    user_id       INT           NOT NULL AUTO_INCREMENT,
    first_name    VARCHAR(100)  NOT NULL,
    last_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(255)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    role          VARCHAR(50)   NOT NULL DEFAULT 'customer',
    created_at    DATETIME      DEFAULT CURRENT_TIMESTAMP,
    is_active     BOOLEAN       DEFAULT TRUE,
    dob			  Date,
    PRIMARY KEY (user_id)
);

CREATE TABLE states (
    state_id      INT           NOT NULL AUTO_INCREMENT,
    name          VARCHAR(100)  NOT NULL UNIQUE,
    delivery_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (state_id)
);

CREATE TABLE categories (
    category_id INT          NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    PRIMARY KEY (category_id)
);

CREATE TABLE products (
    product_id  INT           NOT NULL AUTO_INCREMENT,
    name        VARCHAR(255)  NOT NULL,
    description TEXT,
    base_price  DECIMAL(10,2) NOT NULL,
    is_active   BOOLEAN       DEFAULT TRUE,
    PRIMARY KEY (product_id)
);

CREATE TABLE coupons (
    coupon_id      INT           NOT NULL AUTO_INCREMENT,
    code           VARCHAR(100)  NOT NULL UNIQUE,
    discount_type  VARCHAR(20)   NOT NULL, -- 'percentage' or 'fixed'
    discount_value DECIMAL(10,2) NOT NULL,
    max_uses       INT           DEFAULT NULL,
    times_used     INT           DEFAULT 0,
    expires_at     DATETIME      DEFAULT NULL,
    is_active      BOOLEAN       DEFAULT TRUE,
    PRIMARY KEY (coupon_id)
);

-- ============================================================
-- DEPENDENT TABLES (Users, Products, & Locations)
-- ============================================================

CREATE TABLE phone_numbers (
    user_id      INT          NOT NULL,
    phone_number VARCHAR(30)  NOT NULL,
    PRIMARY KEY (user_id, phone_number),
    CONSTRAINT fk_phone_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE cities (
    city_id  INT           NOT NULL AUTO_INCREMENT,
    name     VARCHAR(100)  NOT NULL,
    state_id INT           NOT NULL,
    PRIMARY KEY (city_id),
    CONSTRAINT fk_city_state FOREIGN KEY (state_id)
        REFERENCES states(state_id) ON DELETE RESTRICT
);

CREATE TABLE addresses (
    address_id     INT           NOT NULL AUTO_INCREMENT,
    user_id        INT           NOT NULL,
    street_address VARCHAR(255)  NOT NULL,
    city_id        INT           NOT NULL,
    state_province INT           NOT NULL,
    postal_code    VARCHAR(20)   NOT NULL,
    country        VARCHAR(100)  NOT NULL,
    is_default     BOOLEAN       DEFAULT FALSE,
    PRIMARY KEY (address_id),
    CONSTRAINT fk_address_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_address_city FOREIGN KEY (city_id)
        REFERENCES cities(city_id) ON DELETE RESTRICT,
    CONSTRAINT fk_address_state FOREIGN KEY (state_province)
        REFERENCES states(state_id) ON DELETE RESTRICT
);

CREATE TABLE product_categories (
    product_id  INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (product_id, category_id),
    CONSTRAINT fk_pc_product  FOREIGN KEY (product_id)
        REFERENCES products(product_id)    ON DELETE CASCADE,
    CONSTRAINT fk_pc_category FOREIGN KEY (category_id)
        REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE product_variants (
    variant_id       INT           NOT NULL AUTO_INCREMENT,
    product_id       INT           NOT NULL,
    sku              VARCHAR(100)  NOT NULL UNIQUE,
    size             VARCHAR(50)   DEFAULT NULL,
    color            VARCHAR(50)   DEFAULT NULL,
    price_adjustment DECIMAL(10,2) DEFAULT 0.00,
    stock_quantity   INT           NOT NULL DEFAULT 0,
    PRIMARY KEY (variant_id),
    CONSTRAINT fk_variant_product FOREIGN KEY (product_id)
        REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE product_images (
    image_id   INT           NOT NULL AUTO_INCREMENT,
    product_id INT           NOT NULL,
    variant_id INT           DEFAULT NULL,
    image_url  VARCHAR(500)  NOT NULL,
    is_primary BOOLEAN       DEFAULT FALSE,
    PRIMARY KEY (image_id),
    CONSTRAINT fk_image_product FOREIGN KEY (product_id)
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_image_variant FOREIGN KEY (variant_id)
        REFERENCES product_variants(variant_id) ON DELETE SET NULL
);

-- ============================================================
-- USER ACTIVITY (Cart, Wishlists, Reviews)
-- ============================================================

CREATE TABLE cart (
    cart_id    INT      NOT NULL AUTO_INCREMENT,
    user_id    INT      NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (cart_id),
    CONSTRAINT fk_cart_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
    cart_item_id INT NOT NULL AUTO_INCREMENT,
    cart_id      INT NOT NULL,
    variant_id   INT NOT NULL,
    quantity     INT NOT NULL DEFAULT 1,
    PRIMARY KEY (cart_item_id),
    UNIQUE KEY uq_cart_variant (cart_id, variant_id),
    CONSTRAINT fk_cartitem_cart    FOREIGN KEY (cart_id)
        REFERENCES cart(cart_id)                   ON DELETE CASCADE,
    CONSTRAINT fk_cartitem_variant FOREIGN KEY (variant_id)
        REFERENCES product_variants(variant_id)    ON DELETE CASCADE,
    CONSTRAINT chk_cartitem_qty CHECK (quantity > 0)
);

CREATE TABLE wishlists (
    wishlist_id INT NOT NULL AUTO_INCREMENT,
    user_id     INT NOT NULL,
    product_id  INT NOT NULL,
    PRIMARY KEY (wishlist_id),
    UNIQUE KEY uq_wishlist (user_id, product_id),
    CONSTRAINT fk_wishlist_user    FOREIGN KEY (user_id)
        REFERENCES users(user_id)        ON DELETE CASCADE,
    CONSTRAINT fk_wishlist_product FOREIGN KEY (product_id)
        REFERENCES products(product_id)  ON DELETE CASCADE
);

CREATE TABLE reviews (
    review_id  INT          NOT NULL AUTO_INCREMENT,
    product_id INT          NOT NULL,
    user_id    INT          NOT NULL,
    rating     TINYINT      NOT NULL,
    title      VARCHAR(255) DEFAULT NULL,
    body       TEXT,
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (review_id),
    UNIQUE KEY uq_review (user_id, product_id),
    CONSTRAINT fk_review_product FOREIGN KEY (product_id)
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_user FOREIGN KEY (user_id)
        REFERENCES users(user_id)       ON DELETE CASCADE,
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5)
);

-- ============================================================
-- THE CHECKOUT FLOW (Orders & Payments)
-- ============================================================

CREATE TABLE orders (
    order_id      INT           NOT NULL AUTO_INCREMENT,
    user_id       INT           NOT NULL,
    address_id    INT           NOT NULL,
    coupon_id     INT           DEFAULT NULL,
    order_date    DATETIME      DEFAULT CURRENT_TIMESTAMP,
    total_amount  DECIMAL(10,2) NOT NULL,
    status        VARCHAR(50)   NOT NULL DEFAULT 'pending',
    delivery_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_order_user    FOREIGN KEY (user_id)
        REFERENCES users(user_id)          ON DELETE RESTRICT,
    CONSTRAINT fk_order_address FOREIGN KEY (address_id)
        REFERENCES addresses(address_id)   ON DELETE RESTRICT,
    CONSTRAINT fk_order_coupon  FOREIGN KEY (coupon_id)
        REFERENCES coupons(coupon_id)      ON DELETE SET NULL
);

CREATE TABLE order_items (
    order_item_id     INT           NOT NULL AUTO_INCREMENT,
    order_id          INT           NOT NULL,
    variant_id        INT           NOT NULL,
    quantity          INT           NOT NULL,
    price_at_purchase DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_item_id),
    UNIQUE KEY uq_order_variant (order_id, variant_id),
    CONSTRAINT fk_orderitem_order   FOREIGN KEY (order_id)
        REFERENCES orders(order_id)              ON DELETE CASCADE,
    CONSTRAINT fk_orderitem_variant FOREIGN KEY (variant_id)
        REFERENCES product_variants(variant_id)  ON DELETE RESTRICT,
    CONSTRAINT chk_orderitem_qty CHECK (quantity > 0)
);

CREATE TABLE payments (
    payment_id     INT           NOT NULL AUTO_INCREMENT,
    order_id       INT           NOT NULL,
    amount         DECIMAL(10,2) NOT NULL,
    method         VARCHAR(50)   NOT NULL,
    status         VARCHAR(50)   NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(255)  UNIQUE DEFAULT NULL,
    paid_at        DATETIME      DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (payment_id),
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE RESTRICT
);

CREATE TABLE payment_methods (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    card_number VARCHAR(16) NOT NULL,
    expiry_date VARCHAR(5) NOT NULL,
    cvc VARCHAR(4) NOT NULL,
    is_default TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE used_coupons (
    used_id   INT NOT NULL AUTO_INCREMENT,
    coupon_id INT NOT NULL,
    user_id   INT NOT NULL,
    PRIMARY KEY (used_id),
    CONSTRAINT fk_usedcoupon_coupon FOREIGN KEY (coupon_id)
        REFERENCES coupons(coupon_id) ON DELETE CASCADE,
    CONSTRAINT fk_usedcoupon_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- PERFORMANCE INDEXES
-- ============================================================
CREATE INDEX idx_orders_user_id  ON orders(user_id);
CREATE INDEX idx_orders_status   ON orders(status);
CREATE INDEX idx_order_items     ON order_items(order_id);
CREATE INDEX idx_cart_items      ON cart_items(cart_id);
CREATE INDEX idx_variants_prod   ON product_variants(product_id);
CREATE INDEX idx_reviews_prod    ON reviews(product_id);
CREATE INDEX idx_addresses_user  ON addresses(user_id);
CREATE INDEX idx_products_active ON products(is_active);