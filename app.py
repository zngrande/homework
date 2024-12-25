from flask import Flask, render_template, request, session, redirect,jsonify, url_for, flash
import sqlite3
from functools import wraps
from dbUtils import get_pending_orders, rate, monthly_orders_d, monthly_orders_r, monthly_orders_g, complete_guest, update_restaurant_points, guest_get_arrive, get_pending_orders_byDid, update_res_information, accept_order, pick_up_order, get_dish_by_id, get_res_by_Rid, complete_order, get_user_by_id, get_prepare_dish, add_user, get_all_restaurants, get_dish_list_by_name, get_restaurant_details_by_name, get_dish_details_by_dish_name, add_to_cart, get_cart_detail, delete_from_cart, send_dish, confirm_receipt, get_order_data, add_dish, update_dish, delete_dish_by_id, transfer_order, get_dish_by_Rid
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
                session['guest_name'] = user['name']
                return redirect("/guestfrontPage")
            elif role == "restaurant":
                session['Rid'] = user['Rid']
                session['restaurant_name'] = user['name']
                return redirect("/confirmreceipt")
            elif role == "delivery":
                session['Did'] = user['Did']
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
@login_required
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
@login_required
def dishes():
    dish_name = request.form.get('dish_name')
    quantity = request.form.get('quantity') 

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
@login_required
def cart_list():
    data = get_cart_detail()
    total_price = sum(item['quantity'] * item['price'] for item in data)
    return render_template('cart.html',data=data, total_price=total_price)

#傳給餐廳訂單
@app.route("/send_to_restaurant", methods=["POST"])
@login_required
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

#客人看訂單
@app.route("/orderlist")
@login_required
def guest_orderlist():
    Gid = session.get('Gid')
    data = guest_get_arrive(status="外送員已領餐", Gid=Gid)
    for rec in data:
        pickup_time = rec.get('pickup_time')
        if pickup_time:
            rec['arrive_time'] = (pickup_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
    
    data_com = guest_get_arrive(status="已送達", Gid=Gid)
    data_history = guest_get_arrive(status="已完成", Gid=Gid)

    return render_template('guest_orderlist.html',data=data, data_history=data_history, data_com=data_com )

@app.route("/guest/accept", methods=['POST'])
@login_required
def accept_guest():
    order_id = request.form.get('order_id')  # 確保從表單取得 order_id
    if not order_id:
        return "Order ID is missing", 400  # 若缺少 order_id，返回錯誤訊息
    try:
        complete_guest(order_id)  # 呼叫完成訂單的函數
        return redirect('/orderlist')  # 重定向到訂單頁面
    except Exception as e:
        print(f"Error accepting order: {e}")
        return "Failed to accept order", 500


#評分
@app.route("/rate", methods=['POST'])
@login_required
def rate_delivery():
    order_id = request.form.get('order_id')
    point = request.form.get('rating')

    if not order_id or not point:
        return "缺少必要參數", 400

    
    rate(point, order_id)
    update_restaurant_points()  # 更新餐廳的平均評分
    return redirect('/orderlist')
    

# deliver

# 查看可接訂單 API
# 此路由用於讓外送員查看所有狀態為 "待接單" 的訂單
@app.route("/view_orders")
@login_required
def view_orders():
    # 從數據庫獲取待接單的訂單資料
    data = get_pending_orders(status="待接單")
    # 將訂單資料渲染到 view_orders.html 頁面
    return render_template("view_orders.html", data=data)

# 接單 API
# 此路由用於外送員接單操作
@app.route("/delivery/accept", methods=['GET', 'POST'])
@login_required
def accept():
    # 獲取外送員的 ID
    Did = session.get('Did')
    if request.method == 'POST':
        form = request.form
        # 從表單中獲取訂單 ID
        order_id = form['order_id']
    # 將訂單狀態更新為 "已找到外送員"
    accept_order(Did, order_id) 
    # 接單完成後重定向到待送訂單頁面
    return redirect('/delivery_list')

# 待送訂單
# 此路由用於顯示外送員已接單但尚未完成的訂單
@app.route("/delivery_list")
@login_required
def delivery_list_page():
    # 獲取外送員的 ID
    Did = session.get('Did')  
    if Did is None: 
        # 如果未登錄，重定向到登錄頁面
        return redirect(url_for('login')) 
    
    # 獲取狀態為 "已找到外送員" 的訂單資料
    data_find_delivery = get_pending_orders_byDid(status='已找到外送員', Did=Did)  
    # 獲取狀態為 "外送員已領餐" 的訂單資料
    data_ready_to_send = get_pending_orders_byDid(status='外送員已領餐', Did=Did)

    # 計算預計送達時間（領餐時間加 30 分鐘）
    for rec in data_ready_to_send:
        pickup_time = rec.get('pickup_time')
        if pickup_time:
            rec['arrive_time'] = (pickup_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

    # 渲染 delivery_list.html，顯示待送訂單
    return render_template("delivery_list.html", data_find_delivery=data_find_delivery, data_ready_to_send=data_ready_to_send)

# 取貨 API
# 此路由用於外送員確認取餐操作
@app.route("/delivery/pickup", methods=['GET', 'POST'])
@login_required
def pick_up():
    if request.method == 'POST':
        form = request.form
        # 從表單中獲取訂單 ID
        order_id = form['order_id']
    # 將訂單狀態更新為 "外送員已領餐"
    pick_up_order(order_id)
    # 完成取餐操作後重定向到待送訂單頁面
    return redirect('/delivery_list')

# 送達 API
# 此路由用於外送員完成送達訂單的操作
@app.route("/delivery/complete", methods=['GET', 'POST'])
@login_required
def complete():
    if request.method == 'POST':
        form = request.form
        # 從表單中獲取訂單 ID
        order_id = form['order_id']
    # 將訂單狀態更新為 "已完成"
    complete_order(order_id)
    # 完成送達操作後重定向到待送訂單頁面
    return redirect('/delivery_list')


#檢查run.bat有沒有連到的東西
if __name__ == "__main__":
    app.run(debug=True)
    
#餐廳
@app.route("/confirmreceipt")
@login_required
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

@app.route("/confirm0", methods=["POST"])
@login_required
def confirm_dish():
    order_id = request.form.get("order_id")
    confirm_receipt(order_id)
    return redirect("/confirmreceipt")  # 成功後重定向回首頁
    
@app.route("/confirm1", methods=["POST"])
@login_required
def confirm_dish1():
    order_id = request.form.get("order_id")
    transfer_order(order_id)
    return redirect("/confirmreceipt")

@app.route("/dish_list")
@login_required
def edit_dish():    
    Rid = session.get('Rid')
    data=get_dish_by_Rid(Rid)
    return render_template('dish_list.html',data=data)

# 修改餐點
@app.route("/editdish/<int:dish_id>", methods=['GET', 'POST'])
@login_required
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


@app.route('/delete_dish/<int:dish_id>', methods=['get'])
@login_required
def delete_dish(dish_id):
    delete_dish_by_id(dish_id)
    return redirect("/dish_list")

@app.route('/add_dish', methods=['POST'])
@login_required
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
@login_required
def add():
    return render_template('/adddish.html')
   
#各自
#d
@app.route('/dm')
@login_required
def dmon():
    Did=session.get('Did')
    data = monthly_orders_d(Did)
    return render_template('/delivery_money.html',data=data)

#r
@app.route('/rm')
@login_required
def rmon():
    Rid=session.get('Rid')
    data = monthly_orders_r(Rid)
    return render_template('/res_money.html',data=data)  

#g
@app.route('/gm')
@login_required
def gmon():
    Gid=session.get('Gid')
    data = monthly_orders_g(Gid)
    return render_template('/g_money.html',data=data) 
        
      
    
    
    
    