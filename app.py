from flask import Flask, render_template, request, session, redirect
import sqlite3
from functools import wraps
from dbUtils import getList, add_user, get_user_by_uid2, get_user_products

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

    user = get_user_by_uid2(id)

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
    session.pop('id', None)  # 清除 id
    session.pop('loginID', None)  # 可選：如果您也使用 loginID，清除它
    return redirect('/loginPage')  # 重定向到登入頁面

#註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        id = form['id']
        identity = form['identity']
        pw = form['pw']

        # 呼叫函數將用戶資料新增到資料庫
        add_user(id, pw, identity)

        # 註冊成功後重定向到登入頁面
        return redirect('/loginPage')
    
    # 使用 GET 方法時，返回註冊頁面
    return render_template('register.html')

#首頁(可以偵測到註冊時的姓名)
@app.route("/frontPage")
def front_page2():
    Gid = session.get('Gid')  # 假設您將 Uid 存儲在 session 中
    name = session.get('name')  # 獲取用戶名稱
    return render_template('frontpage.html', name=name, Gid=Gid)

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


#全部餐廳頁面渲染
@app.route("/restaurantlist")
def product_list():
    dat = getList()
    return render_template('restaurantlist.html', data=dat)



if __name__ == '__main__':
    app.run(debug=True)
    
