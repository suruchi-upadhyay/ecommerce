from django.forms import ModelForm

from shop.models import User

class UserForm(ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password',
        
        ]


    def __str__(self):
        return self.name
