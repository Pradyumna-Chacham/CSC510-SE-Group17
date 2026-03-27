from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from controllers.menu_controller import MenuController

menu_bp = Blueprint("menu", __name__)


# View all menu items (Admin/Staff)
@menu_bp.route("/items", methods=["GET"])
@login_required
def view_items():
    """Display all menu items for management"""
    if current_user.role not in ["admin", "staff"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("auth.dashboard"))

    success, msg, items = MenuController.get_all_items()

    if not success:
        flash(msg, "error")
        items = []

    return render_template("menu/items.html", items=items)


# Create new item - Show form
@menu_bp.route("/items/new", methods=["GET"])
@login_required
def create_item_form():
    """Display form to create a new menu item"""
    if current_user.role not in ["admin", "staff"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("auth.dashboard"))

    return render_template("menu/create_item.html")


# Create new item - Handle form submission
@menu_bp.route("/items/create", methods=["POST"])
@login_required
def create_item():
    """Process form to create a new menu item"""
    if current_user.role not in ["admin", "staff"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("auth.dashboard"))

    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    price = request.form.get("price")
    calories = request.form.get("calories")
    protein = request.form.get("protein")
    image_url = request.form.get("image_url")

    success, msg, item = MenuController.create_item(
        name=name,
        category=category,
        description=description,
        price=price,
        calories=calories if calories else None,
        protein=protein if protein else None,
        image_url=image_url if image_url else None,
    )

    flash(msg, "success" if success else "error")

    if success:
        return redirect(url_for("menu.view_items"))

    return redirect(url_for("menu.create_item_form"))


# Edit item - Show form
@menu_bp.route("/items/<int:item_id>/edit", methods=["GET"])
@login_required
def edit_item_form(item_id):
    """Display form to edit a menu item"""
    if current_user.role not in ["admin", "staff"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("auth.dashboard"))

    success, msg, item = MenuController.get_item_by_id(item_id)

    if not success:
        flash(msg, "error")
        return redirect(url_for("menu.view_items"))

    return render_template("menu/edit_item.html", item=item)


# Edit item - Handle form submission
@menu_bp.route("/items/<int:item_id>/update", methods=["POST"])
@login_required
def update_item(item_id):
    """Process form to update a menu item"""
    if current_user.role not in ["admin", "staff"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("auth.dashboard"))

    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    price = request.form.get("price")
    calories = request.form.get("calories")
    protein = request.form.get("protein")
    image_url = request.form.get("image_url")

    success, msg, item = MenuController.update_item(
        item_id=item_id,
        name=name,
        category=category,
        description=description,
        price=price,
        calories=calories if calories else None,
        protein=protein if protein else None,
        image_url=image_url if image_url else None,
    )

    flash(msg, "success" if success else "error")
    return redirect(url_for("menu.view_items"))


# Delete item
@menu_bp.route("/items/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    """Delete a menu item"""
    if current_user.role != "admin":
        flash("Unauthorized: Only admins can delete items", "error")
        return redirect(url_for("menu.view_items"))

    success, msg, _ = MenuController.delete_item(item_id)
    flash(msg, "success" if success else "error")

    return redirect(url_for("menu.view_items"))


# Toggle availability
@menu_bp.route("/items/<int:item_id>/toggle-availability", methods=["POST"])
@login_required
def toggle_availability(item_id):
    """Toggle item availability status"""
    if current_user.role not in ["admin", "staff"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("menu.view_items"))

    success, msg, _ = MenuController.toggle_availability(item_id)
    flash(msg, "success" if success else "error")

    return redirect(url_for("menu.view_items"))


# Toggle healthy choice
@menu_bp.route("/items/<int:item_id>/toggle-healthy", methods=["POST"])
@login_required
def toggle_healthy(item_id):
    """Toggle healthy choice status"""
    if current_user.role not in ["admin", "staff"]:
        flash("Unauthorized access", "error")
        return redirect(url_for("menu.view_items"))

    success, msg, _ = MenuController.toggle_healthy_choice(item_id)
    flash(msg, "success" if success else "error")

    return redirect(url_for("menu.view_items"))


# Customer view - See available items
@menu_bp.route("/browse", methods=["GET"])
def browse_menu():
    """Public view of available menu items for customers"""
    success, msg, items = MenuController.get_available_items()

    if not success:
        flash(msg, "error")
        items = []

    return render_template("menu/browse.html", items=items)


# View healthy choices
@menu_bp.route("/healthy", methods=["GET"])
def healthy_choices():
    """Display healthy menu options"""
    success, msg, items = MenuController.get_healthy_choices()

    if not success:
        flash(msg, "error")
        items = []

    return render_template("menu/healthy.html", items=items)


# Public view - Browse all available ingredients
@menu_bp.route("/browse-ingredients", methods=["GET"])
def browse_ingredients():
    """Public view of all available menu items/ingredients"""
    success, msg, items = MenuController.get_available_items()

    if not success:
        flash(msg, "error")
        items = []

    # Group items by category for better display
    categorized_items = {}
    for item in items:
        if item.category not in categorized_items:
            categorized_items[item.category] = []
        categorized_items[item.category].append(item)

    return render_template(
        "menu/browse_ingredients.html", categorized_items=categorized_items
    )
