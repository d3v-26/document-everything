"""Users controller."""
from flask import Blueprint, jsonify

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/")
def list_users():
    return jsonify([])
