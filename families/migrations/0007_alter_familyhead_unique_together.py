# Generated by Django 5.1.5 on 2025-02-16 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('families', '0006_alter_familyhead_family_alter_handler_operator_and_more'),
        ('profiles', '0020_alter_offlinerelative_picture'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='familyhead',
            unique_together={('family', 'person')},
        ),
    ]
