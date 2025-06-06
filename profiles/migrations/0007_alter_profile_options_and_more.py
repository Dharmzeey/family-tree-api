# Generated by Django 5.1.5 on 2025-02-03 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_alter_familyrelation_options_alter_profile_picture'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['last_name']},
        ),
        migrations.RenameField(
            model_name='offlinerelative',
            old_name='relative_first_name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='offlinerelative',
            old_name='relative_last_name',
            new_name='last_name',
        ),
        migrations.AlterUniqueTogether(
            name='offlinerelative',
            unique_together={('user', 'first_name', 'last_name')},
        ),
        migrations.AddField(
            model_name='offlinerelative',
            name='other_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
