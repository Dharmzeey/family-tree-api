# Generated by Django 5.1.5 on 2025-03-06 22:39

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0010_alter_eulogy_options_alter_familyhead_options'),
        ('profiles', '0022_alter_profile_family'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='profile',
            unique_together={('user', 'family')},
        ),
    ]
