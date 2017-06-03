#===============================================================================
# import ctypes.wintypes
# CSIDL = 0x28 # CSIDL_PROFILE
# SHGFP_TYPE_CURRENT = 0   # Get current, not default value
# buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
# ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL, None, SHGFP_TYPE_CURRENT, buf)
# windows_user_folder = buf.value
# print(f'Windows itself tells me its in {windows_user_folder}')
#===============================================================================

from json import load, dump
from numpy import average
from pprint import pprint
from datetime import timedelta
import locale

locale.setlocale(locale.LC_ALL, 'pl')

def formatting(number):
    '''putting spaces between 1000s'''
    
    setting = locale.format('%d', number, grouping=True)
    
    return setting

def proper_stats(corporation):
    def a_thing(corp):
        def kurwa(pyk):
            try:
                kek = data[pyk]
            except:
                kek = 0
            return kek
        
        data = corporation[corp]
        proper = {}
        
        ''' data from api as variables '''
        fleet = kurwa('prestigeBonus')
        karma = kurwa('karma')
        game_played = kurwa('gamePlayed')
        won = kurwa('gameWin')
        total_death = kurwa('totalDeath')
        kills = kurwa('totalKill')
        assists = kurwa('totalAssists')
        dmg = round(kurwa('totalDmgDone'), 0)
        cap = kurwa('totalVpDmgDone')
        heal = kurwa('totalHealingDone')
        time = int(round(kurwa('totalBattleTime')/1000, 0))
        
        ''' calculating stats '''
        try:
            win_rate = round(won/(game_played-won), 3)
            win_loss = round(won/game_played, 3)
        except: 
            win_rate = 0
            win_loss = 0
            
        won_games = won
        lost_games = game_played-won
        try:
            eff_rating = int(round(data['effRating'], 0))
        except:
            eff_rating = 0
        kill_death = round(kills/total_death, 2)
        kill_game = round(kills/game_played, 2)
        assist_death = round(assists/total_death, 2)
        assist_game = round(assists/game_played, 2)
        dmg_game = int(round(dmg/game_played, 0))
        cap_game = round(cap/game_played, 2)
        heal_game = int(round(heal/game_played, 0))
        battle_time = timedelta(seconds = time)
        battle_game = timedelta(seconds = round(time/game_played, 0))
        death_game = round(total_death/game_played, 2)
        dmg_min = int(round(dmg/time*60, 0))
        kills_min = round(kills/time*60, 2)
        fleet_strength = int(fleet*100)
    
        ''' output in dict '''
        proper['Win/Loss'] = win_rate
        proper['Eff rating'] = eff_rating
        proper['Kill/Death'] = kill_death
        proper['Kill/Game'] = kill_game
        proper['Assist/Death'] = assist_death
        proper['Assist/Game'] = assist_game
        proper['Death/Game'] = death_game
        proper['Dmg/Game'] = formatting(dmg_game)
        proper['Cap points/Game'] = cap_game
        proper['Heal/Game'] = formatting(heal_game)
        proper['Time/Game'] = battle_game
        
        proper['Total dmg'] = formatting(int(dmg))
        proper['Total heal'] = formatting(heal)
        proper['Total in battle'] = battle_time
        proper['Total cap in CTB'] = formatting(int(cap))
        proper['Total games'] = formatting(int(game_played))
        proper['Total won'] = formatting(int(won_games))
        proper['Total lost'] = formatting(int(lost_games))
        proper['Total kills'] = formatting(int(kills))
        proper['Total deaths'] = formatting(int(total_death))
        proper['Total assists'] = formatting(int(assists))
        
        proper['Dmg/min'] = formatting(dmg_min)
        proper['Kills/min'] = kills_min
        proper['Win Ratio'] = win_loss
        
        proper['User ID'] = data['uid']
        proper['Fleet Strength'] = fleet_strength
        proper['Karma'] = formatting(int(karma))
        
        return proper

    proper = {}
    for corp in corporation:
        try:
            proper[corp] = a_thing(corp)
        except:
            continue
        proper[corp]['players in data'] = corporation[corp]['players in data']

        
    return proper

dumpy = load(open('raw.txt', 'r', encoding='ISO-8859-1'))

stats = {}
corps = {}
something = {}

for player in dumpy:
    player = dumpy[player]
    corp = '{} [{}]'.format(player['name'], player['tag'])
    
    try:
        for key in player:
            try:
                corps[corp][key].append(player[key])
            except KeyError:
                corps[corp][key] = [player[key]]
                continue
    except KeyError:
        corps[corp] = {}
        for key in player:
            try:
                corps[corp][key].append(player[key])
            except KeyError:
                corps[corp][key] = [player[key]]
                continue
        continue

for corp in corps:
    try:
        something[corp] = {}
        something[corp]['players in data'] = len(corps[corp]['uid'])
    except: continue
    
    for stats in corps[corp]:
        try:
            something[corp][stats] = round(average(corps[corp][stats]), 2)
        except:
            continue
        
#pprint(something)
averages = proper_stats(something)

below10 = 0
over10 = 0
over50 = 0
over100 = -1
for corp in averages:
    try:
        players = averages[corp]['players in data']
    except:
        continue
    
    if players == 1:
        #print(f'{corp} have {players} player')
        1
    else:
        #print(f'{corp} has {players} players')
        1
        
    if  players <= 10:
        below10 += 1
    if  players > 10:
        over10 += 1
    if  players > 50:
        over50 += 1
    if  players > 100:
        over100 += 1
        
dump(averages, open('corporations.txt', 'w'), default=str)

print(f'{below10} corporations with less than or equal to 10 active players')
print(f'{over10} corporations with over 10 active players')
print(f'{over50} corporations with over 50 active players')
print(f'{over100} corporations with over 100 active players')
print(f'\nGot {over10+below10-1} corporations\n')

corp = 'The NASA [NASA]'
kek = averages[corp]
print(corp)
for i in kek:
    print(f'{i}: {kek[i]}')
        