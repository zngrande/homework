from flask import Flask, render_template, request, session, redirect
import sqlite3
from functools import wraps
from dbUtils import get_user_by_id, add_user,add_user2, get_all_restaurants, get_dish_list_by_name, get_restaurant_details_by_name, get_dish_details_by_dish_name, add_to_cart, get_cart_detail, delete_from_cart, send_dish

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
            session['Gid'] = user['Gid']
            session['name'] = user['name']
            print(f"用戶 {session['name']} 登錄成功")
            
            if role == "customer":
                return redirect("/guestfrontPage")
            elif role == "restaurant":
                return redirect("/restaurantfrontPage")
            elif role == "delivery":
                return redirect("/deliveryfrontPage")
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
        role = form['role']  # 取得角色

        # 檢查角色並呼叫對應的函數
        if role == "customer" or role == "restaurant":
            address = form['address'] 
            add_user(id, pw, role, name, phone, address)
        elif role == "delivery":
            add_user2(id, pw, role, name, phone) 
        else:
            return "無效的角色", 400  

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
@app.route("/guestfrontPage")
def restaurant_list():
    data = get_all_restaurants()
    return render_template('guestfrontPage.html',data=data)

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





