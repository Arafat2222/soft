from functools import wraps
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import*
from django.views.decorators.csrf import csrf_exempt
from .models import Doctor
from .models import DoctorCategory
from .models import Schedule
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth.models import User 
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.db.models import Count
import os
from .forms import GeneralUserSignupForm
from django.shortcuts import render, redirect
from .models import General_User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.template.defaulttags import register
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import DoctorCategory
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.views.decorators.http import require_POST
import google.generativeai as genai

@require_http_methods(["POST"])
def update_appointment_status(request, appointment_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        if not status:
            return JsonResponse({'success': False, 'message': 'Status is required'})
            
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = status
        appointment.save()
        
        return JsonResponse({'success': True})
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Appointment not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(["POST"])
def delete_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.delete()
        return JsonResponse({'success': True})
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Appointment not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@register.filter
def split(value, key):
    return value.split(key)


def user_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Please login first.')
            return redirect('general_user_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def general_user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Try Doctor login
        try:
            doctor = Doctor.objects.get(email=email)
            if check_password(password, doctor.password):
                if doctor.is_active:
                    request.session['doctor_id'] = doctor.id
                    request.session['doctor_email'] = doctor.email
                    request.session['doctor_name'] = doctor.full_name
                    request.session['user_type'] = 'doctor'
                    messages.success(request, 'Login successful!')
                    return redirect('doctor_home')
                    #return render(request, 'doctors/homepage.html')
                else:
                    messages.error(request, 'Your account is inactive')
            else:
                messages.error(request, 'Invalid credentials')
        except Doctor.DoesNotExist:
            # Try General User login
            try:
                user = General_User.objects.get(email=email)
                if check_password(password, user.password):
                    if user.is_active:
                        request.session['user_id'] = user.id
                        request.session['user_email'] = user.email
                        request.session['user_name'] = user.full_name
                        request.session['user_type'] = 'general_user'
                        messages.success(request, 'Login successful!')
                        return redirect('user_home')
                        
                        #return render(request, 'general user/user_home.html')
                    else:
                        messages.error(request, 'Your account is inactive')
                else:
                    messages.error(request, 'Invalid credentials')
            except General_User.DoesNotExist:
                messages.error(request, 'No account found with this email')
    
    return render(request, 'general user/login.html')

def doctor_home(request):
    if 'doctor_id' not in request.session or request.session.get('user_type') != 'doctor':
        messages.error(request, 'Please login as a doctor first.')
        return redirect('general_user_login')
    
    doctor = get_object_or_404(Doctor, id=request.session.get('doctor_id'))
    today = datetime.now().date()
    
    # Get today's appointments without any status filter
    today_appointments_count = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).count()
    
    # Get total unique patients without status filter
    total_patients = Appointment.objects.filter(
        doctor=doctor
    ).values('patient').distinct().count()
    
    # Calculate working hours from schedule
    schedules = Schedule.objects.filter(doctor=doctor, is_available=True)
    working_hours = 0
    for schedule in schedules:
        start = schedule.start_time.hour + schedule.start_time.minute/60
        end = schedule.end_time.hour + schedule.end_time.minute/60
        working_hours += (end - start)
    
    # Get recent appointments with all statuses
    recent_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient').order_by('-appointment_date', '-id')[:5]
    
    context = {
        'doctor': doctor,
        'today_appointments_count': today_appointments_count,
        'total_patients': total_patients,
        'working_hours': int(working_hours),
        'recent_appointments': recent_appointments,
        'doctor_schedules': schedules,
    }
    
    return render(request, 'doctors/homepage.html', context)
    #return render(request, 'doctors/homepage.html')

def user_home(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'general_user':
        messages.error(request, 'Please login as a general user first.')
        return redirect('general_user_login')
    doctors = Doctor.objects.all().select_related('category')
    return render(request, 'general user/user_home.html', {'doctors': doctors})

   
@user_login_required
def user_profile(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('general_user_login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    
    if request.method == 'POST':
        # Get password for confirmation
        password = request.POST.get('password')
        
        # Verify password
        if not user.check_password(password):
            messages.error(request, 'Incorrect password. Profile update failed.')
            return redirect('user_profile')
        
        # Update user information
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.contact = request.POST.get('contact')
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        
        # Update session data
        request.session['user_name'] = user.full_name
        
        messages.success(request, 'Profile updated successfully')
        return redirect('user_profile')
    
    return render(request, 'users/profile.html', {'user': user})
    context = {
        'user': user,
    }
    return render(request, 'general user/user_profile.html', context)

def general_user_signup(request):
    #print("general_user_signup called")
    if request.method == 'POST':
        try:
            # Print POST data for debugging
            print("POST data:", request.POST)
            
            full_name = request.POST['fullname']
            email = request.POST['email']
            contact = request.POST['contact']
            password = request.POST['password']

            # Create user object
            user = General_User(
                full_name=full_name,
                email=email,
                contact=contact,
                password=make_password(password)
            )
            
            # Save to database
            user.save()
            print("User saved successfully:", user.id)
            
            messages.success(request, 'Account created successfully!')
            return redirect('user_home')
            
            
        except Exception as e:
            print("Error creating user:", str(e))
            
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'general user/signup.html')


@user_login_required
def general_user_logout(request):
    # Clear only the custom session keys
    request.session.flush()  # Completely clears the session
    messages.success(request, 'You have been logged out.')
    return redirect('general_user_login')






   


def index(request):
    
    if 'user_id' not in request.session or request.session.get('user_type') != 'general_user':
        doctors = Doctor.objects.all().select_related('category')
        context = {
            'doctors': doctors,
        }
        return render(request, 'index.html', context)
    doctors = Doctor.objects.all().select_related('category')
    return render(request, 'general user/user_home.html', {'doctors': doctors})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # print("User:", user.email)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('admin_login')
            
    return render(request, 'manager/admin_login.html')

@login_required(login_url='admin_login')
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access Denied: Admin privileges required')
        return redirect('admin_login')
    
    total_doctors = Doctor.objects.count()
    total_specialists = DoctorCategory.objects.count()
    total_employees = Employee.objects.count() + total_doctors
    doctors = Doctor.objects.all().select_related('category')
    categories = DoctorCategory.objects.annotate(
        doctor_count=Count('doctors')
    ).all()

    context = {
        'total_doctors': total_doctors,
        'total_specialists': total_specialists,
        'total_employees': total_employees,
        'doctors': doctors,
        'categories': categories,
    }
    return render(request, 'manager/admin_dashboard.html', context)
    


@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def manage_doctors(request):
    return redirect('admin_dashboard')
@login_required(login_url='admin_login')
def update_doctor(request, doctor_id):
    if request.method == 'POST':
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # Update basic information
        doctor.full_name = request.POST.get('full_name')
        doctor.username = request.POST.get('username')
        doctor.email = request.POST.get('email')
        doctor.degrees = request.POST.get('degrees')
        doctor.experience = request.POST.get('experience')
        doctor.description = request.POST.get('description')
        
        # Update category
        category_id = request.POST.get('category')
        if category_id:
            doctor.category_id = category_id
        
        # Handle image upload
        if 'image' in request.FILES:
            doctor.image = request.FILES['image']
        
        try:
            doctor.save()
            # Return updated doctor data along with success message
            return JsonResponse({
                'success': True,
                'message': 'Doctor information updated successfully!',
                'doctor': {
                    'id': doctor.id,
                    'full_name': doctor.full_name,
                    'username': doctor.username,
                    'email': doctor.email,
                    'degrees': doctor.degrees,
                    'experience': doctor.experience,
                    'description': doctor.description,
                    'category_type': doctor.category.type,
                    'image_url': doctor.image.url if doctor.image else None
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating doctor information: {str(e)}'
            })
    
    return redirect('admin_dashboard')
@login_required(login_url='admin_login')
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # Delete the image file if it exists
    if doctor.image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(doctor.image))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Delete the doctor record
    doctor.delete()
    messages.success(request, 'Doctor deleted successfully!')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@login_required
def search_doctors(request):
    query = request.GET.get('query', '').lower()
    doctors = Doctor.objects.filter(
        Q(full_name__icontains=query) |
        Q(email__icontains=query) |
        Q(category__type__icontains=query)
    )
    
    doctors_data = [{
        'id': doctor.id,
        'full_name': doctor.full_name,
        'username': doctor.username,
        'email': doctor.email,
        'category_type': doctor.category.type,
        'category_id': doctor.category.id,
        'degrees': doctor.degrees,
        'experience': doctor.experience,
        'description': doctor.description,
        'image_url': doctor.image.url if doctor.image else None,
        'created_at': doctor.created_at.strftime("%B %d, %Y")
    } for doctor in doctors]
    
    return JsonResponse({'doctors': doctors_data})


@login_required(login_url='admin_login')
def add_doctor(request):
    if request.method == 'POST':
        try:
            print("Call")
            # Capture all form data first to ensure it's available in case of error
            form_data = {
                'username': request.POST.get('username', ''),
                'email': request.POST.get('email', ''),
                'full_name': request.POST.get('full_name', ''),
                'mobile': request.POST.get('mobile', ''),
                'degrees': request.POST.get('degrees', ''),
                'experience': request.POST.get('experience', ''),
                'category': request.POST.get('category', ''),
                'description': request.POST.get('description', ''),
                'hospital': request.POST.get('hospital', '')
            }
            
            
            # Check if username or email exists as superuser
            if User.objects.filter(Q(username=form_data['username']) | Q(email=form_data['email']), is_superuser=True).exists():
                messages.error(request, 'Username or email already exists')
                categories = DoctorCategory.objects.all()
                return render(request, 'manager/add_doctor.html', {
                    'categories': categories,
                    'form_data': form_data
                })
            
            doctor = Doctor.objects.create(
                username=form_data['username'],
                email=form_data['email'],
                password=request.POST['password'],
                full_name=form_data['full_name'],
                mobile=form_data['mobile'],
                degrees=form_data['degrees'],
                experience=form_data['experience'],
                category_id=form_data['category'],
                description=form_data['description'],
                hospital=form_data['hospital'],
            )
            
            if 'image' in request.FILES:
                doctor.image = request.FILES['image']
                doctor.save()

            # Add schedule for each day
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                start_time = request.POST.get(f'start_time_{day}')
                end_time = request.POST.get(f'end_time_{day}')
                is_available = request.POST.get(f'is_available_{day}') == '1'
                
                if start_time and end_time:  # Only create schedule if times are provided
                    Schedule.objects.create(
                        doctor=doctor,
                        day=day.capitalize(),
                        start_time=start_time,
                        end_time=end_time,
                        is_available=is_available
                    )
            
            messages.success(request, 'Doctor added successfully!')
            return redirect('admin_dashboard')
            
        except Exception as e:
            # error = str(e)
            # print(error)
            if Doctor.objects.filter(username=form_data['username']).exists():
                messages.error(request, 'Username already exists')
            elif Doctor.objects.filter(email=form_data['email']).exists():
                messages.error(request, 'Email already exists')    
            elif Doctor.objects.filter(mobile=form_data['mobile']).exists():
                messages.error(request, 'Mobile number already exists')
            else:
                print(e)
                messages.error(request, 'An error occurred while adding the doctor')
                
            categories = DoctorCategory.objects.all()
            return render(request, 'manager/add_doctor.html', {
                'categories': categories,
                'form_data': form_data  # Pass the form data back on error
            })
    else:
        categories = DoctorCategory.objects.all()
        return render(request, 'manager/add_doctor.html', {'categories': categories})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Store OTP and timestamp in session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            request.session['otp_timestamp'] = timezone.now().timestamp()
            
            # Send email with OTP
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}\nThis OTP is valid for 2 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'OTP has been sent to your email')
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, 'Email not found')
    
    return render(request, 'manager/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        otp_timestamp = request.session.get('otp_timestamp')
        
        # Check if OTP exists and is not expired
        current_time = timezone.now().timestamp()
        if not otp_timestamp or (current_time - float(otp_timestamp)) > 120:  # 120 seconds = 2 minutes
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('forgot_password')
            
        if stored_otp and entered_otp == stored_otp:
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP')
            
    return render(request, 'manager/verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        email = request.session.get('reset_email')
        password = request.POST.get('password')
        
        if email and password:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            del request.session['reset_email']
            messages.success(request, 'Password reset successfully')
            return redirect('admin_login')
    
    return render(request, 'manager/reset_password.html')
    


@login_required(login_url='admin_login')
def doctor_details(request, doctor_id):
    try:
        doctor = get_object_or_404(Doctor.objects.prefetch_related('schedules'), id=doctor_id)
        return render(request, 'manager/doctor_details.html', {'doctor': doctor})
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor not found')
        return redirect('admin_dashboard')


@login_required(login_url='admin_login')
def add_category(request):
    if request.method == 'POST':
        category_type = request.POST.get('type')
        try:
            # Check if category already exists
            if DoctorCategory.objects.filter(type=category_type).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Category already exists'
                })
            
            category = DoctorCategory.objects.create(type=category_type)
            return JsonResponse({
                'success': True,
                'message': 'Category added successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'


    })


@login_required(login_url='admin_login')
def delete_category(request, category_id):
    try:
        category = DoctorCategory.objects.get(id=category_id)
        # Check if category has associated doctors
        if category.doctors.exists():
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete category with associated doctors'
            })
        
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('admin_dashboard')
        
    except DoctorCategory.DoesNotExist:
        messages.error(request, 'Category not found')
        return redirect('admin_dashboard')
    
def doctor_categories(request):
    try:
        total_doctors = Doctor.objects.count()
        total_specialists = DoctorCategory.objects.count()
        total_employees = Employee.objects.count()
        doctors = Doctor.objects.all().select_related('category')
        categories = DoctorCategory.objects.annotate(
            doctor_count=Count('doctors')
        ).all()

        # Remove the nested context
        return render(request, 'manager/doctor_categories.html', {
            'total_doctors': total_doctors,
            'total_specialists': total_specialists,
            'total_employees': total_employees,
            'doctors': doctors,
            'categories': categories,
        })
    except Exception as e:
        return JsonResponse({
           'success': False,
           'message': str(e)
        })

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment

@user_login_required
def appointment_list(request):
    # Get appointments for the logged-in patient using session user_id
    user_id = request.session.get('user_id')
    appointments = Appointment.objects.filter(
        patient_id=user_id
    ).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'appointments': appointments
    }
    return render(request, 'general user/appointment_list.html', context)

@user_login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    today = datetime.now().date()
    max_date = today + timedelta(days=30)

    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        
        if appointment_date:
            try:
                patient = General_User.objects.get(id=request.session.get('user_id'))
            except General_User.DoesNotExist:
                messages.error(request, 'Patient profile not found')
                return redirect('general_user_login')

            selected_day = datetime.strptime(appointment_date, '%Y-%m-%d').strftime('%A').lower()
            schedule = Schedule.objects.filter(
                doctor=doctor,
                day__iexact=selected_day,
                is_available=True
            ).first()
            
            if schedule:
                appointment = Appointment.objects.create(
                    doctor=doctor,
                    patient=patient,
                    appointment_date=appointment_date,
                    status='confirmed'  # Changed from 'pending' to 'confirmed'
                )
                messages.success(request, 'Appointment booked successfully!')
                return redirect('appointment_list')
            else:
                messages.error(request, 'Doctor is not available on this day')
        else:
            messages.error(request, 'Please select a date')

    schedules = Schedule.objects.filter(doctor=doctor, is_available=True)
    
    context = {
        'doctor': doctor,
        'today_date': today,
        'max_date': max_date,
        'schedules': schedules
    }
    return render(request, 'general user/book_appointment.html', context)

def get_available_slots(request, doctor_id, date):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    day_name = selected_date.strftime('%A').lower()
    
    # Get doctor's schedule for the selected day
    schedule = Schedule.objects.filter(
        doctor=doctor,
        day=day_name,
        is_available=True
    ).first()
    
    available_slots = []
    if schedule:
        # Generate time slots from start_time to end_time in 30-minute intervals
        current_time = datetime.strptime(str(schedule.start_time), '%H:%M:%S')
        end_time = datetime.strptime(str(schedule.end_time), '%H:%M:%S')
        
        while current_time < end_time:
            time_str = current_time.strftime('%H:%M')
            # Check if slot is already booked
            is_booked = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=selected_date,
                appointment_time=time_str
            ).exists()
            
            if not is_booked:
                available_slots.append({
                    'time': time_str,
                    'formatted_time': current_time.strftime('%I:%M %p')
                })
            current_time += timedelta(minutes=30)
    
    return JsonResponse({'slots': available_slots})
    return JsonResponse({'slots': []})
    




from datetime import datetime, timedelta
from django.db.models import Q

def doctor_appointments(request):
    if 'doctor_id' not in request.session or request.session.get('user_type') != 'doctor':
        messages.error(request, 'Please login as a doctor first.')
        return redirect('general_user_login')
    
    doctor = get_object_or_404(Doctor, id=request.session.get('doctor_id'))
    status = request.GET.get('status')
    view_type = request.GET.get('view', 'upcoming')  # Default to upcoming appointments
    
    # Base query
    base_query = Appointment.objects.filter(doctor=doctor)
    
    # Apply status filter if provided
    if status and status != 'all':
        base_query = base_query.filter(status=status)
    
    # Apply date filter based on view_type
    today = datetime.now().date()
    if view_type == 'upcoming':
        base_query = base_query.filter(appointment_date__gte=today)
    elif view_type == 'past':
        base_query = base_query.filter(appointment_date__lt=today)
    
    # Group appointments by day
    appointments_by_day = {}
    appointments = base_query.order_by('appointment_date', 'appointment_time')
    
    for appointment in appointments:
        day = appointment.appointment_date.strftime('%A, %B %d, %Y')
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append(appointment)
    
    context = {
        'appointments_by_day': appointments_by_day,
        'current_status': status,
        'current_view': view_type,
    }
    return render(request, 'doctors/appointments.html', context)


def doctor_schedule(request):
    if 'doctor_id' not in request.session or request.session.get('user_type') != 'doctor':
        messages.error(request, 'Please login as a doctor first.')
        return redirect('general_user_login')
    
    doctor = get_object_or_404(Doctor, id=request.session.get('doctor_id'))
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_available = request.POST.get('is_available') == 'on'
        
        if schedule_id:  # Update existing schedule
            schedule = get_object_or_404(Schedule, id=schedule_id, doctor=doctor)
            schedule.day = day
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.is_available = is_available
            schedule.save()
            messages.success(request, 'Schedule updated successfully!')
        else:  # Add new schedule
            if not Schedule.objects.filter(doctor=doctor, day=day).exists():
                Schedule.objects.create(
                    doctor=doctor,
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    is_available=is_available
                )
                messages.success(request, 'Schedule added successfully!')
            else:
                messages.error(request, f'Schedule for {day} already exists.')
        
        return redirect('doctor_schedule')
    
    schedules = Schedule.objects.filter(doctor=doctor)
    return render(request, 'doctors/schedule.html', {'schedules': schedules})


from django.views.decorators.http import require_POST

@require_POST
def delete_schedule(request, schedule_id):
    if 'doctor_id' not in request.session or request.session.get('user_type') != 'doctor':
        return JsonResponse({'success': False, 'message': 'Unauthorized access'}, status=403)

    try:
        schedule = Schedule.objects.get(id=schedule_id, doctor_id=request.session.get('doctor_id'))
        schedule.delete()
        return JsonResponse({'success': True, 'message': 'Schedule deleted successfully'})
    except Schedule.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Schedule not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


from django.http import JsonResponse

def get_doctor_details(request):
    if 'doctor_id' not in request.session:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    try:
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        return JsonResponse({
            'full_name': doctor.full_name,
            'email': doctor.email,
            'mobile': doctor.mobile,
            'degrees': doctor.degrees,
            'description': doctor.description,
        })
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

from django.http import JsonResponse
from django.views.decorators.http import require_POST



def chat_with_gemini(request):
    if request.method == 'POST':
        try:
            # Parse the request body
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Configure the Gemini API
            genai.configure(api_key="AIzaSyAWHroEcKeXLxK5-HRss1NSO0lt2_rcCWY")
            
            # Use Gemini 1.5 Flash model
            model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
            #এটি কি কোন রোগের লক্ষণ হতে পারে? কী ধরনের পরীক্ষা করা উচিত?
            # Enhance the user's question with medical context
            enhanced_question = f"{user_message}  কোন বিশেষজ্ঞ চিকিৎসককে দেখানো উচিত?"
            
            # Generate response
            response = model.generate_content(enhanced_question)
            
            # Return the response
            return JsonResponse({
                'response': response.text
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)



def update_doctor_profile(request):
    if 'doctor_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Not authorized'})
    
    try:
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        doctor.full_name = request.POST.get('full_name')
        doctor.email = request.POST.get('email')
        doctor.mobile = request.POST.get('mobile')
        doctor.degrees = request.POST.get('degrees')
        doctor.description = request.POST.get('description')
        
        if 'image' in request.FILES:
            doctor.image = request.FILES['image']
            
        doctor.save()
        
        # Update session
        request.session['doctor_name'] = doctor.full_name
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
def appointment_details(request, appointment_id):
    if 'doctor_id' not in request.session or request.session.get('user_type') != 'doctor':
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)
    
    try:
        doctor_id = request.session.get('doctor_id')
        appointment = Appointment.objects.get(id=appointment_id, doctor_id=doctor_id)
        
        # Format the appointment data
        appointment_data = {
            'id': appointment.id,
            'patient_name': appointment.patient.full_name,
            'patient_contact': appointment.patient.contact,
            'patient_email': appointment.patient.email,
            'date_time': f"{appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.appointment_time.strftime('%I:%M %p')}",
            'status': appointment.status.title(),
            'reason': appointment.reason
        }
        
        return JsonResponse({
            'success': True,
            'appointment': appointment_data
        })
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Appointment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
        
        
        
