from flask import Flask, render_template, request, session, redirect
import sqlite3
from functools import wraps
from dbUtils import add, update, delete, getList, placePrice,get_user_by_uid2, get_user_products,getHighestPriceById,getProductDetailsById, add_user,get_bid_records_by_pid


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
    Uid = form['Uid']
    pw = form['pw']

    user = get_user_by_uid2(Uid)

    if user:
        if user['pw'] == pw:  # 確保這裡檢查的密碼邏輯正確
            session['loginID'] = Uid  # 可選
            session['Uid'] = Uid
            session['Uname'] = user['Uname']  # 確保正確設置 Uname
            print(f"用戶 {session['Uname']} 登錄成功")  # 調試輸出
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
    session.pop('Uid', None)  # 清除 Uid
    session.pop('loginID', None)  # 可選：如果您也使用 loginID，清除它
    return redirect('/loginPage')  # 重定向到登入頁面

#註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        Uid = form['Uid']
        Uname = form['Uname']
        pw = form['pw']

        # 呼叫函數將用戶資料新增到資料庫
        add_user(Uid, Uname, pw)

        # 註冊成功後重定向到登入頁面
        return redirect('/loginPage')
    
    # 使用 GET 方法時，返回註冊頁面
    return render_template('register.html')

#首頁(可以偵測到註冊時的姓名)
@app.route("/frontPage")
def front_page2():
    Uid = session.get('Uid')  # 假設您將 Uid 存儲在 session 中
    Uname = session.get('Uname')  # 獲取用戶名稱
    return render_template('frontpage.html', Uname=Uname, Uid=Uid)

#個人商品頁面渲染    
@app.route('/ownproductlist')
@login_required  # 確保用戶已登入
def own_product_list():
    Uid = session.get('Uid')  # 獲取當前登入的 Uid
    if not Uid:
        return redirect('/loginPage')  # 如果未登入，重定向到登入頁面

    # 取得當前使用者的商品列表，傳遞 Uid 作為參數
    user_products = get_user_products(Uid)
    return render_template('ownlist.html', data=user_products)

#新增商品頁面渲染
@app.route("/addproducts")
#使用server side render: template 樣板
def c1():
    dat={
		"name": "",
		"content":""
	}
    return render_template('addproducts.html', data=dat)

#新增商品
@app.route('/addProduct', methods=['POST'])
def addproduct():
    if request.method == 'POST':
        form = request.form
    else:
        form = request.args

    name = form['name']  
    cont = form['content']
    price = form['starting_price']
    
    # 獲取當前登入用戶的 Uid
    Uid = session.get('Uid')  # 確保 Uid 存在於 session 中

    # 新增商品到資料庫，並將 Uid 一起傳遞
    add(name, cont, price, Uid)
    
    # 重定向到擁有的商品列表頁面
    return redirect("/ownproductlist")

#修改商品(用Pid)
@app.route("/editproducts/<int:product_id>", methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        # 取得表單數據並更新產品
        form = request.form
        name = form['name']  
        content = form['content']
        starting_price = form['starting_price']
        
        # 更新資料庫中的產品資料
        update(product_id, name, content, starting_price)  
        return redirect("/ownproductlist")
    
    # 使用 GET 請求時，取得產品詳細資料
    product = getProductDetailsById(product_id)
    return render_template('editproducts.html', data=product)

#刪除商品(用Pid)
@app.route('/deleteProduct/<int:Pid>', methods=['GET'])
def delete_product(Pid):
    delete(Pid)  # 呼叫 dbUtils 中的刪除函式
    return redirect("/ownproductlist")

#全部商品頁面渲染
@app.route("/productlist")
def product_list():
    dat = getList()
    return render_template('list.html', data=dat)

#設置競標價格
@app.route('/placeBid', methods=['POST'])
@login_required
def place_bid():
    product_id = request.form.get('Pid')  # 使用 get 方法以防止 KeyError
    bid_amount = request.form['bid_amount']  # 取得競標金額

    # 確保 bid_amount 轉換為整數
    try:
        bid_amount = int(bid_amount)
    except ValueError:
        return "Invalid bid amount.", 400  # 返回 400 錯誤，如果轉換失敗

    # 檢查 Pid 是否存在
    if product_id is None:
        return "Pid is missing.", 400  # 如果 Pid 缺失，返回 400 錯誤

    # 獲取產品詳細信息和目前的最高競標價格
    product = getProductDetailsById(product_id)
    current_highest_price = getHighestPriceById(product_id)

    # 獲取當前登入用戶的 Uid
    Uid = session.get('Uid')

    # 檢查競標金額是否高於目前最高價和底價
    if bid_amount > current_highest_price and bid_amount > product['starting_price']:
        placePrice(bid_amount, product_id, Uid, product['name'])  # 將競標金額、Uid和商品名稱存入資料庫
        return redirect("/productlist")
    else:
        return "Bid must be higher than the current highest bid and the starting price."
    
#競標紀錄
#@app.route("/bidRecords/<int:Pid>")
#def bid_records(Pid):
    bid_records = get_bid_records_by_pid(Pid)
    product = getProductDetailsById(Pid)  # 獲取商品詳細信息
    return render_template('bid_records.html', data=bid_records, product=product)

@app.route("/bidRecords/<int:Pid>")
def bid_records(Pid):
    bid_records = get_bid_records_by_pid(Pid)
    product = getProductDetailsById(Pid)  # 獲取商品詳細信息
    product_name = product['name']  # 取得商品名稱
    return render_template('bid_records.html', data=bid_records, product_name=product_name)



if __name__ == '__main__':
    app.run(debug=True)
    
