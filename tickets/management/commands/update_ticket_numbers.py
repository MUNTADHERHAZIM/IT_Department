"""
Management command لتحديث أرقام الطلبات الموجودة
"""
from django.core.management.base import BaseCommand
from tickets.models import Ticket
from datetime import datetime


class Command(BaseCommand):
    help = 'تحديث أرقام الطلبات الموجودة التي ليس لديها أرقام'

    def handle(self, *args, **options):
        # الحصول على جميع الطلبات بدون رقم
        tickets_without_number = Ticket.objects.filter(ticket_number__isnull=True)
        count = tickets_without_number.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('جميع الطلبات لديها أرقام بالفعل ✓')
            )
            return
        
        self.stdout.write(f'تم العثور على {count} طلب بدون رقم')
        self.stdout.write('جاري تحديث الأرقام...')
        
        updated = 0
        for ticket in tickets_without_number:
            # إنشاء رقم طلب بناءً على تاريخ الإنشاء
            date_str = ticket.created_at.strftime('%Y%m%d')
            
            # البحث عن آخر رقم في نفس اليوم
            last_ticket = Ticket.objects.filter(
                ticket_number__startswith=f'TKT-{date_str}'
            ).order_by('-ticket_number').first()
            
            if last_ticket and last_ticket.ticket_number:
                last_num = int(last_ticket.ticket_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            ticket.ticket_number = f'TKT-{date_str}-{new_num:03d}'
            ticket.save()
            updated += 1
            
            if updated % 10 == 0:
                self.stdout.write(f'  تم تحديث {updated}/{count}...')
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ تم تحديث {updated} طلب بنجاح!')
        )
