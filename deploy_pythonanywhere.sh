#!/bin/bash
# سكريبت النشر السريع على PythonAnywhere

echo "🚀 بدء عملية النشر على PythonAnywhere..."
echo ""

# 1. تفعيل البيئة الافتراضية
echo "✅ تفعيل البيئة الافتراضية..."
source venv/bin/activate

# 2. تشغيل Migrations
echo "✅ تشغيل migrations..."
python manage.py makemigrations
python manage.py migrate

# 3. جمع الملفات الثابتة
echo "✅ جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

# 4. إنشاء superuser (اختياري - علّق هذا السطر بعد أول مرة)
echo "✅ إنشاء حساب المدير..."
echo "⚠️  أدخل بيانات المدير:"
python manage.py createsuperuser

echo ""
echo "✅ تم الانتهاء! الآن:"
echo "   1. اذهب إلى Web tab في PythonAnywhere"
echo "   2. اضغط على زر Reload"
echo "   3. افتح الموقع: https://itdepartment.pythonanywhere.com/"
echo ""
