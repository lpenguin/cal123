from django import forms
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class EventForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Event name"}))
    description = forms.CharField(widget=forms.Textarea, required=False)
    begin_date = forms.DateTimeField(widget=forms.TextInput(attrs={'placeholder': "Event begin date"}))
    end_date = forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'placeholder': "Event end date"}))

#class RegistrationForm(forms.Form):
#    login = forms.CharField()
#    password = forms.CharField(widget=forms.PasswordInput() )
#    email = forms.CharField(validators=[validate_email])

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput() )