from django.db import models
from django.contrib.contenttypes.models import ContentType

class Visitor(models.Model):
    """Individual visitor/person to the barangay"""
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()


class VisitHistory(models.Model):
    """Record of each visit/transaction with the barangay"""
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='visits')
    
    # Visit details
    visit_date = models.DateTimeField(auto_now_add=True)
    purpose_of_visit = models.CharField(max_length=255)
    
    # Processing details
    accommodated_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accommodated_visits'
    )
    
    # Generated certificates in this visit
    generated_certificates = models.ManyToManyField(
        'certificates.GeneratedCertificate',
        related_name='visit_transactions',
        blank=True
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.visitor.full_name} - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def outputs(self):
        """Get list of certificate outputs from this visit"""
        return list(self.generated_certificates.all())
    
    def get_visit_summary(self):
        """Return dictionary with visit summary"""
        return {
            'visitor': self.visitor.full_name,
            'visit_date': self.visit_date,
            'purpose': self.purpose_of_visit,
            'accommodated_by': self.accommodated_by.get_full_name() if self.accommodated_by else 'N/A',
            'certificates_issued': self.generated_certificates.count(),
            'outputs': [cert.template.template_name for cert in self.generated_certificates.all()]
        }


class ActivityLog(models.Model):
    """Detailed audit log of all system activities"""
    LOG_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('certificate_generated', 'Certificate Generated'),
        ('certificate_printed', 'Certificate Printed'),
        ('certificate_deleted', 'Certificate Deleted'),
        ('certificate_requested', 'Certificate Requested'),
        ('record_modified', 'Record Modified'),
        ('record_deleted', 'Record Deleted'),
        ('history_viewed', 'History Viewed'),
        ('user_created', 'User Created'),
        ('user_deleted', 'User Deleted'),
        ('user_permissions_changed', 'User Permissions Changed'),
        ('template_modified', 'Template Modified'),
        ('other', 'Other Activity'),
    )
    
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs'
    )
    
    log_type = models.CharField(max_length=30, choices=LOG_TYPES)
    action_description = models.TextField()
    
    # Optional: Reference to object being acted upon
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['log_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Deleted User'} - {self.log_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
