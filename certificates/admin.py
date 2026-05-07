from django.contrib import admin
from .models import CertificateTemplate, GeneratedCertificate, CertificateRequest


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_name', 'template_type', 'is_active', 'date_created', 'date_updated')
    list_filter = ('template_type', 'is_active', 'date_created')
    search_fields = ('template_name', 'description')
    readonly_fields = ('date_created', 'date_updated')


@admin.register(GeneratedCertificate)
class GeneratedCertificateAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'template', 'status', 'created_date', 'created_by')
    list_filter = ('template', 'status', 'created_date', 'include_signature')
    search_fields = ('recipient_name', 'recipient_email')
    readonly_fields = ('created_date', 'printed_date', 'created_by', 'printed_by')
    
    fieldsets = (
        ('Certificate Info', {
            'fields': ('template', 'recipient_name', 'recipient_email', 'recipient_contact', 'certificate_data')
        }),
        ('Signature', {
            'fields': ('include_signature', 'signature_official')
        }),
        ('Generated Files', {
            'fields': ('docx_file',)
        }),
        ('Status & Tracking', {
            'fields': ('status', 'created_by', 'created_date', 'printed_by', 'printed_date')
        }),
    )


@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'template', 'recipient_name', 'status', 'created_date')
    list_filter = ('status', 'template', 'created_date')
    search_fields = ('requester__username', 'recipient_name', 'recipient_email')
    readonly_fields = ('created_date', 'updated_date', 'reviewed_date')
