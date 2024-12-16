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

#deliver
#獲取待送訂單
def get_pending_orders():
    try:
        cursor.execute("SELECT * FROM orderlist WHERE status = 'pending';")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error fetching pending orders: {e}")
        return []

#接單
def accept_order(order_id, Did):
    try:
        cursor.execute("UPDATE orderlist SET status = 'accepted', Did = %s WHERE order_id = %s AND status = 'pending';", (Did, order_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Error accepting order: {e}")
        return False
#取貨
def pick_up_order(order_id):
    try:
        cursor.execute("UPDATE orderlist SET status = 'picked_up', pickup_time = %s WHERE order_id = %s AND status = 'accepted';", (datetime.now(), order_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Error picking up order: {e}")
        return False

#送達
def complete_order(order_id):
    try:
        cursor.execute("UPDATE orderlist SET status = 'completed', delivery_time = %s WHERE order_id = %s AND status = 'picked_up';", (datetime.now(), order_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"Error completing order: {e}")
        return False
