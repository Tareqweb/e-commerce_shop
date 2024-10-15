from django import forms
from django.forms import ModelForm, inlineformset_factory, TextInput, RadioSelect
from .models import DeliveryAddress, OrderStatus, CancelOrder, BillingAddress


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        exclude = ['user']


class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        exclude = ['billing_user']
        

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        exclude = ['order']
        widgets = {
            'expected_delivery_form': TextInput(attrs={'type': 'date'}),
            'expected_delivery_to': TextInput(attrs={'type': 'date'}),
            }

class PayPalPaymentsForm(forms.Form):
    order_id = forms.CharField(max_length=255)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)    
        self.fields['order_id'].widget = forms.HiddenInput()


class CancelOrderForm(forms.ModelForm):
    class Meta:
        model = CancelOrder
        exclude = ['user', 'vendor_order_product', 'product', 'is_accepted', 'is_rejected', 'cancel_amount']



