from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0008_alter_profile_id'),
        ('items', '0008_profile_fields_update'),
    ]

    operations = [
        # Merge migration: no operations required, this only resolves the two
        # concurrent 0008 migrations so the migration graph has a single leaf.
    ]
