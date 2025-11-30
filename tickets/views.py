from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Ticket, Department, RequestType
from .forms import TicketSubmissionForm, TicketFilterForm


def home(request):
    """الصفحة الرئيسية - تقديم طلب جديد"""
    if request.method == 'POST':
        form = TicketSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save()
            messages.success(
                request, 
                f'تم إرسال طلبك بنجاح! رقم الطلب: {ticket.id}'
            )
            return redirect('tickets:ticket_detail', pk=ticket.id)
    else:
        form = TicketSubmissionForm()
    
    # إحصائيات سريعة
    total_tickets = Ticket.objects.count()
    pending_tickets = Ticket.objects.filter(status='pending').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    
    context = {
        'form': form,
        'total_tickets': total_tickets,
        'pending_tickets': pending_tickets,
        'resolved_tickets': resolved_tickets,
    }
    return render(request, 'tickets/home.html', context)


def ticket_list(request):
    """عرض قائمة الطلبات مع الفلاتر"""
    tickets = Ticket.objects.select_related(
        'department', 
        'request_type', 
        'assigned_to'
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
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(description__icontains=search)
            )
    
    # الترقيم
    paginator = Paginator(tickets, 15)  # 15 طلب في الصفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_count': tickets.count(),
    }
    return render(request, 'tickets/ticket_list.html', context)


def ticket_detail(request, pk):
    """عرض تفاصيل طلب معين"""
    ticket = get_object_or_404(
        Ticket.objects.select_related('department', 'request_type', 'assigned_to'),
        pk=pk
    )
    
    context = {
        'ticket': ticket,
    }
    return render(request, 'tickets/ticket_detail.html', context)


def about(request):
    """صفحة حول النظام"""
    context = {
        'developer_name': 'منتظر حازم ثامر',
        'system_name': 'نظام إدارة طلبات الحاسبة الإلكترونية',
        'university_name': 'جامعة الكنوز',
        'departments_count': Department.objects.count(),
        'request_types_count': RequestType.objects.count(),
        'total_tickets': Ticket.objects.count(),
    }
    return render(request, 'tickets/about.html', context)
