from flask import Flask, render_template, request, session, redirect,jsonify, url_for, flash
import sqlite3
from functools import wraps
from dbUtils import get_pending_orders, update_res_information, accept_order, pick_up_order, get_dish_by_id, get_res_by_Rid, complete_order, get_user_by_id, get_prepare_dish, add_user, get_all_restaurants, get_dish_list_by_name, get_restaurant_details_by_name, get_dish_details_by_dish_name, add_to_cart, get_cart_detail, delete_from_cart, send_dish, confirm_receipt, get_order_data, add_dish, update_dish, delete_dish_by_id, transfer_order, get_dish_by_Rid
from datetime import datetime, timedelta

# creates a Flask application, specify a static folder on /
app = Flask(__name__, static_folder='static', static_url_path='/')
# set a secret key to hash cookies
app.config['SECRET_KEY'] = '123TyU%^&'
#123

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
                session['restaurant_name'] = user['name']
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
def dishes():
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
# 查看可接訂單頁面
<<<<<<< HEAD
@app.route("/view_orders")
=======
'''@app.route("/view_orders")
>>>>>>> 87b1ba5d345f7f89a49018b0e7f7035592175a03
def view_orders_page():
    return render_template("view_orders.html")

# 查看待送清單頁面
@app.route("/delivery_list")
def delivery_list_page():
    return render_template("delivery_list.html")

# 查看可接訂單 API
@app.route("/delivery/orders", methods=['GET'])
def get_view_orders():
<<<<<<< HEAD
    orders = get_pending_orders(status='待接單')  # 餐廳完成的訂單
=======
    orders = get_pending_orders(status='completed')  # 餐廳完成的訂單
>>>>>>> 87b1ba5d345f7f89a49018b0e7f7035592175a03
    return jsonify(orders)

# 接單 API
@app.route("/delivery/accept", methods=['POST'])
def accept():
    order_id = request.json.get('Oid')
    did = session.get('id')  # 外送員 ID
    if accept_order(order_id, did):
        return jsonify({"message": "Order accepted."}), 200
    return jsonify({"message": "Failed to accept order."}), 400

# 查看待送訂單 API
@app.route("/delivery/pending", methods=['GET'])
def get_pending_orders_list():
<<<<<<< HEAD
    orders = get_pending_orders(status='待接單')
=======
    orders = get_pending_orders(status='accepted') + get_pending_orders(status='picked_up')
    return jsonify(orders)

# 取貨 API
@app.route("/delivery/pickup", methods=['POST'])
def pick_up():
    order_id = request.json.get('Oid')
    if pick_up_order(order_id):
        return jsonify({"message": "Order picked up."}), 200
    return jsonify({"message": "Failed to pick up order."}), 400

# 送達 API
# 查看可接訂單頁面
@app.route("/view_orders")
def view_orders_page():
    return render_template("view_orders.html")

# 查看待送清單頁面
@app.route("/delivery_list")
def delivery_list_page():
    return render_template("delivery_list.html")

# 查看可接訂單 API
@app.route("/delivery/orders", methods=['GET'])
def get_view_orders():
    orders = get_pending_orders(status='completed')  # 餐廳完成的訂單
    return jsonify(orders)

# 接單 API
@app.route("/delivery/accept", methods=['POST'])
def accept():
    order_id = request.json.get('Oid')
    did = session.get('id')  # 外送員 ID
    if accept_order(order_id, did):
        return jsonify({"message": "Order accepted."}), 200
    return jsonify({"message": "Failed to accept order."}), 400

# 查看待送訂單 API
@app.route("/delivery/pending", methods=['GET'])
def get_pending_orders_list():
    orders = get_pending_orders(status='accepted') + get_pending_orders(status='picked_up')
>>>>>>> 87b1ba5d345f7f89a49018b0e7f7035592175a03
    return jsonify(orders)

# 取貨 API
@app.route("/delivery/pickup", methods=['POST'])
def pick_up():
    order_id = request.json.get('Oid')
    if pick_up_order(order_id):
        return jsonify({"message": "Order picked up."}), 200
    return jsonify({"message": "Failed to pick up order."}), 400

# 送達 API
@app.route("/delivery/complete", methods=['POST'])
def complete():
    order_id = request.form.get('Oid')
    attachment = request.files.get('attachment')
    if complete_order(order_id, attachment):
        return jsonify({"message": "Order completed."}), 200
<<<<<<< HEAD
    return jsonify({"message": "Failed to complete order."}), 400
=======
    return jsonify({"message": "Failed to complete order."}), 400'''

>>>>>>> 87b1ba5d345f7f89a49018b0e7f7035592175a03
#檢查run.bat有沒有連到的東西
if __name__ == "__main__":
    app.run(debug=True)
    

#餐廳
@app.route("/confirmreceipt")
def order_list_page():
    Rid = session.get('Rid')
    # 取得所有的訂單資料，這裡可以進行 confirm 的過濾
    data_confirm_0 = get_order_data(0, Rid)  # 確認接單的資料
    data_confirm_1 = get_order_data(1, Rid)  # 已接單的資料

    # 處理 confirm_time，加上 30 分鐘
    for rec in data_confirm_1:
        confirm_time = rec.get('confirm_time')
        if confirm_time:
            rec['finish_time'] = (confirm_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

    return render_template('Confirmreceipt.html', data_confirm_0=data_confirm_0, data_confirm_1=data_confirm_1)

'''
@app.route("/confirmreceipt_action", methods=['POST'])
@login_required
def confirm_receipt_action():
    order_id = request.json.get('id')
    confirm_receipt(order_id)  # 處理確認接單操作
    return jsonify({"status": "success"}), 200  # 回傳成功訊息
 ''' 

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
''' 


'''
@app.route('/delete_dish/<int:dish_id>', methods=['POST'])
def delete_dish(dish_id):
    dish = get_dish_by_restaurant_name(dish_id)
    if dish is None or dish['restaurant_name'] != session.get('restaurant_name'):
        flash("找不到該菜品，或者無權刪除")
        return redirect(url_for('adddish'))
    
    delete_dish_by_id(dish_id)
    flash("菜品已刪除")
    return redirect(url_for('adddish'))
'''
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

@app.route("/dish_list")
def edit_dish():    
    Rid = session.get('Rid')
    data=get_dish_by_Rid(Rid)
    return render_template('dish_list.html',data=data)

#修改餐廳資料
@app.route("/regrest", methods=['GET', 'POST'])    
def regrest():
    Rid = session.get('Rid')
    data=get_res_by_Rid(Rid)
    
    if request.method == 'POST':
        form = request.form
        name = form['name']
        address = form['address']
        phone = form['phone']

        update_res_information(name, address, phone, Rid)
        return redirect("/confirmreceipt")
    return render_template('regrest.html',data=data)

# 修改餐點
@app.route("/editdish", methods=['GET', 'POST'])
def edit_product(dish_id):  
    if request.method == 'POST':
        # 取得表單數據並更新產品
        form = request.form
        dish_name = form['dish_name']  
        content = form['content']
        price = form['price']
        
        # 更新餐點
        update_dish(dish_id, dish_name, price, content)
        return redirect("/dish_list")
    
    # GET 請求時，取得餐點詳細資料
    data = get_dish_by_id(dish_id)  # 使用 dish_id 查詢
    return render_template('editdish.html', data=data)

@app.route('/add_dish', methods=['POST'])
def add_new_dish():
    if request.method == 'POST':
        Rid = session.get('Rid')
        restaurant_name = session.get('restaurant_name')
        if not Rid or not restaurant_name:
            flash("餐廳資訊不完整，請重新登入")
            return redirect(url_for('login_page'))
        form = request.form
        dish_name = form['dish_name']  
        content = form['content']
        price = form['price']
        add_dish( Rid, restaurant_name, dish_name, price, content)
        return redirect("/dish_list")
    else:
        flash("尚未登入，請先登入")
        return redirect(url_for('login_page'))
    
@app.route('/adddish')
def add():
    return render_template('/adddish.html')
   

        
        
      
    
    
    
    