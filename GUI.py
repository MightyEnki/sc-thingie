from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pprint import pprint
from json import load, dump
from everything import everything, proper_stats
import sys, kek, locale

# -*- coding: utf-8 -*-
locale.setlocale(locale.LC_ALL, 'pl')

class Combat_log(QMainWindow, kek.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        self.exit_btn.triggered.connect(self.app_close)
        self.open_file.triggered.connect(self.file_open)
        self.actionExit.triggered.connect(self.app_close)
        
        self.stat_table_setup()
        self.line_end = [self.line_player1, self.line_player2, self.line_player3, self.line_player4]
        for line in self.line_end:
            line.editingFinished.connect(self.player_fill)
        
        self.table_stat.cellDoubleClicked.connect(self.new_one)
        
        self.setup_part_tables()
        self.ship_checks = [self.empire_s, self.empire_m, self.empire_l,
                            self.empire_8, self.empire_11, self.empire_14,
                            self.fed_s, self.fed_m, self.fed_l,
                            self.fed_8, self.fed_11, self.fed_14,
                            self.jericho_s, self.jericho_m, self.jericho_l,
                            self.jericho_8, self.jericho_11, self.jericho_14]
        for check in self.ship_checks:
            check.stateChanged.connect(self.need_parts_table)
        
        self.check_all.pressed.connect(self.kek)
        self.uncheck_all.pressed.connect(self.wow)

    def kek(self): 
        for check in self.ship_checks:
            check.setChecked(True)
    
    def wow(self):
        for check in self.ship_checks:
            check.setChecked(False)
            

    def setup_part_tables(self):
        self.data = load(open('data for parts.txt', 'r'))
        have_parts = self.data['have parts']
        self.have_parts = have_parts
        have_materials = self.data['have materials']
        parts = self.data['parts']
        self.required_parts = self.data['ships']
        self.parts = parts
        self.need_parts = {}
        
        stuff = [(self.parts_have, have_parts),(self.materials_have, have_materials)]
        for key, thingie in stuff:     
            nth_part = len(thingie)
            key.setColumnCount(1)
            key.setRowCount(nth_part)
            key.setVerticalHeaderLabels(thingie)
            for n in range(nth_part):
                key.verticalHeaderItem(n).setTextAlignment(Qt.AlignVertical_Mask)
            
            for k, row in zip(thingie, range(-1, len(thingie))):
                item = QTableWidgetItem(str(thingie[k]))
                item.setTextAlignment(Qt.AlignRight)
                key.setItem(row, 1, item)



        
    def add_parts(self, ship):
        needed = self.required_parts[ship]
        for part in needed:
            need = needed[part]
            if need > 0:
                try:
                    self.need_parts[part] += needed[part]
                except KeyError:
                    self.need_parts[part] = needed[part]

    def remove_parts(self, ship):
        needed = self.required_parts[ship]
        for part in needed:
            try:
                self.need_parts[part] -= needed[part]
                if self.need_parts[part] <=0:
                    del self.need_parts[part]
            except: continue

    def progress_table(self):
        parts = self.need_parts
        materials = self.have_parts
        required = {}
        required2 = {}
        for part in parts.keys():
            percent = materials[part]/parts[part]
            if percent < 1:
                required[part] = f'{round(percent*100, 2)}%'
                required2[part] = f'{materials[part]} out of {parts[part]}'
            else:
                required[part] = 'Done - 100%'
                required2[part] = f'{parts[part]} out of {parts[part]}'
                
                
        nth_part = len(required)
        self.progress.setColumnCount(2)
        self.progress.setRowCount(nth_part)
        self.progress.setVerticalHeaderLabels(required)
        for n in range(nth_part):
            self.progress.verticalHeaderItem(n).setTextAlignment(Qt.AlignVertical_Mask)
        
        for k, row in zip(required, range(-1, len(required))):
            item = QTableWidgetItem(str(required[k]))
            item.setTextAlignment(Qt.AlignRight)
            self.progress.setItem(row, 2, item)      
              
        for k, row in zip(required2, range(0, len(required2))):
            item = QTableWidgetItem(str(required2[k]))
            item.setTextAlignment(Qt.AlignRight)
            self.progress.setItem(row, 1, item)
            
        self.progress.resizeColumnsToContents()

    def have_materials_table(self):
        1
    def have_parts_table(self):
        1

    def need_materials_table(self):
        parts = self.need_parts
        materials = self.parts
        required = {}
        for part in parts.keys():
            for mater in materials[part].keys():
                try:
                    required[mater] += parts[part]*materials[part][mater]
                except KeyError:
                    required[mater] = parts[part]*materials[part][mater]
        nth_part = len(required)
        self.materials_need.setColumnCount(1)
        self.materials_need.setRowCount(nth_part)
        self.materials_need.setVerticalHeaderLabels(required)
        for n in range(nth_part):
            self.materials_need.verticalHeaderItem(n).setTextAlignment(Qt.AlignVertical_Mask)
        
        for k, row in zip(required, range(-1, len(required))):
            item = QTableWidgetItem(str(required[k]))
            item.setTextAlignment(Qt.AlignRight)
            self.materials_need.setItem(row, 1, item)

    def need_parts_table(self):
        sender = self.sender()
        ship = sender.text()
        if sender.isChecked() == True:
            self.add_parts(ship) 
        else:
            self.remove_parts(ship)
        
        self.parts_need.setRowCount(0)
        if len(self.need_parts.keys()) != 0:
            nth_part = len(self.need_parts)
            self.parts_need.setColumnCount(1)
            self.parts_need.setRowCount(nth_part)
            self.parts_need.setVerticalHeaderLabels(self.need_parts)
            for n in range(nth_part):
                self.parts_need.verticalHeaderItem(n).setTextAlignment(Qt.AlignVertical_Mask)
            
            for k, row in zip(self.need_parts, range(-1, len(self.need_parts))):
                item = QTableWidgetItem(str(self.need_parts[k]))
                item.setTextAlignment(Qt.AlignRight)
                self.parts_need.setItem(row, 1, item)
        
        self.need_materials_table()
        self.progress_table()




    @pyqtSlot(int,int)
    def new_one(self, row, column):
        try:
            self.coloring(column)
        except: pass
        
    def coloring(self, columns):
        for column in range(0,4):
            try:
                for row in range(2, 28):
                    to_compare = self.table_stat.item(row, columns).text()
                    compared = self.table_stat.item(row, column).text()
    
                    if '.' in compared:
                        to_compare = float(to_compare)
                        compared = float(compared)
                    elif ':' in compared:
                        to_compare = 0
                        compared = 0
                    else:
                        to_compare = int(to_compare.replace(u'\xa0', ''))
                        compared = int(compared.replace(u'\xa0', ''))
                        
                    try:
                        check = to_compare - compared
                        if check < 0.0:
                            self.table_stat.item(row, column).setForeground(QColor(0,160,0))
                        elif check > 0.0:
                            self.table_stat.item(row, column).setForeground(QColor(200,0,0))
                        else:
                            self.table_stat.item(row, column).setForeground(QColor(0,0,0))
                    except: continue
            except: continue
        
    def player_fill(self):
        sender = self.sender()
        text = str(sender.text())
        column = str(sender.objectName()).replace('line_player', '')
        column = int(column) - 1
        try:
            self.stat_table_fill(text, column)
        except:
            if text == '':
                for i in range(len(self.player_rows)):
                    item = QTableWidgetItem('')
                    self.table_stat.setItem(i, column, item)
                item = QTableWidgetItem('Insert player name')
                item.setTextAlignment(Qt.AlignLeft)
                self.table_stat.setItem(0, column, item)
            else:
                for i in range(len(self.player_rows)):
                    item = QTableWidgetItem('')
                    self.table_stat.setItem(i, column, item)
                item = QTableWidgetItem('No player with IGN: {}'.format(text))
                item.setTextAlignment(Qt.AlignLeft)
                self.table_stat.setItem(0, column, item)
            self.table_stat.resizeColumnsToContents()
        
        try:
            self.coloring(0)
        except: pass
        
    def stat_table_fill(self, ign, column):
        stats = proper_stats(str(ign))
        
        row = 0
        for each in self.player_rows:
            if each == 'IGN':
                item = QTableWidgetItem(str(ign))
                item.setTextAlignment(Qt.AlignLeft)
                self.table_stat.setItem(row, column, item)
            elif each == 'Corp':
                corp = '{} [{}]'.format(stats['Corporation name'], stats['Corporation tag'])
                item = QTableWidgetItem(corp)
                item.setTextAlignment(Qt.AlignLeft)
                self.table_stat.setItem(row, column, item)
            else:
                item = QTableWidgetItem(str(stats[each]))
                item.setTextAlignment(Qt.AlignRight)
                self.table_stat.setItem(row, column, item)
            row+=1
        self.table_stat.resizeColumnsToContents()
                
    def stat_table_setup(self):
        self.player_rows = ['IGN', 'Corp', 'Eff rating', 
                'Fleet Strength', 'Karma', 'Win/Loss', 'Win Ratio',
                'Kill/Game', 'Assist/Game', 'Death/Game', 'Dmg/Game', 
                'Heal/Game', 'Cap points/Game', 'Time/Game', 
                'Kill/Death', 'Assist/Death', 
                'Total games', 'Total won',  'Total lost', 'Total kills', 
                'Total deaths', 'Total assists', 'Total dmg', 'Total heal', 
                'Total cap in CTB', 'Total in battle', 'Dmg/min', 'Kills/min']
        columns = ['Player 1', 'Player 2', 'Player 3', 'Player 4']
        
        len_rows = len(self.player_rows)
        self.table_stat.setColumnCount(4)
        self.table_stat.setRowCount(len_rows)
        
        self.table_stat.setHorizontalHeaderLabels(columns)
        self.table_stat.setVerticalHeaderLabels(self.player_rows)
        for n in range(len_rows):
            self.table_stat.verticalHeaderItem(n).setTextAlignment(Qt.AlignVertical_Mask)




    def file_open(self):
        name, _ = QFileDialog.getOpenFileName(self, 'Open File')
        name = name.replace('chat.log', 'game.log').replace('combat.log', 'game.log').replace('game.net.log', 'game.log')
        try:
            self.table_fill(name)  
        except:
            pass
        
    def app_close(self):
        sys.exit()

    def game_choice(self, text):
        text = text.split(' ')[6]
        self.fuckthis(text)
        return text
    
    def table_fill(self, gamelog_open):

        self.full_info, game_keys = everything(gamelog_open)
        self.comboBox.clear()
        
        game = [x for x in range(1, len(game_keys)+1)]
        
        for klucz, which in zip(game_keys, game):
            time = self.full_info[klucz]['times'][0]
            winner = self.full_info[klucz]['winner']
            self.comboBox.addItem('Game '+str(which)+' - '+str(time)+' - ID: '+klucz+' - '+winner)
  
        klucz = game_keys[0]
        self.fuckthis(klucz)
        klucz = self.comboBox.activated[str].connect(self.game_choice)
   
    def fuckthis(self, klucz):
        self.team1.setColumnCount(0)
        self.team1.setRowCount(0)
        self.team2.setColumnCount(0)
        self.team2.setRowCount(0)

        game = self.full_info[str(klucz)]
        
        team_1 = game['Team 1']
        team_2 = game['Team 2']       
        interesting = ['Kills', 'Deaths', 'Damage', 'Score', 'Ships used', 'W/L', 'K/D', 'K/G', 'Dmg/G']
        
        self.table_team(team_1, interesting, self.team1)
        self.table_team(team_2, interesting, self.team2)
        
        self.team1.resizeColumnsToContents()
        self.team2.resizeColumnsToContents()
        
    def table_team(self, team, interesting, table):
        len_columns = len(interesting)
        len_rows = len(team.keys())
    
        table.setColumnCount(len_columns)
        table.setHorizontalHeaderLabels(interesting)
        table.setRowCount(len_rows)
        table.setVerticalHeaderLabels(team.keys())

        for n in range(len_columns):
            table.verticalHeaderItem(n).setTextAlignment(Qt.AlignVertical_Mask)
    
        self.setting_gamedata(len_rows, 0, team, 'kills', table)
        self.setting_gamedata(len_rows, 1, team, 'Deaths', table)
        self.setting_gamedata(len_rows, 2, team, 'Dmg', table)
        self.setting_gamedata(len_rows, 3, team, 'Eff in game', table)
        self.setting_gamedata(len_rows, 4, team, 'Ships used', table)
        self.setting_playerdata(len_rows, 5, team, 'Win/Loss', table)
        self.setting_playerdata(len_rows, 6, team, 'Kill/Death', table)
        self.setting_playerdata(len_rows, 7, team, 'Kill/Game', table)
        self.setting_playerdata(len_rows, 8, team, 'Dmg/Game', table) 
    
        for n in range(len_rows):
            table.verticalHeaderItem(n).setToolTip('whatever'+'\n'*5+str(n))

    def setting_gamedata(self, length, column, data, stat, table):
        players = data.keys()
        if stat == 'Dmg':
            for row, player in zip(range(length), players):
                item = QTableWidgetItem(str(data[player]['Game Stats'][stat]['total']))
                item.setTextAlignment(Qt.AlignRight)
                table.setItem(row, column, item)
        if stat == 'Ships used':
            for row, player in zip(range(length), players):
                try:
                    item = QTableWidgetItem(', '.join(data[player]['Game Stats'][stat]))
                    item.setTextAlignment(Qt.AlignLeft)
                    table.setItem(row, column, item) 
                except:
                    item = QTableWidgetItem('No data')
                    item.setTextAlignment(Qt.AlignLeft)
                    table.setItem(row, column, item)   
        if stat != 'Dmg' and stat != 'Ships used':
            for row, player in zip(range(length), players):
                item = QTableWidgetItem(str(data[player]['Game Stats'][stat]))
                item.setTextAlignment(Qt.AlignRight)
                table.setItem(row, column, item)  

    def setting_playerdata(self, length, column, data, stat, table):
        players = data.keys()
        for row, player in zip(range(length), players):
            try:
                item = QTableWidgetItem(str(data[player]['API'][stat]))
                item.setTextAlignment(Qt.AlignRight)
                table.setItem(row, column, item)   
            except:
                item = QTableWidgetItem('No data')
                item.setTextAlignment(Qt.AlignRight)
                table.setItem(row, column, item)           

def main():
    app = QApplication(sys.argv)
    GUI = Combat_log()
    GUI.show()
    app.exec_()

if __name__ == '__main__':
    main()