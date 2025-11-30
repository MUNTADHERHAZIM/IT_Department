from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Department(models.Model):
    """نموذج الأقسام"""
    name = models.CharField(max_length=200, verbose_name="اسم القسم")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ['name']

    def __str__(self):
        return self.name


class RequestType(models.Model):
    """نموذج أنواع الطلبات"""
    name = models.CharField(max_length=200, verbose_name="نوع الطلب")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "نوع طلب"
        verbose_name_plural = "أنواع الطلبات"
        ordering = ['name']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """نموذج الطلب الرئيسي"""
    
    # خيارات الأولوية
    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
    ]
    
    # خيارات الحالة
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('in_progress', 'قيد التنفيذ'),
        ('resolved', 'تم الحل'),
        ('rejected', 'مرفوض'),
    ]
    
    # الحقول الأساسية
    full_name = models.CharField(max_length=200, verbose_name="الاسم الكامل")
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        verbose_name="القسم",
        related_name='tickets'
    )
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    request_type = models.ForeignKey(
        RequestType, 
        on_delete=models.CASCADE, 
        verbose_name="نوع الطلب",
        related_name='tickets'
    )
    description = models.TextField(verbose_name="وصف المشكلة")
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name="الأولوية"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name="الحالة"
    )
    attachment = models.FileField(
        upload_to='ticket_attachments/', 
        blank=True, 
        null=True,
        verbose_name="ملف مرفق"
    )
    
    # إدارة الطلب
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        verbose_name="معين إلى",
        related_name='assigned_tickets'
    )
    internal_notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name="ملاحظات داخلية"
    )
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.request_type.name}"
    
    def get_status_display_color(self):
        """إرجاع لون CSS حسب الحالة"""
        colors = {
            'pending': 'warning',
            'in_progress': 'info',
            'resolved': 'success',
            'rejected': 'danger',
        }
        return colors.get(self.status, 'secondary')
    
    def get_priority_display_color(self):
        """إرجاع لون CSS حسب الأولوية"""
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
        }
        return colors.get(self.priority, 'secondary')
