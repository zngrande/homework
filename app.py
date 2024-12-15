from flask import Flask, render_template, request, session, redirect
import sqlite3
from functools import wraps
from dbUtils import get_user_by_id, add_user, get_all_restaurants, get_dish_list_by_name, get_restaurant_details_by_name, get_dish_details_by_dish_name, add_to_cart, get_cart_detail, delete_from_cart

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
            session['name'] = user['name']  # 確保正確設置 Uname
            print(f"用戶 {session['name']} 登錄成功")  # 調試輸出
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

#註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        id = form['id']  # ID of the user
        pw = form['pw']  # Password of the user
        role = form['role']  # Role selected by the user (customer, restaurant, or delivery)
    
        # 呼叫函數將用戶資料新增到資料庫
        add_user(id, pw, role)

        # 註冊成功後重定向到登入頁面
        return redirect('/loginPage')

    # 使用 GET 方法時，返回註冊頁面
    return render_template('register.html')

#首頁(可以偵測到註冊時的姓名)
'''
@app.route("/frontPage")
def front_page2():
    id = session.get('id')  # 假設您將 Uid 存儲在 session 中
    name = session.get('name')  # 獲取用戶名稱
    return render_template('frontpage.html', name=name, id=id)
'''
    
#客人看餐廳 渲染
@app.route("/frontPage")
def restaurant_list():
    data = get_all_restaurants()
    return render_template('frontPage.html',data=data)

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
    restaurant_name = request.form.get('restaurant_name')
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

    dish = get_dish_details_by_dish_name(dish_name)
    if quantity == 0:
        delete_from_cart(dish_name)
        return redirect(f"/restaurantdishlist/{dish['restaurant_name']}")
    else:
        # 如果數量大於 0，將餐點加入購物車
        #dish = get_dish_details_by_dish_name(dish_name)
        if not dish:
            return f"未找到餐點資料，餐點名稱: {dish_name}", 404

        add_to_cart(dish['dish_name'], dish['price'], dish['restaurant_name'], quantity)
        return redirect(f"/restaurantdishlist/{dish['restaurant_name']}")


#客人看購物車 渲染
@app.route("/cart")
def cart_list():
    data = get_cart_detail()
    total_price = sum(item['quantity'] * item['price'] for item in data)
    return render_template('cart.html',data=data, total_price=total_price)



