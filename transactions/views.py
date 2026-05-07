from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Visitor, VisitHistory, ActivityLog
from .forms import VisitorForm, VisitHistoryForm, HistorySearchForm
from certificates.models import GeneratedCertificate


@login_required
@require_http_methods(["GET"])
def history_view(request):
    """View visit history with search functionality"""
    if not request.user.can_view_history:
        messages.error(request, 'You do not have permission to view history.')
        return redirect('dashboard')
    
    search_form = HistorySearchForm(request.GET or None)
    
    # Get all visits
    visits = VisitHistory.objects.select_related('visitor', 'accommodated_by').all()
    
    # Get today's visits by default
    today = timezone.now().date()
    visits = visits.filter(visit_date__date=today)
    
    # Apply search filter if provided
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search_query:
            visits = visits.filter(
                Q(visitor__first_name__icontains=search_query) |
                Q(visitor__last_name__icontains=search_query) |
                Q(visitor__email__icontains=search_query) |
                Q(purpose_of_visit__icontains=search_query)
            )
        
        if date_from:
            visits = visits.filter(visit_date__date__gte=date_from)
        
        if date_to:
            visits = visits.filter(visit_date__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(visits, 25)  # 25 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'visits': page_obj,
        'search_form': search_form,
    }
    
    return render(request, 'transactions/history.html', context)


@login_required
@require_http_methods(["GET"])
def visitor_detail_view(request, visitor_id):
    """View detailed history of a specific visitor"""
    if not request.user.can_view_history:
        messages.error(request, 'You do not have permission to view this.')
        return redirect('dashboard')
    
    visitor = get_object_or_404(Visitor, id=visitor_id)
    visits = visitor.visits.select_related('accommodated_by').all()
    
    context = {
        'visitor': visitor,
        'visits': visits,
    }
    
    return render(request, 'transactions/visitor_detail.html', context)


@login_required
@require_http_methods(["POST"])
def delete_record_view(request, record_type, record_id):
    """Delete a record (visitor, visit history, or certificate)"""
    if not request.user.can_delete_records:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('transactions:history')
    
    if record_type == 'visitor':
        visitor = get_object_or_404(Visitor, id=record_id)
        visitor_name = visitor.full_name
        visitor.delete()
        
        ActivityLog.objects.create(
            user=request.user,
            log_type='record_deleted',
            action_description=f"Deleted visitor record: {visitor_name}",
            object_id=record_id,
        )
        
        messages.success(request, 'Visitor record deleted successfully.')
    
    elif record_type == 'visit':
        visit = get_object_or_404(VisitHistory, id=record_id)
        visit_summary = f"{visit.visitor.full_name} - {visit.visit_date.strftime('%Y-%m-%d')}"
        visit.delete()
        
        ActivityLog.objects.create(
            user=request.user,
            log_type='record_deleted',
            action_description=f"Deleted visit record: {visit_summary}",
            object_id=record_id,
        )
        
        messages.success(request, 'Visit record deleted successfully.')
    
    elif record_type == 'certificate':
        certificate = get_object_or_404(GeneratedCertificate, id=record_id)
        cert_summary = f"{certificate.template.template_name} - {certificate.recipient_name}"
        certificate.delete()
        
        ActivityLog.objects.create(
            user=request.user,
            log_type='certificate_deleted',
            action_description=f"Deleted certificate: {cert_summary}",
            object_id=record_id,
        )
        
        messages.success(request, 'Certificate deleted successfully.')
    
    return redirect('transactions:history')


@login_required
@require_http_methods(["GET"])
def activity_log_view(request):
    """View detailed activity log"""
    if not request.user.can_view_history:
        messages.error(request, 'You do not have permission to view activity log.')
        return redirect('dashboard')
    
    activities = ActivityLog.objects.select_related('user').all().order_by('-timestamp')
    
    # Filter by log type if provided
    log_type = request.GET.get('log_type')
    if log_type:
        activities = activities.filter(log_type=log_type)
    
    # Get last 7 days by default
    days_back = request.GET.get('days', 7)
    try:
        days_back = int(days_back)
        date_from = timezone.now() - timedelta(days=days_back)
        activities = activities.filter(timestamp__gte=date_from)
    except ValueError:
        pass
    
    # Pagination
    paginator = Paginator(activities, 50)  # 50 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'activities': page_obj,
        'log_types': ActivityLog.LOG_TYPES,
    }
    
    return render(request, 'transactions/activity_log.html', context)


@login_required
@require_http_methods(["GET"])
def requester_activity_log_view(request):
    """View activity log for requesters"""
    if request.user.role != 'requester':
        messages.error(request, 'This page is for requesters only.')
        return redirect('dashboard')
    
    activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    
    context = {
        'activities': activities,
    }
    
    return render(request, 'transactions/requester_activity_log.html', context)
