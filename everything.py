import json, locale, pprint
import bs4 as bs
from urllib.request import Request, urlopen
from datetime import timedelta

locale.setlocale(locale.LC_ALL, 'pl')

def formatting(number):
    '''putting spaces between 1000s'''
    
    setting = locale.format('%d', number, grouping=True)
    
    return setting

def gamelog_data(file):
    
    def get_time(tup):
        start = tup[0]
        end = tup[1]
        
        hs, ms, ss = start.split(':')
        he, me, se = end.split(':')
    
        sec_start = int(hs)*3600 + int(ms)*60 + int(round(float(ss), 0))
        sec_end = int(he)*3600 + int(me)*60 + int(round(float(se), 0))
        duration = sec_end - sec_start
        
        return sec_start, sec_end, duration
    
    with file as logs:
        
        run, game_line, game_id = 0, 0, 0
        game_players, session_players, game_time, games = [], [], [], []
        
        for line in logs:
            run+=1
            
            if 'MasterServerSession' in line:
                game_id = line.split(',')[1].strip('session ')
                games.append(game_id)
                
            if 'client =' in line:
                game_start = line.split(' ')[0]
                game_line = run
                game_players = []
    
            if 'ADD_PLAYER' in line and run > game_line:
                line = line.replace('\n', '').replace('  ', '')
                game_players.append(line)
                
            if 'downloading' in line:
                game_end = line.split(' ')[0]
                
                start, end, duration = get_time((game_start, game_end))
                
                start = timedelta(seconds = start)
                end = timedelta(seconds = end)
                game_time.append((start, end, duration))
                
                session_players.append(game_players)
                
                game_players = []
            
    session_dict = {}
    
    for game, g_id, when in zip(session_players, games, game_time):
        
        team1, team2 = {}, {}
        
        for player in game:
            
            team = int(player.split(' ')[4])%2
            player_data = player.split('(')[1].split(')')[0].split(', ')
            player = player_data[0].split(' ')
            name = player[0].replace(',','')
            
            if len(player) == 2:
                tag = player[1]
            else:
                tag = 'no tag'
                
            player_id = player_data[1]
            if team == 0:
                team1[name] = {'id':player_id, 'tag':tag, 'team':team+1}
            if team == 1:
                team2[name] = {'id':player_id, 'tag':tag, 'team':team+1}                
        

        session_dict[g_id]= {'Team 1':team1, 'Team 2':team2, 'times':when}  

    return session_dict, games

def proper_stats(ign):
    ''' using data from stats func
    returns dict with additional player stats based on stats form api'''
    
    def stats(ign):
        ''' getting info from api thingie
         returns dict with stats'''
        
        url = 'https://gmt.star-conflict.com/pubapi/v1/userinfo.php?nickname='
        req = Request(url+ign, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = bs.BeautifulSoup(webpage, 'lxml')
        
        keks = soup.findAll('p')
        string = str(keks).strip('[</p>]')
        data = json.loads(string)
        data = data['data']
        player_stat = {}

        for entry in data.keys():
            if entry == 'pvp':
                for key in data['pvp'].keys():
                    value = data['pvp'][key]
                    player_stat[key] = value
                    
            elif entry != 'nickName':
                player_stat[entry] = data[entry]
                    
            if entry == 'clan':
                for key in data['clan'].keys():
                    value = data['clan'][key]
                    player_stat[key] = value
                    
            if 'clan' not in data.keys() and 'name' not in player_stat.keys():
                player_stat['name'] = 'no corp'
                player_stat['tag'] = 'no corp'
            
            if 'karma' not in data.keys() or 'prestigeBonus' not in data.keys():
                player_stat['karma'] = 0
                player_stat['prestigeBonus'] = 0
                
        return player_stat
    
    data = stats(ign)
    proper = {}
    
    ''' data from api as variables '''
    fleet = data['prestigeBonus']
    karma = data['karma']
    game_played = data['gamePlayed']
    total_death = data['totalDeath']
    kills = data['totalKill']
    assists = data['totalAssists']
    dmg = round(data['totalDmgDone'], 0)
    cap = data['totalVpDmgDone']
    heal = data['totalHealingDone']
    time = int(round(data['totalBattleTime']/1000, 0))
    
    ''' calculating stats '''
    win_rate = round(data['gameWin']/(game_played-data['gameWin']), 3)
    win_loss = round(data['gameWin']/game_played, 3)
    eff_rating = int(round(data['effRating'], 0))
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
    lost_games = game_played-data['gameWin']
    won_games = data['gameWin']
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
    proper['Corporation name'] = data['name']
    proper['Corporation tag'] = data['tag']
    proper['Fleet Strength'] = fleet_strength
    proper['Karma'] = formatting(int(karma))
    
    return proper

def everyone_proper(random_player_list):
        
    all_dem_proper_stats = {}
    for player in random_player_list:
        try:
            all_dem_proper_stats[player] = proper_stats(player)
        except: 
            all_dem_proper_stats[player] = 0
    return all_dem_proper_stats

def add_gamelog(file):

    game_log = open(file, 'r')
    
    session, game_keys = gamelog_data(game_log)
    
    games = session.keys()
    
    for game in games:
    
        players = session[str(game)]
        random_player_list = []
        
        for team in players.keys():
            if team != 'times':
                for player in players[team].keys():
                    random_player_list.append(player)
            
        everything = everyone_proper(random_player_list)

        for player in random_player_list:
            api = {}
            try:
                stats = everything[player]
            
                for stat in stats.keys():
                    api[stat] = stats[stat]
            except: 
                api = 0
            
            if player in players['Team 1'].keys():
                players['Team 1'][player]['API'] = api    
                    
            if player in players['Team 2'].keys():
                players['Team 2'][player]['API'] = api    
    
    return session, game_keys

def combatlog_data(combat_path, session, game_keys):
    
    def key_creator(value):
        newlist = {}
        for player in players:
            if player not in newlist.keys():
                newlist[player] = value
        return newlist
    
    def ship_names():
        ship_names = open('ships_namev2.txt', 'r')
        ships = {}
        with ship_names as names:
            for line in names:
                thingie = line.replace('\n', '').split(', ')  
                string = thingie[0]
                name = thingie[1]
                ships[string] = name  
        return ships
    
    def reward_list(line):
        if line.split('\t')[1].split(' ')[0].isdigit()==False:
            howmuch = line.split('\t')[1].split(' ')[1]
        if line.split('\t')[1].split(' ')[0].isdigit()==True:
            howmuch = line.split('\t')[1].split(' ')[0]
        player = line.split('\t')[0].split(' ')[-1]
        return howmuch, player
    
    def session_players(session):
        session_players = []
        for game in session.keys():
            game = session[game]
            game_players = []
            for team in game.keys():
                if 'Team' in team:
                    team = game[team]
                    for pilot in team.keys():
                        game_players.append(pilot)
            session_players.append(game_players)
            
        return session_players

           
    combat_log = open(combat_path, 'r')
    
    n = 0
    players_dict = session_players(session)
    players = players_dict[n]
    sess = game_keys[n]

    
    game_stats = {}
    for klucz in game_keys:
        game_stats[klucz] = {}
    
    game_damage = key_creator(0)
    kills = key_creator(0)
    deaths = key_creator(0)
    used_ships = key_creator([])
    game_score = key_creator(0)
    credits_game = key_creator(0)
    assists = key_creator(0)
    
    ships = ship_names()
    l = 0
    end = -666
    with combat_log as lines:
        for line in lines:
            l+=1
            test = line.split('|')
            
            if len(test) != 0:
                if 'Killed' in line:
                    died = test[1].split(' ')[2].replace('\t', '')
                    killer = test[2].split(' ')[-1]
                    
                    if killer in players and died in players:
                        kills[killer] += 1
                        ifplayer = True
                        
                    if killer in players and died not in players:
                        ifplayer = False
                        
                    if died in players:
                        deaths[died] += 1
                        
            if len(test) == 6:
                logline = line.split('|')
                player_name = logline[1].split(' ')[-1]
                wow = True
                
                while wow:
                    damage = logline[3].split(' ')[1]
                    
                    if damage != '':
                        wow = False
                        
                    if damage == '':
                        damage = logline[3].split(' ')[2]
                        
                        if damage == '':
                            damage = logline[3].split(' ')[3]
                            wow = False
                            
                        wow = False
                
                if player_name in players:
                    game_damage[player_name] += float(damage)
    
            if 'Spawn ' in line:
                name = line.split('(')[1].split(',')[0]
                new_line = line.split(' ')[-1].replace('\'', '').replace('\n', '')
                if name in players:
                    already_used = used_ships.get(name)
                    
                    if 'Race5' not in line:
                        if new_line in ships.keys():
                            ship = ships[new_line]
                            if ship not in already_used:
                                used_ships[name] = already_used+[ship]
                    else:
                        key2 = new_line.split('_')
                        key2 = key2[0], key2[1], key2[2], key2[3]
                        key2 = '_'.join(key2)
                        ship = ships[key2]
                        if key2 in ships.keys():
                            if ship not in already_used:
                                used_ships[name] = already_used+[ship]
                                
            if 'defeat' in line or 'victory' in line:
                howmuch, player = reward_list(line)
                if 'exp' in line:
                    game_score[player] = howmuch
                if 'cred' in line:
                    credits_game[player] = howmuch 
                    end = l
                    
            if 'Participant' in line:
                if ifplayer:
                    parti = line.split('\t')[0].split(' ')[-1]
                    if parti in players:
                        assists[parti] += 1
                        
            if 'Gameplay finished' in line:
                team_won = line.split('.')[2].split('(')[0].strip(' ')
                
            if l == end+5:
                total_dmg = 0
                for pilot in players:
                    total_dmg += game_damage[pilot]
                    
                for pilot in players:
                    game_damage[pilot] = int(game_damage[pilot])
                    dmg = game_damage[pilot]
                    team_dmg = round(dmg/total_dmg*100, 2)
                    dmg = formatting(dmg)
                    kill = kills[pilot]
                    death = deaths[pilot]
                    ship = used_ships[pilot]
                    score = game_score[pilot]
                    creds = credits_game[pilot]
                    assist = assists[pilot]
                    
                    game_stats[str(sess)][pilot] = {'Dmg' : {'total':dmg,
                                        'team dmg': str(team_dmg)+'%', 'kinetic' : 0, 'EM': 0, 
                                        'thermal': 0}, 'Squad' : 0, 'credits':creds,
                                        'Ships used':ship, 'kills':kill, 'Assists':assist, 
                                        'Deaths':death, 'Eff in game':score}
                    
            if l == end+6:
                game_stats[str(sess)]['winner'] = team_won
                if n<len(game_keys)-1:
                    n += 1
                players = players_dict[n]
                sess = game_keys[n]
                game_damage = key_creator(0)
                kills = key_creator(0)
                deaths = key_creator(0)
                used_ships = key_creator([])
                game_score = key_creator(0)
                credits_game = key_creator(0)
                assists = key_creator(0)
                         
    return game_stats

def add_combatlog(session, combatlog_path, game_keys):

    game_stats = combatlog_data(combatlog_path, session, game_keys)

    games = session.keys()
    
    for game in games:
    
        players = session[str(game)]
        random_player_list = []
        pilot = game_stats[str(game)]
        players['winner'] = pilot['winner']
        
        for team in players.keys():
            if team != 'times' and team != 'winner':
                for player in players[team].keys():
                    random_player_list.append(player)

        for player in random_player_list:

            if player in players['Team 1'].keys():
                players['Team 1'][player]['Game Stats'] = pilot[player]
                    
            if player in players['Team 2'].keys():
                players['Team 2'][player]['Game Stats'] = pilot[player]
    
    return session

def everything(gamelog_file):
    gamelog_path = gamelog_file
    combatlog_path = gamelog_file.replace('game.log', 'combat.log')
    session, game_keys = add_gamelog(gamelog_path)
    moar = add_combatlog(session, combatlog_path, game_keys)
    #pprint.pprint(moar)
    return moar, game_keys

#pprint.pprint(everything('Y:\Python\\test\game.log'))
#pprint.pprint(proper_stats('Tillowaty'))