from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import pytz
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import pytz

class General_User(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        
        bd_timezone = pytz.timezone('Asia/Dhaka')
        current_time = timezone.now().astimezone(bd_timezone)
        
        if not self.id:
            self.created_at = current_time
        self.updated_at = current_time
        super(General_User, self).save(*args, **kwargs)
    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'general_user'

def get_default_category():
    return DoctorCategory.objects.first().id
class DoctorCategory(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        bd_timezone = pytz.timezone('Asia/Dhaka')
        current_time = timezone.now().astimezone(bd_timezone)
        
        if not self.id:
            self.created_at = current_time
        self.updated_at = current_time
        super(DoctorCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.type

    class Meta:
        verbose_name_plural = 'Doctor Categories'

class Doctor(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True,null = True)  # Removed null and blank
    full_name = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  # Changed max_length to 128, removed default
    category = models.ForeignKey(
        DoctorCategory, 
        on_delete=models.SET_DEFAULT, 
        #on_delete=models.CASCADE,  # This deletes doctors when their category is deleted
        related_name='doctors',
        default=get_default_category,
    )
    email = models.EmailField(max_length=254, unique=True)
    mobile = models.CharField(max_length=15,unique=True,null = True)
    degrees = models.CharField(max_length=200)
    hospital = models.CharField(max_length=200, default='')
    experience = models.IntegerField(help_text='Experience in years')
    description = models.TextField(default='')
    image = models.ImageField(upload_to='static/images/doctors/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        
        bd_timezone = pytz.timezone('Asia/Dhaka')
        current_time = timezone.now().astimezone(bd_timezone)
        
        if not self.id:
            self.created_at = current_time
        self.updated_at = current_time
        super(Doctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    
    
class Employee(models.Model):
    EMPLOYEE_CATEGORIES = [
        ('Doctor', 'Doctor'),
        ('Nurse', 'Nurse'),
        ('Surgeon', 'Surgeon'),
        ('Wardboy', 'Wardboy'),
        ('Cleaner', 'Cleaner'),
        ('Receptionist', 'Receptionist'),
        ('HR', 'HR'),
        ('Lab Assistant', 'Lab Assistant'),
        ('Pharmacist', 'Pharmacist'),
        ('Radiologist', 'Radiologist'),
        ('Anesthetist', 'Anesthetist'),
        ('Pathologist', 'Pathologist'),
        ('Physiotherapist', 'Physiotherapist'),
        ('IT Support', 'IT Support'),
        ('Security Guard', 'Security Guard'),
        ('Accountant', 'Accountant'),
        ('Medical Technician', 'Medical Technician'),
        ('Ambulance Driver', 'Ambulance Driver'),
        ('Dietitian', 'Dietitian'),
        ('Billing Executive', 'Billing Executive'),
        ('Operation Theatre Assistant', 'Operation Theatre Assistant'),
        ('Front Desk Executive', 'Front Desk Executive'),
        ('Maintenance Staff', 'Maintenance Staff'),
        ('Medical Records Officer', 'Medical Records Officer'),
        ('Blood Bank Staff', 'Blood Bank Staff'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    present_address = models.TextField()
    permanent_address = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    mobile_no = models.CharField(max_length=15)
    category = models.CharField(max_length=50, choices=EMPLOYEE_CATEGORIES)
    image = models.ImageField(upload_to='static/images/employees/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        bd_timezone = pytz.timezone('Asia/Dhaka')
        current_time = timezone.now().astimezone(bd_timezone)
        
        if not self.id:
            self.created_at = current_time
        self.updated_at = current_time
        super(Employee, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.category}"

    class Meta:
        verbose_name_plural = 'Employees'

class Hospital(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    address = models.TextField()
    google_maps_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        bd_timezone = pytz.timezone('Asia/Dhaka')
        current_time = timezone.now().astimezone(bd_timezone)
        
        if not self.id:
            self.created_at = current_time
        self.updated_at = current_time
        super(Hospital, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'hospital'

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        bd_timezone = pytz.timezone('Asia/Dhaka')
        current_time = timezone.now().astimezone(bd_timezone)
        
        if not self.id:
            self.created_at = current_time
        self.updated_at = current_time
        super(Schedule, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor.full_name} - {self.day} ({self.start_time} - {self.end_time})"

    class Meta:
        db_table = 'schedule'
        unique_together = ['doctor', 'day']
        ordering = ['doctor', 'day']


class Appointment(models.Model):
    APPOINTMENT_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(General_User, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    appointment_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']