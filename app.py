from flask import Flask, render_template, request, session, redirect,jsonify, url_for, flash
import sqlite3
from functools import wraps
from dbUtils import get_pending_orders, accept_order, pick_up_order, complete_order, get_user_by_id, get_prepare_dish, add_user, get_all_restaurants, get_dish_list_by_name, get_restaurant_details_by_name, get_dish_details_by_dish_name, add_to_cart, get_cart_detail, delete_from_cart, send_dish, confirm_receipt, get_order_data, add_dish, update_dish, delete_dish_by_id, transfer_order, get_dish_by_id
from datetime import datetime, timedelta

# creates a Flask application, specify a static folder on /
app = Flask(__name__, static_folder='static', static_url_path='/')
# set a secret key to hash cookies
app.config['SECRET_KEY'] = '123TyU%^&'


# define a function wrapper to check login session
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loginID = session.get('loginID')
        if not loginID:
            return redirect('/loginPage.html')
        return f(*args, **kwargs)
    return wrapper

# another way to check login session
def isLogin():
    return session.get('loginID')

@app.route("/test/<string:name>/<int:id>")
# 取得網址作為參數
def useParam(name, id):
    # check login inside the function
    if not isLogin():
        return redirect('/loginPage.html')
    return f"got name={name}, id={id} "

# 登入頁面渲染
@app.route('/loginPage')
def login_page():
    return render_template('loginPage.html')

@app.route('/login', methods=['POST'])
def login():
    form = request.form
    id = form['id']
    pw = form['pw']
    role = form['role']  # 獲取角色類型

    user = get_user_by_id(id, role)  # 傳入角色參數

    if user:
        if user['pw'] == pw:
            session['loginID'] = id
            session['id'] = id
            session['name'] = user['name']
            print(f"用戶 {session['name']} 登錄成功")
            
            if role == "customer":
                session['Gid'] = user['Gid']
                return redirect("/guestfrontPage")
            elif role == "restaurant":
                session['Rid'] = user['Rid']
                return redirect("/confirmreceipt")
            elif role == "delivery":
                return redirect("/view_orders")
        else:
            print("密碼不正確")
            return redirect("/loginPage?error=wrong_password")
    else:
        print("用戶不存在")
        return redirect("/loginPage?error=user_not_found")

#登出    
@app.route('/logout')
@login_required  # 確保用戶已登入
def logout():
    session.pop('id', None)  # 清除 id
    session.pop('loginID', None)  # 可選：如果您也使用 loginID，清除它
    return redirect('/loginPage')  # 重定向到登入頁面

# 註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        id = form['id']
        pw = form['pw']
        name = form['name']
        phone = form['phone']
        role = form['role'] 
        address = form['address']

        # 新增使用者
        add_user(id, pw, role, name, phone, address)

        # 註冊成功後重定向到登入頁面
        return redirect('/loginPage')

    # 使用 GET 方法時，返回註冊頁面
    return render_template('register.html')
    
#客人看餐廳 渲染
@app.route("/guestfrontPage")
def restaurant_list():
    name = session.get('name', '訪客')
    data = get_all_restaurants()
    return render_template('guestfrontPage.html',data=data, name = name)

@app.route("/restaurantdishlist/<string:name>")
def dish_records(name):
    # 根據餐廳名稱查詢對應的餐廳和菜單記錄
    dish_records = get_dish_list_by_name(name)
    restaurant = get_restaurant_details_by_name(name)  # 獲取餐廳詳細信息
    cart_data = get_cart_detail()  # 獲取當前購物車資料

    # 創建一個字典，將每道菜的名稱映射到其在購物車中的數量
    cart_dict = {}
    for item in cart_data:
        cart_dict[item['dish_name']] = item['quantity']

    if restaurant:
        restaurant_name = restaurant['name']
    else:
        return "餐廳不存在", 404  # 如果餐廳不存在返回 404
    
    return render_template('restaurantdishlist.html', data=dish_records, restaurant=restaurant_name, cart_dict=cart_dict)


# 新增或更新購物車
@app.route('/place_dishes', methods=['POST'])
def place_dishes():
    dish_name = request.form.get('dish_name')
    quantity = request.form.get('quantity')  # 使用 get() 防止 KeyError

    if not dish_name or not quantity:
        return "未提供餐點名稱或數量", 400  # 這裡會返回具體的錯誤訊息

    try:
        quantity = int(quantity)
        if quantity < 0:
            return "數量必須大於或等於 0", 400
    except ValueError:
        return "數量必須為整數", 400

    # 從 session 中獲取用戶的 Gid
    gid = session.get('Gid')
    if not gid:
        return redirect("/loginPage?error=not_logged_in")  # 用戶未登入，跳轉到登入頁面

    # 獲取菜品詳細資料
    dish = get_dish_details_by_dish_name(dish_name)
    
    if quantity == 0:
        delete_from_cart(dish_name, gid)  # 修改 delete_from_cart 函數，傳入 Gid
        return redirect(f"/restaurantdishlist/{dish['restaurant_name']}")
    else:
        if not dish:
            return f"未找到餐點資料，餐點名稱: {dish_name}", 404

        # 使用 Gid 呼叫 add_to_cart
        add_to_cart(dish['dish_name'], dish['price'], dish['restaurant_name'], quantity, gid)
        return redirect(f"/restaurantdishlist/{dish['restaurant_name']}")


#客人看購物車 渲染
@app.route("/cart")
def cart_list():
    data = get_cart_detail()
    total_price = sum(item['quantity'] * item['price'] for item in data)
    return render_template('cart.html',data=data, total_price=total_price)

#傳給餐廳訂單
@app.route("/send_to_restaurant", methods=["POST"])
def send_to_restaurant():
    try:
        # 獲取 Gid，通常從 session 中獲取
        gid = session.get('Gid')
        if not gid:
            return redirect("/loginPage?error=not_logged_in")  # 用戶未登入，跳轉到登入頁面

        # 呼叫 send_dish 函數，將購物車資料送到 prepare_dish 表
        send_dish(gid)

        # 重定向到首頁或其他頁面
        return redirect("/guestfrontPage")  # 成功後重定向回首頁
    except Exception as e:
        print(f"Error sending order to restaurant: {e}")
        return "發生錯誤，請稍後再試！", 500

# deliver
# deliver
@app.route("/deliveryfrontPage")
@login_required
def delivery_front_page():
    return render_template("view_orders.html")  # 顯示可接訂單頁面，首頁

# 查看待接訂單頁面
@app.route("/delivery/orders_page")
@login_required
def view_orders_page():
    return render_template("view_orders.html")  # HTML 中需建立動態表格顯示可接訂單

# 查看待接訂單 API
@app.route("/delivery/orders")
@login_required
def view_orders():
    orders = get_pending_orders(status='pending')
    return jsonify(orders)

# 接單 API
@app.route("/delivery/accept", methods=['POST'])
@login_required
def accept():
    order_id = request.json.get('Oid')
    did = session.get('id')  # 外送員 ID
    if accept_order(order_id, did):
        return jsonify({"message": "Order accepted."}), 200
    return jsonify({"message": "Failed to accept order."}), 400

# 查看待送訂單頁面
@app.route("/delivery/pending_orders_page")
@login_required
def pending_orders_page():
    return render_template("delivery_list.html")  # HTML 用來顯示待送清單並提供操作按鈕

# 查看待送訂單 API
@app.route("/delivery/pending")
@login_required
def pending_orders():
    orders = get_pending_orders(status='accepted') + get_pending_orders(status='picked_up')
    return jsonify(orders)

# 取貨 API
@app.route("/delivery/pickup", methods=['POST'])
@login_required
def pick_up():
    order_id = request.json.get('Oid')
    if pick_up_order(order_id):
        return jsonify({"message": "Order picked up."}), 200
    return jsonify({"message": "Failed to pick up order."}), 400

# 送達 API
@app.route("/delivery/complete", methods=['POST'])
@login_required
def complete():
    order_id = request.form.get('Oid')
    attachment = request.files.get('attachment')  # 處理附件
    if complete_order(order_id):
        return jsonify({"message": "Order completed."}), 200
    return jsonify({"message": "Failed to complete order."}), 400
'''
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
'''
#檢查run.bat有沒有連到的東西
if __name__ == "__main__":
    app.run(debug=True)
    

#好冷嘎嘎ㄍ嘎嘎嘎嘎阿嘎ㄚㄚㄚㄚㄚㄚㄚ

#餐廳
@app.route("/confirmreceipt")
def order_list_page():
    Rid = session.get('Rid')
    #data=get_prepare_dish(Rid)
    # 取得所有的訂單資料，這裡可以進行 confirm 的過濾
    data_confirm_0 = get_order_data(0, Rid)  # 確認接單的資料
    data_confirm_1 = get_order_data(1, Rid)  # 已接單的資料

    # 處理 confirm_time，加上 30 分鐘
    for rec in data_confirm_1:
        confirm_time = rec.get('confirm_time')
        if confirm_time:
            rec['finish_time'] = (confirm_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

    return render_template('Confirmreceipt.html', data_confirm_0=data_confirm_0, data_confirm_1=data_confirm_1)

@app.route('/regrest')        
def regrest():
    return render_template('regrest.html')
'''
@app.route("/confirmreceipt_action", methods=['POST'])
@login_required
def confirm_receipt_action():
    order_id = request.json.get('id')
    confirm_receipt(order_id)  # 處理確認接單操作
    return jsonify({"status": "success"}), 200  # 回傳成功訊息
 '''   
@app.route("/confirmOrder", methods=["POST"])
def confirm_order():
    try:
        # 獲取前端傳來的訂單 ID
        data = request.json
        order_id = data.get("order_id")

        # 驗證輸入
        if not order_id:
            return jsonify({"status": "error", "message": "缺少訂單 ID"}), 400

        # 調用 transfer_order 函數
        success, message = transfer_order(order_id)

        if success:
            return jsonify({"status": "success", "message": message}), 200
        else:
            return jsonify({"status": "error", "message": message}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"伺服器錯誤: {e}"}), 500

@app.route('/add_dish', methods=['POST'])
def add_new_dish():
    if 'restaurant_name' in session:
        dish_name = request.form['dish_name']
        price = float(request.form['price'])
        content = request.form['content']
        try:
            add_dish(session['restaurant_name'], dish_name, price, content)
            flash("新增成功！")
        except Exception as e:
            flash(f"新增失敗: {e}")
    else:
        flash("尚未登入，請先登入")
        return redirect(url_for('login_page'))
    return redirect(url_for('adddish'))

@app.route('/adddish')
def adddish():
        return render_template('adddish.html')   
        
@app.route('/edit_dish/<int:dish_id>', methods=['GET', 'POST'])
def edit_dish(dish_id):
    dish = get_dish_by_id(dish_id)
    if dish is None or dish['restaurant_name'] != session.get('restaurant_name'):
        flash("找不到該菜品，或者該菜品無權限編輯")
        return redirect(url_for('adddish'))
    
    if request.method == 'POST':
        dish_name = request.form['dish_name']
        price = float(request.form['price'])
        content = request.form['content']
        update_dish(dish_id, dish_name, content, price)
        flash("菜品已更新")
        return redirect(url_for('adddish'))
    
    return render_template('edit_dish.html', dish=dish)

@app.route('/delete_dish/<int:dish_id>', methods=['POST'])
def delete_dish(dish_id):
    dish = get_dish_by_id(dish_id)
    if dish is None or dish['restaurant_name'] != session.get('restaurant_name'):
        flash("找不到該菜品，或者無權刪除")
        return redirect(url_for('adddish'))
    
    delete_dish_by_id(dish_id)
    flash("菜品已刪除")
    return redirect(url_for('adddish'))

@app.before_request
def before_request():
    print(f"Session at start: {session}")  # 確保會話資訊是正確的

@app.route("/confirm0", methods=["POST"])
def confirm_dish():
    order_id = request.form.get("order_id")
    confirm_receipt(order_id)
    return redirect("/confirmreceipt")  # 成功後重定向回首頁
    
@app.route("/confirm1", methods=["POST"])
def confirm_dish1():
    order_id = request.form.get("order_id")
    transfer_order(order_id)
    return redirect("/confirmreceipt")