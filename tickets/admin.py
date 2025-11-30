from django.contrib import admin
from .models import Department, RequestType, Ticket


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """إدارة الأقسام"""
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    list_per_page = 20


@admin.register(RequestType)
class RequestTypeAdmin(admin.ModelAdmin):
    """إدارة أنواع الطلبات"""
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    list_per_page = 20


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """إدارة الطلبات"""
    list_display = [
        'id',
        'full_name', 
        'department', 
        'request_type', 
        'priority_badge',
        'status_badge',
        'assigned_to',
        'created_at'
    ]
    list_filter = [
        'status', 
        'priority', 
        'department', 
        'request_type',
        'created_at'
    ]
    search_fields = [
        'full_name', 
        'email', 
        'description',
        'internal_notes'
    ]
    list_editable = ['assigned_to']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': (
                'full_name', 
                'email', 
                'department', 
                'request_type'
            )
        }),
        ('تفاصيل الطلب', {
            'fields': (
                'description', 
                'priority', 
                'attachment'
            )
        }),
        ('الإدارة', {
            'fields': (
                'status', 
                'assigned_to', 
                'internal_notes'
            )
        }),
        ('التواريخ', {
            'fields': (
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def priority_badge(self, obj):
        """عرض شارة ملونة للأولوية"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return f'<span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 3px;">{obj.get_priority_display()}</span>'
    
    priority_badge.short_description = 'الأولوية'
    priority_badge.allow_tags = True
    
    def status_badge(self, obj):
        """عرض شارة ملونة للحالة"""
        colors = {
            'pending': '#ffc107',
            'in_progress': '#17a2b8',
            'resolved': '#28a745',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return f'<span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 3px;">{obj.get_status_display()}</span>'
    
    status_badge.short_description = 'الحالة'
    status_badge.allow_tags = True
    
    actions = ['mark_as_in_progress', 'mark_as_resolved', 'mark_as_rejected']
    
    def mark_as_in_progress(self, request, queryset):
        """تعيين الحالة إلى قيد التنفيذ"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "قيد التنفيذ"')
    
    mark_as_in_progress.short_description = 'تعيين كـ "قيد التنفيذ"'
    
    def mark_as_resolved(self, request, queryset):
        """تعيين الحالة إلى تم الحل"""
        updated = queryset.update(status='resolved')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "تم الحل"')
    
    mark_as_resolved.short_description = 'تعيين كـ "تم الحل"'
    
    def mark_as_rejected(self, request, queryset):
        """تعيين الحالة إلى مرفوض"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'تم تحديث {updated} طلب إلى حالة "مرفوض"')
    
    mark_as_rejected.short_description = 'تعيين كـ "مرفوض"'


# تخصيص عنوان الإدارة
admin.site.site_header = 'نظام إدارة الطلبات - جامعة الكنوز'
admin.site.site_title = 'إدارة الطلبات'
admin.site.index_title = 'لوحة التحكم'
