"""
Custom account views for Aether — themed register + profile hooks.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User
from apps.core.views import _get_site_data


class AetherRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm placeholder-white/40 focus:outline-none focus:border-[var(--accent-cyan)]',
        'placeholder': 'you@starlink.example'
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm placeholder-white/40 focus:outline-none focus:border-[var(--accent-cyan)]',
        'placeholder': 'First name (optional)'
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm placeholder-white/40 focus:outline-none focus:border-[var(--accent-cyan)]',
        'placeholder': 'Last name (optional)'
    }))

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the other fields like the custom ones
        for name in ['username', 'password1', 'password2']:
            if name in self.fields:
                self.fields[name].widget.attrs.update({
                    'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm placeholder-white/40 focus:outline-none focus:border-[var(--accent-cyan)]'
                })
        self.fields['username'].help_text = "Used for your flight log. Letters, numbers, @ . + - _ only."
        self.fields['email'].label = "Command Email"
        self.fields['username'].label = "Callsign / Username"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A explorer with this command frequency already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


def register(request):
    if request.user.is_authenticated:
        return redirect('learning:dashboard')

    if request.method == 'POST':
        form = AetherRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto login
            login(request, user)
            return redirect('learning:dashboard')
    else:
        form = AetherRegisterForm()

    site, *_ = _get_site_data()
    return render(request, 'accounts/register.html', {'form': form, 'site': site})
