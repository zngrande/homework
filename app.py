from flask import Flask, render_template, request, session, redirect,jsonify
import sqlite3
from functools import wraps
from dbUtils import get_user_by_id, add_user, get_pending_orders, accept_order, pick_up_order, complete_order #, update, getGuestDetailsById


# creates a Flask application, specify a static folder on /
app = Flask(__name__, static_folder='static',static_url_path='/')
#set a secret key to hash cookies
app.config['SECRET_KEY'] = '123TyU%^&'

#define a function wrapper to check login session
def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		loginID = session.get('loginID')
		if not loginID:
			return redirect('/loginPage.html')
		return f(*args, **kwargs)
	return wrapper

#another way to check login session
def isLogin():
	return session.get('loginID')

@app.route("/test/<string:name>/<int:id>")
#取得網址作為參數
def useParam(name,id):
	#check login inside the function
	if not isLogin():
		return redirect('/loginPage.html')
	return f"got name={name}, id={id} "

#登入頁面渲染
@app.route('/loginPage')
def login_page():
    return render_template('loginPage.html')

#登入
@app.route('/login', methods=['POST'])
def login():
    form = request.form
    id = form['id']
    pw = form['pw']

    user = get_user_by_id(id)

    if user:
        if user['pw'] == pw:  # 確保這裡檢查的密碼邏輯正確
            session['loginID'] = id  # 可選
            session['id'] = id
            return redirect("/frontPage")
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
    session.pop('id', None)  # 清除 Uid
    session.pop('loginID', None)  # 可選：如果您也使用 loginID，清除它
    return redirect('/loginPage')  # 重定向到登入頁面

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        id = form.get('id')  # 使用 .get() 避免 KeyError
        pw = form.get('pw')
        identity = form.get('identity')
        
        # 確保所有字段都已填寫
        if not id or not pw or not identity:
            return "所有字段均為必填", 400

        # 呼叫函數將用戶資料新增到資料庫
        add_user(id, pw, identity)

        # 註冊成功後重定向到登入頁面
        return redirect('/loginPage')

    # 使用 GET 方法時，返回註冊頁面
    return render_template('register.html')


#首頁(可以偵測到註冊時的姓名)
@app.route("/frontPage")
def front_page2():
    id = session.get('id')  # 假設您將 Uid 存儲在 session 中
    name = session.get('name')  # 獲取用戶名稱
    return render_template('frontpage.html', name=name, id=id)
'''
# 修改資料 (客戶)
@app.route("/guestinformation", methods=['GET', 'POST'])
def guest_information():
    if request.method == 'POST':
        # 獲取表單數據
        Gid = request.form.get('Gid')  # 隱藏欄位 Gid
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # 更新資料庫
        update(Gid, name, phone, address)
        return redirect(f"/guestinformation?Gid={Gid}")
    
    # 使用 GET 請求時，取得產品詳細資料
    guest = getGuestDetailsById(Gid)
    return render_template('guestinformation.html', data=guest)
'''
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
