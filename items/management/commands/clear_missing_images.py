from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from items.models import LostItem

class Command(BaseCommand):
    help = "Clear image field for LostItem records where the file is missing in storage."

    def handle(self, *args, **options):
        cleared = 0
        total = 0
        for item in LostItem.objects.all():
            total += 1
            img = getattr(item, 'image', None)
            if img and getattr(img, 'name', None):
                if not default_storage.exists(img.name):
                    item.image = None
                    item.save(update_fields=['image'])
                    cleared += 1
        self.stdout.write(self.style.SUCCESS(f"Checked {total} items; cleared {cleared} missing images."))