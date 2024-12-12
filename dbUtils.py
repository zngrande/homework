#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector #mariadb

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


# 新增註冊者
def add_user(id, pw, role):
    """
    根據使用者角色將其新增到相應的資料表中。
    若角色為 '客戶'，則分配下一個可用的 Gid。
    若角色為 '餐廳'，則分配下一個可用的 Rid。
    若角色為 '外送員'，則分配下一個可用的 Did。
    """
    try:
        if role == "客戶":
            # 取得最大 Gid 並加 1 為新使用者分配 Gid
            cursor.execute("SELECT MAX(Gid) AS max_gid FROM guest;")
            result = cursor.fetchone()
            new_gid = (result['max_gid'] + 1) if result['max_gid'] is not None else 1
            sql = "INSERT INTO accounts (Gid, id, pw, identity) VALUES (%s, %s, %s,'客戶');"
            cursor.execute(sql, (new_gid, id, pw))

        elif role == "餐廳":
            # 取得最大 Rid 並加 1 為新使用者分配 Rid
            cursor.execute("SELECT MAX(Rid) AS max_rid FROM restaurant;")
            result = cursor.fetchone()
            print("最大 Rid:", result)  # 輸出查詢結果
            new_rid = (result['max_rid'] + 1) if result['max_rid'] is not None else 1
            sql = "INSERT INTO accounts (Rid, id, pw, identity) VALUES (%s, %s, %s,'餐廳');"
            cursor.execute(sql, (new_rid, id, pw))

        elif role == "外送員":
            # 取得最大 Did 並加 1 為新使用者分配 Did
            cursor.execute("SELECT MAX(Did) AS max_did FROM delivery_man;")
            result = cursor.fetchone()
            print("最大 Did:", result)  # 輸出查詢結果
            new_did = (result['max_did'] + 1) if result['max_did'] is not None else 1
            sql = "INSERT INTO accounts (Did, Uid, pw, identity) VALUES (%s, %s, %s, '外送員');"
            cursor.execute(sql, (new_did, id, pw))

        else:
            print("無效的角色")
            return

        # 提交變更到資料庫
        conn.commit()
        print(f"{role} 註冊成功，ID 為 {id}")
    
    except mysql.connector.Error as e:
        print("註冊使用者時發生錯誤:", e)



# 測試函數
if __name__ == "__main__":
    # 假設前端傳入的數據
    sample_data = {
        "id": "C123",
        "pw": "securepassword",
        "role": "customer",
        "name": "John Doe"
    }
    add_user(sample_data["id"], sample_data["pw"], sample_data["role"], sample_data["name"])

# 拿到用戶ID，根據角色從對應表查詢
def get_user_by_id(id, role):
    """
    根據用戶 ID 和角色類型獲取用戶資訊
    :param xid: 用戶的 ID（Uid, Rid, Did）
    :param role: 用戶的角色（customer, restaurant, delivery）
    :return: 查詢結果（字典型態），如果找不到則返回 None
    """
    try:
        if role == "customer":
            sql = "SELECT * FROM customers WHERE Uid = %s;"
        elif role == "restaurant":
            sql = "SELECT * FROM restaurants WHERE Rid = %s;"
        elif role == "delivery":
            sql = "SELECT * FROM delivery WHERE Did = %s;"
        else:
            print("角色無效")
            return None

        cursor.execute(sql, (id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"查詢用戶時發生錯誤: {e}")
        return None







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

