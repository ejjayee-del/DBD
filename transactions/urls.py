from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('history/', views.history_view, name='history'),
    path('requester/<int:requester_id>/', views.requester_visit_history_view, name='requester_detail'),
    path('delete/<str:record_type>/<int:record_id>/', views.delete_record_view, name='delete_record'),
    path('activity_log/', views.activity_log_view, name='activity_log'),
    path('requester_activity_log/', views.requester_activity_log_view, name='requester_activity_log'),
]
