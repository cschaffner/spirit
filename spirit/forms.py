from __future__ import division
from django import forms
from django.forms.widgets import RadioSelect, Textarea
from django.utils.html import mark_safe

class SpiritForm(forms.Form):
    opponent_name = forms.CharField(max_length=100, required=False)
    game_start = forms.DateTimeField(required=False)
    occasion = forms.CharField(max_length=100, required=False)

    CHOICES = ((0, '0 - Poor'),
               (1, '1 - Not Good'),
               (2, '2 - Good'),
               (3, '3 - Very Good'),
               (4, '4 - Excellent'))

    help_text =  "<span class='ex0'>Examples(0): They repeatedly exhibited poor knowledge of the rules. They often disregarded or purposefully misinterpreted the rules. They refused to learn details of the rules and SOTG. </span>"
    help_text += "<span class='ex1'>Examples(1): For the level of play they showed a general lack of rules knowledge. They disregarded or purposefully misinterpreted the rules during the game a few times. They were resistant to being taught rules or elements of SOTG. They didn't keep to time limit. They were Offside during pulls even after an initial warning. </span>"
    help_text += "<span class='ex2'>Examples(2): For the level of play they showed good knowledge of the rules. They did not purposefully misinterpret the rules. They kept to time limits. When they didn't know the rules, they showed a real willingness to learn them. </span>"
    help_text += "<span class='ex3'>Examples(3): For the level of play they showed an above average knowledge of the rules. There was at least one case where they helped us learn some of the rules we did not know. </span>"
    help_text += "<span class='ex4'>Examples(4): For the level of play they showed excellent knowledge of the rules. They abided by the rules throughout the game. They explained the rules we did not know very clearly, efficiently, and in a way that added to our joy of the game. </span>"
    spirit_rules = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                          label="Rules Knowledge and Use",
                                          help_text=mark_safe(help_text))

    help_text =  "<span class='ex0'>Examples(0): Even after repeated calls they continued to have the same foul or contact issues. There were several instances of dangerous or reckless plays. They made little effort to avoid body contact. </span>"
    help_text += "<span class='ex1'>Examples(1): The amount of non-incidental body contact was a bit too much. There were a few instances of dangerous or reckless plays. </span>"
    help_text += "<span class='ex2'>Examples(2): Nothing significant occurred beyond incidental contact. </span>"
    help_text += "<span class='ex3'>Examples(3): There was at least one clear case of thoughtful contact avoidance. </span>"
    help_text += "<span class='ex4'>Examples(4): There were several clear cases of thoughtful contact avoidance. They played in a style that avoided the potential for both fouls and unnecessary body contact. </span>"
    spirit_fouls = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                          label="Fouls and Body Contact",
                                          help_text=mark_safe(help_text))

    help_text =  "<span class='ex0'>Examples(0): . </span>"
    help_text += "<span class='ex1'>Examples(1): . </span>"
    help_text += "<span class='ex2'>Examples(2): . </span>"
    help_text += "<span class='ex3'>Examples(3): . </span>"
    help_text += "<span class='ex4'>Examples(4): . </span>"
    spirit_fair = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                         label="Fair-Mindedness",
                                         help_text="Examples: They apologized in situations where it was appropriate, informed teammates about wrong/unnecessary calls. Only called significant breaches")

    help_text =  "<span class='ex0'>Examples(0): . </span>"
    help_text += "<span class='ex1'>Examples(1): . </span>"
    help_text += "<span class='ex2'>Examples(2): . </span>"
    help_text += "<span class='ex3'>Examples(3): . </span>"
    help_text += "<span class='ex4'>Examples(4): . </span>"
    spirit_attitude = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                             label="Positive Attitude and Self-Control",
                                             help_text="Examples: They were polite. They played with appropriate intensity irrespective of the score. They left an overall positive impression during and after the game.")

    help_text =  "<span class='ex0'>Examples(0): . </span>"
    help_text += "<span class='ex1'>Examples(1): . </span>"
    help_text += "<span class='ex2'>Examples(2): . </span>"
    help_text += "<span class='ex3'>Examples(3): . </span>"
    help_text += "<span class='ex4'>Examples(4): . </span>"
    spirit_communication = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                                  label="Communication",
                                                  help_text="Examples: They communicated respectfully. They listened. They kept to discussion time limits.")
    spirit_score = forms.IntegerField(min_value=0, max_value=20, required=False)
    spirit_comment = forms.CharField(max_length=500, required=False, widget=Textarea,
                                     label="Comment Box",
                                     help_text="If you have selected 0 or 4 in any category, please explain in few words what happened. Compliments as well as negative feedback will be passed to the teams in the appropriate manner.")

