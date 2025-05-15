from django.db import migrations

def create_default_category(apps, schema_editor):
    DoctorCategory = apps.get_model('myapp', 'DoctorCategory')
    default_category = DoctorCategory.objects.create(
        type='General'
    )

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0005_alter_doctor_password'),  # Replace with your last migration name
    ]

    operations = [
        migrations.RunPython(create_default_category),
    ]