from django import forms
from .models import Doctor
from .models import General_User
class DoctorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = Doctor
        fields = ['full_name', 'username', 'email', 'degrees', 'experience', 'category', 'description', 'image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True
            



class GeneralUserSignupForm(forms.ModelForm):
    class Meta:
        model = General_User
        fields = ['full_name', 'email', 'contact', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if General_User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True
                   