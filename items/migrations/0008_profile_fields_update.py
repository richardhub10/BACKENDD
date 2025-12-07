from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0007_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='first_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.RemoveField(
            model_name='profile',
            name='full_name',
        ),
    ]
