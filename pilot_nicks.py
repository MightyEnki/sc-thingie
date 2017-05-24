import os, json, locale
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from scipy.stats import norm
from datetime import datetime
from pprint import pprint
from everything import proper_stats
from multiprocessing.dummy import Pool as ThreadPool
from matplotlib.axes import Axes
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
import bs4 as bs
from urllib.request import Request, urlopen


# -*- coding: utf-8 -*-

path = 'Y:/python/logs'
dirs = os.listdir(path)

def api_stats(ign):
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
            player_stat['name'] = 'w/o corp'
            player_stat['tag'] = '>.<'
        
        if 'karma' not in data.keys() or 'prestigeBonus' not in data.keys():
            player_stat['karma'] = 0
            player_stat['prestigeBonus'] = 0
            
    return player_stat

def parser():
    players = []
    num = [x for x in range(len(dirs))]
    def multi(dir, num):
        proper_path = f'{path}/{dir}/game.log'
        with open(proper_path, 'r') as f:
            for line in f:
                if 'ADD_' in line:
                    ign = line.split(' (')[1].split(',')[0]
                    if ' ' in ign:
                        ign = ign.split(' ')[0]
                    players.append(ign)
                    
    pool = ThreadPool(8) 
    pool.starmap(multi, zip(dirs, num))
    pool.close()
    pool.join()

    #===========================================================================
    # for dir in dirs:
    #     proper_path = f'{path}/{dir}/game.log'
    #     with open(proper_path, 'r') as f:
    #         for line in f:
    #             if 'ADD_' in line:
    #                 ign = line.split(' (')[1].split(',')[0]
    #                 if ' ' in ign:
    #                     ign = ign.split(' ')[0]
    #                 players.append(ign)
    #===========================================================================
    
    return players

def stats(players):
    data = {}
    amount = len(players)
    num = [x for x in range(len(players))]
    starting = datetime.now()
    
    def multi(player, i):
        start = datetime.now()

        kek = str(i).zfill(4)
        try:
            data[player] = proper_stats(player)
            #data[player] = api_stats(player)
        except:
            print(f'{kek} kurwa nie działa') 
            pass
        end = datetime.now()
        print(f'{kek} out of {amount} which took {end-start}')

    pool = ThreadPool(16) 
    
    pool.starmap(multi, zip(players, num))
    
    pool.close()
    pool.join()
    
    
    finish = datetime.now()
    print(f'\nGot all data in {finish-starting}')
    return data

def averages(data):
    players = len(data.keys())
    
    av = {}
    for thing in data['Tillowaty'].keys():
        av[thing] = 0.0
        
    for key in data.keys():
        player = data[key]
        for thing in player.keys():
            value = player[thing]
            if '\xa0' in str(value):
                av[thing] += int(value.replace(u'\xa0', ''))
            elif '.' in str(value):
                av[thing] += value
            elif ':' not in str(value) and not isinstance(value, str):
                av[thing] += value
        
    print(f'Average based on {players} players.\n')
    for stat in av.keys():
        kek = av[stat]/players
        if kek > 10:
            print(f'Average {stat}: {int(round(kek, 0))}')
        else:
            print(f'Average {stat}: {round(kek, 2)}')

def chat_parser(players):
    for dir in dirs:
        proper_path = f'{path}/{dir}/chat.log'
        with open(proper_path, 'r', encoding='ISO-8859-1') as kek:
            for one in kek:
                if '>[' in one:
                    ign = one.split('>[')[1].split(']')[0].strip(' ')
                    players.append(ign)
    return players

def normal_dist(data):
    players = len(data.keys())
    
    av = {}
    for thing in data['Tillowaty'].keys():
        av[thing] = []
        
    for key in data.keys():
        player = data[key]
        for thing in player.keys():
            value = player[thing]
            if '\xa0' in str(value):
                av[thing].append(int(value.replace(u'\xa0', '')))
            elif '.' in str(value):
                av[thing].append(value)
            elif ':' not in str(value) and not isinstance(value, str):
                av[thing].append(value)
    return av

def graphing(what, data, who):
    
    kek = data[who][what]    
    fig = figure()
    ax = fig.add_subplot(111)
    if '\xa0' in str(kek):
       kek = (int(kek.replace(u'\xa0', '')))
        
    data = stuff[what]
    mean, sigma = norm.fit(data)
    plt.hist(data, bins = 1000, normed=True, alpha=0.4)
    
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 1000)
    p = norm.pdf(x, mean, sigma)
    plt.plot(x, p, 'k', linewidth=2)
    title = f'{what}\nFit results: mean = {round(mean,2)}, sigma = {round(sigma,2)}'
    plt.title(title)
    
    two, eight = norm.interval(.999, loc = mean, scale = sigma)
    plt.xlim(0, eight)
    
    new = norm.pdf(kek, mean, sigma)
    plt.plot([kek, kek], [0, new], color='r', linestyle='--')
    if what == 'Death/Game':
        at = round((1-norm.cdf(kek, mean, sigma))*100, 2)
    else:
        at = round(norm.cdf(kek, mean, sigma)*100, 2)
    text = f'You are better than \n{at}% players'
    ax.annotate(text, xy=(kek, new), xytext=(0.7, 0.8), textcoords='axes fraction',
                arrowprops=dict(facecolor='g', color='g'))
    
    what = what.replace('/', '-')
    #plt.show()
    plt.savefig(f'Y:/python/graphs/data/{what}.png')
    #plt.close()

def scales(stuff):
    limits = {}
    for key in stuff.keys():
        try:
            data = stuff[key]
            mean, sigma = norm.fit(data)
            
            one, nine = norm.interval(.99, loc = mean, scale = sigma)
            two, eight = norm.interval(.9, loc = mean, scale = sigma)
            three, seven = norm.interval(.7, loc = mean, scale = sigma)
            four, six = norm.interval(.5, loc = mean, scale = sigma)
            five = mean
            
            if key != 'Karma':
                if four < 0:
                    four = five/2
                if three < 0:
                    three = four/2
                if two < 0:
                    two = three/2
                if one < 0:
                    one = two/2
                    
            if key == 'Fleet Strength':
                if nine > 200:
                    nine = 200
            if key == 'Eff rating':
                if nine > 9000:
                    nine = 9000
            
            if key == 'Death/Game' or key == 'Total deaths':
                limits[key] = {one: 9, two: 8, three: 7, four: 6, five: 5,
                               six: 4, seven: 3, eight: 2, nine: 1}      
            else:
                limits[key] = {one: 1, two: 2, three: 3, four: 4, five: 5,
                               six: 6, seven: 7, eight: 8, nine: 9}                
            
        except: continue
    return limits

def rating(ign):
    try:
        player_data = data[ign]
    except:
        player_data = proper_stats(ign)
    stuff_to_check = ['Total games', 'Dmg/Game', 'Kill/Game', 'Death/Game', 
                      'Assist/Game', 'Heal/Game', 'Cap points/Game', 'Win/Loss']
    av = {}
    rate_pilot = {}
    
    for key in stuff_to_check:
        av[key] = 0
        rate_pilot[key] = 0
        
    for thing in stuff_to_check:
        value = player_data[thing]
        if '\xa0' in str(value):
            av[thing] = int(value.replace(u'\xa0', ''))
        elif '.' in str(value):
            av[thing] = value
        elif ':' not in str(value) and not isinstance(value, str):
            av[thing] = value
    
    for key in stuff_to_check:
        compare = points[key]
        value = av[key]
        kek = 42
        for rate in compare:
            if value > rate and 'Death' not in key:
                rate_pilot[key] = compare[rate]
            
            if value < rate and 'Death' in key and rate < kek:
                rate_pilot[key] = compare[rate]
                kek = rate
    
    #print(ign)           
    #pprint(rate_pilot)
    return rate_pilot
    
def radar(points, rate, base1):    
    
    def radar_factory(num_vars, frame='circle'):
        """Create a radar chart with `num_vars` axes.
    
        This function creates a RadarAxes projection and registers it.
    
        Parameters
        ----------
        num_vars : int
            Number of variables for radar chart.
        frame : {'circle' | 'polygon'}
            Shape of frame surrounding axes.
    
        """
        # calculate evenly-spaced axis angles
        theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
        # rotate theta such that the first axis is at the top
        theta += np.pi/2
    
        def draw_poly_patch(self):
            verts = unit_poly_verts(theta)
            return plt.Polygon(verts, closed=True, edgecolor='k')
    
        def draw_circle_patch(self):
            # unit circle centered on (0.5, 0.5)
            return plt.Circle((0, 0), 1)
    
        patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
        if frame not in patch_dict:
            raise ValueError('unknown value for `frame`: %s' % frame)
    
        class RadarAxes(PolarAxes):
    
            name = 'radar'
            # use 1 line segment to connect specified points
            RESOLUTION = 1
            # define draw_frame method
            draw_patch = patch_dict[frame]
    
            def fill(self, *args, **kwargs):
                """Override fill so that line is closed by default"""
                closed = kwargs.pop('closed', True)
                return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)
    
            def plot(self, *args, **kwargs):
                """Override plot so that line is closed by default"""
                lines = super(RadarAxes, self).plot(*args, **kwargs)
                for line in lines:
                    self._close_line(line)
    
            def _close_line(self, line):
                x, y = line.get_data()
                # FIXME: markers at x[0], y[0] get doubled-up
                if x[0] != x[-1]:
                    x = np.concatenate((x, [x[0]]))
                    y = np.concatenate((y, [y[0]]))
                    line.set_data(x, y)
    
            def set_varlabels(self, labels):
                self.set_thetagrids(np.degrees(theta), labels)
    
            def _gen_axes_patch(self):
                return self.draw_patch()
    
            def _gen_axes_spines(self):
                if frame == 'circle':
                    return PolarAxes._gen_axes_spines(self)
                # The following is a hack to get the spines (i.e. the axes frame)
                # to draw correctly for a polygon frame.
    
                # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
                spine_type = 'circle'
                verts = unit_poly_verts(theta)
                # close off polygon by repeating first vertex
                verts.append(verts[0])
                path = Path(verts)
    
                spine = Spine(self, spine_type, path)
                spine.set_transform(self.transAxes)
                return {'polar': spine}
    
        register_projection(RadarAxes)
        return theta
    
    
    def unit_poly_verts(theta):
        """Return vertices of polygon for subplot axes.
    
        This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
        """
        x0, y0, r = [0.5] * 3
        verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
        return verts
    
    
    def example_data():
        something = []
        base2 = []
        for key in rate.keys():
            something.append(rate[key])
            base2.append(base1[key])

        data = [
            ['Experience', 'DD', 'Kills', 'Survivability', 
                      'Support', 'Heals', 'Cap', 'Win ratio'],
            (ign, something),
            (base, base2)
            
        ]
        return data
    
    
    if __name__ == '__main__':
        N = len(rate.keys())
        theta = radar_factory(N, frame='polygon')
        data = example_data()
    
    #===========================================================================
    #     fig, axes = plt.subplots(figsize=(8, 8), nrows=2, ncols=2,
    #                              subplot_kw=dict(projection='radar'))
    #     fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    # 
    #     colors = ['b']
    #     # Plot the four cases from the example data on separate axes
    #     for ax, (title, case_data) in zip(axes.flatten(), data):
    #         ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
    #                      horizontalalignment='center', verticalalignment='center')
    #         for d, color in zip(case_data, colors):
    #             ax.plot(theta, d, color=color)
    #             ax.fill(theta, d, facecolor=color, alpha=0.25)
    #         ax.set_varlabels(spoke_labels)
    #===========================================================================

        d = data[1][1]
        compare = data[2][1]
        labels = data[0]
        fig = plt.figure()
        fig.text(0.1, 0.95, ign)
        ax = fig.add_subplot(1, 1, 1, projection='radar')
        ax.plot(theta, d, color='b')
        ax.fill(theta, d, facecolor='g', alpha=0.25)
        
        #ax.plot(theta, compare, color='g', alpha=0.2)
        #ax.fill(theta, compare, facecolor='g', alpha=0.1)
        
        ax.set_varlabels(labels)
        ax.set_rgrids([1,2,3,4,5,6,7,8,9])
        
        plt.show()
        #fig.savefig(f'Y:/python/graphs/{ign}.png')
    
start = datetime.now()
                 
#===============================================================================
# players = chat_parser(parser()) + json.load(open('names_dump.txt', 'r'))
# print(f'Players in logs: {len(players)}')
# players = list(set(players))
# print(f'Unique players in logs: {len(players)}')
#     
# data = stats(players)
# print(f'Players which didn\'t change nick: {len(list(data.keys()))}')
# json.dump(data, open('lies.txt', 'w', encoding='ISO-8859-1'), default=str)
#===============================================================================


#===============================================================================
# data = json.load(open('lies.txt', 'r'))
# all_names = list(data.keys())
#===============================================================================

#===============================================================================
# test1 = json.load(open('names_dump.txt', 'r'))
# test2 = open('igns.txt', 'r', encoding='ISO-8859-1')
# with test2 as f:
#     kek = []
#     print(f)
#     for line in f:
#         kek.append(line.replace('\n', ''))
#          
# all_names = test1 + kek
# print(len(all_names))
# all_names = list(set(all_names))
# print(len(all_names))
#  
# json.dump(all_names, open('names_dump.txt', 'w'), default=str)
# all_names = json.load(open('names_dump.txt', 'r'))
#  
# with open('names.txt', 'w', encoding='ISO-8859-1') as f:
#     i = 0
#     for name in all_names:
#         i += 1
#         num = str(i).zfill(4)
#         f.write(f'{num}. {name}\n')
#===============================================================================

#===============================================================================
# #averages(data)
# stuff = normal_dist(data)
# points = scales(stuff)
# #pprint(points)
# ign = 'Tillowaty'
# rate = rating(ign)
# proper_data = ['Total games', 'Dmg/Game', 'Kill/Game', 'Death/Game', 
#                 'Assist/Game', 'Heal/Game', 'Cap points/Game', 'Win/Loss']
# for name in proper_data:
#     graphing(name, data, ign)
#     i=0
# #graphing('Assist/Game', data, ign)
# 
# players = ['Tillowaty', 'Gizmomac', 'niripas', 'Entersprite', 'OregyenDuero', 'SpongeJohn',
#            'JCNB', 'Aggressor', 'Koromac', 'Swifter', 'Shotan', 'Cr0', 'ItalianBadBoy',
#            'millanbel', 'Shotan', 'Bliksem', 'YuriVonFluri', 'AccessDenied', 'Ruda007',
#            'Mzhelskii', 'TheDarkRedFox', 'TESLA', 'RamboX', 'MisakaMikoto', 'g4borg',
#            'xGeneStarwind']
# players = ['Tillowaty']
# base = 'Tillowaty'
# base_rating = rating(base)
# for ign in players:
#     rate = rating(ign)
#     #radar(points, rate, base_rating)
#===============================================================================

end = datetime.now()

print(f'\nDone in {end-start}')