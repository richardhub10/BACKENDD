from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0009_merge_profile_migrations'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='message_attachments/'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(blank=True),
        ),
    ]
