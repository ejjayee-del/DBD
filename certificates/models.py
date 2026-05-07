from django.db import models
from django.core.validators import FileExtensionValidator
from django_summernote.fields import SummernoteTextField
# DO NOT put executable code here!

class CertificateTemplate(models.Model):
    """Store certificate templates with dynamic fields"""
    TEMPLATE_TYPES = (
        ('barangay_clearance', 'Barangay Clearance'),
        ('residency', 'Certificate of Residency'),
        ('non-residency', 'Certificate of Non-Residency'),
        ('Food_Assistance', 'Certificate of Food Assistance'),
        ('Financial_Assistance', 'Certificate of Financial Assistance'),
        ('Program_Certificate', 'Certificate of Program'),
        ('Participation', 'Certificate of Participation/Conduct of Activity'),
        ('indigency', 'Certificate of Indigency'),
        ('animal_ownership', 'Certificate of Ownership (Livestock)'),
        ('certification', 'BHERT Certification'),
        ('appearance', 'Certification of Appearance'),
        ('death_certificate', 'Death Certification'),
        ('duration', 'Duration Certificate'),
        ('settlement', 'Amicable Settlement Form'),
        ('complaint_form', 'Complaint Form'),
        ('hearing_notice', 'Notice of Hearing'),
        ('business_permit', 'Business Permit'),
        ('first_time_job_seeker', 'First Time Job Seeker'),
        ('solo_parent', 'Solo Parent Certificate'),
        ('senior_citizen', 'Senior Citizen Certificate'),
        ('pwd', 'PWD Certificate'),
        ('other', 'Other Certificate'),
    )
    
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES, unique=True)
    template_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Template content - HTML format for displaying in certificate
    html_template = models.TextField(help_text="HTML template with {{field_name}} placeholders")
    
    # Dynamic fields in JSON format: {"field_name": {"label": "...", "type": "text|textarea|date|select", "required": true}}
    required_fields = models.JSONField(default=dict, help_text="Required fields for this certificate")
    
    # Optional fields JSON
    optional_fields = models.JSONField(default=dict, help_text="Optional fields for this certificate")
    
    template_file = models.FileField(
        upload_to='templates/',
        validators=[FileExtensionValidator(['docx', 'pdf'])],
        null=True,
        blank=True,
        help_text="Original template file (Word/PDF) for reference"
    )
    
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_type']
    
    def __str__(self):
        return self.template_name
    
    def get_all_fields(self):
        """Get combined required and optional fields"""
        all_fields = {}
        
        # Handle required_fields - could be dict or list
        if isinstance(self.required_fields, dict):
            all_fields.update(self.required_fields)
        elif isinstance(self.required_fields, list):
            # Convert list to dict with default config
            for field_name in self.required_fields:
                all_fields[field_name] = {
                    'label': field_name.replace('_', ' ').title(),
                    'type': 'text',
                    'required': True
                }
        
        # Handle optional_fields - could be dict or list
        if isinstance(self.optional_fields, dict):
            all_fields.update(self.optional_fields)
        elif isinstance(self.optional_fields, list):
            # Convert list to dict with default config
            for field_name in self.optional_fields:
                all_fields[field_name] = {
                    'label': field_name.replace('_', ' ').title(),
                    'type': 'text',
                    'required': False
                }
        
        return all_fields


class GeneratedCertificate(models.Model):
    """Store generated certificate records"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('printed', 'Printed'),
        ('archived', 'Archived'),
    )
    
    template = models.ForeignKey(CertificateTemplate, on_delete=models.SET_NULL, null=True)
    
    # Recipient information
    recipient_name = models.CharField(max_length=300)
    recipient_email = models.EmailField(blank=True)
    recipient_contact = models.CharField(max_length=20, blank=True)
    
    # Certificate data - JSON format storing all filled fields
    certificate_data = models.JSONField(default=dict)
    
    # Signature settings
    include_signature = models.BooleanField(default=False)
    signature_official = models.ForeignKey(
        'accounts.OfficialSignature',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Generated file (Word document only)
    docx_file = models.FileField(upload_to='certificates/docx/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Tracking
    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_certificates'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    printed_date = models.DateTimeField(null=True, blank=True)
    printed_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='printed_certificates'
    )
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.template.template_name} - {self.recipient_name}"


class CertificateRequest(models.Model):
    """Store certificate requests submitted by requesters"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE)
    requester = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='certificate_requests')
    recipient_name = models.CharField(max_length=300)
    recipient_email = models.EmailField(blank=True)
    recipient_contact = models.CharField(max_length=20, blank=True)
    request_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_certificate_requests'
    )
    reviewed_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    generated_certificate = models.OneToOneField(
        GeneratedCertificate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificate_request'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.template.template_name} request by {self.requester.username} - {self.get_status_display()}"


class CertificateField(models.Model):
    """Individual fields that appear in certificate templates"""
    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE, related_name='fields')
    
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=200)
    field_type = models.CharField(
        max_length=50,
        choices=[
            ('text', 'Text'),
            ('textarea', 'Text Area'),
            ('date', 'Date'),
            ('email', 'Email'),
            ('phone', 'Phone Number'),
            ('select', 'Dropdown'),
            ('radio', 'Radio Button'),
            ('number', 'Number'),
        ]
    )
    is_required = models.BooleanField(default=False)
    help_text = models.CharField(max_length=255, blank=True)
    placeholder = models.CharField(max_length=255, blank=True)
    
    # For select/radio fields: comma-separated options
    choices = models.TextField(blank=True, help_text="For select/radio: comma-separated values")
    
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.template.template_name} - {self.field_label}"
    

class CertificateDocument(models.Model):
    title = models.CharField(max_length=200)
    content = SummernoteTextField()  # Use SummernoteTextField instead
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    certificate_type = models.CharField(max_length=100, default='barangay_clearance')
    
    def __str__(self):
        return self.title