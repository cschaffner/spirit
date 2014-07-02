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
    spirit_rules = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                          label="Rules Knowledge and Use", help_text="Examples: They did not purposefully misinterpret the rules. They kept to time limits. When they didn't know the rules they showed a real willingness to learn")
    spirit_fouls = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                          label="Fouls and Body Contact", help_text="Examples: They avoided fouling, contact, and dangerous plays.")
    spirit_fair = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                         label="Fair-Mindedness", help_text="Examples: They apologized in situations where it was appropriate, informed teammates about wrong/unnecessary calls. Only called significant breaches")
    spirit_attitude = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                             label="Positive Attitude and Self-Control", help_text="Examples: They were polite. They played with appropriate intensity irrespective of the score. They left an overall positive impression during and after the game.")
    spirit_communication = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                                  label="Communication", help_text="Examples: They communicated respectfully. They listened. They kept to discussion time limits.")
    spirit_score = forms.IntegerField(min_value=0,max_value=20, required=False)
    spirit_comment = forms.CharField(max_length=500, required=False, widget=Textarea,
                                     label="Comment Box", help_text="If you have selected 0 or 4 in any category, please explain in few words what happened. Compliments as well as negative feedback will be passed to the teams in the appropriate manner.")

