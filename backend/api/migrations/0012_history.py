# Generated by Django 5.0.6 on 2024-09-01 12:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_booked_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='static/media/history/', verbose_name='Аватарка пользователя')),
                ('max_people', models.IntegerField(blank=True, verbose_name='Макс. человек')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='Имя зала')),
                ('booked_time', models.DateField(verbose_name='Время бронирования')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
            ],
            options={
                'verbose_name': 'История',
                'verbose_name_plural': 'Истории',
            },
        ),
    ]
