from django.db import models

# Create your models here.

class Contact(models.Model):
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    linked_id = models.IntegerField(null=True, blank=True)
    LINK_PRECEDENCE_CHOICES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary')
    ]
    link_precedence = models.CharField(max_length=10, choices=LINK_PRECEDENCE_CHOICES, default='primary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
