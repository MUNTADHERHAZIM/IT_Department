# نظام إدارة طلبات الحاسبة الإلكترونية
# جامعة الكنوز

from django.core.management.base import BaseCommand
from tickets.models import Department, RequestType


class Command(BaseCommand):
    help = 'تحميل البيانات الأولية للنظام'

    def handle(self, *args, **options):
        self.stdout.write('جاري تحميل البيانات الأولية...')

        # إضافة الأقسام
        departments = [
            ('قسم الحاسبة الإلكترونية', 'القسم الرئيسي'),
            ('قسم تقنيات الحاسوب', 'قسم التقنيات'),
            ('قسم أنظمة المعلومات', 'قسم الأنظمة'),
            ('قسم البرمجيات', 'قسم هندسة البرمجيات'),
            ('إدارة الكلية', 'الإدارة العامة'),
        ]

        for name, desc in departments:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ تم إضافة القسم: {name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- القسم موجود مسبقاً: {name}')
                )

        # إضافة أنواع الطلبات
        request_types = [
            ('دعم فني', 'طلبات الدعم الفني العام'),
            ('تنصيب برنامج', 'طلب تنصيب برامج جديدة'),
            ('مشكلة عتادية', 'مشاكل الأجهزة والعتاد'),
            ('صيانة', 'طلبات الصيانة الدورية'),
            ('استفسار', 'استفسارات عامة'),
            ('طلب جديد', 'طلب نظام أو خدمة جديدة'),
            ('تحديث نظام', 'طلبات تحديث الأنظمة'),
            ('تدريب', 'طلبات تدريب على أنظمة أو برامج'),
        ]

        for name, desc in request_types:
            req_type, created = RequestType.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ تم إضافة نوع الطلب: {name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- نوع الطلب موجود مسبقاً: {name}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n✅ تم تحميل البيانات الأولية بنجاح!')
        )
