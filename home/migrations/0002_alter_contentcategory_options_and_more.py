# Generated by Django 5.0.6 on 2024-09-15 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contentcategory',
            options={'verbose_name_plural': 'Content Categories'},
        ),
        migrations.RemoveField(
            model_name='contentrequest',
            name='user',
        ),
        migrations.AlterField(
            model_name='contentcategory',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='platform',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
