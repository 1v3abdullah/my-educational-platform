import os  # 👈 خطوة هامة: استيراد مكتبة النظام لقراءة متغيرات السيرفر
from flask import Flask, render_template, request, redirect, url_for, session
from db_auth import init_db, check_user_credentials, register_new_user, get_user_name
from datetime import timedelta, datetime, date

app = Flask(__name__)

# 🔑 تعديل المفتاح السري ليعمل بنظام البيئة الديناميكي الموزع
app.secret_key = os.environ.get('SECRET_KEY', 'alpha_developer_secret_key_2026')

# 🛡️ تعزيز أمان الجلسات وسرعة توزيعها بين خوادم معالجة الضغط
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,  
    SESSION_COOKIE_SECURE=True,    # 👈 قمنا بتغييرها إلى True لأن سيرفر النشر (Render) يوفر لك شهادة SSL/HTTPS مجانية لحماية المستخدمين
    SESSION_COOKIE_SAMESITE='Lax', 
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30) 
)

# تهيئة قاعدة البيانات مرة واحدة عند الإقلاع (مكانها الحالي سليم)
init_db()


@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if check_user_credentials(username, password):
            session['user'] = username 
            
            
            # التحويل فوراً إلى دالة صفحة الطالب المخصصة له
            return redirect(url_for('student_home_page')) 
        else:
            message = "اسم المستخدم أو كلمة المرور غير صحيحة"
            
    return render_template('login.html', message=message)


# 🛠️ استبدل الدالة السفلية بهذا الشكل تماماً:
@app.route('/student-dashboard') # 👈 تأكد من إضافة هذا السطر فوق الدالة
def student_home_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    current_username = session['user']
    
    # استدعاء الدالة الجاهزة والمجربة من ملف db_auth
    student_name = get_user_name(current_username)
    
    # إذا كانت النتيجة عبارة عن Tuple (مصفوفة من قاعدة البيانات)، نأخذ العنصر الأول الصافي
    if isinstance(student_name, tuple):
        student_name = student_name[0]
        
    return render_template('student_home_page.html', username=current_username, student_name=student_name)



# # 4. دالة تسجيل الخروج (إضافية لتدمير الجلسة)
# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        gender = request.form.get('gender')
        
        if password and len(password) < 6:
            message = 'عذراً، يجب أن تكون كلمة المرور <span style="font-family: \'Segoe UI\', Tahoma, Geneva, sans-serif; font-weight: normal;">6</span> حروف على الأقل.'
            return render_template('register.html', message=message)
        
        
        if birthday:
            # تحويل النص القادم من المتصفح إلى تاريخ حقيقي يفهمه بايثون
            birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()
            today = date.today()
            
            # حساب العمر بدقة بالسنوات (مع مراعاة هل مر يوم ميلاده هذا العام أم لا)
            age = today.year - birthday_date.year - ((today.month, today.day) < (birthday_date.month, birthday_date.day))
            
            if age < 13:
                # قمنا بوضع رقم 13 داخل span مع تحديد خط الويندوز الافتراضي Arial كمثال
                message = 'عذراً، يجب أن يكون عمرك <span style="font-family: \'Segoe UI\', Tahoma, Geneva, sans-serif; font-weight: normal;">13</span> عاماً على الأقل للتسجيل في المنصة.'
                return render_template('register.html', message=message)

            
        else:
            message = "الرجاء إدخال تاريخ الميلاد."
            return render_template('register.html', message=message)
        
        # 1. استدعاء دالة التسجيل والتأكد من نجاحها في قاعدة البيانات
        if register_new_user(username, password, name, birthday, gender):
            # 2. ضربة المعلم: تسجيل دخول الطالب تلقائياً فور نجاح التسجيل
            session['user'] = username
            session['name'] = name
            
            # 3. تحويله مباشرة للمنصة مع ترحيب فوري باسمه
            return redirect(url_for('student_home_page'))
        else:
            # في حال كان اسم المستخدم محجوزاً مسبقاً في قاعدة البيانات
            message = "خطأ: اسم المستخدم هذا مسجل مسبقاً في النظام"
            
    return render_template('register.html', message=message)
    








# قم بتطبيق نفس جدار الحماية (Check Session) على بقية مساراتك الداخلية لتبقى محمية:
@app.route('/categories')
def categories():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('categories.html')

@app.route('/about_the_developer')
def about_the_developer2():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('about_the_developer2.html')

@app.route('/profile')
def student_profile():  # قمنا بتغيير اسم الدالة هنا ليطابق الـ Endpoint المطلوبة
    if 'user' not in session: 
        return redirect(url_for('login'))
    return render_template('student_profile.html', username=session['user'])

if __name__ == '__main__':
    app.run(debug=True)
