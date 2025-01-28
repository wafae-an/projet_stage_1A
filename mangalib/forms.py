from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User
from .models import Message

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Champs à afficher dans le formulaire

class PasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = [ 'body']  # On inclut seulement le sujet et le corps du message
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message...'}),
        }

