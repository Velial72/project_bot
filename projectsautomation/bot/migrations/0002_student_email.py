# Generated by Django 3.2.22 on 2023-10-27 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.CharField(default='example@gmail.com', max_length=255, verbose_name='Почта ученика'),
        ),
    ]
