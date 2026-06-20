# core/models.py

from features.user.models.user import User
from features.auth.models.refresh_token import RefreshToken
# from features.orders.models.order import Order
# from features.products.models.product import Product
# ... una línea por cada modelo de cada feature

__all__ = [
    "User",
    "RefreshToken",
    # "Order",
    # "Product",
]