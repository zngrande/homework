from flask import Flask, render_template, request, session, redirect
import sqlite3
from functools import wraps
from dbUtils import get_user_by_id, add_user


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
@app.route("/frontPage")
def front_page2():
    id = session.get('id')  # 假設您將 Uid 存儲在 session 中
    name = session.get('name')  # 獲取用戶名稱
    return render_template('frontpage.html', name=name, id=id)



'''
from flask import Flask, render_template, request, session, redirect
import json
from functools import wraps
#from dbUtils import getList
import dbUtils as DB

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
	

@app.route("/")
#check login with decorator function
@login_required
def hello(): 
	message = "Hello, World 1"
	return message

@app.route("/getAjaxData", methods=['POST'])
#取得網址作為參數
def getdata111():
    id=request.form['userID']
    name=request.form['userName']
    return f"I got your input: {id}, {name}"

@app.route("/test/<string:name>/<int:id>")
#取得網址作為參數
def useParam(name,id):
	#check login inside the function
	if not isLogin():
		return redirect('/loginPage.html')
	return f"got name={name}, id={id} "

@app.route("/secret")
#使用server side render: template 樣板
def showSecret():
    return "<img src='/dog.jpg' />";

@app.route("/edit")
#使用server side render: template 樣板
def h1():
	dat={
		"name": "大牛",
		"content":"內容說明文字"
	}
	#editform.html 存在於 templates目錄下, 將dat 作為參數送進 editform.html, 名稱為 data
	return render_template('editform.html', data=dat)

@app.route("/list")
#使用server side render: template 樣板
def h2():
	dat=[
		{
			"name": "大牛",
			"p":"愛吃瓜"
		},
		{
			"name": "小李",
			"p":"怕榴槤"
		},
		{
			"name": "",
			"p":"ttttt"
		},
		{
			"name": "老謝",
			"p":"來者不拒"
		}
	]
	return render_template('list.html', data=dat)

#取得使用者輸入之資料
@app.route('/input', methods=['GET', 'POST'])
def userInput():
	if request.method == 'POST':
		form =request.form
	else:
		form= request.args

	txt = form['txt']  # pass the form field name as key
	note =form['note']
	select = form['sel']
	msg=f"method: {request.method} txt:{txt} note:{note} sel: {select}"
	return msg

#call utils.py 之函數取得資料資料，再用template產生網頁傳給browser
@app.route("/listJob")
#使用server side render: template 樣板
def gl():
	dat=DB.getList()
	return render_template('todolist.html', data=dat)

#call utils.py 之函數取得資料資料，將資料包成JSON格式，傳給browser處理
@app.route("/getListJSON", methods=['POST'])
#使用server side render: template 樣板
def listJSON():

	dat=DB.getList()
	return json.dumps(dat)

#取得使用者指定的todo job，將資料包成JSON格式，傳給browser處理
@app.route("/getTodoJob", methods=['GET'])
#使用server side render: template 樣板
def jobJSON():
	jobID = request.args['id']
	dat=DB.getJob(jobID)
	return json.dumps(dat)



#handles login request
@app.route('/login', methods=['POST'])
def login():
	form =request.form
	id = form['ID']
	pwd =form['PWD']
	#validate id/pwd
	if id=='123' and pwd=='456':
		session['loginID']=id
		return redirect("/")
	else:
		session['loginID']=False
		return redirect("/loginForm")
'''
    


'''
# 是否登入檢查
def isLogin():
    return session.get('loginID')

@app.route("/test/<string:name>/<int:id>")
#取得網址作為參數
def useParam(name,id):
	#check login inside the function
	if not isLogin():
		return redirect('/loginPage.html')
	return f"got name={name}, id={id} "

# 渲染登入頁面
@app.route('/loginPage')
def login_page():
    return render_template('loginPage.html')

# 登入功能
@app.route('/login', methods=['POST'])
def login():
    form = request.form
    id = form['id']
    pw = form['pw']

    user = get_user_by_uid2(id)  # 從資料庫獲取用戶

    if user:
        if user['pw'] == pw:
            # 登入成功，將資訊存入 session
            session['loginID'] = id
            session['role'] = user['identity']
            session['name'] = user['name']
            print(f"用戶 {user['name']} ({user['identity']}) 登錄成功")
            return redirect("/frontPage")
        else:
            print("密碼不正確")
            return redirect("/loginPage?error=wrong_password")
    else:
        print("用戶不存在")
        return redirect("/loginPage?error=user_not_found")

# 登出功能
@app.route('/logout')
@login_required
def logout():
    session.clear()  # 清空 session
    return redirect('/loginPage')

# 註冊功能
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = request.form
        id = form['id']  # 對應前端的 ID 欄位
        pw = form['pw']
        role = form['role']  # 角色
        name = form['name']  # 姓名

        # 將用戶資料新增到資料庫
        add_user(id, pw, role, name)

        # 註冊成功後跳轉到登入頁面
        return redirect('/loginPage')

    # GET 方法時渲染註冊頁面
    return render_template('register.html')

# 首頁功能
@app.route('/frontPage')
@login_required
def front_page():
    name = session.get('name')  # 用戶姓名
    role = session.get('role')  # 用戶角色
    return render_template('frontpage.html', name=name, role=role)
'''
'''
#個人商品頁面渲染    
@app.route('/ownproductlist')
@login_required  # 確保用戶已登入
def own_product_list():
    id = session.get('id')  # 獲取當前登入的 id
    if not id:
        return redirect('/loginPage')  # 如果未登入，重定向到登入頁面

    # 取得當前使用者的商品列表，傳遞 id 作為參數
    user_products = get_user_products(id)
    return render_template('ownlist.html', data=user_products)


#全部餐廳頁面渲染
@app.route("/restaurantlist")
def product_list():
    dat = getList()
    return render_template('restaurantlist.html', data=dat)



if __name__ == '__main__':
    app.run(debug=True)
   ''' 
