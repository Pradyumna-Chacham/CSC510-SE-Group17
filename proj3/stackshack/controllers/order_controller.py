from models.order import Order, OrderItem
from database.db import db


class OrderController:

    @staticmethod
    def get_user_orders(user_id):
        """Retrieves all orders for a specific user."""
        try:
            orders = (
                Order.query.filter_by(user_id=user_id)
                .order_by(Order.ordered_at.desc())
                .all()
            )
            return True, "Orders retrieved successfully", orders
        except Exception as e:
            return False, f"Error retrieving orders: {str(e)}", None

    @staticmethod
    def create_new_order(user_id, item_data):
        """Creates a new order for the specified user with the given items."""
        if not item_data:
            return False, "Order cannot be empty.", None

        total_price = 0
        new_order = Order(user_id=user_id, total_price=0, status="Pending")
        db.session.add(new_order)
        db.session.flush()  # Get the order ID before commit

        try:
            for item_id, price, quantity, name in item_data:
                price_float = float(price)
                quantity_int = int(quantity)

                if quantity_int <= 0:
                    continue

                order_item = OrderItem(
                    order_id=new_order.id,
                    menu_item_id=item_id if item_id else None,
                    name=name,
                    price=price_float,
                    quantity=quantity_int,
                )
                db.session.add(order_item)
                total_price += price_float * quantity_int

            new_order.total_price = total_price
            db.session.commit()
            return True, f"Order #{new_order.id} placed successfully.", new_order
        except Exception as e:
            db.session.rollback()
            return False, f"Error placing order: {str(e)}", None
