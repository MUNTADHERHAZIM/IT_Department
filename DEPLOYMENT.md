# دليل النشر - نظام إدارة الطلبات

## 🚀 خيارات النشر

### الخيار 1: Render (مُوصى به - مجاني)

#### الخطوات:

1. **إنشاء حساب على Render**
   - انتقل إلى https://render.com
   - سجل حساب جديد (مجاني)

2. **رفع المشروع إلى GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

3. **إنشاء PostgreSQL Database**
   - من لوحة Render، اضغط **New** → **PostgreSQL**
   - اسم قاعدة البيانات: `kunuz_tickets_db`
   - اختر الخطة المجانية
   - اضغط **Create Database**
   - احفظ `Internal Database URL`

4. **إنشاء Web Service**
   - من لوحة Render، اضغط **New** → **Web Service**
   - اربط حساب GitHub
   - اختر المستودع (repository)
   - الإعدادات:
     - **Name**: `kunuz-tickets`
     - **Region**: اختر الأقرب
     - **Branch**: `main`
     - **Runtime**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn kunuz_tickets.wsgi:application`

5. **إضافة المتغيرات البيئية (Environment Variables)**
   في قسم **Environment**:
   ```
   SECRET_KEY = أي نص عشوائي طويل (استخدم مولد)
   DEBUG = False
   ALLOWED_HOSTS = your-app-name.onrender.com
   DATABASE_URL = [الصق Internal Database URL من الخطوة 3]
   ```

6. **نشر التطبيق**
   - اضغط **Create Web Service**
   - انتظر حتى ينتهي النشر (3-5 دقائق)
   - افتح الرابط: `https://your-app-name.onrender.com`

7. **إنشاء مستخدم إداري**
   - من لوحة Render → Shell
   ```bash
   python manage.py createsuperuser
   ```

8. **إضافة البيانات الأولية**
   - ادخل إلى `/admin/`
   - أضف الأقسام وأنواع الطلبات

---

### الخيار 2: PythonAnywhere

#### الخطوات:

1. **إنشاء حساب**
   - انتقل إلى https://www.pythonanywhere.com
   - سجل حساب مجاني

2. **رفع الملفات**
   - من لوحة التحكم → **Files**
   - ارفع جميع ملفات المشروع
   - أو استخدم Git:
   ```bash
   git clone YOUR_GITHUB_REPO_URL
   ```

3. **إنشاء Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 kunuz_env
   pip install -r requirements.txt
   ```

4. **إعداد Web App**
   - **Web** → **Add a new web app**
   - اختر **Manual configuration**
   - اختر **Python 3.10**

5. **تكوين WSGI**
   - عدّل ملف `/var/www/your_username_pythonanywhere_com_wsgi.py`:
   ```python
   import sys
   import os
   
   path = '/home/yourusername/نظام القسم'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['DJANGO_SETTINGS_MODULE'] = 'kunuz_tickets.settings'
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

6. **إعداد Static Files**
   - في قسم **Static files**:
   - URL: `/static/`
   - Directory: `/home/yourusername/نظام القسم/staticfiles/`

7. **جمع الملفات الثابتة**
   ```bash
   python manage.py collectstatic
   ```

8. **تطبيق الهجرات**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

9. **إعادة تحميل التطبيق**
   - من **Web** → اضغط **Reload**

---

### الخيار 3: Railway

#### الخطوات السريعة:

1. انتقل إلى https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. اختر المستودع
4. أضف **PostgreSQL** من **Add a Service**
5. أضف المتغيرات البيئية
6. سيتم النشر تلقائياً

---

## 🔒 إعدادات الأمان للإنتاج

### 1. توليد SECRET_KEY جديد
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. إنشاء ملف .env
- انسخ `.env.example` إلى `.env`
- املأ القيم الحقيقية
- **لا ترفع** ملف `.env` إلى GitHub!

### 3. تحديث .gitignore
تأكد من وجود:
```
.env
*.pyc
db.sqlite3
media/
staticfiles/
```

---

## ✅ قائمة التحقق قبل النشر

- [ ] تحديث `SECRET_KEY` بقيمة عشوائية آمنة
- [ ] تعيين `DEBUG = False`
- [ ] تحديث `ALLOWED_HOSTS`
- [ ] إعداد قاعدة بيانات PostgreSQL
- [ ] جمع الملفات الثابتة: `python manage.py collectstatic`
- [ ] تطبيق الهجرات: `python manage.py migrate`
- [ ] إنشاء مستخدم إداري
- [ ] إضافة البيانات الأولية
- [ ] اختبار جميع الصفحات
- [ ] إعداد البريد الإلكتروني (اختياري)
- [ ] إعداد نسخ احتياطي للبيانات

---

## 📧 إعداد البريد الإلكتروني (Gmail)

1. **تفعيل التحقق بخطوتين** على حساب Gmail
2. **إنشاء App Password**:
   - Google Account → Security → 2-Step Verification → App passwords
   - اختر "Mail" و "Other (Custom name)"
   - انسخ كلمة المرور المكونة من 16 حرف

3. **تحديث .env**:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   ```

---

## 🔧 أوامر مفيدة

```bash
# جمع الملفات الثابتة
python manage.py collectstatic --no-input

# تطبيق الهجرات
python manage.py migrate

# إنشاء مستخدم إداري
python manage.py createsuperuser

# تشغيل مع gunicorn
gunicorn kunuz_tickets.wsgi:application

# التحقق من النشر
python manage.py check --deploy
```

---

## 🆘 حل المشاكل الشائعة

### مشكلة: Static files لا تظهر
```bash
python manage.py collectstatic --clear
python manage.py collectstatic --no-input
```

### مشكلة: DisallowedHost
- تأكد من إضافة النطاق الخاص بك في `ALLOWED_HOSTS`

### مشكلة: Database connection
- تحقق من صحة `DATABASE_URL`
- تأكد من تثبيت `psycopg2-binary`

---

## 📞 الدعم

للمساعدة في النشر، راجع:
- [Render Docs](https://render.com/docs)
- [PythonAnywhere Help](https://help.pythonanywhere.com)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

**المطور**: منتظر حازم ثامر  
**النظام**: نظام إدارة طلبات الحاسبة الإلكترونية - جامعة الكنوز
