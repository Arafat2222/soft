from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# Add this to your urlpatterns list



urlpatterns = [
    path('', views.index, name='index'),
    path('admin_login/', views.admin_login, name='admin_login'), 
    path('admin_dashboard/',views.admin_dashboard,name = 'admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('manage_doctors/', views.manage_doctors, name='manage_doctors'),
    path('search_doctors/', views.search_doctors, name='search_doctors'),
    path('update_doctor/<int:doctor_id>/', views.update_doctor, name='update_doctor'),
    path('delete_doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('doctor_details/<int:doctor_id>/', views.doctor_details, name='doctor_details'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('add_category/', views.add_category, name='add_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('doctor_categories/', views.doctor_categories, name='doctor_categories'),
    path('general_user_login/', views.general_user_login, name='general_user_login'),
    path('general_user_signup/', views.general_user_signup, name='general_user_signup'),
    path('general_user_home/', views.user_home, name='user_home'),
    path('general_user_logout/', views.general_user_logout, name='general_user_logout'),
    path('doctor_home/', views.doctor_home, name='doctor_home'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('get-available-slots/<int:doctor_id>/<str:date>/', views.get_available_slots, name='get_available_slots'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('update-appointment-status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('doctor/get-details/', views.get_doctor_details, name='get_doctor_details'),
    path('doctor/update-profile/', views.update_doctor_profile, name='update_doctor_profile'),
    path('chat-with-gemini/', views.chat_with_gemini, name='chat_with_gemini'),
    path('appointment-details/<int:appointment_id>/', views.appointment_details, name='appointment_details'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
