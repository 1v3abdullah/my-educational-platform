import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "platform_data.db"

def init_db():
    """إنشاء قاعدة البيانات والجدول وحفظ التعديلات"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, 
            password TEXT,
            name TEXT,
            birthday TEXT,
            gender TEXT
        )
    """)
    conn.commit()  # 👈 إضافة حفظ التعديل
    conn.close()   # 👈 إضافة إغلاق الاتصال

def register_new_user(username, password, name, birthday, gender):
    """تشفير كلمة المرور الجديدة وحفظها بأمان"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    hashed_password = generate_password_hash(password)
    
    try:
        cursor.execute(
            "INSERT INTO accounts (username, password, name, birthday, gender) VALUES (?, ?, ?, ?, ?)", 
            (username, hashed_password, name, birthday, gender)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close() # 👈 وضعها هنا يضمن إغلاق الاتصال حتى لو حدث خطأ
    return success

def check_user_credentials(username, password):
    """جلب الرمز المشفر والتحقق منه بأمان"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 👈 توحيد حالة الأحرف لتطابق الجدول (username و password)
    cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        db_hashed_password = row[0]
        return check_password_hash(db_hashed_password, password)
        
    return False



def get_user_name(username):
    """جلب الاسم الفعلي للمستخدم بناءً على اسم المستخدم الخاص به"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM accounts WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row[0]  # إرجاع الاسم الفعلي الصافي
    return username  # كاحتياط إذا لم يجد الاسم يعود باسم المستخدم
