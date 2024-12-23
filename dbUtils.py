#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector #mariadb
from datetime import datetime


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

def get_all_restaurants():
    sql = """
    SELECT name, address, point
    FROM restaurant;
    """
    cursor.execute(sql)
    return cursor.fetchall()

#餐廳菜單
def get_dish_list_by_name(name):
    sql = """
    SELECT restaurant.name, dish.dish_name, dish.price, dish.content
    FROM restaurant
    JOIN dish ON restaurant.name = dish.restaurant_name
    WHERE restaurant.name = %s;
    """
    cursor.execute(sql, (name,))
    return cursor.fetchall()


#拿到餐聽資訊
def get_restaurant_details_by_name(name):
    sql = "SELECT * FROM restaurant WHERE name = %s;"
    cursor.execute(sql, (name,))
    return cursor.fetchone()

#拿到餐點資訊
def get_dish_details_by_dish_name(dish_name):
    sql = "SELECT * FROM dish WHERE dish_name = %s;"
    cursor.execute(sql, (dish_name,))
    return cursor.fetchone()

# 新增或更新購物車
def add_to_cart(dish_name, price, restaurant_name, quantity, Gid):
    try:
        # 如果數量為0，刪除該菜品
        if quantity == 0:
            sql_delete = """
                DELETE FROM guest_cart
                WHERE dish_name = %s AND restaurant_name = %s AND Gid = %s;
            """
            cursor.execute(sql_delete, (dish_name, restaurant_name, Gid))
            conn.commit()
            print(f"已刪除 {dish_name} 的購物車項目")
        else:
            # 檢查購物車中是否已經有該菜品
            sql_check = """
                SELECT * FROM guest_cart
                WHERE dish_name = %s AND restaurant_name = %s AND Gid = %s;
            """
            cursor.execute(sql_check, (dish_name, restaurant_name, Gid))
            existing_item = cursor.fetchone()

            if existing_item:
                # 如果已經有該菜品，更新數量
                sql_update = """
                    UPDATE guest_cart
                    SET quantity = %s
                    WHERE dish_name = %s AND restaurant_name = %s AND Gid = %s;
                """
                cursor.execute(sql_update, (quantity, dish_name, restaurant_name, Gid))
                print(f"已更新 {dish_name} 的數量為 {quantity}")
            else:
                # 如果購物車中沒有該菜品，新增該菜品
                sql_insert = """
                    INSERT INTO guest_cart (dish_name, price, restaurant_name, quantity, Gid)
                    VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(sql_insert, (dish_name, price, restaurant_name, quantity, Gid))
                print(f"已將 {dish_name} 新增到購物車")

        # 提交變更
        conn.commit()
    except mysql.connector.Error as e:
        print("處理購物車時發生錯誤:", e)


#刪除購物車內容
def delete_from_cart(dish_name, Gid):
    try:
        sql = "DELETE FROM guest_cart WHERE dish_name = %s AND Gid = %s;"
        cursor.execute(sql, (dish_name,Gid,))
        conn.commit()
        print(f"已從購物車中刪除餐點: {dish_name}")
    except mysql.connector.Error as e:
        print("刪除餐點時發生錯誤:", e)


#拿到購物車資訊
def get_cart_detail():
    sql = "SELECT * FROM guest_cart;"
    cursor.execute(sql)
    return cursor.fetchall()

#傳訂單給餐廳
def send_dish(Gid):
    # 查詢購物車中的資料
    sql_select = """
    SELECT guest_cart.restaurant_name, guest_cart.dish_name, guest_cart.price, guest_cart.quantity, 
           guest_cart.Gid, restaurant.Rid, guest.name AS guest_name
    FROM guest_cart
    JOIN restaurant ON restaurant.name = guest_cart.restaurant_name
    JOIN guest ON guest.Gid = guest_cart.Gid
    WHERE guest_cart.Gid = %s;
    """
    
    # 插入訂單的語句（order_id 是自動增長的）
    sql_insert_order = """
    INSERT INTO orders (Gid, order_date)
    VALUES (%s, NOW());
    """
    
    # 插入到 prepare_dish 表的語句
    sql_insert_prepare_dish = """
    INSERT INTO prepare_dish (Rid, dish_name, quantity, price, Gid, guest_name,  order_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        # 取得購物車資料
        cursor.execute(sql_select, (Gid,))
        cart_data = cursor.fetchall()

        if not cart_data:
            print("購物車中沒有資料")
            return

        print(cart_data)

        # 插入訂單並獲取自動生成的 order_id
        cursor.execute(sql_insert_order, (Gid,))
        order_id = cursor.lastrowid  # 獲取剛剛插入的訂單的 order_id

        print(f"生成的訂單 ID: {order_id}")

        # 插入資料到 prepare_dish
        for item in cart_data:
            Rid = item['Rid']
            dish_name = item['dish_name']
            quantity = item['quantity']
            Gid = item['Gid']
            price = item['price']
            guest_name = item['guest_name']
            print(f"插入資料: Rid={Rid}, dish_name={dish_name}, quantity={quantity}, price={price}, Gid={Gid}, guest_name={guest_name}, order_id={order_id}")
            cursor.execute(sql_insert_prepare_dish, (Rid, dish_name, quantity, price, Gid, guest_name, order_id))

        # 清空該使用者的購物車資料
        sql_delete = "DELETE FROM guest_cart WHERE Gid = %s;"
        cursor.execute(sql_delete, (Gid,))

        print(f"清空用戶 {Gid} 的購物車資料")
        
        # 提交變更
        conn.commit()
        return "訂單成功送出", 200

    except mysql.connector.Error as e:
        print(f"資料庫錯誤: {e}")
        return "資料庫錯誤，請稍後再試！", 500

#客人拿到訂單
def guest_get_arrive(status, Gid):
    sql='''
    SELECT orderlist.order_id, 
           restaurant.name AS restaurant_name, 
           SUM(history_orderlists.quantity * history_orderlists.price) AS total_price,
           delivery_man.name AS d_name,
           orderlist.pickup_time,
           guest.Gid,
           orderlist.point
    FROM orderlist
    JOIN restaurant ON restaurant.Rid = orderlist.Rid
    JOIN guest ON guest.Gid = orderlist.Gid
    JOIN delivery_man ON delivery_man.Did = orderlist.Did
    JOIN history_orderlists ON history_orderlists.order_id = orderlist.order_id
    WHERE orderlist.status = %s AND guest.Gid = %s
    GROUP BY orderlist.order_id
    '''
    cursor.execute(sql, (status, Gid,))
    return cursor.fetchall()

#客人評分
def rate(point, order_id):
    sql="""
        UPDATE orderlist
        SET point = %s 
        WHERE order_id = %s
        """
    cursor.execute(sql, (point, order_id))
    conn.commit()
    
#更新餐廳評分
def update_restaurant_points():
    sql = """
    UPDATE restaurant r
    JOIN (
        SELECT 
            o.Rid, 
            AVG(o.point) AS avg_point
        FROM orderlist o
        WHERE o.point IS NOT NULL
        GROUP BY o.Rid
    ) avg_data ON r.Rid = avg_data.Rid
    SET r.point = avg_data.avg_point;
    """
    try:
        cursor.execute(sql)
        conn.commit()
    except mysql.connector.Error as e:
        print(f"更新餐廳評分失敗: {e}")
        conn.rollback()

#deliver

# 獲取待處理訂單
def get_pending_orders(status):
    sql = """
    SELECT orderlist.order_id, 
           orderlist.Rid, 
           restaurant.name AS restaurant_name, 
           orderlist.Gid, 
           guest.address, 
           guest.name AS guest_name, 
           SUM(history_orderlists.quantity * history_orderlists.price) AS total_price
    FROM orderlist
    JOIN restaurant ON restaurant.Rid = orderlist.Rid
    JOIN guest ON guest.Gid = orderlist.Gid
    JOIN history_orderlists ON history_orderlists.order_id = orderlist.order_id
    WHERE orderlist.status = %s
    GROUP BY orderlist.order_id, 
             orderlist.Rid, 
             restaurant.name, 
             orderlist.Gid, 
             guest.address, 
             guest.name;
    """
    cursor.execute(sql, (status,))
    return cursor.fetchall()


def accept_order(Did, order_id):
    try:
        sql="""
            UPDATE orderlist
            SET Did = %s, status = '已找到外送員'
            WHERE order_id = %s 
        """
        cursor.execute(sql, (Did, order_id))
        conn.commit()
    except mysql.connector.Error as e:
        print("確認外送員時發生錯誤:", e)

#看待送
def get_pending_orders_byDid(status, Did):
    sql = """
    SELECT orderlist.order_id, 
           orderlist.Rid, 
           restaurant.name AS restaurant_name, 
           orderlist.Gid, 
           guest.address, 
           orderlist.pickup_time,
           guest.name AS guest_name, 
           SUM(history_orderlists.quantity * history_orderlists.price) AS total_price
    FROM orderlist
    JOIN restaurant ON restaurant.Rid = orderlist.Rid
    JOIN guest ON guest.Gid = orderlist.Gid
    JOIN history_orderlists ON history_orderlists.order_id = orderlist.order_id
    WHERE orderlist.status = %s AND Did = %s
    GROUP BY orderlist.order_id, 
             orderlist.Rid, 
             restaurant.name, 
             orderlist.Gid, 
             guest.address, 
             guest.name;
    """
    cursor.execute(sql, (status,Did))
    return cursor.fetchall()


# 取貨
def pick_up_order(order_id):
    try:
        cursor.execute(
            "UPDATE orderlist SET status = '外送員已領餐', pickup_time = %s WHERE order_id = %s AND status = '已找到外送員';",
            (datetime.now(), order_id),
        )
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error picking up order: {e}")
        

# 送達
def complete_order(order_id):
    try:
        cursor.execute(
            "UPDATE orderlist SET status = '已完成', arrive_time = %s WHERE order_id = %s;",
            (datetime.now(), order_id),
        )
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error picking up order: {e}")


#餐廳    
def confirm_receipt(order_id):
    try:
        sql_update = """
            UPDATE prepare_dish
            SET confirm = 1, confirm_time = NOW()
            WHERE confirm = 0 AND order_id = %s;
        """
        cursor.execute(sql_update, (order_id,))
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback()
        print("錯誤: ", e)

        
def transfer_order(order_id):
    print(order_id)
    try:
        sql = "SELECT * FROM prepare_dish WHERE order_id = %s AND confirm = 1 ORDER BY confirm_time ASC"
        cursor.execute(sql, (order_id,))
        order = cursor.fetchall()

        if not order:
            return "訂單不存在"

        for item in order:
            Rid = item['Rid']
            Gid = item['Gid']
            order_id = item['order_id']
            quantity = item['quantity']
            price = item['price']

            # 插入 history_orderlists 表
            sql_insert_history = "INSERT INTO history_orderlists (order_id, quantity, price) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert_history, (order_id, quantity, price))
        # 插入 orderlist 表
        sql_insert = "INSERT INTO orderlist (Rid, Gid, order_id, finish_time, status) VALUES (%s, %s, %s, NOW(), '待接單')"
        cursor.execute(sql_insert, (Rid, Gid, order_id))
        # 刪除已轉移的資料
        sql_delete = "DELETE FROM prepare_dish WHERE order_id = %s"
        cursor.execute(sql_delete, (order_id,))

        # 提交變更
        conn.commit()
        return "訂單已成功轉移"

    except mysql.connector.Error as e:
        conn.rollback()
        return f"資料庫操作失敗: {e}"


def get_order_data(confirm, Rid):
    sql = "SELECT * FROM prepare_dish WHERE confirm = %s AND Rid=%s ;"
    cursor.execute(sql, (confirm,Rid,))
    return [dict(row) for row in cursor.fetchall()]  # 確保返回格式一致

def add_dish(Rid, restaurant_name, dish_name, price, content):
    # 獲取最大 dish_id
    cursor.execute("SELECT MAX(dish_id) AS max_dishid FROM dish;")
    result = cursor.fetchone()
    new_dishid = (result['max_dishid'] + 1) if result['max_dishid'] is not None else 1
    
    # 插入新餐點
    sql = """
        INSERT INTO dish (dish_id, Rid, restaurant_name, dish_name, price, content)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    param = (new_dishid, Rid, restaurant_name, dish_name, price, content)
    cursor.execute(sql, param)
    conn.commit()


def update_dish(dish_id, dish_name, price, content):
    cursor.execute("UPDATE dish SET dish_name = %s, price = %s, content = %s WHERE dish_id = %s", (dish_name, price, content, dish_id))
    conn.commit()

def delete_dish_by_id(dish_id):   
    cursor.execute("DELETE FROM dish WHERE dish_id = %s", (dish_id,))
    conn.commit()

def get_dish_by_Rid(Rid):
    sql = "SELECT * FROM dish WHERE Rid = %s ;"
    cursor.execute(sql,(Rid,))
    return cursor.fetchall()
def get_dish_by_id(dish_id):
    sql = "SELECT * FROM dish WHERE dish_id = %s"
    cursor.execute(sql, (dish_id,))
    return cursor.fetchone()  # 返回單筆資料


def get_prepare_dish(Rid):
    sql = "SELECT * FROM prepare_dish WHERE Rid = %s AND confirm=0;"
    cursor.execute(sql,(Rid,))
    return cursor.fetchall()

def get_finish_dish(Rid):
    sql = "SELECT * FROM prepare_dish WHERE Rid = %s AND confirm=1;"
    cursor.execute(sql,(Rid,))
    return cursor.fetchall()
def get_res_by_Rid(Rid):
    sql = "SELECT * FROM restaurant WHERE Rid = %s;"
    cursor.execute(sql,(Rid,))
    return cursor.fetchone()
def update_res_information(name, address, phone, Rid):
    sql = "UPDATE restaurant SET name = %s, address = %s, phone = %s WHERE Rid = %s"
    cursor.execute(sql,(name,address,phone,Rid,))
    conn.commit()