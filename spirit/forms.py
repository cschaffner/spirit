from __future__ import division
from django import forms
from django.forms.widgets import RadioSelect, Textarea


class SpiritForm(forms.Form):
    opponent_name = forms.CharField(max_length=100, required=False)
    game_start = forms.DateTimeField(required=False)
    occasion = forms.CharField(max_length=100, required=False)

    CHOICES=((0, '0 - Poor'),
             (1, '1 - Not Good'),
             (2, '2 - Good'),
             (3, '3 - Very Good'),
             (4, '4 - Excellent'))
    spirit_rules = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_fouls = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_fair = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_attitude = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_communication = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_score = forms.IntegerField(min_value=0,max_value=20, required=False)
    spirit_comment = forms.CharField(max_length=500, required=False, widget=Textarea)

