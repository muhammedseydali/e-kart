from importlib.metadata import files
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','phone','email','address_line','address_line2','country','state','city','order_note']