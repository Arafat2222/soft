from django.contrib import admin
from .models import Appointment, Doctor, DoctorCategory, Employee, General_User, Hospital, Schedule

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'category', 'experience')
    search_fields = ('username', 'full_name', 'email')
    list_filter = ('category', 'created_at')
    list_per_page = 10
    exclude = ('password',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['username'].required = True
        form.base_fields['full_name'].required = True
        form.base_fields['email'].required = True
        form.base_fields['degrees'].required = True
        form.base_fields['experience'].required = True
        form.base_fields['category'].required = True
        return form

@admin.register(DoctorCategory)
class DoctorCategoryAdmin(admin.ModelAdmin):
    list_display = ('type', 'created_at', 'updated_at')
    search_fields = ('type',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'mobile_no', 'salary', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'mobile_no', 'category')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 10
    ordering = ('-created_at',)
    

@admin.register(General_User)
class GeneralUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'contact', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('full_name', 'email', 'contact')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'google_maps_url', 'created_at', 'updated_at')
    search_fields = ('name', 'address', 'location_description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 10
    ordering = ('-created_at',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day', 'start_time', 'end_time', 'is_available')
    list_filter = ('day', 'is_available', 'doctor')
    search_fields = ('doctor__full_name', 'doctor__email', 'day')
    ordering = ('doctor', 'day')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__full_name', 'doctor__full_name')
    date_hierarchy = 'appointment_date'
