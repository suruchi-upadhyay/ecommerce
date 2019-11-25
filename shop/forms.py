from django.forms import ModelForm
from django.forms import ChoiceField
from shop.models import User

from django import forms


class TypeForm(forms.Form):
    type = ChoiceField(choices=[(x, x) for x in ['Customer', 'Vendor']])


class UserForm(ModelForm, TypeForm):

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(ModelForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:

            user.save()
        return user

    class Meta:

        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
            'type',

        ]

    def __str__(self):
        return self.name
