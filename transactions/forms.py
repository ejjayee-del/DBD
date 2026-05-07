from django import forms
from .models import Visitor, VisitHistory


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'contact_number', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
        }


class VisitHistoryForm(forms.ModelForm):
    class Meta:
        model = VisitHistory
        fields = ['visitor', 'purpose_of_visit', 'notes']
        widgets = {
            'visitor': forms.Select(attrs={'class': 'form-control'}),
            'purpose_of_visit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose of Visit'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notes', 'rows': 4}),
        }


class HistorySearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or purpose...',
            'id': 'searchInput'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
