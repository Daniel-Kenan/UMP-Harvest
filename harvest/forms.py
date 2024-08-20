from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email Address')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')



# forms.py
# forms.py
from django import forms
from .models import User

class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'style': 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem;'
        }),
        min_length=6
    )
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repeat Password',
            'style': 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem;'
        }),
        min_length=6
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': "w-full px-4 py-2 rounded-lg bg-gray-200 mt-2 border focus:border-blue-500 focus:bg-white focus:outline-none" ,
                'placeholder': 'Username',
                'style': 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem;'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First Name',
                'style': 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem;'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last Name',
                'style': 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem;'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone Number',
                'style': 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem;'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email Address',
                'style': 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem;'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')

        if password != repeat_password:
            self.add_error('repeat_password', "Passwords do not match")



from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'rating', 'parent']  # Include 'parent' field for replies
    
    def __init__(self, *args, **kwargs):
        # Allow parent field to be set dynamically
        parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        if parent:
            self.fields['parent'].initial = parent

    def clean(self):
        cleaned_data = super().clean()
        comment = cleaned_data.get('comment')
        if not comment:
            raise forms.ValidationError('Comment field cannot be empty.')
        return cleaned_data
