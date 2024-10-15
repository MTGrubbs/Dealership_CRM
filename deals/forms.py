from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from deals.models import Deal, Manager, Salesperson

class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
#        fields = ['car_type', 'recap_number', 'date', 'stock_number', 'customer_name', 'vehicle_model', 
#                  'manager', 'salesperson', 'gross', 'has_trade', 'trade_make', 
#                  'trade_model', 'trade_value']
        exclude = ['recap_number']
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DealForm, self).__init__(*args, **kwargs)
        if user and not user.has_perm('deals.view_all_deals'):
            del self.fields['manager']
            del self.fields['salesperson']

class UserRegistrationForm(UserCreationForm):
    ROLES = (
        ('manager', 'Manager'),
        ('salesperson', 'Salesperson'),
    )
    role = forms.ChoiceField(choices=ROLES)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['role', 'username', 'first_name', 'last_name', 'password1', 'password2']

class ManagerForm(forms.ModelForm):
    class Meta:
        model = Manager
        fields = []  # Leave this empty if Manager model doesn't have additional fields

class SalespersonForm(forms.ModelForm):
    class Meta:
        model = Salesperson
        fields = []  # Leave this empty if Salesperson model doesn't have additional fields