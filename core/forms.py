from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Apartment, Reservation, Message


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription utilisateur"""
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('proprietaire', 'Propriétaire'), ('client', 'Client')],
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']


class ApartmentForm(forms.ModelForm):
    """Formulaire de création/modification d'appartement"""
    class Meta:
        model = Apartment
        fields = ['title', 'description', 'address', 'city', 'price_per_night', 
                  'bedrooms', 'max_guests', 'photos']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'address': forms.TextInput(attrs={'placeholder': 'Adresse complète'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ville'}),
            'title': forms.TextInput(attrs={'placeholder': 'Titre de l\'annonce'}),
        }


class ReservationForm(forms.ModelForm):
    """Formulaire de réservation"""
    class Meta:
        model = Reservation
        fields = ['check_in_date', 'check_out_date', 'number_of_guests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError("La date de départ doit être postérieure à la date d'arrivée.")
        
        return cleaned_data


class MessageForm(forms.ModelForm):
    """Formulaire d'envoi de message"""
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'subject': forms.TextInput(attrs={'placeholder': 'Sujet du message'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Le champ receiver n'est pas nécessaire si on passe par l'URL
        if 'receiver' in self.fields:
            self.fields['receiver'].required = False
