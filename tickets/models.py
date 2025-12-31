from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta


class Department(models.Model):
    """نموذج الأقسام"""
    name = models.CharField(max_length=200, verbose_name="اسم القسم")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    head_of_department = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="رئيس القسم"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="الهاتف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_total_tickets(self):
        """حساب إجمالي الطلبات للقسم"""
        return self.tickets.count()
    
    def get_pending_tickets(self):
        """حساب الطلبات المعلقة"""
        return self.tickets.filter(status='pending').count()


class RequestType(models.Model):
    """نموذج أنواع الطلبات"""
    name = models.CharField(max_length=200, verbose_name="نوع الطلب")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="أيقونة",
        help_text="اسم أيقونة Bootstrap Icons (مثل: bi-laptop)"
    )
    color = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="اللون",
        help_text="اللون بصيغة hex (مثل: #FF5733)"
    )
    estimated_time = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="الوقت المتوقع (بالساعات)",
        help_text="الوقت المتوقع لإنجاز هذا النوع من الطلبات"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "نوع طلب"
        verbose_name_plural = "أنواع الطلبات"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_total_tickets(self):
        """حساب إجمالي الطلبات لهذا النوع"""
        return self.tickets.count()


class Ticket(models.Model):
    """نموذج الطلب الرئيسي"""
    
    # خيارات الأولوية
    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),  # أضفنا أولوية عاجلة
    ]
    
    # خيارات الحالة
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('in_progress', 'قيد التنفيذ'),
        ('on_hold', 'معلق مؤقتاً'),  # حالة جديدة
        ('resolved', 'تم الحل'),
        ('rejected', 'مرفوض'),
        ('closed', 'مغلق'),  # حالة جديدة
    ]
    
    # الحقول الأساسية
    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,  # إضافة null=True
        verbose_name="رقم الطلب",
        help_text="يتم إنشاؤه تلقائياً"
    )
    full_name = models.CharField(max_length=200, verbose_name="الاسم الكامل")
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        verbose_name="القسم",
        related_name='tickets'
    )
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="رقم الهاتف"
    )
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
    
    # حقول جديدة
    is_urgent = models.BooleanField(
        default=False,
        verbose_name="طلب عاجل",
        help_text="حدد إذا كان الطلب يحتاج معالجة عاجلة"
    )
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="تاريخ الاستحقاق",
        help_text="الموعد النهائي لإنجاز الطلب"
    )
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="تاريخ الحل"
    )
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات الحل",
        help_text="تفاصيل حول كيفية حل الطلب"
    )
    views_count = models.IntegerField(
        default=0,
        verbose_name="عدد المشاهدات"
    )
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
        ]
    
    def save(self, *args, **kwargs):
        """حفظ مخصص لإنشاء رقم الطلب تلقائياً"""
        if not self.ticket_number:
            # إنشاء رقم طلب فريد بصيغة TKT-YYYYMMDD-XXX
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_ticket = Ticket.objects.filter(
                ticket_number__startswith=f'TKT-{date_str}'
            ).order_by('-ticket_number').first()
            
            if last_ticket:
                last_num = int(last_ticket.ticket_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.ticket_number = f'TKT-{date_str}-{new_num:03d}'
        
        # تحديث تاريخ الحل تلقائياً
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ticket_number} - {self.full_name}"
    
    def get_status_display_color(self):
        """إرجاع لون CSS حسب الحالة"""
        colors = {
            'pending': 'warning',
            'in_progress': 'info',
            'on_hold': 'secondary',
            'resolved': 'success',
            'rejected': 'danger',
            'closed': 'dark',
        }
        return colors.get(self.status, 'secondary')
    
    def get_priority_display_color(self):
        """إرجاع لون CSS حسب الأولوية"""
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'danger',
        }
        return colors.get(self.priority, 'secondary')
    
    def get_age(self):
        """حساب عمر الطلب بالأيام"""
        return (timezone.now() - self.created_at).days
    
    def get_resolution_time(self):
        """حساب وقت الحل بالساعات"""
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return round(delta.total_seconds() / 3600, 1)
        return None
    
    def is_overdue(self):
        """التحقق من تجاوز الموعد النهائي"""
        if self.due_date and self.status not in ['resolved', 'closed', 'rejected']:
            return timezone.now() > self.due_date
        return False


class Comment(models.Model):
    """نموذج التعليقات على الطلبات"""
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="الطلب"
    )
    author_name = models.CharField(
        max_length=200,
        verbose_name="اسم الكاتب"
    )
    author_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="البريد الإلكتروني"
    )
    author_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ticket_comments',
        verbose_name="المستخدم"
    )
    comment_text = models.TextField(verbose_name="التعليق")
    is_internal = models.BooleanField(
        default=False,
        verbose_name="ملاحظة داخلية",
        help_text="التعليقات الداخلية لا تظهر للعموم"
    )
    attachment = models.FileField(
        upload_to='comment_attachments/',
        blank=True,
        null=True,
        verbose_name="مرفق"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تعليق"
        verbose_name_plural = "التعليقات"
        ordering = ['created_at']
    
    def __str__(self):
        return f"تعليق من {self.author_name} على {self.ticket.ticket_number}"


class Notification(models.Model):
    """نموذج الإشعارات"""
    
    NOTIFICATION_TYPES = [
        ('new_ticket', 'طلب جديد'),
        ('status_change', 'تغيير حالة'),
        ('new_comment', 'تعليق جديد'),
        ('assigned', 'تم التعيين'),
        ('due_soon', 'موعد قريب'),
        ('overdue', 'متأخر'),
    ]
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="الطلب"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name="نوع الإشعار"
    )
    recipient_email = models.EmailField(verbose_name="المستلم")
    recipient_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='notifications',
        verbose_name="المستخدم المستلم"
    )
    title = models.CharField(max_length=200, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    is_sent = models.BooleanField(default=False, verbose_name="تم الإرسال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="تاريخ القراءة"
    )
    
    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient_email}"
    
    def mark_as_read(self):
        """تعليم الإشعار كمقروء"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class ActivityLog(models.Model):
    """نموذج سجل الأنشطة"""
    
    ACTION_TYPES = [
        ('created', 'تم الإنشاء'),
        ('updated', 'تم التحديث'),
        ('status_changed', 'تغيير الحالة'),
        ('priority_changed', 'تغيير الأولوية'),
        ('assigned', 'تم التعيين'),
        ('commented', 'تم التعليق'),
        ('resolved', 'تم الحل'),
        ('rejected', 'تم الرفض'),
        ('closed', 'تم الإغلاق'),
    ]
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name="الطلب"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="نوع الإجراء"
    )
    performed_by_name = models.CharField(
        max_length=200,
        verbose_name="نفذ بواسطة"
    )
    performed_by_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='activity_logs',
        verbose_name="المستخدم"
    )
    description = models.TextField(verbose_name="الوصف")
    old_value = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="القيمة القديمة"
    )
    new_value = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="القيمة الجديدة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="التاريخ")
    
    class Meta:
        verbose_name = "سجل نشاط"
        verbose_name_plural = "سجلات الأنشطة"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action_type} - {self.ticket.ticket_number}"


class Rating(models.Model):
    """نموذج تقييم الطلبات المحلولة"""
    
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name="الطلب"
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="التقييم",
        help_text="من 1 إلى 5 نجوم"
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name="الملاحظات"
    )
    rated_by_name = models.CharField(
        max_length=200,
        verbose_name="المقيّم"
    )
    rated_by_email = models.EmailField(verbose_name="البريد الإلكتروني")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقييم")
    
    class Meta:
        verbose_name = "تقييم"
        verbose_name_plural = "التقييمات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"تقييم {self.score}/5 - {self.ticket.ticket_number}"
    
    def get_stars_display(self):
        """عرض النجوم"""
        return '⭐' * self.score
