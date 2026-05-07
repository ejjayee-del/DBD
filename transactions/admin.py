from django.contrib import admin
from .models import Visitor, VisitHistory, ActivityLog


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'contact_number', 'date_created')
    search_fields = ('first_name', 'last_name', 'email', 'contact_number')
    list_filter = ('date_created',)
    readonly_fields = ('date_created', 'date_updated')


@admin.register(VisitHistory)
class VisitHistoryAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'visit_date', 'purpose_of_visit', 'accommodated_by')
    list_filter = ('visit_date', 'accommodated_by')
    search_fields = ('visitor__first_name', 'visitor__last_name', 'purpose_of_visit')
    readonly_fields = ('visit_date',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'log_type', 'timestamp', 'action_description')
    list_filter = ('log_type', 'timestamp', 'user')
    search_fields = ('user__username', 'action_description')
    readonly_fields = ('timestamp', 'user')
