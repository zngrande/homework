from flask import Flask, render_template, request, session, redirect, jsonify, url_for, flash
import sqlite3
from functools import wraps
from dbUtils import get_user_by_id, add_user, confirm_receipt, get_order_data, add_dish, update_dish, delete_dish_by_id, transfer_order, get_dish_by_id
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
                return redirect("/confirmreceipt")
            elif role == "delivery":
                return redirect("/deliveryfrontPage")
        else:
            print("密碼不正確")
            return redirect("/loginPage?error=wrong_password")
    else:
        print("用戶不存在")
        return redirect("/loginPage?error=user_not_found")

@app.route("/orderlistPage")
def order_list_page():
    # 取得所有的訂單資料，這裡可以進行 confirm 的過濾
    data_confirm_0 = get_order_data(confirm=0)  # 確認接單的資料
    data_confirm_1 = get_order_data(confirm=1)  # 已接單的資料

    # 處理 confirm_time，加上 30 分鐘
    for rec in data_confirm_1:
        confirm_time = rec.get('confirm_time')
        if confirm_time:
            rec['finish_time'] = (confirm_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

    return render_template('Confrimreceipt.html', data_confirm_0=data_confirm_0, data_confirm_1=data_confirm_1)

@app.route('/regrest')        
def regrest():
    return render_template('regrest.html')
    
@app.route('/confirmreceipt')        
def confirmreceipt():
    return render_template('confirmreceipt.html')

@app.route("/confirmreceipt_action", methods=['POST'])
@login_required
def confirm_receipt_action():
    order_id = request.json.get('id')
    confirm_receipt(order_id)  # 處理確認接單操作
    return jsonify({"status": "success"}), 200  # 回傳成功訊息
    
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
