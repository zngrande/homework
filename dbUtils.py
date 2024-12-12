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


def get_all_restaurants():
    sql = """
    SELECT name, address, point
    FROM restaurant;
    """
    cursor.execute(sql)
    return cursor.fetchall()

#餐廳菜單
def get_dish_list_by_Rid(Rid):
    sql = """
    SELECT restaurant.name, dish.dish_name, dish.price, dish.content
    FROM restaurant
    JOIN dish ON restaurant.name = dish.restaurant_name
    WHERE restaurant.Rid = %s;
    """
    cursor.execute(sql, (Rid,))
    return cursor.fetchall()

#拿到餐點資訊
def getdishDetailsById(Rid):
    sql = "SELECT * FROM restaurant WHERE Rid = %s;"
    cursor.execute(sql, (Rid,))
    return cursor.fetchone()
