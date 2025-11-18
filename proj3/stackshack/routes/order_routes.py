from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from controllers.order_controller import OrderController
from controllers.menu_controller import MenuController
from models.menu_item import MenuItem

order_bp = Blueprint("order", __name__)


@order_bp.route("/history", methods=["GET"])
@login_required
def order_history():
    user_id = current_user.id
    success, msg, orders = OrderController.get_user_orders(user_id)
    if not success:
        flash(msg, "error")
        orders = []
    return render_template("orders/history.html", orders=orders)


@order_bp.route("/ingredients/<category>")
def get_ingredients(category):
    items = MenuItem.query.filter(MenuItem.category.ilike(f"%{category}%")).all()
    data = [
        {
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "description": item.description,
            "is_healthy": item.is_healthy_choice,
            "image_url": item.image_url,
        }
        for item in items
    ]
    return jsonify(data)


@order_bp.route("/new", methods=["GET"])
@login_required
def create_order_form():
    success, msg, items = MenuController.get_available_items()
    if not success:
        flash("Error loading menu items: " + msg, "error")
        items = []
    return render_template("orders/create.html", items=items)


@order_bp.route("/place", methods=["POST"])
@login_required
def place_order():
    user_id = current_user.id
    item_data = []
    for key, value in request.form.items():
        if key.startswith("quantity_"):
            try:
                item_id = key.split("_")[1]
                quantity = int(value)
                if quantity > 0:
                    price = request.form.get(f"price_{item_id}")
                    name = request.form.get(f"name_{item_id}")
                    if price and name:
                        item_data.append((item_id, price, quantity, name))
            except ValueError:
                continue
    success, msg, _ = OrderController.create_new_order(user_id, item_data)
    flash(msg, "success" if success else "error")
    if success:
        return redirect(url_for("order.order_history"))
    else:
        return redirect(url_for("order.create_order_form"))
