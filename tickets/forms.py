from django import forms
from .models import Ticket, Department, RequestType, Comment


class TicketSubmissionForm(forms.ModelForm):
    """نموذج تقديم الطلب من قبل المستخدمين"""
    
    class Meta:
        model = Ticket
        fields = [
            'full_name',
            'email',
            'phone',
            'department',
            'request_type',
            'description',
            'priority',
            'attachment'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الاسم الكامل',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@alkunuz.edu.iq',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '07XX XXX XXXX',
                'dir': 'ltr'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'request_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'اكتب وصفاً تفصيلياً للمشكلة أو الطلب...',
                'required': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            })
        }
        labels = {
            'full_name': 'الاسم الكامل',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الهاتف (اختياري)',
            'department': 'القسم',
            'request_type': 'نوع الطلب',
            'description': 'وصف المشكلة أو الطلب',
            'priority': 'الأولوية',
            'attachment': 'ملف مرفق (اختياري)'
        }
        help_texts = {
            'attachment': 'يمكنك إرفاق ملف (PDF, Word, أو صورة) بحجم أقصى 5 ميجابايت',
            'phone': 'رقم الهاتف للتواصل السريع'
        }
    
    def clean_attachment(self):
        """التحقق من حجم الملف المرفق"""
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('حجم الملف يجب أن لا يتجاوز 5 ميجابايت')
        return attachment


class CommentForm(forms.ModelForm):
    """نموذج إضافة تعليق"""
    
    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'comment_text', 'attachment']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسمك',
                'required': True
            }),
            'author_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'بريدك الإلكتروني'
            }),
            'comment_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اكتب تعليقك هنا...',
                'required': True
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            })
        }
        labels = {
            'author_name': 'الاسم',
            'author_email': 'البريد الإلكتروني',
            'comment_text': 'التعليق',
            'attachment': 'مرفق (اختياري)'
        }


class TicketFilterForm(forms.Form):
    """نموذج فلترة الطلبات"""
    
    status = forms.ChoiceField(
        choices=[('', 'الكل')] + list(Ticket.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الحالة'
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'الكل')] + list(Ticket.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='الأولوية'
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='الكل',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='القسم'
    )
    
    request_type = forms.ModelChoiceField(
        queryset=RequestType.objects.all(),
        required=False,
        empty_label='الكل',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='نوع الطلب'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ابحث في الاسم أو البريد الإلكتروني...'
        }),
        label='بحث'
    )
