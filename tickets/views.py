from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Ticket, Department, RequestType, Comment, ActivityLog
from .forms import TicketSubmissionForm, TicketFilterForm, CommentForm


def home(request):
    """الصفحة الرئيسية - تقديم طلب جديد"""
    if request.method == 'POST':
        form = TicketSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save()
            
            # إنشاء سجل نشاط
            ActivityLog.objects.create(
                ticket=ticket,
                action_type='created',
                performed_by_name=ticket.full_name,
                description=f'تم إنشاء الطلب {ticket.ticket_number}'
            )
            
            messages.success(
                request, 
                f'تم إرسال طلبك بنجاح! رقم الطلب: {ticket.ticket_number}'
            )
            return redirect('tickets:ticket_detail', pk=ticket.id)
    else:
        form = TicketSubmissionForm()
    
    # إحصائيات محسّنة
    total_tickets = Ticket.objects.count()
    pending_tickets = Ticket.objects.filter(status='pending').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    urgent_tickets = Ticket.objects.filter(is_urgent=True).exclude(
        status__in=['resolved', 'closed', 'rejected']
    ).count()
    
    # أحدث الطلبات
    recent_tickets = Ticket.objects.select_related(
        'department', 
        'request_type'
    ).order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'total_tickets': total_tickets,
        'pending_tickets': pending_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'urgent_tickets': urgent_tickets,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'tickets/home.html', context)


def ticket_list(request):
    """عرض قائمة الطلبات مع الفلاتر"""
    tickets = Ticket.objects.select_related(
        'department', 
        'request_type', 
        'assigned_to'
    ).prefetch_related('comments').annotate(
        comment_count=Count('comments')
    ).all()
    
    # تطبيق الفلاتر
    filter_form = TicketFilterForm(request.GET)
    
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        department = filter_form.cleaned_data.get('department')
        request_type = filter_form.cleaned_data.get('request_type')
        search = filter_form.cleaned_data.get('search')
        
        if status:
            tickets = tickets.filter(status=status)
        if priority:
            tickets = tickets.filter(priority=priority)
        if department:
            tickets = tickets.filter(department=department)
        if request_type:
            tickets = tickets.filter(request_type=request_type)
        if search:
            tickets = tickets.filter(
                Q(ticket_number__icontains=search) |
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(description__icontains=search)
            )
    
    # الترقيم
    paginator = Paginator(tickets, 20)  # 20 طلب في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_count': tickets.count(),
    }
    return render(request, 'tickets/ticket_list.html', context)


def ticket_detail(request, pk):
    """عرض تفاصيل طلب معين مع التعليقات"""
    ticket = get_object_or_404(
        Ticket.objects.select_related('department', 'request_type', 'assigned_to'),
        pk=pk
    )
    
    # زيادة عدد المشاهدات
    ticket.views_count += 1
    ticket.save(update_fields=['views_count'])
    
    # التعليقات العامة (ليست داخلية)
    comments = ticket.comments.filter(is_internal=False).order_by('created_at')
    
    # سجل الأنشطة
    activity_logs = ticket.activity_logs.all().order_by('-created_at')[:10]
    
    # معالجة نموذج التعليق
    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.save()
            
            # إنشاء سجل نشاط
            ActivityLog.objects.create(
                ticket=ticket,
                action_type='commented',
                performed_by_name=comment.author_name,
                description=f'أضاف تعليقاً جديداً'
            )
            
            messages.success(request, 'تم إضافة تعليقك بنجاح!')
            return redirect('tickets:ticket_detail', pk=ticket.id)
    else:
        comment_form = CommentForm()
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_count': comments.count(),
        'activity_logs': activity_logs,
        'comment_form': comment_form,
    }
    return render(request, 'tickets/ticket_detail.html', context)


def about(request):
    """صفحة حول النظام"""
    # إحصائيات متقدمة
    from django.db.models import Avg
    from django.db.models.functions import TruncDate
    
    total_tickets = Ticket.objects.count()
    departments_count = Department.objects.count()
    request_types_count = RequestType.objects.count()
    total_comments = Comment.objects.count()
    
    # متوسط التقييم
    avg_rating = Ticket.objects.filter(
        rating__isnull=False
    ).aggregate(avg=Avg('rating__score'))['avg'] or 0
    
    context = {
        'developer_name': 'منتظر حازم ثامر',
        'system_name': 'نظام إدارة طلبات الحاسبة الإلكترونية',
        'university_name': 'جامعة الكنوز',
        'departments_count': departments_count,
        'request_types_count': request_types_count,
        'total_tickets': total_tickets,
        'total_comments': total_comments,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'tickets/about.html', context)
