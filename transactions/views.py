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
from certificates.models import GeneratedCertificate, CertificateRequest


@login_required
@require_http_methods(["GET"])
def history_view(request):
    """View certificate request history (repurposed visit history tracker)"""
    if not request.user.can_view_history:
        messages.error(request, 'You do not have permission to view history.')
        return redirect('dashboard')

    search_form = HistorySearchForm(request.GET or None)

    # Base queryset — certificate requests act as visit records
    cert_requests = CertificateRequest.objects.select_related(
        'template', 'requester', 'reviewed_by', 'generated_certificate'
    ).all()

    # Default: show today's requests
    today = timezone.now().date()
    date_filtered = False

    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')

        if search_query:
            cert_requests = cert_requests.filter(
                Q(requester__first_name__icontains=search_query) |
                Q(requester__last_name__icontains=search_query) |
                Q(requester__username__icontains=search_query) |
                Q(recipient_name__icontains=search_query) |
                Q(template__template_name__icontains=search_query)
            )

        if date_from:
            cert_requests = cert_requests.filter(created_date__date__gte=date_from)
            date_filtered = True

        if date_to:
            cert_requests = cert_requests.filter(created_date__date__lte=date_to)
            date_filtered = True

    if not date_filtered and not (search_form.is_valid() and search_form.cleaned_data.get('search_query')):
        cert_requests = cert_requests.filter(created_date__date=today)

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        cert_requests = cert_requests.filter(status=status_filter)

    # Summary counts (all-time, not filtered)
    total_requests = CertificateRequest.objects.count()
    pending_count = CertificateRequest.objects.filter(status='pending').count()
    completed_count = CertificateRequest.objects.filter(status='completed').count()
    today_count = CertificateRequest.objects.filter(created_date__date=today).count()

    # Pagination
    paginator = Paginator(cert_requests, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'visits': page_obj,
        'search_form': search_form,
        'status_filter': status_filter,
        'total_requests': total_requests,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'today_count': today_count,
        'status_choices': CertificateRequest.STATUS_CHOICES,
    }

    return render(request, 'transactions/history.html', context)


@login_required
@require_http_methods(["GET"])
def requester_visit_history_view(request, requester_id):
    """View all certificate requests from a specific requester (their visit history)"""
    if not request.user.can_view_history:
        messages.error(request, 'You do not have permission to view this.')
        return redirect('dashboard')

    from accounts.models import CustomUser
    requester = get_object_or_404(CustomUser, id=requester_id, role='requester')
    cert_requests = CertificateRequest.objects.filter(requester=requester).select_related(
        'template', 'reviewed_by', 'generated_certificate'
    ).order_by('-created_date')

    context = {
        'requester': requester,
        'cert_requests': cert_requests,
        'total': cert_requests.count(),
        'pending': cert_requests.filter(status='pending').count(),
        'completed': cert_requests.filter(status='completed').count(),
        'rejected': cert_requests.filter(status='rejected').count(),
    }

    return render(request, 'transactions/visitor_detail.html', context)


@login_required
@require_http_methods(["POST"])
def delete_record_view(request, record_type, record_id):
    """Delete a record (certificate request or generated certificate)"""
    if not request.user.can_delete_records:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('transactions:history')

    if record_type == 'request':
        cert_request = get_object_or_404(CertificateRequest, id=record_id)
        summary = f"{cert_request.requester.get_full_name()} - {cert_request.template.template_name}"
        cert_request.delete()

        ActivityLog.objects.create(
            user=request.user,
            log_type='record_deleted',
            action_description=f"Deleted certificate request: {summary}",
            object_id=record_id,
        )
        messages.success(request, 'Certificate request record deleted successfully.')

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
