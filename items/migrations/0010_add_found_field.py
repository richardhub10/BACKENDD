from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0009_merge_profile_migrations'),
    ]

    operations = [
        migrations.AddField(
            model_name='lostitem',
            name='found',
            field=models.BooleanField(default=False, help_text='Marked true when staff/admin mark the item as found'),
        ),
    ]
