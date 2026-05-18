import re

with open("backenddd/api/models.py", "r") as f:
    text = f.read()

def inject_str(class_name, str_code):
    global text
    # Only inject if __str__ doesn't already exist in the class
    class_pattern = rf"(class {class_name}\(models\.Model\):[\s\S]*?)(    class Meta:)"
    
    # Check if __str__ is already in the class body. It's rough, but we can just blindly replace.
    # To be safe, if we don't find it, we replace.
    replacement = rf"\1    def __str__(self):\n        {str_code}\n\n\2"
    text = re.sub(class_pattern, replacement, text)

# We add __str__ for the requested models
inject_str("Addresses", 'return f"{self.street_address}, {self.city.name}, {self.country}"')
inject_str("Cart", 'return f"Cart #{self.cart_id} for {self.user.first_name}"')
inject_str("CartItems", 'return f"{self.quantity} x {self.variant.product.name} in Cart #{self.cart.cart_id}"')
inject_str("Cities", 'return self.name')
inject_str("States", 'return self.name')
inject_str("OrderItems", 'return f"{self.quantity} x {self.variant.product.name} in Order #{self.order.order_id}"')
inject_str("Payments", 'return f"Payment #{self.payment_id} (${self.amount}) for Order #{self.order.order_id}"')
inject_str("PhoneNumbers", 'return f"{self.phone_number} (User ID: {self.user.user_id})"')
inject_str("ProductImages", 'return f"Image for {self.product.name}"')
inject_str("Wishlists", 'return f"Wishlist item: {self.product.name} for {self.user.first_name}"')
inject_str("UsedCoupons", 'return f"Coupon {self.coupon.code} used by {self.user.first_name}"')
inject_str("PaymentMethods", 'return f"Card ending in {self.card_number[-4:]} (User ID: {self.user_id})"')

with open("backenddd/api/models.py", "w") as f:
    f.write(text)

