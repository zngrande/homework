#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector #mariadb
import sqlite3

try:
	#連線DB
	conn = mysql.connector.connect(
		user="root",
		password="",
		host="localhost",
		port=3306,
		database="food_pangolin"
	)
	#建立執行SQL指令用之cursor, 設定傳回dictionary型態的查詢結果 [{'欄位名':值, ...}, ...]
	cursor=conn.cursor(dictionary=True)
except mysql.connector.Error as e: # mariadb.Error as e:
	print(e)
	print("Error connecting to DB")
	exit(1)

#新增註冊者
def add_user(id, pw, identity):
    try:
        sql = "INSERT INTO accounts1 (id, pw, identity) VALUES (%s, %s, %s);"
        cursor.execute(sql, (id, pw, identity))
        conn.commit()
        print("用戶註冊成功")
    except mysql.connector.Error as e:
        print("註冊用戶時發生錯誤:", e)









'''
#新增商品
def add(name, content, starting_price, Uid):
    try:
        sql = "INSERT INTO website1 (name, content, starting_price, Uid) VALUES (%s, %s, %s, %s);"
        param = (name, content, starting_price, Uid)
        cursor.execute(sql, param)
        conn.commit()
        print("商品已成功新增")
    except mysql.connector.Error as e:
         print("新增商品時發生錯誤:", e)

#刪除商品
def delete(Pid):
    try:
        # 先删除 price1 表中引用的记录
        delete_price_sql = "DELETE FROM price1 WHERE Pid = %s;"
        cursor.execute(delete_price_sql, (Pid,))
        
        # 然后再删除 website1 表中的记录
        sql = "DELETE FROM website1 WHERE Pid = %s;"
        cursor.execute(sql, (Pid,))
        conn.commit()
        print("商品已成功刪除")
    except mysql.connector.Error as e:
        print("刪除商品時發生錯誤:", e)



#修改商品
def update(Pid, name, content, starting_price):
    sql = "UPDATE website1 SET name = %s, content = %s, starting_price = %s WHERE Pid = %s;"
    param = (name, content, starting_price, Pid)
    cursor.execute(sql, param)
    conn.commit()


def getList():
    sql = """
    SELECT website1.Pid, website1.name, website1.content, website1.starting_price,  
           COALESCE(MAX(price1.now_price), 0) AS highest_price,
           COALESCE((SELECT Uname FROM accounts1 WHERE Uid = (SELECT Uid FROM price1 WHERE Pid = website1.Pid ORDER BY now_price DESC LIMIT 1)), '無') AS Uname
    FROM website1 
    LEFT JOIN price1 ON website1.Pid = price1.Pid
    GROUP BY website1.Pid, website1.name, website1.content, website1.starting_price;
    """
    cursor.execute(sql)
    return cursor.fetchall()

#設置競標價格
def placePrice(now_price, Pid, Uid, name):
    sql = "INSERT INTO price1 (now_price, Pid, Uid, name) VALUES (%s, %s, %s, %s);"
    cursor.execute(sql, (now_price, Pid, Uid, name))
    conn.commit()   

#拿到用戶ID
def get_user_by_uid2(Uid):
    sql = "SELECT * FROM accounts1 WHERE Uid = %s;"
    cursor.execute(sql, (Uid,))
    user = cursor.fetchone()
    return user

def get_user_products(Uid):
    sql = """
    SELECT website1.Pid, website1.name, website1.content, website1.starting_price,
           COALESCE(MAX(price1.now_price), 0) AS highest_price 
    FROM website1 
    LEFT JOIN price1 ON website1.Pid = price1.Pid
    WHERE website1.Uid = %s
    GROUP BY website1.Pid, website1.name, website1.content, website1.starting_price;
    """
    cursor.execute(sql, (Uid,))
    products = cursor.fetchall()
    return products

#拿到商品資訊
def getProductDetailsById(Pid):
    sql = "SELECT * FROM website1 WHERE Pid = %s;"
    cursor.execute(sql, (Pid,))
    return cursor.fetchone()

#拿到最高價的人
def getHighestPriceById(Pid):
    sql = "SELECT MAX(now_price) AS highest_price FROM price1 WHERE Pid = %s;"
    cursor.execute(sql, (Pid,))
    result = cursor.fetchone()
    return result['highest_price'] if result['highest_price'] else 0

#競標紀錄
def get_bid_records_by_pid(Pid):
    sql = """
    SELECT accounts1.Uname, price1.now_price, price1.bid_time
    FROM price1
    JOIN accounts1 ON price1.Uid = accounts1.Uid
    WHERE price1.Pid = %s
    ORDER BY price1.bid_time DESC;
    """
    cursor.execute(sql, (Pid,))
    return cursor.fetchall()

'''

