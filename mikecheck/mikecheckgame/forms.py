from django import forms
from .models import JOIN_CODE_LENGTH

class TakeTurnForm(forms.Form):
    pass

class CreateGameForm(forms.Form):
    pass

class JoinGameForm(forms.Form):
    player = forms.CharField(max_length=255) # to match the player.handle field
    join_code = forms.CharField(max_length=JOIN_CODE_LENGTH)
