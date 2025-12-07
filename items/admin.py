from django.contrib import admin
from .models import LostItem

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'category', 'date_found', 'claimed', 'user', 'created_at')
    list_filter = ('category', 'date_found', 'claimed')
    search_fields = ('uuid', 'name', 'description', 'user__username')
    readonly_fields = ('uuid',)
