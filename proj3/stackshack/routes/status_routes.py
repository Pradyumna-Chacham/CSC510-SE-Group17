from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from controllers.status_controller import StatusController

status_bp = Blueprint("status", __name__)


@status_bp.route("/update", methods=["POST"])
@login_required
def update_status():
    """Update the status of an order (staff only)."""
    try:
        if not StatusController.is_staff(current_user.id):
            return (
                jsonify(
                    {"success": False, "message": "Only staff can update order status."}
                ),
                403,
            )

        data = request.get_json()
        order_id = data.get("order_id")
        new_status = data.get("status")

        if not order_id or not new_status:
            return (
                jsonify({"success": False, "message": "Missing order_id or status"}),
                400,
            )

        order_id = int(order_id)

        from models.order import Order

        order = Order.query.filter_by(id=order_id).first()
        if not order:
            return jsonify({"success": False, "message": "Order not found."}), 404

        success, msg, updated_order = StatusController.update_order_status(
            order_id, new_status
        )
        if not success:
            return jsonify({"success": False, "message": msg}), 400

        return (
            jsonify(
                {
                    "success": True,
                    "message": msg,
                    "order": {"id": updated_order.id, "status": updated_order.status},
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@status_bp.route("/cancel/<int:order_id>", methods=["POST"])
@login_required
def cancel_order(order_id):
    """Cancel an order."""
    try:
        success, msg, order = StatusController.cancel_order(order_id, current_user.id)
        if not success:
            return jsonify({"success": False, "message": msg}), 400

        return (
            jsonify(
                {
                    "success": True,
                    "message": msg,
                    "order": {"id": order.id, "status": order.status},
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@status_bp.route("/flow", methods=["GET"])
def get_status_flow():
    """Get the status flow configuration for frontend."""
    try:
        flow = StatusController.get_status_flow()
        return jsonify({"success": True, "flow": flow}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@status_bp.route("/manage", methods=["GET"])
@login_required
def manage_orders():
    """Staff/Admin view to manage all orders with status updates."""
    if not StatusController.is_staff(current_user.id):
        flash("Access denied. Only staff can manage orders.", "error")
        return redirect(url_for("order.order_history"))

    success, msg, orders = StatusController.get_all_orders_for_staff()
    if not success:
        flash(msg, "error")
        orders = []

    status_flow = {
        "Pending": "Preparing",
        "Preparing": "Ready for Pickup",
        "Ready for Pickup": "Delivered",
        "Delivered": None,
        "Cancelled": None,
    }

    return render_template(
        "orders/history.html",
        orders=orders,
        manage_mode=True,
        status_flow=status_flow,
        page_title="Manage Orders",
        header_title="Manage All Orders",
    )
