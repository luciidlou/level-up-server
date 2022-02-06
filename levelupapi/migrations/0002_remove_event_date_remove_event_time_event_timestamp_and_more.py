# Generated by Django 4.0.1 on 2022-02-04 03:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('levelupapi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='time',
        ),
        migrations.AddField(
            model_name='event',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organizing', to='levelupapi.gamer'),
        ),
    ]