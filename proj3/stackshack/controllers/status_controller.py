from models.order import Order
from models.user import User
from database.db import db


class StatusController:
    STATUS_FLOW = {
        "Pending": "Preparing",
        "Preparing": "Ready for Pickup",
        "Ready for Pickup": "Delivered",
        "Delivered": None,
        "Cancelled": None,
    }

    @staticmethod
    def get_status_flow():
        """Returns the status flow mapping for frontend consumption."""
        return {
            "Pending": {
                "display": "Your order has been received and is waiting to be prepared",
                "icon": "📋",
                "nextStatuses": (
                    ["Preparing"] if StatusController.STATUS_FLOW["Pending"] else []
                ),
            },
            "Preparing": {
                "display": "Your order is being prepared in our kitchen",
                "icon": "👨‍🍳",
                "nextStatuses": (
                    ["Ready for Pickup"]
                    if StatusController.STATUS_FLOW["Preparing"]
                    else []
                ),
            },
            "Ready for Pickup": {
                "display": "Your order is ready! Come pick it up",
                "icon": "📦",
                "nextStatuses": (
                    ["Delivered"]
                    if StatusController.STATUS_FLOW["Ready for Pickup"]
                    else []
                ),
            },
            "Delivered": {
                "display": "Your order has been delivered successfully",
                "icon": "✓",
                "nextStatuses": [],
            },
            "Cancelled": {
                "display": "This order has been cancelled",
                "icon": "✗",
                "nextStatuses": [],
            },
        }

    @staticmethod
    def update_order_status(order_id, new_status):
        """Updates the status of an order if the transition is valid."""
        try:
            order = Order.query.filter_by(id=order_id).first()
            if not order:
                return False, "Order not found.", None

            current_status = order.status

            if current_status == "Cancelled":
                return False, "Cannot update a cancelled order.", None

            if current_status == "Delivered":
                return False, "Cannot update a delivered order.", None

            valid_next_status = StatusController.STATUS_FLOW.get(current_status)
            if new_status != valid_next_status:
                return (
                    False,
                    f"Invalid status transition from {current_status} to {new_status}.",
                    None,
                )

            order.status = new_status
            db.session.commit()
            return True, f"Order status updated to {new_status}.", order
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating order status: {str(e)}", None

    @staticmethod
    def cancel_order(order_id, user_id):
        """Cancels an order if it hasn't been delivered yet."""
        try:
            order = Order.query.filter_by(id=order_id, user_id=user_id).first()
            if not order:
                return False, "Order not found.", None

            if order.status in ["Delivered", "Cancelled"]:
                return (
                    False,
                    f"Cannot cancel an order that is {order.status.lower()}.",
                    None,
                )

            order.status = "Cancelled"
            db.session.commit()
            return True, "Order cancelled successfully.", order
        except Exception as e:
            db.session.rollback()
            return False, f"Error cancelling order: {str(e)}", None

    @staticmethod
    def get_order_by_id(order_id, user_id):
        """Retrieves an order by ID, checking ownership."""
        try:
            order = Order.query.filter_by(id=order_id, user_id=user_id).first()
            if not order:
                return False, "Order not found or access denied.", None
            return True, "Order retrieved successfully.", order
        except Exception as e:
            return False, f"Error retrieving order: {str(e)}", None

    @staticmethod
    def get_all_orders_for_staff():
        """Retrieves all orders for staff/admin management."""
        try:
            orders = Order.query.order_by(Order.ordered_at.desc()).all()
            return True, "All orders retrieved successfully.", orders
        except Exception as e:
            return False, f"Error retrieving orders: {str(e)}", None

    @staticmethod
    def is_staff(user_id):
        """Checks if the user is staff or admin."""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return False
            return user.role in ["staff", "admin"]
        except Exception:
            return False
