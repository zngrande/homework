from flask import Flask, render_template, request, session, redirect,jsonify
import sqlite3
from functools import wraps
from dbUtils import get_pending_orders, accept_order, pick_up_order, complete_order


# creates a Flask application, specify a static folder on /
app = Flask(__name__, static_folder='static',static_url_path='/')
#set a secret key to hash cookies
app.config['SECRET_KEY'] = '123TyU%^&'


# deliver
@app.route("/delivery/orders")
@login_required
def view_orders():
#1查看待送訂單
    orders = get_pending_orders()
    return jsonify(orders)

@app.route("/delivery/accept", methods=['POST'])
@login_required
def accept():
#2接單
    order_id = request.json.get('Oid')
    did = session.get('Did')
    if accept_order(order_id, did):
        return jsonify({"message": "Order accepted."}), 200
    return jsonify({"message": "Failed to accept order."}), 400

@app.route("/delivery/pickup", methods=['POST'])
@login_required
def pick_up():
#3取貨
    order_id = request.json.get('Oid')
    if pick_up_order(order_id):
        return jsonify({"message": "Order picked up."}), 200
    return jsonify({"message": "Failed to pick up order."}), 400

@app.route("/delivery/complete", methods=['POST'])
@login_required
def complete():
#4送達
    order_id = request.json.get('Oid')
    if complete_order(order_id):
        return jsonify({"message": "Order completed."}), 200
    return jsonify({"message": "Failed to complete order."}), 400

#檢查run.bat有沒有連到的東西
if __name__ == "__main__":
    app.run(debug=True)

#好冷嘎嘎ㄍ嘎嘎嘎嘎阿嘎ㄚㄚㄚㄚㄚㄚㄚ
