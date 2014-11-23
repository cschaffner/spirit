from __future__ import division
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.utils.dateparse import parse_datetime, parse_date
from django.forms.formsets import formset_factory
from django.core.cache import cache
from django.views.generic.base import RedirectView

from operator import itemgetter
from datetime import datetime, timedelta
from forms import SpiritForm
from spirit_wrapper import api_recent_tournaments, api_recent_games, api_team_playersbyplayer, api_token_from_code, \
    api_teambyid, api_gamesbyteam, api_spiritbygame, api_addspirit, api_seasonbyid, api_spiritbyseason, \
    api_gamesbyseason_restricted, api_tournamentbyid, api_spiritbytournament, api_gamesbytournament, api_gamebyid, \
    api_getspiritbyid, api_deletespirit
from pprint import pformat
import json
import settings
import logging



# Get an instance of a logger
logger = logging.getLogger('spirit')


class MyRedirectView(RedirectView):

    permanent = True
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        url = super(MyRedirectView, self).get_redirect_url(*args, **kwargs)
        return '{0}{1}/'.format(url, kwargs.get('id', None))


def home(request):
    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    recent_tournaments = api_recent_tournaments(20)
    recent_games = api_recent_games(10)

    context = {}
    if recent_tournaments['meta']['total_count'] > 0:
        context['recent_tournaments'] = recent_tournaments['objects']
    if recent_games['meta']['total_count'] > 0:
        context['recent_games'] = recent_games['objects']

    if user_id == None or user_first_name == None:
        context['loginurl'] = settings.LOGINURL
        return render_to_response('spirit.html', context)
    else:
        context['user_first_name'] = user_first_name
        context['team_players'] = api_team_playersbyplayer(user_id)['objects']
        return render_to_response('spirit_loggedin.html', context)


def instructions(request):
    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    return render_to_response('instructions.html',
                              {'user_first_name': user_first_name,
                               'user_id': user_id})


def login(request):
    # #  disable
    # return render_to_response('spirit_wwx.html', {'loginurl': settings.LOGINURL})
    return redirect(settings.LOGINURL)


def logout(request):
    # flushes the session down the toilet
    # in particular, erases 'user_id', 'user_first_name', and 'access_token" and makes it inaccessible for following session
    request.session.flush()

    return redirect('/')


def code(request):
    code = request.GET.get('code', None)
    if code != None:
        # retrieve authentication token
        access_token = api_token_from_code(request, code)
    return redirect('/')


def team(request, team_id):
    t = api_teambyid(team_id)
    games = api_gamesbyteam(team_id)
    # remove BYE games, as those are irrelavant for spirit scores:
    games['objects'] = [g for g in games['objects'] if g['team_2_id']]

    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    user_teamids = request.session.get('user_teamids', [])

    game_ids = []
    for g in games['objects']:
        g['datetime'] = parse_datetime(g['start_time'])
        # make a list of game_ids so that all those spirit scores can be retrieved later in one query
        game_ids.append(g['id'])
        # figure out which is my team, which is the opponent
        if g['team_1_id'] == int(team_id):
            g['my_team'] = 1
            g['opp_team'] = 2
            g['opp_id'] = g['team_2_id']
            g['opp'] = g['team_2']
            g['my_score'] = g['team_1_score']
            g['opp_score'] = g['team_2_score']
            if g['team_1_id'] in user_teamids:
                g['spirit_given_editable'] = True
            if g['team_2_id'] in user_teamids:
                g['spirit_received_editable'] = True
        elif g['team_2_id'] == int(team_id):
            g['my_team'] = 2
            g['opp_team'] = 1
            g['opp_id'] = g['team_1_id']
            g['opp'] = g['team_1']
            g['my_score'] = g['team_2_score']
            g['opp_score'] = g['team_1_score']
            if g['team_2_id'] in user_teamids:
                g['spirit_given_editable'] = True
            if g['team_1_id'] in user_teamids:
                g['spirit_received_editable'] = True
        else:
            logger.error('at least one of the teams should be the one with id: {0}'.format(team_id))
        g['score_string'] = score_string(g['my_score'], g['opp_score'])

    # retrieve spirit score of all games in game_ids
    spirit = api_spiritbygame(game_ids)

    for g in games['objects']:
        if g['team_1_id'] == int(team_id):
            for s in spirit['objects']:
                if s['game_id'] == g['id']:
                    if not 'spirit_received' in g and s['team_1_score'] != u'':
                        g['spirit_received'] = json.loads(s['team_1_score'])
                    if not 'spirit_given' in g and s['team_2_score'] != u'':
                        g['spirit_given'] = json.loads(s['team_2_score'])
        elif g['team_2_id'] == int(team_id):
            for s in spirit['objects']:
                if s['game_id'] == g['id']:
                    if not 'spirit_received' in g and s['team_2_score'] != u'':
                        g['spirit_received'] = json.loads(s['team_2_score'])
                    if not 'spirit_given' in g and s['team_1_score'] != u'':
                        g['spirit_given'] = json.loads(s['team_1_score'])
        else:
            logger.error('at least one of the teams should be the one with id: {0}'.format(team_id))

    return render_to_response('team.html', {'team': t,
                                            'games': games['objects'],
                                            'user_first_name': user_first_name})


def team_date(request, team_id, year, month, day):
    team = api_teambyid(team_id)
    all_games = api_gamesbyteam(team_id)
    # remove BYE games, as those are irrelavant for spirit scores:
    all_games['objects'] = [g for g in all_games['objects'] if g['team_2_id']]

    # filter games on particular date
    games = []
    for game in all_games['objects']:
        game['datetime'] = parse_datetime(game['start_time'])
        if (game['datetime'].day == int(day) and game['datetime'].month == int(month) and game['datetime'].year == int(
                year)):
            if int(game['team_1_id']) == int(team['id']):
                game['my_team'] = 1
            elif int(game['team_2_id']) == int(team['id']):
                game['my_team'] = 2
            else:
                raise Exception('team {0} should be one of the two teams in game {1}'.format(team['name'], game['id']))
            games.append(game)

    # sort games according to start time
    games = sorted(games, key=itemgetter('datetime'))

    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    access_token = request.session.get('access_token', None)

    if not user_id:
        return render_to_response('error_login.html')

    SpiritFormSet = formset_factory(SpiritForm, extra=len(games))

    if request.method == 'POST':  # If the form has been submitted...
        formset = SpiritFormSet(request.POST)  # A form bound to the POST data
        if formset.is_valid():  # All validation rules pass
            # Processing the data in form.cleaned_data
            for form, game in zip(formset, games):
                # logger.info(pformat(form.cleaned_data))
                scores = [form.cleaned_data['spirit_rules'], form.cleaned_data['spirit_fouls'],
                          form.cleaned_data['spirit_fair'], form.cleaned_data['spirit_attitude'],
                          form.cleaned_data['spirit_communication']]
                data = {'team_1_id': game['team_1_id'],
                        'team_2_id': game['team_2_id']}
                if game['my_team'] == 1:
                    data['team_2_score'] = scores
                    data['team_2_comment'] = form.cleaned_data['spirit_comment']
                else:
                    data['team_1_score'] = scores
                    data['team_1_comment'] = form.cleaned_data['spirit_comment']
                logger.info(api_addspirit(access_token, game['id'], data))

            return HttpResponseRedirect('/teams/{0}/'.format(team['id']))  # Redirect after POST
    else:
        formset = SpiritFormSet()  # Unbound forms
        warning = None
        for form, game in zip(formset, games):
            form.fields['game_start'].initial = game['datetime']
            if game['datetime'] > datetime.now(game['datetime'].tzinfo):
                warning = 'One of the games has not started yet!'
            elif game['datetime'] < datetime.now(game['datetime'].tzinfo) - timedelta(settings.ALLOWED_DAYS_TO_ENTER):
                warning = 'One of the games was played already more than {0} days ago!'.format(settings.ALLOWED_DAYS_TO_ENTER)
            if game['tournament']:
                form.fields['occasion'].initial = game['tournament']['name']
            if game['swiss_round_id']:
                form.fields['occasion'].initial += ', Swissround {0}'.format(game['swiss_round']['round_number'])

            if game['my_team'] == 1:
                form.fields['opponent_name'].initial = game['team_2']['name']
            else:
                form.fields['opponent_name'].initial = game['team_1']['name']
            form.fields['opponent_name'].disabled = True

            spirit = api_spiritbygame(game['id'])
            if spirit['meta']['total_count'] > 0:
                # spirit scores are sorted according to time_last_updated
                # so we go through the list and take the first one that matches
                team_1_scores = []
                team_2_scores = []
                for score in spirit['objects']:
                    if game['my_team'] == 1:
                        if score['team_2_score'] != u'' and team_2_scores == []:
                            team_2_scores = json.loads(score['team_2_score'])
                            form.fields['spirit_rules'].initial = team_2_scores[0]
                            form.fields['spirit_fouls'].initial = team_2_scores[1]
                            form.fields['spirit_fair'].initial = team_2_scores[2]
                            form.fields['spirit_attitude'].initial = team_2_scores[3]
                            form.fields['spirit_communication'].initial = team_2_scores[4]
                            form.fields['spirit_comment'].initial = score['team_2_comment']
                    elif game['my_team'] == 2:
                        if score['team_1_score'] != u'' and team_1_scores == []:
                            team_1_scores = json.loads(score['team_1_score'])
                            form.fields['spirit_rules'].initial = team_1_scores[0]
                            form.fields['spirit_fouls'].initial = team_1_scores[1]
                            form.fields['spirit_fair'].initial = team_1_scores[2]
                            form.fields['spirit_attitude'].initial = team_1_scores[3]
                            form.fields['spirit_communication'].initial = team_1_scores[4]
                            form.fields['spirit_comment'].initial = score['team_1_comment']

    return render(request, 'team_date_submit.html', {
        'formset': formset,
        'user_first_name': user_first_name,
        'team': team,
        'year': year,
        'month': month,
        'day': day,
        'warning': warning,
    })


def score_string(my_score, opp_score):
    # returns a string like "W 12-8" or "L 4-15" or "T 5-5"
    if int(my_score) > int(opp_score):
        sstring = u'W'
    elif int(my_score) < int(opp_score):
        sstring = u'L'
    else:
        sstring = u'T'
    return sstring + u' {0}-{1}'.format(my_score, opp_score)


def season(request, season_id):
    info = api_seasonbyid(season_id)
    # retrieve all games of this season
    spirit = api_spiritbyseason(season_id)
    games = api_gamesbyseason_restricted(season_id)

    # logger.info(pformat(spirit))

    if (u'errors' in spirit):
        errmsg = '{0}'.format(spirit['errors'])
        return render_to_response('error.html', {'error': errmsg})

    # remove BYE games, as those are irrelevant for spirit scores:
    games['objects'] = [g for g in games['objects'] if g['team_2_id']]

    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    user_teamids = request.session.get('user_teamids', [])
    for g in games['objects']:
        g['datetime'] = parse_datetime(g['start_time'])
        g['team_1_spirit_editable'] = g['team_2_id'] in user_teamids
        g['team_2_spirit_editable'] = g['team_1_id'] in user_teamids

    # compute spirit score overview
    teams, games_wspirit = TeamsFromGames(spirit['objects'], games['objects'])
    return render_to_response('season.html', {'user_first_name': user_first_name,
                                              'id': season_id,
                                              'games': games_wspirit,
                                              'teams': teams,
                                              'info': info})


def tournament(request, tournament_id):
    info = api_tournamentbyid(tournament_id)
    info[u'start_datetime'] = parse_date(info['start_date'])
    info[u'end_datetime'] = parse_date(info['end_date'])
    # retrieve all games of this tournament
    spirit = api_spiritbytournament(tournament_id)
    games = api_gamesbytournament(tournament_id)
    if (u'errors' in spirit):
        errmsg = '{0}'.format(spirit['errors'])
        return render_to_response('error.html', {'error': errmsg})

    # remove BYE games, as those are irrelevant for spirit scores:
    games['objects'] = [g for g in games['objects'] if g['team_2_id']]

    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    user_teamids = request.session.get('user_teamids', [])
    for g in games['objects']:
        g['datetime'] = parse_datetime(g['start_time'])
        g['team_1_spirit_editable'] = g['team_2_id'] in user_teamids
        g['team_2_spirit_editable'] = g['team_1_id'] in user_teamids

    # compute spirit score overview
    teams, games_wspirit = TeamsFromGames(spirit['objects'], games['objects'])
    return render_to_response('tournament.html', {'user_first_name': user_first_name,
                                                  'id': tournament_id,
                                                  'games': games_wspirit,
                                                  'teams': teams,
                                                  'info': info})


def result(request, tournament_id):
    info = api_tournamentbyid(tournament_id)
    # retrieve all games of this tournament
    spirit = api_spiritbytournament(tournament_id)
    games = api_gamesbytournament(tournament_id)
    # remove BYE games, as those are irrelevant for spirit scores:
    games['objects'] = [g for g in games['objects'] if g['team_2_id']]

    if (u'errors' in spirit):
        errmsg = '{0}'.format(spirit['errors'])
        return render_to_response('error.html', {'error': errmsg})

    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    user_teamids = request.session.get('user_teamids', [])
    for g in games['objects']:
        g['datetime'] = parse_datetime(g['start_time'])
        g['team_1_spirit_editable'] = g['team_2_id'] in user_teamids
        g['team_2_spirit_editable'] = g['team_1_id'] in user_teamids

    # compute spirit score overview
    teams, games_wspirit = TeamsFromGames(spirit['objects'], games['objects'])

    end_result = sorted(teams.iteritems(), key=lambda x: x[1].get('avg_received_total'), reverse=True)
    return render_to_response('result.html', {'teams': end_result})


def game(request, game_id):
    # retrieve this game
    game = api_gamebyid(game_id);

    if (u'errors' in game):
        errmsg = '{0}'.format(game_id)
        return render_to_response('error.html', {'error': errmsg})

    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    user_teamids = request.session.get('user_teamids', [])
    game['team_2_spirit_editable'] = game['team_1_id'] in user_teamids
    game['team_1_spirit_editable'] = game['team_2_id'] in user_teamids

    # if user_id != None:
    #        # determine from the user_id which team he belongs to
    #        team_players=api_team_playersbyplayer(user_id)
    #        for tp in team_players['objects']:
    #            if tp['team_id']==game['team_1_id']:
    #                team_giving=u'1'
    #                break
    #            elif tp['team_id']==game['team_2_id']:
    #                team_giving=u'2'
    #                break

    spirit = api_spiritbygame(game_id)
    for s in spirit['objects']:
        # list is sorted according to time_last_updated
        # so we can simply go through the list and take the first score that matches
        if not 'team_1_spirit' in game and s['team_1_score'] != '':
            game['team_1_spirit'] = s['team_1_score']
            game['team_1_comment'] = s['team_1_comment']
        if not 'team_2_spirit' in game and s['team_2_score'] != '':
            game['team_2_spirit'] = s['team_2_score']
            game['team_2_comment'] = s['team_2_comment']

    return render_to_response('game.html', {'loginurl': settings.LOGINURL,
                                            'user_first_name': user_first_name,
                                            'user_id': user_id,
                                            'game': game, 'spirit': spirit})


def game_submit(request, game_id, team_idx_giving):
    # retrieve this game
    game = api_gamebyid(game_id);

    if (u'errors' in game):
        errmsg = '{0}'.format(game_id)
        return render_to_response('error.html', {'error': errmsg})

    user_id = request.session.get('user_id', None)
    user_first_name = request.session.get('user_first_name', None)
    access_token = request.session.get('access_token', None)
    if not user_id:
        return render_to_response('error_login.html')

    # user_team_ids=request.session.get('user_teamids',None)
    # if (team_idx_giving == u'1' and not game['team_1_id'] in user_team_ids):
    # return render_to_response('error.html', {'error': 'You have to be a member of team {0} in order to submit this spirit score (and you are not).'.format(game['team_1']['name'])})
    # if (team_idx_giving == u'2' and not game['team_2_id'] in user_team_ids):
    #     return render_to_response('error.html', {'error': 'You have to be a member of team {0} in order to submit this spirit score (and you are not).'.format(game['team_2']['name'])})

    if request.method == 'POST':  # If the form has been submitted...
        form = SpiritForm(request.POST)  # A form bound to the POST data
        #            form.fields['team_giving'].choices=((1,game['team_1']['name']),(2,game['team_2']['name']))
        if form.is_valid():  # All validation rules pass
            # Processing the data in form.cleaned_data
            logger.info(pformat(form.cleaned_data))
            scores = [form.cleaned_data['spirit_rules'], form.cleaned_data['spirit_fouls'],
                      form.cleaned_data['spirit_fair'], form.cleaned_data['spirit_attitude'],
                      form.cleaned_data['spirit_communication']]
            data = {'team_1_id': game['team_1_id'],
                    'team_2_id': game['team_2_id']}
            if team_idx_giving == u'1':
                data['team_2_score'] = scores
                data['team_2_comment'] = form.cleaned_data['spirit_comment']
            elif team_idx_giving == u'2':
                data['team_1_score'] = scores
                data['team_1_comment'] = form.cleaned_data['spirit_comment']
            logger.info(api_addspirit(access_token, game['id'], data))

            return HttpResponseRedirect('/games/{0}/'.format(game_id))  # Redirect after POST
    else:
        form = SpiritForm()  # An unbound form
        game['datetime'] = parse_datetime(game['start_time'])
        form.fields['game_start'].initial = game['datetime']
        warning = None
        if game['datetime'] > datetime.now(game['datetime'].tzinfo):
            warning = 'Game has not started yet!'
        elif game['datetime'] < datetime.now(game['datetime'].tzinfo) - timedelta(settings.ALLOWED_DAYS_TO_ENTER):
            warning = 'Game was played already more than {0} days ago!'.format(settings.ALLOWED_DAYS_TO_ENTER)
        if game['tournament']:
            form.fields['occasion'].initial = game['tournament']['name']
        if game['swiss_round_id']:
            form.fields['occasion'].initial += ', Swissround {0}'.format(game['swiss_round']['round_number'])
        if team_idx_giving == u'1':
            form.fields['opponent_name'].initial = game['team_2']['name']
        elif team_idx_giving == u'2':
            form.fields['opponent_name'].initial = game['team_1']['name']

        spirit = api_spiritbygame(game_id)
        if spirit['meta']['total_count'] > 0:
            # spirit scores are sorted according to time_last_updated
            # so we go through the list and take the first one that matches
            team_1_scores = []
            team_2_scores = []
            for score in spirit['objects']:
                if team_idx_giving == u'1':
                    if score['team_2_score'] != u'' and team_2_scores == []:
                        team_2_scores = json.loads(score['team_2_score'])
                        form.fields['spirit_rules'].initial = team_2_scores[0]
                        form.fields['spirit_fouls'].initial = team_2_scores[1]
                        form.fields['spirit_fair'].initial = team_2_scores[2]
                        form.fields['spirit_attitude'].initial = team_2_scores[3]
                        form.fields['spirit_communication'].initial = team_2_scores[4]
                        form.fields['spirit_comment'].initial = score['team_2_comment']
                elif team_idx_giving == u'2':
                    if score['team_1_score'] != u'' and team_1_scores == []:
                        team_1_scores = json.loads(score['team_1_score'])
                        form.fields['spirit_rules'].initial = team_1_scores[0]
                        form.fields['spirit_fouls'].initial = team_1_scores[1]
                        form.fields['spirit_fair'].initial = team_1_scores[2]
                        form.fields['spirit_attitude'].initial = team_1_scores[3]
                        form.fields['spirit_communication'].initial = team_1_scores[4]
                        form.fields['spirit_comment'].initial = score['team_1_comment']

                        #            form.fields['team_giving'].choices=((1,game['team_1']['name']),(2,game['team_2']['name']))

    if team_idx_giving == u'1':
        team_giving = game['team_1']
        team_receiving = game['team_2']
    elif team_idx_giving == u'2':
        team_giving = game['team_2']
        team_receiving = game['team_1']
    return render(request, 'game_submit.html', {
        'form': form,
        'game': game,
        'user_first_name': user_first_name,
        'team_giving': team_giving,
        'team_idx_giving': team_idx_giving,
        'team_receiving': team_receiving,
        'warning': warning,
    })


def delete(request, score_id):
    access_token = request.session.get('access_token', None)
    if access_token is None:
        return render_to_response('error_unauthorized.html')

    spirit_score = api_getspiritbyid(score_id)
    game_id = spirit_score.get('game_id', None)
    if not game_id:
        return render_to_response('error.html',
                                  {
                                  'error': 'Spirit score with id {0} does not exist and can therefore not be deleted.'.format(
                                      score_id)})
    response = api_deletespirit(access_token, score_id)
    if response.status_code > 400:
        return render_to_response('error_unauthorized.html')

    # after adding a new spirit score, all bets about caching are off, we have to clear the cache
    # TODO: be more clever here and only clear affected caches...
    cache.clear()

    return HttpResponseRedirect('/games/{0}/'.format(game_id))  # Redirect after POST


def TeamsFromGames(spirit, games):
    # first go through the whole list and fill in missing team_id's
    # we should be able to get them from the according games
    for score in spirit:
        if score['team_1_id'] == None or score['team_2_id'] == None:
            for g in games:
                if g['id'] == score['game_id']:
                    score['team_1_id'] = g['team_1_id']
                    score['team_1'] = g['team_1']
                    score['team_2_id'] = g['team_2_id']
                    score['team_2'] = g['team_2']
                    break

                    # computes a dictionary of team names and accumulated spirit scores from the data in games
    teams = {}
    for score in spirit:
        # spirit scores are sorted by time_last_updated
        # so we simply go through the list and take the first score that matches
        if score['team_1_id'] != None and score['team_2_id'] != None:
            if not score['team_1_id'] in teams:
                teams[score['team_1_id']] = {'name': score['team_1']['name'],
                                             'id': score['team_1_id'],
                                             'received': {},
                                             'given': {}}
            if not score['team_2_id'] in teams:
                teams[score['team_2_id']] = {'name': score['team_2']['name'],
                                             'id': score['team_2_id'],
                                             'received': {},
                                             'given': {}}
            if score['team_1_score'] != u'':
                # decode string into list
                team_1_score = json.loads(score['team_1_score'])
                # double check
                if not _score_is_valid(team_1_score) or len(team_1_score) <= 1:
                    logger.error('decoding of {0} did probably not work!'.format(team_1_score))
                else:
                    if not score['game_id'] in teams[score['team_1_id']]['received']:
                        teams[score['team_1_id']]['received'][score['game_id']] = team_1_score
                    if not score['game_id'] in teams[score['team_2_id']]['given']:
                        teams[score['team_2_id']]['given'][score['game_id']] = team_1_score
            if score['team_2_score'] != u'':
                # decode string into list
                team_2_score = json.loads(score['team_2_score'])
                # double check                        
                if not _score_is_valid(team_2_score) or len(team_2_score) <= 1:
                    logger.error('decoding of {0} did probably not work!'.format(team_2_score))
                else:
                    if not score['game_id'] in teams[score['team_2_id']]['received']:
                        teams[score['team_2_id']]['received'][score['game_id']] = team_2_score
                    if not score['game_id'] in teams[score['team_1_id']]['given']:
                        teams[score['team_1_id']]['given'][score['game_id']] = team_2_score
            elif score['team_1_score'] == u'':
                logger.warning('strangely, no team seems to have a spirit score...')

    for game in games:
        try:
            game['team_1_spirit'] = teams[game['team_1_id']]['received'][game['id']]
        except KeyError:
            pass
        try:
            game['team_2_spirit'] = teams[game['team_2_id']]['received'][game['id']]
        except KeyError:
            pass

    for id, team in teams.iteritems():
        teams[id]['nr_received'] = len(team['received'])
        teams[id]['nr_given'] = len(team['given'])
        if teams[id]['nr_received'] > 0:
            # compute averages, individually per entry of the list
            teams[id]['avg_received'] = map(lambda x: sum(x) / teams[id]['nr_received'],
                                            zip(*team['received'].values()))
            teams[id]['avg_received_total'] = sum(teams[id]['avg_received'])
            teams[id]['avg_received'] = map(lambda x: round(x, 2), teams[id]['avg_received'])
        if teams[id]['nr_given'] > 0:
            teams[id]['avg_given'] = map(lambda x: sum(x) / teams[id]['nr_given'], zip(*team['given'].values()))
            teams[id]['avg_given_total'] = sum(teams[id]['avg_given'])
            teams[id]['avg_given'] = map(lambda x: round(x, 2), teams[id]['avg_given'])
    logger.debug(pformat(teams))
    return teams, games


def _score_is_valid(score):
    try:
        if len(score) != 5:
            return False
        for s in score:
            if not isinstance(s, int):
                return False
        return True
    except:
        return False


def list_avg(list):
    # takes unicode list of lists and computes average
    return list

