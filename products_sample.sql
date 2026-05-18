
-- 1. PREPARE THE DATABASE
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Product_Categories;
TRUNCATE TABLE Product_Variants;
TRUNCATE TABLE product_images;
TRUNCATE TABLE Products;
TRUNCATE TABLE Categories;
SET FOREIGN_KEY_CHECKS = 1;

-- 2. INSERT CATEGORIES
INSERT INTO Categories (category_id, parent_category_id, name) VALUES
(1, NULL, 'Swim Shorts'),
(2, NULL, 'Goggles'),
(3, NULL, 'Swim Caps'),
(4, NULL, 'Fins');

-- 3. INSERT PRODUCTS
INSERT INTO Products (product_id, name, description, base_price, is_active) VALUES
-- Swim Shorts (1-11)
(1,  'Blue Swim Shorts',             'Light blue solid color swim shorts with drawstring waist and silver-tipped cords.', 89.99, 1),
(2,  'Gucci GG Swim Shorts',         'Dark green swim shorts with all-over GG monogram jacquard pattern and drawstring waist.', 299.99, 1),
(3,  'Pink Swim Shorts',             'Rose/mauve solid color swim shorts with cream drawstring and embroidered logo.', 179.99, 1),
(4,  'Black Swim Shorts',            'Black solid color swim shorts with grey drawstring and embroidered logo detail.', 179.99, 1),
(5,  'Blue Splash Print Swim Shorts','Blue and white abstract splash/mosaic print swim shorts with white drawstring.', 129.99, 1),
(6,  'Blue Stripe Swim Shorts',      'Light blue and white vertical stripe seersucker swim shorts with white drawstring.', 119.99, 1),
(7,  'Turtle Print Swim Shorts',     'Black swim shorts with colorful turtle all-over print in blue, teal and white, blue rope drawstring.', 149.99, 1),
(8,  'Pro Swim Goggles Black',       'Sleek black professional swim goggles with smoked lenses and adjustable strap.', 49.99, 1),
(9,  'Training Swim Goggles',        'Grey and black wide-lens training swim goggles with anti-fog smoked lenses and adjustable strap.', 39.99, 1),
(10, 'Forza Kids Swim Goggles',      'Colorful kids swim goggles in pink, purple and teal with pink lenses by Forza.', 24.99, 1),
(11, 'White Stripe Swim Shorts',     'Light blue and white vertical stripe seersucker swim shorts with white drawstring.', 119.99, 1),
-- Swim Caps (12-16)
(12, 'Speedo Solid Silicone Cap Blue',  'Classic adult silicone swim cap in blue, latex-free, chlorine-resistant, snag-free fit.', 12.99, 1),
(13, 'Arena Moulded Silicone Cap',      'Ergonomic 3D moulded silicone cap for a hydrodynamic, wrinkle-free fit. Ideal for training and competition.', 14.99, 1),
(14, 'TYR Latex Solid Swim Cap',        'Lightweight breathable latex cap, budget-friendly option for daily training.', 6.99,  1),
(15, 'Speedo Long Hair Silicone Cap',   'Extra-volume silicone cap designed for long, thick, or natural hair with a low bun.', 18.99, 1),
(16, 'Kids Silicone Swim Cap Pink',     'Soft, durable silicone cap sized for youth swimmers in a bright pink color.', 9.99,  1),
-- Fins (17-21)
(17, 'Speedo Short Blade Training Fins','Short blade fins for faster kick tempo and leg strength development. Open heel design.', 35.00, 1),
(18, 'Arena Training Swim Fins',        'Soft short-blade fins for fitness and competitive swimmers, open heel for freedom of movement.', 38.99, 1),
(19, 'FINIS Long Floating Fins',        'Long blade fins for maximum propulsion and endurance training. Great for snorkeling too.', 55.00, 1),
(20, 'CAPAS Short Blade Swim Fins',     'Closed heel soft rubber fins promoting shorter, faster kicks. Suitable for all skill levels.', 29.99, 1),
(21, 'Mermaid Monofin',                 'Butterfly dolphin-kick monofin for advanced technique training. Adult size.', 65.00, 1);

-- 4. LINK PRODUCTS TO CATEGORIES
INSERT INTO Product_Categories (product_id, category_id) VALUES
(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(11,1),
(8,2),(9,2),(10,2),
(12,3),(13,3),(14,3),(15,3),(16,3),
(17,4),(18,4),(19,4),(20,4),(21,4);

-- 5. INSERT PRODUCT VARIANTS
INSERT INTO Product_Variants (product_id, sku, size, color, price_adjustment, stock_quantity) VALUES
(1,  'SKU-001', 'Medium',    'Light Blue',          0.00, 50),
(2,  'SKU-002', 'Medium',    'Dark Green',          0.00, 20),
(3,  'SKU-003', 'Medium',    'Rose/Mauve',          0.00, 35),
(4,  'SKU-004', 'Medium',    'Black',               0.00, 35),
(5,  'SKU-005', 'Medium',    'Blue/White',          0.00, 45),
(6,  'SKU-006', 'Medium',    'Blue/White Stripe',   0.00, 40),
(7,  'SKU-007', 'Medium',    'Black/Turtle Print',  0.00, 30),
(8,  'SKU-008', 'One Size',  'Black',               0.00, 60),
(9,  'SKU-009', 'One Size',  'Grey/Black',          0.00, 60),
(10, 'SKU-010', 'Kids',      'Pink/Purple/Teal',    0.00, 80),
(11, 'SKU-011', 'Medium',    'White/Blue Stripe',   0.00, 40),
(12, 'SKU-012', 'One Size',  'Blue',                0.00, 150),
(13, 'SKU-013', 'One Size',  'Royal Blue',          0.00, 120),
(14, 'SKU-014', 'One Size',  'Black',               0.00, 300),
(15, 'SKU-015', 'One Size',  'Black',               0.00, 80),
(16, 'SKU-016', 'Kids',      'Pink',                0.00, 100),
(17, 'SKU-017', 'Medium (8-9)',   'Blue/Yellow',    0.00, 60),
(18, 'SKU-018', 'Medium',         'Black/Blue',     0.00, 50),
(19, 'SKU-019', 'Large (10-11)',  'Black',          0.00, 40),
(20, 'SKU-020', 'Medium (8-9)',   'Grey',           0.00, 75),
(21, 'SKU-021', 'Adult',          'Black',          0.00, 15);

-- 6. INSERT PRODUCT IMAGES
INSERT INTO product_images (product_id, variant_id, image_url, is_primary) VALUES
(1,  NULL, 'https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcQ90pIXMzEoMpsywQvGpuNc36Xmaefvuz6Rn_sau79GIRZ3PPKgVaMdJIhARJWdKK223io4RF0dFDXy9aJ1rE0sRQVbv1yqQlaBLG0b-grWM6Ug3DUBAxZLbZfpDvluJnnJAI-aONc&usqp=CAc', 1),
(2,  NULL, 'https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcSF47YUlfjizPPJjiBoc4YR1OpAulnnGHOnktm9TCOzlz-rFjrA9dFwxGeX1ovsKwp16cg1iGKjzRNx1MmcthTP0nJ3gIdHuC301TwYJde2iz3qZtA8mnNArasGoBilMgSNH40mhQ&usqp=CAc', 1),
(3,  NULL, 'https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcTNvST1-_5yEi9zpxaiP3F_W7lty6UWAExYJkHyt6Acl09AR_g9zwAhAiJuh8iBI79ACHk4QyKps4myThpUnHymFVfx5fh4AArFc00Fmkb5jAbIHbGTiA5DEouJVKSvD0AT98vIkA&usqp=CAc', 1),
(4,  NULL, 'https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQYGPcbzW5ZNYXYNnq9JzkmM8BCj5IrYjOvsQaObvTi5-OFdAk409jMdj6UwJquhauT9oBJMWr28USUcID6asY-FQUuYzS4UlRrJ8aZzWTyAxAAAqJp9CKGWUrOHnnNJFysuiO4Kks&usqp=CAc', 1),
(5,  NULL, 'https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcT4AS3gNJTEqL-M6zXssLzlXIA8K-SAuMsNsCTpiWOSvCIL7W1jdS4NjnB3BsfE4qIdEH4GiJ5OEDCEVQzDWsuXrFtZAaIdxiS2__XEfjq95JldPPAmr3Jl9EQDHyA8BL6sS_0fFQk&usqp=CAc', 1),
(6,  NULL, 'https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcS-6fse_lbxrbS86Xbr9oqGPfhmbNJZxV-r7PTq06IVE-CEVFH-obJYtF2HieMJtdr7H3khID48mLz-h71v7VOuLXGrF3Kh1fFIV2_TsBSAAMR2SA&usqp=CAc', 1),
(7,  NULL, 'https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcSeCmGKArAkHNOAAEZsYvC1Tvnz_U3RswX0KYVer_IwXvmrPdjJKME2Ry-pDXkXF3W1gr2rQym3szbEFkuT1MwyFkvvjzh6HTaw65OZj60Ey4h3wxlpD4i7b6neVxELiLJ7xG6rag&usqp=CAc', 1),
(8,  NULL, 'https://contents.mediadecathlon.com/p2867725/k$cdf7dc72916c0f2009c8109396804419/bfit-500-adult-swimming-goggles-mirrored-lenses-blue-slash-black.jpg', 1),
(9,  NULL, 'https://cdn.thewirecutter.com/wp-content/media/2025/05/BEST-SWIM-GOGGLES-ADULTS-KIDS-7550.jpg?width=2048&quality=60&crop=2048:1365&auto=webp', 1),
(10, NULL, 'https://nwscdn.com/media/catalog/product/cache/h900xw900/f/o/forza_kids_goggles_config_main.jpg', 1),
(11, NULL, 'https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcTTZ6CwvAND7rs8K-h6Jb4PjXkgba3R2RAYxi4kkCN28AyTA7KzF88cBzSF5X4jnfzQ2oocGexvEdtGucirOZXEhT1dI0tRI-zDlhT4H77BJs8QBt1dVpk0jMF7yR3hNRGECsVFzw&usqp=CAc', 1),
(12, NULL, 'https://en-kw.sssports.com/dw/image/v2/BDVB_PRD/on/demandware.static/-/Sites-akeneo-master-catalog/default/dw414049d9/sss/SSS2/S/D/8/7/0/SSS2_SD8709908420_5053744445298_2.jpg?sw=700&sh=700&sm=fit', 1),
(13, NULL, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRV-eCYPhABLviol1zod86_DBMDVKta7Kfm9g&s', 1),
(14, NULL, 'https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcT5jE_mkjOAG_RAPREsZodKLuwYD9oSDEkxFzdmPxNQsJ5IVfROlnwCxx4fdoAiCju-ciTbyUW9dDv2zdb2zCBz4grkPh20dOOoPI5UCEBx0_FTJuR9Pn5P0horU9mPlg&usqp=CAc', 1),
(15, NULL, 'https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcT2LnTCl8_QZ2nEr296W9ot8NeJCWLxnL2pAKRR511VwXRVhLr1WFieIvrjZsTXkqneg5cRWEsv5B3UQpO43hcSBTOp9xIwJQ6tTHvy5dFL1sHd311sXrp6vwFc1YPSSx8CInYBPg&usqp=CAc', 1),
(16, NULL, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMUmaVvMuMFVhr4P84hBNmDd_MzkfTAYsHmg&s', 1),
(17, NULL, 'https://www.proswimwear.eu/wp-content/uploads/2025/11/sc-jr-pnk-1.jpg', 1),
(18, NULL, 'https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcSLs_2IYxPodn57RnJtM3JfV0GLwe9_WvItqRXc4ZHIexLYzeoZt37reW8Dt312FQaRvdvBpQ0xqANO_cVqljraKHKtnHlrAGqtSqOZ4CGzlZBvFAUuDjkRZCTxr6G3Nw&usqp=CAc', 1),
(19, NULL, 'https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcSmzYDTC0xjw3Sk9jhn3kloIMxvuSJcaJOQwzO1tGTX_En5ERG1jK1DdDhWJUgRcLQOX2BTV65SFqGIiBUVgp9I32vnQAzpHt8R17njxHQMYg4i6Ft1vXaXOdK-6Wkjl4_LgffZ67SvdQ&usqp=CAc', 1),
(20, NULL, 'https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcSMYlmrIcbVCQvh8eZ8RX9OmvJAeHtj6bL21NXaj53lOGcINKNaEsl-XmE1XmJMmOZ6VWFocIKpDEOx5D06QYNVJopychS2C4b2R8XX4p7U3fMTnzNVMfmucg&usqp=CAc', 1),
(21, NULL, 'https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcS6qbVhj-Ub8HfCQUc3bLW0AP1XQo8zGthGYJN3U7ewAbRLtknAmtNWkfJ9iAphbOuszqd84AX8rjKyuOT4J7UeZNxgOuLTiuzFiVjSdMFlOQNJvU1L5kQIuXSvkEROshpRmCzR4ngDuHc&usqp=CAc', 1);