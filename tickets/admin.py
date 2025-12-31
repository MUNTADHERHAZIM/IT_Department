from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib.auth.models import User
from .models import (
    Department, 
    RequestType, 
    Ticket, 
    Comment, 
    Notification, 
    ActivityLog, 
    Rating
)


# ============= Comment Inline =============
class CommentInline(admin.TabularInline):
    """عرض التعليقات داخل صفحة الطلب"""
    model = Comment
    extra = 0
    fields = ['author_name', 'comment_text', 'is_internal', 'created_at']
    readonly_fields = ['created_at']
    can_delete = True
    max_num = 50


# ============= ActivityLog Inline =============
class ActivityLogInline(admin.TabularInline):
    """عرض سجل الأنشطة داخل صفحة الطلب"""
    model = ActivityLog
    extra = 0
    fields = ['action_type', 'performed_by_name', 'description', 'created_at']
    readonly_fields = ['action_type', 'performed_by_name', 'description', 'created_at']
    can_delete = False
    max_num = 20
    
    def has_add_permission(self, request, obj=None):
        return False


# ============= Department Admin =============
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """إدارة الأقسام المحسنة"""
    list_display = [
        'name', 
        'head_of_department',
        'email',
        'phone',
        'total_tickets_display',
        'pending_tickets_display',
        'is_active_badge',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'head_of_department', 'email']
    list_per_page = 20
    
    fieldsets = (
        ('معلومات القسم', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('معلومات الاتصال', {
            'fields': ('head_of_department', 'email', 'phone')
        }),
        ('إحصائيات', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    @admin.display(description='إجمالي الطلبات')
    def total_tickets_display(self, obj):
        """عرض إجمالي الطلبات"""
        count = obj.get_total_tickets()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            count
        )
    
    @admin.display(description='طلبات معلقة')
    def pending_tickets_display(self, obj):
        """عرض الطلبات المعلقة"""
        count = obj.get_pending_tickets()
        color = '#dc3545' if count > 5 else '#ffc107'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color, count
        )
    
    @admin.display(description='الحالة')
    def is_active_badge(self, obj):
        """عرض حالة النشاط"""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745;">✓ نشط</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ غير نشط</span>'
        )


# ============= RequestType Admin =============
@admin.register(RequestType)
class RequestTypeAdmin(admin.ModelAdmin):
    """إدارة أنواع الطلبات المحسنة"""
    list_display = [
        'name',
        'icon_display',
        'color_display',
        'estimated_time',
        'total_tickets_display',
        'is_active_badge',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_per_page = 20
    
    fieldsets = (
        ('معلومات نوع الطلب', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('تخصيص العرض', {
            'fields': ('icon', 'color'),
            'description': 'يمكنك تخصيص الأيقونة واللون لهذا النوع من الطلبات'
        }),
        ('الوقت المتوقع', {
            'fields': ('estimated_time',),
        }),
    )
    
    readonly_fields = ['created_at']
    
    @admin.display(description='الأيقونة')
    def icon_display(self, obj):
        """عرض الأيقونة"""
        if obj.icon:
            return format_html(
                '<i class="bi {}" style="font-size: 20px;"></i>',
                obj.icon
            )
        return '-'
    
    @admin.display(description='اللون')
    def color_display(self, obj):
        """عرض اللون"""
        if obj.color:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; '
                'border: 1px solid #ddd; border-radius: 3px;"></div>',
                obj.color
            )
        return '-'
    
    @admin.display(description='عدد الطلبات')
    def total_tickets_display(self, obj):
        """عرض إجمالي الطلبات"""
        count = obj.get_total_tickets()
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            count
        )
    
    @admin.display(description='الحالة')
    def is_active_badge(self, obj):
        """عرض حالة النشاط"""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745;">✓ نشط</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ غير نشط</span>'
        )


# ============= Ticket Admin =============
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """إدارة الطلبات الاحترافية المتطورة"""
    list_display = [
        'ticket_number',
        'full_name',
        'department',
        'request_type',
        'priority_badge',
        'status_badge',
        'is_urgent_badge',
        'assigned_to',
        'age_display',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'priority',
        'is_urgent',
        'department',
        'request_type',
        'assigned_to',
        ('created_at', admin.DateFieldListFilter),
        ('due_date', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'ticket_number',
        'full_name',
        'email',
        'phone',
        'description',
        'internal_notes'
    ]
    
    list_editable = ['assigned_to']
    readonly_fields = [
        'ticket_number',
        'created_at',
        'updated_at',
        'resolved_at',
        'views_count',
        'age_display',
        'resolution_time_display',
        'is_overdue_display'
    ]
    
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    # استخدام Inlines
    inlines = [CommentInline, ActivityLogInline]
    
    fieldsets = (
        ('معلومات الطلب الأساسية', {
            'fields': (
                'ticket_number',
                'full_name',
                'email',
                'phone',
                'department',
                'request_type'
            )
        }),
        ('تفاصيل الطلب', {
            'fields': (
                'description',
                'priority',
                'is_urgent',
                'attachment'
            )
        }),
        ('الإدارة والمتابعة', {
            'fields': (
                'status',
                'assigned_to',
                'due_date',
                'internal_notes'
            ),
            'classes': ('wide',)
        }),
        ('حل الطلب', {
            'fields': (
                'resolution_notes',
                'resolved_at'
            ),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية', {
            'fields': (
                'views_count',
                'age_display',
                'resolution_time_display',
                'is_overdue_display',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Custom Actions
    actions = [
        'mark_as_pending',
        'mark_as_in_progress',
        'mark_as_on_hold',
        'mark_as_resolved',
        'mark_as_rejected',
        'mark_as_closed',
        'mark_as_urgent',
        'assign_to_me',
        'export_as_csv'
    ]
    
    @admin.display(description='الأولوية')
    def priority_badge(self, obj):
        """عرض شارة ملونة للأولوية"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 15px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    
    @admin.display(description='الحالة')
    def status_badge(self, obj):
        """عرض شارة ملونة للحالة"""
        colors = {
            'pending': '#ffc107',
            'in_progress': '#17a2b8',
            'on_hold': '#6c757d',
            'resolved': '#28a745',
            'rejected': '#dc3545',
            'closed': '#343a40',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 15px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    
    @admin.display(description='عاجل')
    def is_urgent_badge(self, obj):
        """عرض علامة الاستعجال"""
        if obj.is_urgent:
            return format_html(
                '<span style="color: #dc3545; font-size: 18px;" title="عاجل">🚨</span>'
            )
        return '-'
    
    @admin.display(description='العمر')
    def age_display(self, obj):
        """عرض عمر الطلب"""
        age = obj.get_age()
        color = '#28a745' if age < 2 else '#ffc107' if age < 5 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} يوم</span>',
            color, age
        )
    
    @admin.display(description='وقت الحل')
    def resolution_time_display(self, obj):
        """عرض وقت الحل"""
        time = obj.get_resolution_time()
        if time:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} ساعة</span>',
                time
            )
        return '-'
    
    @admin.display(description='حالة الموعد')
    def is_overdue_display(self, obj):
        """عرض حالة التأخير"""
        if obj.is_overdue():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ متأخر</span>'
            )
        elif obj.due_date:
            return format_html(
                '<span style="color: #28a745;">✓ في الموعد</span>'
            )
        return '-'
    
    # ============= Custom Actions =============
    
    def mark_as_pending(self, request, queryset):
        """تعيين الحالة إلى قيد المراجعة"""
        updated = queryset.update(status='pending')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "قيد المراجعة"')
    mark_as_pending.short_description = '🔄 تعيين كـ "قيد المراجعة"'
    
    def mark_as_in_progress(self, request, queryset):
        """تعيين الحالة إلى قيد التنفيذ"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "قيد التنفيذ"')
    mark_as_in_progress.short_description = '⚙️ تعيين كـ "قيد التنفيذ"'
    
    def mark_as_on_hold(self, request, queryset):
        """تعيين الحالة إلى معلق مؤقتاً"""
        updated = queryset.update(status='on_hold')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "معلق مؤقتاً"')
    mark_as_on_hold.short_description = '⏸️ تعيين كـ "معلق مؤقتاً"'
    
    def mark_as_resolved(self, request, queryset):
        """تعيين الحالة إلى تم الحل"""
        from django.utils import timezone
        updated = queryset.filter(resolved_at__isnull=True).update(
            status='resolved',
            resolved_at=timezone.now()
        )
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "تم الحل"')
    mark_as_resolved.short_description = '✅ تعيين كـ "تم الحل"'
    
    def mark_as_rejected(self, request, queryset):
        """تعيين الحالة إلى مرفوض"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "مرفوض"')
    mark_as_rejected.short_description = '❌ تعيين كـ "مرفوض"'
    
    def mark_as_closed(self, request, queryset):
        """تعيين الحالة إلى مغلق"""
        updated = queryset.update(status='closed')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "مغلق"')
    mark_as_closed.short_description = '🔒 تعيين كـ "مغلق"'
    
    def mark_as_urgent(self, request, queryset):
        """تعليم الطلبات كعاجلة"""
        updated = queryset.update(is_urgent=True, priority='urgent')
        self.message_user(request, f'تم تعليم {updated} طلب كطلبات عاجلة')
    mark_as_urgent.short_description = '🚨 تعليم كعاجل'
    
    def assign_to_me(self, request, queryset):
        """تعيين الطلبات للمستخدم الحالي"""
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f'تم تعيين {updated} طلب لك')
    assign_to_me.short_description = '👤 تعيين لي'
    
    def export_as_csv(self, request, queryset):
        """تصدير الطلبات المحددة كملف CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="tickets_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'رقم الطلب', 'الاسم', 'البريد', 'القسم', 'نوع الطلب',
            'الأولوية', 'الحالة', 'المعين إلى', 'تاريخ الإنشاء'
        ])
        
        for ticket in queryset:
            writer.writerow([
                ticket.ticket_number,
                ticket.full_name,
                ticket.email,
                ticket.department.name,
                ticket.request_type.name,
                ticket.get_priority_display(),
                ticket.get_status_display(),
                ticket.assigned_to.username if ticket.assigned_to else 'غير معين',
                ticket.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        self.message_user(request, f'تم تصدير {queryset.count()} طلب بنجاح')
        return response
    
    export_as_csv.short_description = '📥 تصدير كـ CSV'


# ============= Comment Admin =============
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """إدارة التعليقات"""
    list_display = [
        'ticket',
        'author_name',
        'comment_preview',
        'is_internal_badge',
        'created_at'
    ]
    list_filter = ['is_internal', 'created_at']
    search_fields = ['author_name', 'author_email', 'comment_text']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    @admin.display(description='التعليق')
    def comment_preview(self, obj):
        """عرض معاينة التعليق"""
        preview = obj.comment_text[:50] + '...' if len(obj.comment_text) > 50 else obj.comment_text
        return preview
    
    @admin.display(description='النوع')
    def is_internal_badge(self, obj):
        """عرض نوع التعليق"""
        if obj.is_internal:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 10px;">داخلي</span>'
            )
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; '
            'border-radius: 10px; font-size: 10px;">عام</span>'
        )


# ============= Notification Admin =============
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """إدارة الإشعارات"""
    list_display = [
        'title',
        'notification_type_badge',
        'recipient_email',
        'ticket',
        'is_read_badge',
        'is_sent_badge',
        'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'is_sent', 'created_at']
    search_fields = ['title', 'message', 'recipient_email']
    readonly_fields = ['created_at', 'read_at']
    list_per_page = 30
    
    actions = ['mark_as_read', 'mark_as_sent']
    
    @admin.display(description='النوع')
    def notification_type_badge(self, obj):
        """عرض نوع الإشعار"""
        colors = {
            'new_ticket': '#17a2b8',
            'status_change': '#ffc107',
            'new_comment': '#28a745',
            'assigned': '#6f42c1',
            'due_soon': '#fd7e14',
            'overdue': '#dc3545',
        }
        color = colors.get(obj.notification_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_notification_type_display()
        )
    
    @admin.display(description='القراءة')
    def is_read_badge(self, obj):
        """عرض حالة القراءة"""
        if obj.is_read:
            return format_html('<span style="color: #28a745;">✓ مقروء</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ غير مقروء</span>')
    
    @admin.display(description='الإرسال')
    def is_sent_badge(self, obj):
        """عرض حالة الإرسال"""
        if obj.is_sent:
            return format_html('<span style="color: #28a745;">✓ تم الإرسال</span>')
        return format_html('<span style="color: #ffc107;">⏳ معلق</span>')
    
    def mark_as_read(self, request, queryset):
        """تعليم كمقروء"""
        from django.utils import timezone
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'تم تعليم {updated} إشعار كمقروء')
    mark_as_read.short_description = '✓ تعليم كمقروء'
    
    def mark_as_sent(self, request, queryset):
        """تعليم كمرسل"""
        updated = queryset.update(is_sent=True)
        self.message_user(request, f'تم تعليم {updated} إشعار كمرسل')
    mark_as_sent.short_description = '📧 تعليم كمرسل'


# ============= ActivityLog Admin =============
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """إدارة سجلات الأنشطة"""
    list_display = [
        'ticket',
        'action_type_badge',
        'performed_by_name',
        'description_preview',
        'created_at'
    ]
    list_filter = ['action_type', 'created_at']
    search_fields = ['ticket__ticket_number', 'performed_by_name', 'description']
    readonly_fields = ['created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """منع الإضافة اليدوية"""
        return False
    
    @admin.display(description='الإجراء')
    def action_type_badge(self, obj):
        """عرض نوع الإجراء"""
        colors = {
            'created': '#17a2b8',
            'updated': '#ffc107',
            'status_changed': '#6f42c1',
            'priority_changed': '#fd7e14',
            'assigned': '#20c997',
            'commented': '#28a745',
            'resolved': '#28a745',
            'rejected': '#dc3545',
            'closed': '#343a40',
        }
        color = colors.get(obj.action_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_action_type_display()
        )
    
    @admin.display(description='الوصف')
    def description_preview(self, obj):
        """عرض معاينة الوصف"""
        preview = obj.description[:60] + '...' if len(obj.description) > 60 else obj.description
        return preview


# ============= Rating Admin =============
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """إدارة التقييمات"""
    list_display = [
        'ticket',
        'stars_display',
        'rated_by_name',
        'feedback_preview',
        'created_at'
    ]
    list_filter = ['score', 'created_at']
    search_fields = ['ticket__ticket_number', 'rated_by_name', 'feedback']
    readonly_fields = ['created_at']
    list_per_page = 30
    
    @admin.display(description='التقييم')
    def stars_display(self, obj):
        """عرض النجوم"""
        stars = '⭐' * obj.score
        color = '#ffc107' if obj.score >= 4 else '#fd7e14' if obj.score >= 3 else '#dc3545'
        return format_html(
            '<span style="font-size: 16px; color: {};">{} ({}/5)</span>',
            color, stars, obj.score
        )
    
    @admin.display(description='الملاحظات')
    def feedback_preview(self, obj):
        """عرض معاينة الملاحظات"""
        if obj.feedback:
            preview = obj.feedback[:50] + '...' if len(obj.feedback) > 50 else obj.feedback
            return preview
        return '-'


# ============= تخصيص الإدارة =============
admin.site.site_header = '🎓 نظام إدارة طلبات قسم الحاسبة الإلكترونية - جامعة الكنوز'
admin.site.site_title = 'إدارة الطلبات'
admin.site.index_title = 'لوحة التحكم الرئيسية'
