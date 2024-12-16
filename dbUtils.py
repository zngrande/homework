#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector #mariadb
import datetime

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
def add_user(id, pw, role, name, phone, address):
    try:
        if role == "customer":
            # 取得最大 Gid 並加 1 為新使用者分配 Gid
            cursor.execute("SELECT MAX(Gid) AS max_gid FROM guest;")
            result = cursor.fetchone()
            new_gid = (result['max_gid'] + 1) if result['max_gid'] is not None else 1
            sql = "INSERT INTO guest (Gid, id, pw, name, phone, address) VALUES (%s, %s, %s, %s, %s, %s);"
            cursor.execute(sql, (new_gid, id, pw, name, phone, address))

        elif role == "restaurant":
            # 取得最大 Rid 並加 1 為新使用者分配 Rid
            cursor.execute("SELECT MAX(Rid) AS max_rid FROM restaurant;")
            result = cursor.fetchone()
            new_rid = (result['max_rid'] + 1) if result['max_rid'] is not None else 1
            sql = "INSERT INTO restaurant (Rid, id, pw, name, phone, address) VALUES (%s, %s, %s, %s, %s, %s);"
            cursor.execute(sql, (new_rid, id, pw, name, phone, address))

        elif role == "delivery":
            # 取得最大 Did 並加 1 為新使用者分配 Did
            cursor.execute("SELECT MAX(Did) AS max_did FROM delivery_man;")
            result = cursor.fetchone()
            new_did = (result['max_did'] + 1) if result['max_did'] is not None else 1
            sql = "INSERT INTO delivery_man (Did, id, pw, name, phone, address) VALUES (%s, %s, %s, %s, %s, %s);"
            cursor.execute(sql, (new_did, id, pw, name, phone, address))

            # 提交變更到資料庫
            conn.commit()
            print(f"{role} 註冊成功，ID 為 {id}")
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
    try:
        if role == "customer":
            sql = "SELECT * FROM guest WHERE id = %s;"
        elif role == "restaurant":
            sql = "SELECT * FROM restaurant WHERE id = %s;"
        elif role == "delivery":
            sql = "SELECT * FROM delivery_man WHERE id = %s;"
        else:
            print("角色無效")
            return None

        cursor.execute(sql, (id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"查詢用戶時發生錯誤: {e}")
        return None
    
def confirm_receipt(order_id):
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql_update = """
            UPDATE prepare_dish
            SET confirm = 1, confirm_time = %s
            WHERE id = %s AND confirm = 0;
        """
        cursor.execute(sql_update, (current_time, order_id))
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback()
        print("錯誤: ", e)

        
def transfer_order(order_id):
    try:
        cursor.execute("SELECT Rid, Uid, dish_name FROM prepare_dish WHERE id = %s AND confirm = 1", (order_id,))
        order = cursor.fetchone()

        if not order:
            return False, "訂單不存在"

        cursor.execute(
            "INSERT INTO orderlist (Rid, Uid, dish_name, order_time) VALUES (%s, %s, %s, NOW())",
            (order['Rid'], order['Uid'], order['dish_name'])
        )
        cursor.execute("DELETE FROM prepare_dish WHERE id = %s", (order_id,))
        conn.commit()
        return True, "訂單已成功轉移"
    except mysql.connector.Error as e:
        conn.rollback()
        return False, f"資料庫操作失敗: {e}"
        
def get_order_data(confirm):
    sql = "SELECT * FROM prepare_dish WHERE confirm = %s;"
    cursor.execute(sql, (confirm,))
    return [dict(row) for row in cursor.fetchall()]  # 確保返回格式一致

def add_dish(restaurant_name, dish_name, price, content):
    sql = "INSERT INTO dish (restaurant_name, dish_name, price, content) VALUES (%s, %s, %s, %s)"
    param = (restaurant_name, dish_name, price, content)
    cursor.execute(sql, param)
    dish_id = cursor.lastrowid  # 取得新增商品的 ID
    conn.commit()  # 提交變更

def update_dish(dish_id, dish_name, price, content):
    cursor.execute("UPDATE dish SET dish_name = %s, price = %s, content = %s WHERE id = %s", (dish_name, price, content, dish_id))
    conn.commit()


def delete_dish_by_id(dish_id):   
    cursor.execute("DELETE FROM dish WHERE id = %s", (dish_id,))
    conn.commit()

def get_dish_by_id(dish_id):
    """
    根據菜品 ID 查詢菜品詳細資訊
    :param dish_id: 菜品 ID
    :return: 查詢到的菜品資訊字典，若查無資料則返回 None
    """
    try:
        # 執行 SQL 查詢
        sql = "SELECT * FROM dish WHERE id = %s;"
        cursor.execute(sql, (dish_id,))
        # 獲取結果
        dish = cursor.fetchone()
        if dish:
            return dish
        else:
            print(f"未找到對應的菜品 (ID: {dish_id})")
            return None
    except mysql.connector.Error as e:
        print("查詢菜品時發生錯誤:", e)
        return None
