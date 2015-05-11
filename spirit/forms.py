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

    help_text =  "<span class='ex0'>Examples(0): The opposing team always took the stance that they were right on calls. When asked, teammates did not give their opinion on calls where the result could have gone against their team. They made many unjustifiable calls/contests. They made retaliatory calls. They frequently fouled and/or made calls for tactical reasons. They unduly delayed the game for tactical reasons. </span>"
    help_text += "<span class='ex1'>Examples(1): They often gave the impression they would only see things in a manner favorable to their team. They made a few unjustifiable calls/contests. They were not consistent in their calls throughout the game. They were quick to complain when we made a call, irrespective of the appropriateness of the call. </span>"
    help_text += "<span class='ex2'>Examples(2): They didn't call breaches that did not affect the outcome of the action, such as a minimal travel on an unmarked thrower, or fouls on throws they made that would not have been caught anyway. They respected and acknowledged our opinions on calls, even when they disagreed. They apologized in situations where it was appropriate (like an uncontested foul). They adjusted their behavior based on our feedback in a way that improved the enjoyment of the game. </span>"
    help_text += "<span class='ex3'>Examples(3): There was at least one case where they informed teammates when they made wrong or unnecessary calls/contests. They retracted calls when they thought they were wrong. </span>"
    help_text += "<span class='ex4'>Examples(4): There were several clear examples of opposition players seeking to uphold the truth of the situation, even if it did not benefit them. They remained fair-minded even in crucial situations (eg. Universe point). </span>"
    spirit_fair = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                         label="Fair-Mindedness",
                                          help_text=mark_safe(help_text))

    help_text =  "<span class='ex0'>Examples(0): Players and/or their sideline were often rude and discourteous towards opponents, their own teammates, officials, volunteers, organizers, and/or spectators. Physical confrontation occurred on/off the field. Several instances of edge-down spiking, or aggressive celebration towards opponent. Several instances of deliberately damaging equipment. They played in a patronizing manner (e.g. scoober only points, trick plays, etc...). </span>"
    help_text += "<span class='ex1'>Examples(1): Players and/or sideline sometimes exhibited a lack of self-control and positive attitude towards opponents, their own teammates, officials, volunteers, organizers, and/or spectators. They actively celebrated our errors to humiliate players. A few instances of edge-down spiking or aggressive celebration towards opponent. A few instances of deliberately damaging equipment. </span>"
    help_text += "<span class='ex2'>Examples(2): Players and/or sideline generally exhibited self-control and positive attitude towards opponents, officials, and spectators. Opposing team left an overall positive impression during and after the game, e.g. during the Spirit circle. They were polite to us, their teammates, officials and spectators. They thanked us for the game. They played with appropriate intensity irrespective of the score. </span>"
    help_text += "<span class='ex3'>Examples(3): They introduced themselves to us. They complimented us on a good play or celebrated good plays by either team in a positive manner. There were 1-2 instances where they clearly showed very good self-control. </span>"
    help_text += "<span class='ex4'>Examples(4): Demonstrated excellent self control on the field during potentially stressful situations. Highest level of self-control and positive attitude shown throughout game towards opponents, officials, and spectators. </span>"
    spirit_attitude = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                             label="Positive Attitude and Self-Control",
                                          help_text=mark_safe(help_text))

    help_text =  "<span class='ex0'>Examples(0): They frequently refused to discuss issues/calls. They got angry/reacted with contempt at several calls/contests. They frequently used offensive language. Their body language was frequently rude or aggressive, such as smirking or making offensive hand gestures. </span>"
    help_text += "<span class='ex1'>Examples(1): Players not involved in the play got involved without having best perspective or being asked/getting permission several times. There were a few instances where they were not calm while communicating. There were a few instances where their body language was rude or aggressive, such as smirking or making offensive hand gestures. They did not keep to discussion time limits. </span>"
    help_text += "<span class='ex2'>Examples(2): Conflicts were resolved without incident. They communicated respectfully. They listened. They kept to discussion time limits. They clearly explained their point of view. The sideline/other players helped out when asked. </span>"
    help_text += "<span class='ex3'>Examples(3): They provided evidence to support their calls. They communicated their point of view effectively and calmly. Their captain/leaders communicated with our leaders very effectively. They brought up spirit issues and general concerns as early as possible. </span>"
    help_text += "<span class='ex4'>Examples(4): They explained the game to spectators and newcomers. They motivated us to keep high spirit and suggested concrete examples on how to do it. They communicated very effectively and made us feel comfortable discussing the game. They properly used official hand signals to indicate fouls, scores, etc.... </span>"
    spirit_communication = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int, initial=2,
                                                  label="Communication",
                                          help_text=mark_safe(help_text))
    spirit_score = forms.IntegerField(min_value=0, max_value=20, required=False)
    spirit_comment = forms.CharField(max_length=500, required=False, widget=Textarea,
                                     label="Comment Box",
                                     help_text="If you have selected 0 or 4 in any category, please explain in few words what happened. Compliments as well as negative feedback will be passed to the teams in the appropriate manner.")

