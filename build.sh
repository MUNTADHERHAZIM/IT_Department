#!/usr/bin/env bash
# exit on error
set -o errexit

# تثبيت المتطلبات
pip install -r requirements.txt

# جمع الملفات الثابتة
python manage.py collectstatic --no-input

# تطبيق الهجرات
python manage.py migrate

# تحميل البيانات الأولية
python manage.py load_initial_data
