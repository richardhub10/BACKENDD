from rest_framework import serializers
from .models import LostItem, Message
from django.contrib.auth.models import User
from django.core.files.storage import default_storage


class LostItemSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = LostItem
        fields = ['id', 'uuid', 'user_name', 'name', 'category', 'description', 'date_found', 'image', 'created_at', 'claimed', 'found']
        read_only_fields = ['id', 'uuid', 'user_name', 'created_at']

    def validate(self, attrs):
        # Enforce image mandatory for creation; allow existing items without image when updating
        if self.instance is None and not attrs.get('image'):
            raise serializers.ValidationError({'image': 'Image is required for a new lost item.'})
        return attrs

    def to_representation(self, instance):
        """Return a safe representation where `image` is None when missing on disk.

        Some seed data may reference filenames that aren't present in the deployed
        media directory. Returning a broken URL leads to 404s in the client. This
        normalizes such cases so the UI can show its built-in placeholder.
        """
        data = super().to_representation(instance)
        try:
            img = getattr(instance, 'image', None)
            # When a file is set but doesn't actually exist in storage, hide it
            if img and getattr(img, 'name', None):
                if not default_storage.exists(img.name):
                    data['image'] = None
        except Exception:
            # On any error determining file existence, prefer a clean fallback
            data['image'] = None
        return data


class MessageSerializer(serializers.ModelSerializer):
    # Allow admin to provide a user id when replying; for regular users this is ignored.
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    # Friendly display name for the user (first + last or username) to avoid misinformation
    user_display = serializers.SerializerMethodField(read_only=True)
    # Attachment uploads removed: chat no longer supports attachments

    class Meta:
        model = Message
        fields = ['id', 'sender', 'user', 'user_name', 'user_display', 'text', 'created_at']
        read_only_fields = ['id', 'created_at', 'sender', 'user_name']

    def get_user_display(self, obj):
        # obj may be a Message instance or a validated_data dict during serializer.data
        user = None
        try:
            if isinstance(obj, dict):
                user = obj.get('user')
            else:
                user = getattr(obj, 'user', None)
        except Exception:
            user = None
        if not user:
            return None
        # user may be a User instance
        try:
            name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip()
            return name if name else user.username
        except Exception:
            # fallback when user is not a User instance
            try:
                return str(user)
            except Exception:
                return None

    # No create override required when attachments are disabled
