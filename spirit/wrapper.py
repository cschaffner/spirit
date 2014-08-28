## this module contains leaguevine-calls
## operates on tournament_id basis
## todo: all Windmill logic should be kept out of here... 

from django.conf import settings
from django.core.cache import cache

from settings import CACHE_TIME

import requests
import logging
from sys import getsizeof
import csv
import itertools
import json
from pprint import pformat


logging.basicConfig(level=logging.DEBUG)
# Get an instance of a logger
logger = logging.getLogger('spirit')

access_token = cache.get('access_token')
# if access_token is None:
#     # Make a request for an access_token
#     if settings.OFFLINE:
#         access_token='offline'
#     else:
#         url=u'{0}/oauth2/token/?client_id={1}&client_secret={2}&grant_type=client_credentials&scope=universal'.format(settings.TOKEN_URL, settings.CLIENT_ID, settings.CLIENT_PWD)
#         r=requests.get(url)
#         # parse string into Python dictionary
#         r_dict = r.json()
#         access_token = r_dict.get('access_token')
#         cache.set('access_token', access_token)
#         cache.set('user_id', u'anonymous')
#         logger.info('in wrapper: retrieved a new access token: {0}'.format(access_token))
# else:
#     logger.info('in wrapper: retrieved token from cache')

session = requests.Session()
session.headers.update({'Authorization': 'bearer {0}'.format(access_token),
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'})

def api_token_from_code(request, code):
    global my_headers

    url=u'{0}/oauth2/token/?client_id={1}&client_secret={2}&code={3}&grant_type=authorization_code&redirect_uri={4}'.format(settings.TOKEN_URL, settings.CLIENT_ID, settings.CLIENT_PWD, code, settings.REDIRECT_URI)
    r=requests.get(url)
    # parse string into Python dictionary
    r_dict = r.json()
    access_token = r_dict.get('access_token')
    request.session['access_token']=access_token
    cache.set('access_token', access_token)
    logger.info('retrieved a new access token: {0}'.format(access_token))
    
    # determine user
    player = api_me(access_token)
    request.session['user_id']=player['id']
    request.session['user_first_name']=player['first_name']
    # for convenience, we also store a list of the user's team ids in the session
    user_teamids=[]
    team_playerids=api_team_playeridsbyplayer(player['id']) 
    for team_ids in team_playerids['objects']:
        user_teamids.append(team_ids['team_id'])
    request.session['user_teamids']=user_teamids

    # my_headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'bearer {0}'.format(access_token)}

    return access_token


def api_get(url):
    if cache.get(url):
        logger.debug('returning cached data ({0} bytes) from URL: {1}'.format(getsizeof(cache.get(url)), url))
        response_dict = cache.get(url)
    else:
        response = session.get(url)
        logger.info(response.elapsed)
        response_dict = response.json()
        cache.set(url, response_dict, CACHE_TIME)

    objects=response_dict['objects']
    while response_dict['meta']['next'] != None:
        next_url=response_dict['meta']['next']
        if cache.get(next_url):
            response_dict = cache.get(next_url)
        else:
            response = session.get(next_url)
            logger.info(response.elapsed)
            response_dict = response.json()
        objects=objects + response_dict['objects']
    response_dict['objects']=objects
    cache.set(url, response_dict, CACHE_TIME)
    return response_dict


def api_post(url, dict):
    response = session.post(url, data=json.dumps(dict))
    if response.status_code != requests.codes.created:
        logger.error(response.status_code)
        logger.error(response.text)
        response.raise_for_status()

    logger.info(pformat(response.json()))
    return response.json()


def api_delete(url):
    response = session.delete(url)
    if response.status_code != requests.codes.no_content:
        logger.error(response.status_code)
        logger.error(response.text)
        # response.raise_for_status()
    return response



def api_put(url, dict):
    response = session.put(url, data=json.dumps(dict))
    if response.status_code != requests.codes.accepted:
        logger.error(response.status_code)
        logger.error(response.text)
        response.raise_for_status()

    logger.info(pformat(response.json()))
    return response.json()


def api_update(url, updatedict={}):
    # first retrieves the data of an object
    # then merges the fields with updatedict
    # and PUTs it again
    # works e.g. for tournaments and games

    response = session.get(url)
    response_dict = response.json()

    new_dict = {}
    for key, val in response_dict.iteritems():
        if ((val is not None) and (not isinstance(val, dict)) and (key != 'leaguevine_url') and
                (key != 'resource_uri') and (key != 'time_last_updated') and (key != 'time_created') and
                (key != 'objects')):
            new_dict[key] = val
            # # fix a leaguevine bug here:
            if key == "start_time" and val[-6:] == "+01:20":
                raise Exception('problem here!!!')
                new_dict[key] = val[:-6] + "+02:00"

    logger.info('before updating: {0}'.format(pformat(new_dict)))
    new_dict.update(updatedict)
    logger.info('after updating: {0}'.format(pformat(new_dict)))

    return api_put(url, new_dict)


def api_me(access_token):
    global session
    session.headers.update({'Authorization': 'bearer {0}'.format(access_token),
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'})

    url='{0}/v1/players/me/'.format(settings.HOST)
    response = session.get(url)
    return response.json()


def api_recent_tournaments(limit=10):
    url = '{0}/v1/tournaments/?order_by=%5B-end_date%5D&limit={1}'.format(settings.HOST, limit)
    response = session.get(url)
    return response.json()


def api_recent_games(limit=10):
    url = '{0}/v1/games/?order_by=%5B-start_time%5D&limit={1}'.format(settings.HOST, limit)
    response = session.get(url)
    return response.json()


def api_team_playeridsbyplayer(player_id):
    url='{0}/v1/team_players/?player_ids=%5B{1}%5D&fields=%5Bteam_id%5D'.format(settings.HOST,player_id)
    response = session.get(url)
    return response.json()
    

def api_team_playersbyplayer(player_id):
    url='{0}/v1/team_players/?player_ids=%5B{1}%5D'.format(settings.HOST,player_id)
    response = session.get(url)
    return response.json()
    
 
def api_tournamentbyid(tournament_id):
    url='{0}/v1/tournaments/{1}/'.format(settings.HOST,tournament_id)
    response = session.get(url)
    return response.json()

def api_seasonbyid(season_id):
    url='{0}/v1/seasons/{1}/'.format(settings.HOST,season_id)
    response = session.get(url)
    return response.json()

def api_tournament_teams(tournament_id):
    url='{0}/v1/tournament_teams/?tournament_ids=%5B{1}%5D&limit=200'.format(settings.HOST,tournament_id)
    response = session.get(url)
    return response.json()

def api_nrswissrounds(tournament_id):
# returns the number of existing swissdraw rounds
    if settings.OFFLINE:
        return 6
    url='{0}/v1/swiss_rounds/?tournament_id={1}&fields=%5Bid%5D'.format(settings.HOST,tournament_id)
    response = session.get(url)
    response_dict = response.json()
    return response_dict['meta']['total_count']

def api_game_final(game_id):
    url='{0}/v1/game_scores/?game_id={1}&order_by=%5B-id%5D&limit=30'.format(settings.HOST,game_id)
    response = session.get(url)
    response_dict = response.json()
    final=False
    for gu in response_dict['objects']:
        if gu['is_final']:
            final=True
            break
    return final

def api_swissround_final(tournament_id,round_number):
    url='{0}/v1/swiss_rounds/?tournament_id={1}&round_number={2}&fields=%5Bgames%5D'.format(settings.HOST,tournament_id,round_number)
    response = session.get(url)
    response_dict = response.json()
    final=True
    for g in response_dict['objects'][0]['games']:
        if not api_game_final(g['id']):
            final=False
            break
    return final

def api_swissroundinfo_roundonly(tournament_id,round_number=None,ordered=False):
    if settings.OFFLINE:
        return swissinfo()
     
    if round_number is None:
        if ordered:
            url='{0}/v1/swiss_rounds/?tournament_id={1}&fields=%5Bround_number%5D&order_by=%5Bid%5D'.format(settings.HOST,tournament_id)
        else:
            url='{0}/v1/swiss_rounds/?tournament_id={1}&fields=%5Bround_number%5D'.format(settings.HOST,tournament_id)            
    else:
        url='{0}/v1/swiss_rounds/?tournament_id={1}&fields=%5Bround_number%5D&round_number={2}'.format(settings.HOST,tournament_id,round_number)        
    response = session.get(url)
    return response.json()

    
def api_swissroundinfo(tournament_id,round_number=None,ordered=False):
    if settings.OFFLINE:
        return swissinfo()
     
    if round_number is None:
        if ordered:
            url='{0}/v1/swiss_rounds/?tournament_id={1}&order_by=%5Bid%5D'.format(settings.HOST,tournament_id)
        else:
            url='{0}/v1/swiss_rounds/?tournament_id={1}'.format(settings.HOST,tournament_id)            
    else:
        url='{0}/v1/swiss_rounds/?tournament_id={1}&round_number={2}'.format(settings.HOST,tournament_id,round_number)        
    response = session.get(url)
    return response.json()


def api_poolinfo(tournament_id):
    url='{0}/v1/pool_rounds/?tournament_id={1}'.format(settings.HOST,tournament_id)
    response = session.get(url)
    return response.json()

def api_gamesbytournament_restr(tournament_id,offset=0):
    url='{0}/v1/games/?limit=200&tournament_id={1}&order_by=%5Bid%5D&fields=%5Bteam_1%2Cteam_1_id%2Cteam_2%2Cteam_2_id%2Cgame_site%2Cstart_time%2Cid%2Ctournament%5D&'.format(settings.HOST,tournament_id)
    if offset>0:
        url += '&offset={0}'.format(offset)
    response = session.get(url)
    return response.json()

def api_gamesbytournament(tournament_id):
    url='{0}/v1/games/?limit=100&tournament_id={1}'.format(settings.HOST,tournament_id)
    return api_get(url)

def api_spiritbyseason(season_id):
    # the most recent score will be reported first, so we can just go through the list
    # and the first score with the right properties we encounter will be the most recent one
    url='{0}/v1/game_sportsmanship_scores/?limit=100&season_id={1}&order_by=%5B-time_last_updated%5D'.format(settings.HOST,season_id)
    return api_get(url)


def api_spiritbytournament(tournament_id):
    # the most recent score will be reported first, so we can just go through the list
    # and the first score with the right properties we encounter will be the most recent one
    url='{0}/v1/game_sportsmanship_scores/?limit=100&tournament_id={1}&order_by=%5B-time_last_updated%5D'.format(settings.HOST,tournament_id)
    return api_get(url)

def api_spiritbygame(game_id):
    # the most recent score will be reported first, so we can just go through the list
    # and the first score with the right properties we encounter will be the most recent one
    if type(game_id) is unicode or type(game_id) is int:
        url='{0}/v1/game_sportsmanship_scores/?limit=100&game_ids=%5B{1}%5D&order_by=%5B-time_last_updated%5D'.format(settings.HOST,game_id)
    elif type(game_id) is list:
        url='{0}/v1/game_sportsmanship_scores/?limit=100&game_ids={1}&order_by=%5B-time_last_updated%5D'.format(settings.HOST,game_id)
    else:
        raise('a game-id should be provided!')
    return api_get(url)


def api_gamesbyseason(season_id):
    url='{0}/v1/games/?limit=200&season_id={1}'.format(settings.HOST,season_id)
    return api_get(url)


def api_gamesbyteam(team_id):
    url='{0}/v1/games/?limit=10&team_ids=%5B{1}%5D&order_by=%5B-start_time%5D'.format(settings.HOST,team_id)
    return api_get(url)


def api_gamebyid(game_id):
    url='{0}/v1/games/{1}/'.format(settings.HOST,game_id)
    response = session.get(url)
    return response.json()

def api_bracketsbytournament(tournament_id):
    url='{0}/v1/brackets/?limit=50&tournament_id={1}'.format(settings.HOST,tournament_id)
    response = session.get(url)
    return response.json()

def api_bracketbyid(bracket_id):
    url='{0}/v1/brackets/{1}/'.format(settings.HOST,bracket_id)
    response = session.get(url)
    return response.json()

def api_teambyid(team_id):
    url='{0}/v1/teams/{1}/'.format(settings.HOST,team_id)
    response = session.get(url)
    return response.json()

def api_rankedteamids(tournament_id,round_number):
    swiss = api_swissroundinfo(tournament_id,round_number)
    idlist=[]
    for team in swiss['objects'][0]['standings']:
        idlist.append(team['team_id'])

    return idlist

def api_url(url):
    response = session.get(url)
    response_dict = response.json()
    logger.info(response_dict)
    return response_dict
    

def api_result(game_id,score1,score2,final=False):
    # upload scores to leaguevine
    url='{0}/v1/game_scores/'.format(settings.HOST)
    game_dict = {"game_id": "{0}".format(game_id),
                "team_1_score": "{0}".format(score1),
                "team_2_score": "{0}".format(score2),
                "is_final": "{0}".format(final)}
    return api_post(url,game_dict)

# def api_cleanteams(tournament_id):
#     # retrieve all teams of a particular tournament
#     url='{0}/v1/tournament_teams/?tournament_ids=%5B{1}%5D'.format(settings.HOST,tournament_id)
#     next=True
#     while next:
#         # we do not use the next-url, but the original one because we have removed some teams in the meantime
#         response = session.get(url)
#         response_dict = response.json()
#         logger.info(response_dict)
#
#         for team in response_dict.get('objects'):
#             # remove this team from tournament
#             remove_url='{0}/v1/tournament_teams/{1}/{2}/'.format(settings.HOST,tournament_id,team.get('team_id'))
#             response = requests.delete(url=remove_url,headers=my_headers,config=my_config)
#             if response.status_code == 204:
#                 logger.info('removed team with id {0}'.format(team.get('team_id')))
#             else:
#                 response.raise_for_status()
#
#         # check if there are more teams
#         next=response_dict.get('meta').get('next')
#     return

def api_weblink(tournament_id):
    url='{0}/v1/tournaments/{1}/'.format(settings.HOST,tournament_id)
    response = session.get(url)
    response_dict = response.json()
    return response_dict.get('leaguevine_url')
    

def api_newtournament(data_dict):
# expects a data_dictionary with leaguevine tournament specification
    url='{0}/v1/tournaments/'.format(settings.HOST)
    response_dict=api_post(url, data_dict)

    tournament_id = response_dict.get('id')
    logger.info('added tournament with id: {0}'.format(tournament_id))

    return tournament_id

def api_createteam(season_id,name,info,city,country):
# creates a new team in season_id with name and info (if does not exists yet)
# returns id of newly created or existing team with this name

    # first check if team with this name already exists in season_id
    logger.info(name)
    url=u'{0}/v1/teams/?name={1}&season_id={2}'.format(settings.HOST,name,season_id)
    response=session.get(url)
    response_dict = response.json()
    if response_dict.get('meta').get('total_count')==0:
        # create a new team in season_id
        url='{0}/v1/teams/'.format(settings.HOST)
        team_data_dict = {"name": u"{0}".format(name), 
                  "season_id": season_id,
                  "info": "{0}".format(info),
                  "city": "{0}".format(city),
                  "country": "{0}".format(country)}
        response_dict = api_post(url,team_data_dict)
        team_id = response_dict.get('id')
    else:
        # otherwise, get the id from the first object
        team_id = response_dict.get('objects')[0].get('id')
        logger.warning(u'team with name {0} already exists (l_id: {1})'.format(name,team_id))
        # and update the object
        # create a new team in season_id
        url='{0}/v1/teams/{1}/'.format(settings.HOST,team_id)
        team_data_dict = {"name": u"{0}".format(name), 
                  "season_id": season_id,
                  "info": "{0}".format(info),
                  "city": "{0}".format(city),
                  "country": "{0}".format(country)}
        response_dict = api_update(url,team_data_dict)
        team_id = response_dict.get('id')        
    
    return team_id


def api_addteam(tournament_id,team_id,seed):
# adds team to tournament
# returns response_dict

    url='{0}/v1/tournament_teams/'.format(settings.HOST)
    tournament_team_data_dict = {"tournament_id": tournament_id,
                                 "team_id": "{0}".format(team_id),
                                 "seed": "{0}".format(seed) }
    
    response= api_post(url,tournament_team_data_dict) 
    logger.info(response)       
    if response.has_key('errors'):
        # then team in tournament already exists, so just update its seed
        logger.info('team already exists, updating the seed instead,')
        url='{0}/v1/tournament_teams/{1}/{2}/'.format(settings.HOST,tournament_id,team_id)
        tournament_team_data_dict = {"seed": "{0}".format(seed) }
        response= api_put(url,tournament_team_data_dict)        
    
    return response
        

def api_updatepairingtype(tournament_id,pairing='adjacent pairing'):
    url='{0}/v1/tournaments/{1}/'.format(settings.HOST,tournament_id)
    tournament_dict = {"swiss_pairing_type": "{0}".format(pairing)}
    return api_update(url,tournament_dict)
    

def api_addswissround(tournament_id,starttime,pairing='adjacent pairing',team_ids=[]):
    
    api_updatepairingtype(tournament_id,pairing)
    # create the round
    url='{0}/v1/swiss_rounds/'.format(settings.HOST)
    swissround_dict = {"tournament_id": tournament_id,
                       "start_time": "{0}".format(starttime),
                       "visibility": "hidden",
                       "team_ids": team_ids}
    return api_post(url,swissround_dict)    

def api_cleanbrackets(tournament_id):
    # retrieve all teams of a particular tournament
    url='{0}/v1/brackets/?tournament_id={1}&fields=%5Bid%5D'.format(settings.HOST,tournament_id) 
    next=True  
    while next:
        # we do not use the next-url, but the original one because we have removed some teams in the meantime
        response = session.get(url)
        response_dict = response.json()
        logger.info(pformat(response_dict))
        
        for bracket in response_dict.get('objects'):
            # remove this team from tournament
            remove_url='{0}/v1/brackets/{1}/'.format(settings.HOST,bracket.get('id'))
            response = session.delete(url=remove_url,headers=my_headers,config=my_config)
            if response.status_code == 204:
                logger.info('removed bracket with id {0}'.format(bracket.get('id')))
            else:
                response.raise_for_status()
            
        # check if there are more teams
        next=response_dict.get('meta').get('next')
    return
    
def api_addbracket(tournament_id,starttime,number_of_rounds,time_between_rounds=180):
    # create the bracket
    url='{0}/v1/brackets/'.format(settings.HOST)
    bracket_dict = {"tournament_id": tournament_id,
                       "start_time": "{0}".format(starttime),
                       "number_of_rounds": "{0}".format(number_of_rounds),    
                       "time_between_rounds": "{0}".format(time_between_rounds) }
    return api_post(url,bracket_dict)    


def api_addfull3bracket(tournament_id,starttimeQF,starttimeSF,starttimeF,starttimeBigF,time_between_rounds=180):
    # creates a full playoff bracket with 3 rounds
    
    # example of full 3-round bracket:
    # http://www.wcbu2011.org/scores/?view=poolstatus&Pool=1009
    
    # create main winner bracket
    url='{0}/v1/brackets/'.format(settings.HOST)
    bracket_dict = {"tournament_id": tournament_id,
                   "start_time": "{0}".format(starttimeQF),
                   "number_of_rounds": "3",    
                   "time_between_rounds": "{0}".format(time_between_rounds),
                   "column_position": "1",
                   "row_position": "1",
                   "name": "playoff" }
    response=api_post(url,bracket_dict)
    winnerbr=api_bracketbyid(response['id'])
#    winnerbr=response

    # adjust the big final's time
    for r in winnerbr['rounds']:
        if r['round_number']==0:
            for g in r['games']:
                api_settimeingame(g['id'],starttimeBigF)                
    

        
    # create loser's final
    bracket_dict = {"tournament_id": tournament_id,
                       "start_time": "{0}".format(starttimeF),
                       "number_of_rounds": "1",    
                       "time_between_rounds": "{0}".format(time_between_rounds),
                       "column_position": "3",
                       "row_position": "2",
                       "name": "bronze game" }
    response=api_post(url,bracket_dict)
    bronzegame=api_bracketbyid(response['id'])
#    bronzegame=response
    # auto-move losers of semifinal to bronze-game
    for r in winnerbr['rounds']:
        if r['round_number']==1:
            team_nr=1
            for g in r['games']:
                # we also fix the starting time of the semifinals
                api_settimeingame(g['id'],starttimeSF)        
                        
                api_loserconnect(g['id'],bronzegame['rounds'][0]['games'][0]['id'],team_nr)
                team_nr += 1
                
    # create lower half of playoff tree (loser's tree)
    bracket_dict = {"tournament_id": tournament_id,
                       "start_time": "{0}".format(starttimeSF),
                       "number_of_rounds": "2",    
                       "time_between_rounds": "{0}".format(time_between_rounds),
                       "column_position": "2",
                       "row_position": "3",
                       "name": "playoff losers" }
    response=api_post(url,bracket_dict)
    loserstree=api_bracketbyid(response['id'])
#    loserstree=response
    
    # auto-move losers of quarter-finals to loser-tree
    for r in winnerbr['rounds']:
        if r['round_number']==2:
            team_nr=1
            game_nr=0
            for g in r['games']:
                # adjust starting times (leaguevine-bug)
                api_settimeingame(g['id'],starttimeQF)

                api_loserconnect(g['id'],loserstree['rounds'][0]['games'][game_nr]['id'],team_nr)
                team_nr += 1
                if team_nr == 3:
                    game_nr += 1
                    team_nr = 1
    
    # create game for place 7-8
    bracket_dict = {"tournament_id": tournament_id,
                       "start_time": "{0}".format(starttimeF),
                       "number_of_rounds": "1",    
                       "time_between_rounds": "{0}".format(time_between_rounds),
                       "column_position": "3",
                       "row_position": "4",
                       "name": u"game for 7-8" }
    response=api_post(url,bracket_dict)
    placementgame=api_bracketbyid(response['id'])
#    placementgame=response
    # auto-move losers of semifinal to bronze-game
    for r in loserstree['rounds']:
        if r['round_number']==0:
            team_nr=1
            for g in r['games']:
                api_loserconnect(g['id'],placementgame['rounds'][0]['games'][0]['id'],team_nr)
                team_nr += 1
        
def api_loserconnect(source_game,target_game,team_nr):
    # establishes that the loser of source_game
    # becomes team team_nr of target_game
    # where team_nr is 1 or 2

    # weirdly, leaguevine requires start_time and season_id
    # therefore, we retrieve the game info first
    sgame=api_gamebyid(source_game)
    
    url='{0}/v1/games/{1}/'.format(settings.HOST,source_game)
#    game_dict = {"start_time": "{0}".format(sgame['start_time']),
#                    "next_game_for_loser": "{0}".format(target_game),    
#                    "next_team_for_loser": "{0}".format(team_nr),
#                    "season_id": "{0}".format(sgame['season_id'])}
#    return api_put(url,game_dict)
    game_dict = {"next_game_for_loser_id": "{0}".format(target_game),    
                 "next_team_for_loser": "{0}".format(team_nr)}
    return api_update(url,game_dict)

def api_settimeingame(game_id,start_time):
    url='{0}/v1/games/{1}/'.format(settings.HOST,game_id)
    time_dict={"start_time": "{0}".format(start_time)}
    return api_update(url,time_dict)


def api_setteamsingame(game_id,team_1_id,team_2_id):
    url='{0}/v1/games/{1}/'.format(settings.HOST,game_id)
    game_dict = {"team_1_id": "{0}".format(team_1_id),    
                 "team_2_id": "{0}".format(team_2_id)}
    return api_update(url,game_dict)

def api_setteamsingame_OLD(game_id,team_1_id,team_2_id):
    # weirdly, leaguevine requires start_time and season_id when updating a game
    # therefore, we retrieve the game info first
    game=api_gamebyid(game_id)
    
    url='{0}/v1/games/{1}/'.format(settings.HOST,game_id)
    game_dict = {"start_time": "{0}".format(game['start_time']),
                 "team_1_id": "{0}".format(team_1_id),    
                 "team_2_id": "{0}".format(team_2_id),
                 "season_id": "{0}".format(game['season_id'])}
    return api_put(url,game_dict)
        
    
def api_addpool(tournament_id,starttime,name,team_ids=[],time_between_rounds=120,generate_matchups=False):
    # create the pool
    url='{0}/v1/pools/'.format(settings.HOST)
    pool_dict = {"tournament_id": tournament_id,
                   "start_time": "{0}".format(starttime),
                   "name": "{0}".format(name),    
                   "time_between_rounds": "{0}".format(time_between_rounds),
                   "generate_matchups": generate_matchups,
                   "team_ids": team_ids}
    return api_post(url,pool_dict)    

def api_getspiritbyid(score_id):
    url = '{0}/v1/game_sportsmanship_scores/{1}/'.format(settings.HOST, score_id)
    response = session.get(url)
    return response.json()


def api_deletespirit(score_id):
    url = '{0}/v1/game_sportsmanship_scores/{1}/'.format(settings.HOST, score_id)
    response = api_delete(url)
    return response



def api_addspirit(game_id,data_dict):
    url='{0}/v1/game_sportsmanship_scores/'.format(settings.HOST)
    data_dict['game_id']=game_id
    response = api_post(url,data_dict)
    # after adding a new spirit score, all bets about caching are off, we have to clear the cache
    # TODO: be more clever here and only clear affected caches...
    cache.clear()
    return response


def result_in_swissround(round,team_id):
    for g in round['games']:
        if g['team_1_id']==team_id:
            score = g['team_1_score']
            opp_score = g['team_2_score']
        elif g['team_2_id']==team_id:
            score = g['team_2_score']
            opp_score = g['team_1_score']
        else:
            continue
        if score > opp_score:
            return '{0}-{1} win'.format(score,opp_score)
        elif score < opp_score:
            return '{0}-{1} loss'.format(score,opp_score)
        elif score == opp_score:
            return '{0}-{1} tie'.format(score,opp_score)

def rank_in_swissround(round,team_id):
    # returns rank in swissround as ordinal
    # corrects for 8 places if round_number > 5
    for t in round['standings']:
        if t['team_id']==team_id:
            rank=int(t['ranking'])
            if round['round_number']>5: # top 8 teams have left for brackets
                rank += 8
            return u'{0}'.format(ordinal(rank)) # TODO make ordinal

def ordinal(value):
    from django.utils.translation import ugettext as _
    """
    Converts an integer to its ordinal as a string. 1 is '1st', 2 is '2nd',
    3 is '3rd', etc. Works for any integer.
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    suffixes = (_('th'), _('st'), _('nd'), _('rd'), _('th'), _('th'), _('th'), _('th'), _('th'), _('th'))
    if value % 100 in (11, 12, 13): # special case
        return u"%d%s" % (value, suffixes[0])
    return u"%d%s" % (value, suffixes[value % 10])

