from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse
from transactions.models import ActivityLog
from .forms import UserLoginForm, RequesterRegistrationForm


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register':
            register_form = RequesterRegistrationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                messages.success(request, 'Registration successful! You can now log in.')
                return redirect('accounts:login')
            else:
                form = UserLoginForm()
        else:
            form = UserLoginForm(request.POST)
            register_form = RequesterRegistrationForm()
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if not user.is_active_user:
                        messages.error(request, 'Your account is inactive. Please contact an administrator.')
                        return render(request, 'accounts/login.html', {'form': form, 'register_form': register_form})
                    login(request, user)
                    
                    # Log the login activity
                    ActivityLog.objects.create(
                        user=user,
                        log_type='login',
                        action_description=f"User {username} logged in",
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
        register_form = RequesterRegistrationForm()
    
    return render(request, 'accounts/login.html', {'form': form, 'register_form': register_form})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """User logout view"""
    user = request.user
    ActivityLog.objects.create(
        user=user,
        log_type='logout',
        action_description=f"User {user.username} logged out",
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """Dashboard - shows different content based on user role"""
    from certificates.models import GeneratedCertificate, CertificateRequest
    from transactions.models import VisitHistory
    
    if request.user.role == 'requester':
        # Requester dashboard
        user_requests = CertificateRequest.objects.filter(requester=request.user).order_by('-created_date')[:10]
        context = {
            'user_requests': user_requests,
            'is_requester': True,
            'total_requests': CertificateRequest.objects.filter(requester=request.user).count(),
            'pending_requests': CertificateRequest.objects.filter(requester=request.user, status='pending').count(),
            'completed_requests': CertificateRequest.objects.filter(requester=request.user, status='completed').count(),
            'rejected_requests': CertificateRequest.objects.filter(requester=request.user, status='rejected').count(),
        }
        return render(request, 'accounts/requester_dashboard.html', context)
    
    # Staff dashboard
    if not request.user.can_view_history and not request.user.can_print_certificates:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:login')
    
    # Get stats
    total_certificates = GeneratedCertificate.objects.count()
    total_visits = CertificateRequest.objects.count()  # requests = visits
    pending_requests = CertificateRequest.objects.filter(status='pending').count()
    recent_activities = ActivityLog.objects.select_related('user').all()[:10]
    
    context = {
        'total_certificates': total_certificates,
        'total_visits': total_visits,
        'pending_requests': pending_requests,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'accounts/dashboard.html', context)
