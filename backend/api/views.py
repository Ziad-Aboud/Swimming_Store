import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
# Added PhoneNumbers to the end of this line!
from .models import Products, Users, Cart, CartItems, ProductVariants, Coupons, UsedCoupons, Orders, OrderItems, Wishlists, PhoneNumbers, Addresses, Cities, States, PaymentMethods, Payments, Reviews, Categories, ProductCategories, ProductImages
from django.db import transaction
from django.core.paginator import Paginator

# 1. Get Products with Advanced Filtering & Pagination
def get_products(request):
    if request.method == 'GET':
        try:
            query = Products.objects.filter(is_active=True)

            # --- Search Filter ---
            search = request.GET.get('search')
            if search:
                query = query.filter(name__icontains=search)

            # --- Category Filter ---
            category_ids = request.GET.getlist('category')
            if category_ids:
                linked_ids = ProductCategories.objects.filter(
                    category_id__in=category_ids
                ).values_list('product_id', flat=True)
                query = query.filter(product_id__in=linked_ids)

            # --- Price Range Filter ---
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')
            if min_price:
                query = query.filter(base_price__gte=min_price)
            if max_price:
                query = query.filter(base_price__lte=max_price)

            # --- Sorting Logic ---
            sort = request.GET.get('sort', 'default')
            if sort == 'price-low' or sort == 'price_low':
                query = query.order_by('base_price') # Cheapest first
            elif sort == 'price-high' or sort == 'price_high':
                query = query.order_by('-base_price') # Most expensive first
            elif sort == 'name':
                query = query.order_by('name') # Alphabetical A-Z
            else:
                query = query.order_by('-product_id') # Newest default
            
            query = query.values('product_id', 'name', 'description', 'base_price')
            
            # --- Pagination Logic ---
            # Show 12 products per page
            paginator = Paginator(query, 12) 
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            product_list = list(page_obj.object_list)
            for prod in product_list:
                # Ask the database for the images linked to this specific product_id
                images = ProductImages.objects.filter(product_id=prod['product_id']).values('image_url', 'is_primary')
                prod['images'] = list(images) # Attach them to the dictionary!
            
            # We now return the products with their images!
            return JsonResponse({
                'products': product_list,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'total_items': paginator.count
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 2. Register User
@csrf_exempt 
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password_hash = data.get('password_hash')

            if not all([first_name, last_name, email, password_hash]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            email_regex = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
            if not re.match(email_regex, email):
                return JsonResponse({'error': 'Invalid email format.'}, status=400)

            # Check if email exists 
            if Users.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists.'}, status=400)

            # Hash the password before saving
            hashed_password = make_password(password_hash)

            # 4. Save to database 
            new_user = Users.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=hashed_password,
                role='customer',
                created_at=timezone.now(), 
                is_active=1
            )

            return JsonResponse({
                'message': 'Customer registered successfully!',
                'userId': new_user.user_id
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
# 3. User Login
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = Users.objects.filter(email=email).first()

            if not user:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)

            if check_password(password, user.password_hash) or user.password_hash == password:
                if user.password_hash == password:
                    user.password_hash = make_password(password)
                    user.save()

                phone_record = PhoneNumbers.objects.filter(user_id=user.user_id).first()
                user_phone = phone_record.phone_number if phone_record else ""

                return JsonResponse({
                    'message': 'Login successful!',
                    'user': {
                        'id': user.user_id,
                        'first_name': user.first_name,
                        'last_name': user.last_name, 
                        'email': user.email,
                        'dob': str(user.dob) if user.dob else "", # Safely format the date
                        'phone': user_phone,         
                        'role': user.role
                    }
                }, status=200)
            else:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
# 4. Add to Cart (The Secure Version)
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            variant_id = data.get('variant_id')
            quantity = int(data.get('quantity', 1))

            variant = ProductVariants.objects.filter(variant_id=variant_id).first()
            if not variant:
                return JsonResponse({'error': 'Product variant not found.'}, status=404)

            cart, created = Cart.objects.get_or_create(user_id=user_id)
            
            # --- FIX: Update the Cart Timestamps! ---
            from django.utils import timezone
            if created:
                cart.created_at = timezone.now()
            cart.updated_at = timezone.now()
            cart.save()

            cart_item = CartItems.objects.filter(cart_id=cart.cart_id, variant_id=variant_id).first()
            
            current_qty_in_cart = cart_item.quantity if cart_item else 0
            proposed_total_qty = current_qty_in_cart + quantity

            if proposed_total_qty > variant.stock_quantity:
                return JsonResponse({
                    'error': f'Cannot add {quantity}. You already have {current_qty_in_cart} in your cart, and only {variant.stock_quantity} exist in stock.'
                }, status=400)
            
            if cart_item:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                CartItems.objects.create(cart_id=cart.cart_id, variant_id=variant_id, quantity=quantity)

            return JsonResponse({'message': 'Item successfully added to cart!'}, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. Manage Cart Items (Update Quantity or Delete)
@csrf_exempt
def manage_cart_item(request, cart_item_id):
    cart_item = CartItems.objects.filter(cart_item_id=cart_item_id).first()
    
    if not cart_item:
        return JsonResponse({'error': 'Item not found in cart.'}, status=404)

    from django.utils import timezone
    cart = cart_item.cart
    cart.updated_at = timezone.now()
    cart.save()

    if request.method == 'DELETE':
        cart_item.delete() 
        return JsonResponse({'message': 'Item successfully removed from cart!'})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            new_quantity = int(data.get('quantity', 0))

            if new_quantity <= 0:
                cart_item.delete()
                return JsonResponse({'message': 'Quantity reached 0. Item removed from cart.'})

            variant = cart_item.variant
            if new_quantity > variant.stock_quantity:
                return JsonResponse({
                    'error': 'Not enough stock available.',
                    'available_stock': variant.stock_quantity
                }, status=400)

            cart_item.quantity = new_quantity
            cart_item.save()
            return JsonResponse({'message': 'Cart quantity updated successfully!'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 6. View User's Cart (The Mega Join, Python Style)
def view_cart(request, user_id):
    if request.method == 'GET':
        try:
            # 1. Find the cart for this user
            cart = Cart.objects.filter(user_id=user_id).first()
            
            # If they don't have a cart, or the cart exists but has no items
            if not cart or not CartItems.objects.filter(cart_id=cart.cart_id).exists():
                return JsonResponse({'message': 'Your cart is empty.', 'items': []}, status=200)

            # 2. Get all items in this cart
            items = CartItems.objects.filter(cart_id=cart.cart_id)
            
            cart_data = []
            grand_total = 0

            # 3. Loop through the items and jump across tables using dot notation!
            for item in items:
                variant = item.variant 
                product = variant.product 

                img_record = ProductImages.objects.filter(product_id=product.product_id).first()
                p_image = img_record.image_url if img_record else '../assets/placeholder.jpg'

                unit_price = product.base_price + variant.price_adjustment
                total_item_price = unit_price * item.quantity
                grand_total += total_item_price

                cart_data.append({
                    'cart_item_id': item.cart_item_id,
                    'product_id': product.product_id,
                    'product_name': product.name,
                    'color': variant.color,
                    'size': variant.size,
                    'quantity': item.quantity,
                    'unit_price': float(unit_price),
                    'total_item_price': float(total_item_price),
                    'image': p_image
                })

            return JsonResponse({
                'message': 'Cart retrieved successfully',
                'grand_total': float(grand_total),
                'items': cart_data
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 8. Checkout (The Database Transaction)
@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            coupon_code = data.get('coupon_code') 
            address_id = data.get('address_id') 
            payment_method_str = data.get('payment_method')

            # 1. Basic Validation
            if not address_id:
                return JsonResponse({'error': 'Shipping address is required.'}, status=400)

            cart = Cart.objects.filter(user_id=user_id).first()
            if not cart:
                return JsonResponse({'error': 'No active cart found.'}, status=400)

            items = CartItems.objects.filter(cart_id=cart.cart_id)
            if not items.exists():
                return JsonResponse({'error': 'Your cart is empty.'}, status=400)

            from django.utils import timezone

            with transaction.atomic():
                
                # 2. Calculate Subtotal & Check Stock
                subtotal = 0
                for item in items:
                    variant = item.variant
                    if item.quantity > variant.stock_quantity:
                        raise Exception(f"Not enough stock for {variant.product.name}. Only {variant.stock_quantity} left.")
                    
                    unit_price = variant.product.base_price + variant.price_adjustment
                    subtotal += float(unit_price) * item.quantity

                discounted_subtotal = subtotal
                applied_coupon = None

                # 3. Handle Coupon Validation & Math
                if coupon_code:
                    coupon = Coupons.objects.filter(code=coupon_code, is_active=1).first()
                    if not coupon:
                        raise Exception("Invalid or expired coupon.")
                    if coupon.max_uses and coupon.times_used >= coupon.max_uses:
                        raise Exception("This coupon has reached its usage limit.")
                    if UsedCoupons.objects.filter(user_id=user_id, coupon=coupon).exists():
                        raise Exception("You have already used this coupon.")
                    
                    if str(coupon.discount_type) == '1': 
                        discount = subtotal * (float(coupon.discount_value) / 100)
                    else:
                        discount = float(coupon.discount_value)
                    
                    discounted_subtotal -= discount
                    if discounted_subtotal < 0: discounted_subtotal = 0 
                    
                    applied_coupon = coupon
                    coupon.times_used += 1
                    coupon.save()

                # 4. Add Shipping and Tax
                shipping = 0 if discounted_subtotal > 100 else 9.99
                tax = discounted_subtotal * 0.08
                final_total = discounted_subtotal + shipping + tax

                # 5. Create the Order
                new_order = Orders.objects.create(
                    user_id=user_id,
                    address_id=address_id,
                    total_amount=final_total,
                    delivery_cost=shipping,
                    status='Pending',
                    coupon=applied_coupon,
                    order_date=timezone.now()
                )

                # 0 for Cash, 1 for Card
                method_code = 0 if payment_method_str == 'cash' else 1
                
                payment_status = 'Pending' if method_code == 0 else 'Completed'
                paid_time = None if method_code == 0 else timezone.now()
                txn_id = None if method_code == 0 else f"TXN-{new_order.order_id}-{int(timezone.now().timestamp())}"

                Payments.objects.create(
                    order=new_order,
                    amount=final_total,
                    method=method_code,
                    status=payment_status,
                    transaction_id=txn_id,
                    paid_at=paid_time
                )

                # 6. Move Items to OrderItems & Deduct Stock
                for item in items:
                    variant = item.variant
                    unit_price = variant.product.base_price + variant.price_adjustment
                    
                    OrderItems.objects.create(
                        order=new_order,
                        variant=variant,
                        quantity=item.quantity,
                        price_at_purchase=unit_price
                    )
                    variant.stock_quantity -= item.quantity
                    variant.save()

                # 7. Lock the Coupon for this user
                if applied_coupon:
                    UsedCoupons.objects.create(user_id=user_id, coupon=applied_coupon)

                # 8. Empty the Cart
                items.delete()

            return JsonResponse({
                'message': 'Order placed successfully!',
                'order_id': new_order.order_id
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
# 9. Get Single Product Details & Variants
def get_product_detail(request, product_id):
    if request.method == 'GET':
        try:
            product = Products.objects.filter(product_id=product_id, is_active=True).first()
            if not product:
                return JsonResponse({'error': 'Product not found'}, status=404)

            # Fetch all variants linked to this specific product
            variants = ProductVariants.objects.filter(product_id=product_id)
            variant_data = []
            
            for v in variants:
                variant_data.append({
                    'variant_id': v.variant_id,
                    'size': v.size,
                    'color': v.color,
                    'stock': v.stock_quantity,
                    'price_adjustment': float(v.price_adjustment)
                })

            # Fetch all images for this specific product 
            images = ProductImages.objects.filter(product_id=product_id).values('image_url', 'is_primary')

            return JsonResponse({
                'product_id': product.product_id,
                'name': product.name,
                'description': product.description,
                'base_price': float(product.base_price),
                'variants': variant_data,
                'images': list(images) 
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 10. Toggle Wishlist (Add or Remove)
@csrf_exempt
def toggle_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            product_id = data.get('product_id')

            # Check if it's already there
            wish_item = Wishlists.objects.filter(user_id=user_id, product_id=product_id).first()

            if wish_item:
                wish_item.delete()
                return JsonResponse({'message': 'Removed from wishlist', 'added': False})
            else:
                Wishlists.objects.create(user_id=user_id, product_id=product_id)
                return JsonResponse({'message': 'Added to wishlist!', 'added': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 11. Get User's Wishlist (Upgraded with Images)
def get_wishlist(request, user_id):
    if request.method == 'GET':
        try:
            # 1. Get the list of product IDs this user likes
            wish_ids = list(Wishlists.objects.filter(user_id=user_id).values_list('product_id', flat=True))
            
            # 2. Fetch the actual product data for those IDs
            products = Products.objects.filter(product_id__in=wish_ids, is_active=True).values(
                'product_id', 'name', 'description', 'base_price'
            )
            
            # --- Fetch images for the wishlist products! ---
            product_list = list(products)
            for prod in product_list:
                images = ProductImages.objects.filter(product_id=prod['product_id']).values('image_url', 'is_primary')
                prod['images'] = list(images)
            
            valid_wish_ids = [p['product_id'] for p in product_list]
            
            # 3. Send BOTH back to the frontend
            return JsonResponse({
                'wishlist_ids': valid_wish_ids, 
                'products': product_list
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 12. Get User Order History
def get_user_orders(request, user_id):
    if request.method == 'GET':
        try:
            # Get all orders for this user, newest first
            orders = Orders.objects.filter(user_id=user_id).order_by('-order_id')
            
            order_list = []
            for order in orders:
                items = OrderItems.objects.filter(order=order)
                item_list = []
                
                for item in items:
                    # Safely try to get the product details AND the image
                    try:
                        p_name = item.variant.product.name
                        p_color = item.variant.color
                        p_size = item.variant.size
                        
                        p_id = item.variant.product.product_id
                        img_record = ProductImages.objects.filter(product_id=p_id).first()
                        p_image = img_record.image_url if img_record else '../assets/placeholder.jpg'
                        
                    except Exception:
                        # Fallback for deleted products
                        p_name = "Discontinued Item"
                        p_color = "N/A"
                        p_size = "N/A"
                        p_image = '../assets/placeholder.jpg'

                    item_list.append({
                        'product_name': p_name,
                        'color': p_color,
                        'size': p_size,
                        'quantity': item.quantity,
                        'price': float(item.price_at_purchase),
                        'image': p_image  
                    })
                    
                order_list.append({
                    'order_id': order.order_id,
                    'status': order.status,
                    'total': float(order.total_amount),
                    'items': item_list
                })
                
            return JsonResponse({'orders': order_list}, status=200)
            
        except Exception as e:
            print("Order History Error:", str(e)) 
            return JsonResponse({'error': str(e)}, status=500)
        
# 13. Update User Profile
@csrf_exempt
def update_profile(request, user_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = Users.objects.filter(user_id=user_id).first()

            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)

            current_password = data.get('current_password')
            new_password = data.get('new_password')

            if new_password:
                if not current_password:
                    return JsonResponse({'error': 'Current password is required to change it.'}, status=400)
                if user.password_hash != current_password:
                    return JsonResponse({'error': 'Incorrect current password.'}, status=400)
                
                user.password_hash = new_password

            # --- 2. UPDATE PERSONAL INFO ---
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            
            if 'dob' in data and data['dob']:
                user.dob = data.get('dob')

            user.save()

            phone_input = data.get('phone')
            if phone_input:
                phone_record = PhoneNumbers.objects.filter(user_id=user.user_id).first()
                if phone_record:
                    # Update existing record
                    phone_record.phone_number = phone_input
                    phone_record.save()
                else:
                    # Create new record if they didn't have one
                    PhoneNumbers.objects.create(user_id=user.user_id, phone_number=phone_input)

            # --- 3. SEND BACK THE UPDATED DATA ---
            updated_phone = PhoneNumbers.objects.filter(user_id=user.user_id).first()
            
            return JsonResponse({
                'message': 'Profile updated successfully!',
                'user': {
                    'id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'dob': str(user.dob) if user.dob else "",
                    'phone': updated_phone.phone_number if updated_phone else ''
                }
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 14. Manage Addresses
@csrf_exempt
def manage_addresses(request, user_id):
    # --- GET ALL SAVED ADDRESSES ---
    if request.method == 'GET':
        try:
            addresses = Addresses.objects.filter(user_id=user_id)
            addr_list = []
            for addr in addresses:
                addr_list.append({
                    'address_id': addr.address_id,
                    'street_address': addr.street_address,
                    'city': addr.city.name if addr.city else '',
                    'state': addr.state_province.name if addr.state_province else '',
                    'postal_code': addr.postal_code,
                    'country': addr.country,
                    'is_default': bool(addr.is_default)
                })
            return JsonResponse({'addresses': addr_list}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # --- ADD A NEW ADDRESS ---
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extract City and State text from the frontend
            state_name = data.get('state', 'Unknown State')
            city_name = data.get('city', 'Unknown City')
            
            # Safely Get or Create the State (Defaults delivery cost to $10 if it's brand new)
            state_obj, _ = States.objects.get_or_create(
                name=state_name, 
                defaults={'delivery_cost': 10.00}
            )
            
            # Safely Get or Create the City
            city_obj, _ = Cities.objects.get_or_create(
                name=city_name,
                defaults={'state': state_obj}
            )

            # Save the new Address linked to the User, City, and State
            new_address = Addresses.objects.create(
                user_id=user_id,
                street_address=data.get('street_address'),
                city=city_obj,
                state_province=state_obj,
                postal_code=data.get('postal_code'),
                country=data.get('country', 'Egypt'),
                is_default=1 if data.get('is_default') else 0
            )
            
            # If they checked "Set as Default", remove the default flag from their old addresses
            if new_address.is_default:
                Addresses.objects.filter(user_id=user_id).exclude(address_id=new_address.address_id).update(is_default=0)

            return JsonResponse({'message': 'Address added successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 15. Delete Address
@csrf_exempt
def delete_address(request, address_id):
    if request.method == 'DELETE':
        try:
            address = Addresses.objects.filter(address_id=address_id).first()
            
            if not address:
                return JsonResponse({'error': 'Address not found.'}, status=404)

            address.delete()
            return JsonResponse({'message': 'Address deleted successfully!'}, status=200)
            
        except Exception as e:
            error_msg = str(e)
            
            if '1451' in error_msg or 'foreign key constraint fails' in error_msg.lower():
                return JsonResponse({
                    'error': 'Cannot delete this address because it is linked to your past orders.'
                }, status=400)
                
            return JsonResponse({'error': error_msg}, status=500)
        
# 16. Set Default Address
@csrf_exempt
def set_default_address(request, user_id, address_id):
    if request.method == 'PUT':
        try:
            with transaction.atomic():
                # 1. Unset the default flag for all of this user's addresses
                Addresses.objects.filter(user_id=user_id).update(is_default=0)
                
                # 2. Set the specific address as the new default
                address = Addresses.objects.filter(address_id=address_id, user_id=user_id).first()
                if not address:
                    return JsonResponse({'error': 'Address not found'}, status=404)
                
                address.is_default = 1
                address.save()
                
            return JsonResponse({'message': 'Default address updated!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
# 17. Validate Coupon
@csrf_exempt
def validate_coupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('coupon_code')
            user_id = data.get('user_id')
            
            # 1. Find the coupon
            coupon = Coupons.objects.filter(code=code, is_active=1).first()
            
            if not coupon:
                return JsonResponse({'error': 'Invalid or expired coupon code.'}, status=404)
            
            # 2. Check Expiry Date (if set)
            from django.utils import timezone
            if coupon.expires_at and coupon.expires_at < timezone.now():
                return JsonResponse({'error': 'This coupon has expired.'}, status=400)
            
            # 3. Check Usage Limits
            if coupon.max_uses and coupon.times_used >= coupon.max_uses:
                return JsonResponse({'error': 'This coupon has reached its usage limit.'}, status=400)
            
            # 4. Check if User has already used it
            if UsedCoupons.objects.filter(user_id=user_id, coupon=coupon).exists():
                return JsonResponse({'error': 'You have already used this coupon.'}, status=400)
            
            # 5. Return success and the discount details
            return JsonResponse({
                'message': 'Coupon applied!',
                'discount_type': coupon.discount_type,
                'discount_value': float(coupon.discount_value)
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
from django.db import transaction

# 18. Manage Payment Methods
@csrf_exempt
def manage_payments(request, user_id):
    if request.method == 'GET':
        try:
            payments = PaymentMethods.objects.filter(user_id=user_id)
            pay_list = []
            for p in payments:
                pay_list.append({
                    'payment_id': p.payment_id,
                    'last_four': p.card_number[-4:], 
                    'expiry_date': p.expiry_date,
                    'is_default': bool(p.is_default)
                })
            return JsonResponse({'payments': pay_list}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            with transaction.atomic():
                new_card = PaymentMethods.objects.create(
                    user_id=user_id,
                    card_number=data.get('card_number'),
                    expiry_date=data.get('expiry_date'),
                    cvc=data.get('cvc'),
                    is_default=1 if data.get('is_default') else 0
                )
                
                # If set as default, unset all others
                if new_card.is_default:
                    PaymentMethods.objects.filter(user_id=user_id).exclude(payment_id=new_card.payment_id).update(is_default=0)

            return JsonResponse({'message': 'Card added successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 19. Delete Payment Method
@csrf_exempt
def delete_payment(request, payment_id):
    if request.method == 'DELETE':
        try:
            PaymentMethods.objects.filter(payment_id=payment_id).delete()
            return JsonResponse({'message': 'Card deleted!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 20. Set Default Payment Method
@csrf_exempt
def set_default_payment(request, user_id, payment_id):
    if request.method == 'PUT':
        try:
            with transaction.atomic():
                PaymentMethods.objects.filter(user_id=user_id).update(is_default=0)
                card = PaymentMethods.objects.filter(payment_id=payment_id, user_id=user_id).first()
                if card:
                    card.is_default = 1
                    card.save()
            return JsonResponse({'message': 'Default updated!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
# 22. Get Product Reviews
def get_product_reviews(request, product_id):
    if request.method == 'GET':
        try:
            # Fetch reviews, ordered by newest first
            reviews = Reviews.objects.filter(product_id=product_id).order_by('-created_at')
            review_list = []
            total_rating = 0
            
            for r in reviews:
                total_rating += r.rating
                review_list.append({
                    'review_id': r.review_id,
                    'user_id': r.user_id,
                    'user_name': f"{r.user.first_name} {r.user.last_name}",
                    'rating': r.rating,
                    'title': r.title,
                    'body': r.body,
                    # Format the date nicely
                    'date': r.created_at.strftime("%B %d, %Y") if r.created_at else "Unknown Date"
                })
                
            # Calculate the average rating safely
            avg_rating = total_rating / len(reviews) if len(reviews) > 0 else 0
            
            return JsonResponse({
                'reviews': review_list,
                'average_rating': round(avg_rating, 1),
                'total_reviews': len(reviews)
            }, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 23. Add a Product Review
@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            product_id = data.get('product_id')
            
            # 1. Validation: Make sure they sent a rating
            rating = int(data.get('rating', 0))
            if rating < 1 or rating > 5:
                return JsonResponse({'error': 'Please provide a valid rating between 1 and 5.'}, status=400)
            
            # 2. Database Constraint Check: Has this user already reviewed this product?
            existing_review = Reviews.objects.filter(user_id=user_id, product_id=product_id).first()
            if existing_review:
                return JsonResponse({'error': 'You have already reviewed this product.'}, status=400)
                
            from django.utils import timezone
            
            # 3. Save the Review
            new_review = Reviews.objects.create(
                user_id=user_id,
                product_id=product_id,
                rating=rating,
                title=data.get('title', ''),
                body=data.get('body', ''),
                created_at=timezone.now()
            )
            
            return JsonResponse({'message': 'Thank you! Your review has been submitted.'}, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
# 24. Delete Review
@csrf_exempt
def delete_review(request, review_id):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            # Security Check: We filter by BOTH review_id and user_id to ensure 
            # a user can only delete their own review!
            review = Reviews.objects.filter(review_id=review_id, user_id=user_id).first()
            if not review:
                return JsonResponse({'error': 'Review not found or unauthorized.'}, status=403)
                
            review.delete()
            return JsonResponse({'message': 'Review deleted successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 25. Update Review
@csrf_exempt
def update_review(request, review_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            # Security Check again!
            review = Reviews.objects.filter(review_id=review_id, user_id=user_id).first()
            if not review:
                return JsonResponse({'error': 'Review not found or unauthorized.'}, status=403)
                
            review.rating = int(data.get('rating', review.rating))
            review.title = data.get('title', review.title)
            review.body = data.get('body', review.body)
            review.save()
            
            return JsonResponse({'message': 'Review updated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
# 26. Get All Categories (with Product Counts!)
def get_categories(request):
    if request.method == 'GET':
        try:
            categories = Categories.objects.all()
            cat_list = []
            
            for cat in categories:
                # Count how many products are linked to this category in the junction table
                count = ProductCategories.objects.filter(category_id=cat.category_id).count()
                
                cat_list.append({
                    'category_id': cat.category_id,
                    'name': cat.name,
                    'product_count': count
                })
                
            return JsonResponse({'categories': cat_list}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 27. Get Related Products (Same Category)
def get_related_products(request, product_id):
    if request.method == 'GET':
        try:
            # 1. Find which categories the current product belongs to
            category_ids = ProductCategories.objects.filter(
                product_id=product_id
            ).values_list('category_id', flat=True)

            # 2. Find other products in those exact categories, EXCLUDING the current product
            related_ids = ProductCategories.objects.filter(
                category_id__in=category_ids
            ).exclude(product_id=product_id).values_list('product_id', flat=True)
            
            query = Products.objects.filter(
                product_id__in=related_ids, 
                is_active=True
            ).distinct()[:4]
            
            products = query.values('product_id', 'name', 'description', 'base_price')
            
            product_list = list(products)
            for prod in product_list:
                images = ProductImages.objects.filter(product_id=prod['product_id']).values('image_url', 'is_primary')
                prod['images'] = list(images)
            
            return JsonResponse({'related_products': product_list}, status=200)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)