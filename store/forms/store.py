from curses.ascii import isdigit
from django.forms import ModelForm, ValidationError
from ..models import Store
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description', 'phone', 'address']
    
    def clean_phone(self):
        data = self.cleaned_data['phone']
        for char in data:
            if not isdigit(char):
                raise ValidationError(_('Phone number must be numeric'))
        return data