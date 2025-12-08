from django.contrib import admin
from django.core.files.storage import default_storage
from .models import LostItem, Message

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'category', 'date_found', 'claimed', 'user', 'created_at')
    list_filter = ('category', 'date_found', 'claimed')
    search_fields = ('uuid', 'name', 'description', 'user__username')
    readonly_fields = ('uuid',)

    actions = ['clear_missing_images']

    def clear_missing_images(self, request, queryset):
        """Admin action: clear image field for selected items if file missing."""
        cleared = 0
        total = 0
        for item in queryset:
            total += 1
            img = getattr(item, 'image', None)
            if img and getattr(img, 'name', None):
                if not default_storage.exists(img.name):
                    item.image = None
                    item.save(update_fields=['image'])
                    cleared += 1
        self.message_user(request, f"Checked {total} items; cleared {cleared} missing images.")
    clear_missing_images.short_description = "Clear missing image files for selected items"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'sender', 'user', 'text', 'created_at')
    list_filter = ('sender', 'created_at')
    search_fields = ('text', 'user__username')
