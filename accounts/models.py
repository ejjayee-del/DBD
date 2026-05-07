from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Extended User model with role-based access control"""
    ROLE_CHOICES = (
        ('requester', 'Requester - Request Certificates'),
        ('secretary', 'Secretary - View & Print'),
        ('officer', 'Officer - View, Print & Edit'),
        ('admin', 'Admin - Full Access (View, Print, Edit, Delete)'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='secretary')
    can_view_history = models.BooleanField(default=True)
    can_print_certificates = models.BooleanField(default=True)
    can_edit_records = models.BooleanField(default=False)
    can_delete_records = models.BooleanField(default=False)
    is_active_user = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'requester':
            self.can_view_history = False
            self.can_print_certificates = False
            self.can_edit_records = False
            self.can_delete_records = False
        elif self.role == 'secretary':
            self.can_view_history = True
            self.can_print_certificates = True
            self.can_edit_records = False
            self.can_delete_records = False
        elif self.role == 'officer':
            self.can_view_history = True
            self.can_print_certificates = True
            self.can_edit_records = True
            self.can_delete_records = False
        elif self.role == 'admin':
            self.can_view_history = True
            self.can_print_certificates = True
            self.can_edit_records = True
            self.can_delete_records = True
        super().save(*args, **kwargs)
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        perms = {
            'view_history': self.can_view_history,
            'print_certificates': self.can_print_certificates,
            'edit_records': self.can_edit_records,
            'delete_records': self.can_delete_records,
        }
        return perms.get(permission, False)


class OfficialSignature(models.Model):
    """Store signature images of barangay officials"""
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)  # e.g., "Barangay Captain", "Secretary"
    signature_image = models.ImageField(upload_to='signatures/')
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', 'position']
    
    def __str__(self):
        return f"{self.name} - {self.position}"
