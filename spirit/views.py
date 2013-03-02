from __future__ import division
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.conf import settings
from wrapper import *
from django import forms

from django.core.cache import cache

from django.forms.widgets import RadioSelect



class SpiritForm(forms.Form):
    CHOICES=((0, '0 - poor'),
             (1, '1 - not so good'),
             (2, '2 - good'),
             (3, '3 - very good'),
             (4, '4 - excellent'))
    SPIRIT_CHOICES = ((0, '0 - our spirit was much better'),
                     (1, '1 - our spirit was slightly better'),
                     (2, '2 -our spirit was the same'),
                     (3, '3 - our spirit was slightly worse'),
                     (4, '4 - our spirit was much worse'))
    spirit_rules = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_fouls = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_fair = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_attitude = forms.TypedChoiceField(choices=CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_our = forms.TypedChoiceField(choices=SPIRIT_CHOICES, widget=RadioSelect, coerce=int,initial=2)
    spirit_score = forms.IntegerField(min_value=0,max_value=20, required=False)

#    team_giving = forms.TypedChoiceField(coerce=int, widget=HiddenInput)


import logging
from pprint import pformat

# Get an instance of a logger
logger = logging.getLogger('spirit')


def home(request):
    user_id=request.session.get('user_id',None)
       
    if user_id == None:
        redirect_uri='http://127.0.0.1:8000/'
        loginurl='{0}/oauth2/authorize/?client_id={1}&response_type=code&redirect_uri={2}&scope=universal'.format(settings.TOKEN_URL,settings.CLIENT_ID,settings.REDIRECT_URI)
        return render_to_response('spirit.html', {'loginurl': loginurl})
    else:
        team_players=api_team_playersbyplayer(user_id) 
        logger.info(pformat(team_players))       
        return render_to_response('spirit_loggedin.html', {'first_name': request.session['first_name'],
                                                           'team_players': team_players['objects']})
def logout(request):
    # flushes the session down the toilet
    # in particular, erases 'user_id', 'first_name', and 'access_token" and makes it inaccessible for following session
    request.session.flush()  
    
    return redirect('/')
        

def code(request):
    code=request.GET.get('code',None)
    if code != None:
        # retrieve authentication token
        access_token=api_token_from_code(request,code)
    return redirect('/')

def team(request,team_id):
    t=api_teambyid(team_id)
    games=api_gamesbyteam(team_id)
    for g in games['objects']:
        # retrieve spirit scores
        spirit=api_spiritbygame(g['id'])
        # figure out which is my team, which is the opponent
        if g['team_1_id']==int(team_id):
            g['opp_id']=g['team_2_id']
            g['opp']=g['team_2']
            g['my_score']=g['team_1_score']
            g['opp_score']=g['team_2_score']
        elif g['team_2_id']==int(team_id):
            g['opp_id']=g['team_1_id']
            g['opp']=g['team_1']
            g['my_score']=g['team_2_score']
            g['opp_score']=g['team_1_score']
        else:
            logger.error('at least one of the teams should be the one with id: {0}'.format(team_id))
        g['score_string']=score_string(g['my_score'],g['opp_score'])
        
        
    return render_to_response('team.html', {'team': t,
                                            'games': games['objects'],
                                            'first_name': request.session['first_name']})
def score_string(my_score,opp_score):
    # returns a string like "W 12-8" or "L 4-15" or "T 5-5"
    if int(my_score) > int(opp_score):
        sstring = u'W'
    elif int(my_score) < int(opp_score):
        sstring = u'L'
    else:
        sstring = u'T'
    return sstring + u' {0}-{1}'.format(my_score,opp_score)

def season(request,season_id):
    info = api_seasonbyid(season_id)
    # retrieve all games of this season
    games = api_gamesbyseason(season_id);
    logger.info(pformat(games))
    
    if (u'errors' in games):
        errmsg = '{0}'.format(games['errors'])
        return render_to_response('error.html',{'error': errmsg})
    else:
        # compute spirit score overview
        teams = TeamsFromGames(games['objects'])
        return render_to_response('tournament.html',{'type': 'Season', 'id': season_id, 'games': games['objects'], 'teams': teams, 'info': info})


def tournament(request,tournament_id):
    info = api_tournamentbyid(tournament_id)
    # retrieve all games of this tournament
    spirit = api_spiritbytournament(tournament_id)
    games = api_gamesbytournament(tournament_id)
    logger.info(pformat(spirit))

    if (u'errors' in spirit):
        errmsg = '{0}'.format(spirit['errors'])
        return render_to_response('error.html',{'error': errmsg})
    else:
        # compute spirit score overview
        teams,games_wspirit = TeamsFromGames(spirit['objects'],games['objects'])
        return render_to_response('tournament.html',{'type': 'Tournament', 'id': tournament_id, 'games': games_wspirit, 'teams': teams, 'info': info})

def game(request,game_id):
    # retrieve this game
    game = api_gamebyid(game_id);
 
    if (u'errors' in game):
        errmsg = '{0}'.format(game_id)
        return render_to_response('error.html',{'error': errmsg})
    
    user_id=request.session.get('user_id',None)
    if user_id != None:
        # determine from the user_id which team he belongs to
        team_players=api_team_playersbyplayer(user_id) 
        for tp in team_players['objects']:
            if tp['team_id']==game['team_1_id']:
                team_giving=u'1'
                break
            elif tp['team_id']==game['team_2_id']:
                team_giving=u'2'
                break
            
    spirit=api_spiritbygame(game_id)
    for s in spirit['objects']:
        if not 'team_1_spirit' in game and s['team_1_score']!='':
            game['team_1_spirit']=s['team_1_score']
        if not 'team_2_spirit' in game and s['team_2_score']!='':
            game['team_2_spirit']=s['team_2_score']
    
    return render_to_response('game.html', {'game': game, 'spirit': spirit})

def game_submit(request,game_id,team_giving):
    # retrieve this game
    game = api_gamebyid(game_id);
 
    if (u'errors' in game):
        errmsg = '{0}'.format(game_id)
        return render_to_response('error.html',{'error': errmsg})
    else:
        user_id=request.session.get('user_id',None)
        if team_giving==u'' and user_id==None:
            logger.error('the team giving the spirit could not been determined, setting to default 1')
            team_giving=u'1'
        elif user_id != None:
            # determine from the user_id which team he belongs to
            team_players=api_team_playersbyplayer(user_id) 
            for tp in team_players['objects']:
                if tp['team_id']==game['team_1_id']:
                    team_giving=u'1'
                    break
                elif tp['team_id']==game['team_2_id']:
                    team_giving=u'2'
                    break
        if request.method == 'POST': # If the form has been submitted...
            form = SpiritForm(request.POST) # A form bound to the POST data
#            form.fields['team_giving'].choices=((1,game['team_1']['name']),(2,game['team_2']['name']))
            if form.is_valid(): # All validation rules pass
                # Processing the data in form.cleaned_data
                logger.info(pformat(form.cleaned_data))
                scores=[form.cleaned_data['spirit_rules'],form.cleaned_data['spirit_fouls'],form.cleaned_data['spirit_fair'],form.cleaned_data['spirit_attitude'],form.cleaned_data['spirit_our']]
                data={'team_1_id': game['team_1_id'],
                      'team_2_id': game['team_2_id']}
                if team_giving==u'1':
                    data['team_2_score']=scores
                elif team_giving==u'2':
                    data['team_1_score']=scores
                logger.info(api_addspirit(game['id'],data))
                    
                return HttpResponseRedirect('/tournament/{0}/'.format(game['tournament_id'])) # Redirect after POST
        else:
            form = SpiritForm() # An unbound form
            spirit = api_spiritbygame(game_id)
            if spirit['meta']['total_count']>0:
                for score in spirit['objects']:
                    if team_giving==u'1':
                        if score['team_2_score']!=u'':
                            scores=json.loads(score['team_2_score'])
                            form.fields['spirit_rules'].initial=scores[0]
                            form.fields['spirit_fouls'].initial=scores[1]
                            form.fields['spirit_fair'].initial=scores[2]
                            form.fields['spirit_attitude'].initial=scores[3]
                            form.fields['spirit_our'].initial=scores[4]
                    elif team_giving==u'2':
                        if score['team_1_score']!=u'':
                            scores=json.loads(score['team_1_score'])
                            form.fields['spirit_rules'].initial=scores[0]
                            form.fields['spirit_fouls'].initial=scores[1]
                            form.fields['spirit_fair'].initial=scores[2]
                            form.fields['spirit_attitude'].initial=scores[3]
                            form.fields['spirit_our'].initial=scores[4]
                    
#            form.fields['team_giving'].choices=((1,game['team_1']['name']),(2,game['team_2']['name']))

        if team_giving==u'1':
            team_giving_name=game['team_1']['name']
            team_receiving_name=game['team_2']['name']
        elif team_giving==u'2':
            team_giving_name=game['team_2']['name']
            team_receiving_name=game['team_1']['name']
        return render(request, 'game_submit.html', {
            'form': form,
            'game': game,
            'team_giving': team_giving,
            'team_giving_name': team_giving_name,
            'team_receiving_name': team_receiving_name
        })

def TeamsFromGames(spirit,games):
    # computes a dictionary of team names and accumulated spirit scores from the data in games
    teams={}
    for score in spirit:
        if score['team_1_id']!=None and score['team_2_id']!=None:
            if not score['team_1_id'] in teams:
                teams[score['team_1_id']]={'name': score['team_1']['name'],
                                           'received': {},
                                           'given': {}}
            if not score['team_2_id'] in teams:
                teams[score['team_2_id']]={'name': score['team_2']['name'],
                                           'received': {},
                                           'given': {}}
            if score['team_1_score']!=u'':
                # decode string into list
                team_1_score=json.loads(score['team_1_score'])
                # double check
                if len(team_1_score)<=1:
                    logger.error('decoding did probably not work!')
                if score['game_id'] in teams[score['team_1_id']]['received']:
                    logger.warning('spirit score for team_1 received of game id {0} has already been registered'.format(score['game_id']))
                teams[score['team_1_id']]['received'][score['game_id']]=team_1_score
                if score['game_id'] in teams[score['team_2_id']]['given']:
                    logger.warning('spirit score for team_2 given of game id {0} has already been registered and will be overwritten'.format(score['game_id']))
                teams[score['team_2_id']]['given'][score['game_id']]=team_1_score
            if score['team_2_score']!=u'':
                # decode string into list
                team_2_score=json.loads(score['team_2_score'])
                # double check
                if len(team_2_score)<=1:
                    logger.error('decoding did probably not work!')
                if score['game_id'] in teams[score['team_2_id']]['received']:
                    logger.warning('spirit score for team_2 received of game id {0} has already been registered and will be overwritten'.format(score['game_id']))
                teams[score['team_2_id']]['received'][score['game_id']]=team_2_score
                if score['game_id'] in teams[score['team_1_id']]['given']:
                    logger.warning('spirit score for team_1 given of game id {0} has already been registered and will be overwritten'.format(score['game_id']))
                teams[score['team_1_id']]['given'][score['game_id']]=team_2_score
            elif score['team_1_score']==u'':
                logger.warning('strangely, no team seems to have a spirit score...')
                
    for game in games:
        try:
            game['team_1_spirit']=teams[game['team_1_id']]['received'][game['id']]
        except KeyError:
            pass
        try:
            game['team_2_spirit']=teams[game['team_2_id']]['received'][game['id']]
        except KeyError:
            pass
        
    for id,team in teams.iteritems():
        teams[id]['nr_received']=len(team['received'])
        teams[id]['nr_given']=len(team['given'])
        if teams[id]['nr_received']>0:
            # compute averages, individually per entry of the list
            teams[id]['avg_received']=map(lambda x:sum(x)/teams[id]['nr_received'],zip(*team['received'].values()))
            teams[id]['avg_received_total']=sum(teams[id]['avg_received'])
        if teams[id]['nr_given']>0:
            teams[id]['avg_given']=map(lambda x:sum(x)/teams[id]['nr_given'],zip(*team['given'].values()))
            teams[id]['avg_given_total']=sum(teams[id]['avg_given'])
    logger.info(pformat(teams))
    return teams,games

def list_avg(list):
    # takes unicode list of lists and computes average
    return list
            