# Generated by Django 5.2 on 2025-05-02 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_general_user_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='general_user',
            name='contact',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
