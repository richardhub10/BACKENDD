from django.db import models
from django.contrib.auth.models import User
import uuid

class LostItem(models.Model):
    CATEGORY_CHOICES = [
        ("electronics", "Electronics"),
        ("documents", "Documents"),
        ("clothing", "Clothing"),
        ("accessories", "Accessories"),
        ("other", "Other"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    date_found = models.DateField()
    # Switch to FileField for development so Pillow isn't required to run the dev server.
    # Replace back to ImageField when Pillow is installed in the environment.
    image = models.FileField(upload_to="item_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    claimed = models.BooleanField(default=False, help_text="Marked true when verified claimed by rightful owner")
    found = models.BooleanField(default=False, help_text="Marked true when staff/admin mark the item as found")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, help_text="Public unique identifier")

    def __str__(self):
        return f"{self.name} ({self.category})"


class Message(models.Model):
    SENDER_CHOICES = [
        ("user", "User"),
        ("admin", "Admin"),
    ]
    sender = models.CharField(max_length=8, choices=SENDER_CHOICES)
    # Link the message to the user who started the conversation (the regular user).
    # Admin replies will also set this field to the target user.
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True)
    # optional attachment
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('unspecified', 'Unspecified'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, default='unspecified')

    def __str__(self):
        return f"Profile({self.user.username})"
