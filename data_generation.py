import requests
from bs4 import BeautifulSoup
import pdb
from tqdm import tqdm
import multiprocessing
from multiprocessing import Manager
import threading
#https://stats.espncricinfo.com/ci/engine/stats/index.html?batting_fielding_first=1;captain_involve=7593;class=2;filter=advanced;floodlit=2;home_or_away=1;home_or_away=2;home_or_away=3;host=2;innings_number=1;orderby=team_score;result=1;team=6;template=results;toss=1;type=team;view=innings


BAT_FIRST = 1
BALL_FIRST = 2

TOSS_WON = 1
TOSS_LOST = 2

MATCH_WON = 1
MATCH_LOST = 2

DAY_MATCH = 1
DAY_NIGHT_MATCH = 2
NIGHT_MATCH = 3

ODI = 2
TT = 3

HOSTS = {6:"india", 1:"england",2:"australia",3: "south_africa", 4:"west_indis",5:"new_zealand",7:"pakistan",8:"sri_lanka",9:"zimbambave",11:"usa",12:"bermuda",15:"netherlands",16:"malaysia",17:"canada",27:"uae",29:"ireland",30:"scotland", 25:"bangladesh",26:"kenya"}
OPP = HOSTS.copy()
OPP[40] = 'afganistan'

PLAYERS = {}
CAPTAINS = {}


#class to 
class DataScrapper:

    def __init__(self, host, opp, players = {}, captains = {}):

        #store the players and captains
        self.players = players
        self.captains = captains
        
        #set up all other queries
        self.host = host
        self.opp = opp
        self.team = opp
        self.day_match = {DAY_MATCH: 1, DAY_NIGHT_MATCH: 0, NIGHT_MATCH: 2}
        self.toss = {TOSS_WON: 1, TOSS_LOST: 0}
        self.bat_first = {BAT_FIRST:1, BALL_FIRST:0}
        self.result = {'won':1, 'lost':0}
        self.format = {ODI: 0, TT:1}

    def get_url(self, host, format, day_match, toss, bat_first, opp, team, player = None, captain = None):

        url = "https://stats.espncricinfo.com/ci/engine/stats/index.html?" + \
                    "home_or_away=1;home_or_away=2;home_or_away=3;orderby=team_score;size=200;" + \
                    f"team={team};template=results;type=team;view=innings;filter=advanced;innings_number=1;" + \
                    f"batting_fielding_first={bat_first};" + \
                    f"class={format};" + \
                    f"floodlit={day_match};" + \
                    f"host={host};" + \
                    f"toss={toss};" + \
                    f"opposition={opp};"
        if(bat_first == 2):
            url += 'team_view=bowl;'
        if(captain is not None):
            url += f'captain_involve={captain};'
        return url

    def get_data(self, host, format, day_match, toss, bat_first, opp, team):
    
        
        url = self.get_url(host, format, day_match, toss, bat_first, opp, team)
        import time 
        time.sleep(2)
        response = requests.get(url)
        data = BeautifulSoup(response.content, 'html.parser')

        match_dict_orig = {'team': self.team[team], 'opp':self.opp[opp], 'host':self.host[host], 'toss':self.toss[toss], 'day_match': self.day_match[day_match], 'bat_first':self.bat_first[bat_first], 'format':self.format[format]}
        match_dict_orig['fow'] = 10
        matches = data.findAll("tr", attrs = {"class":"data1"})
        
        if(len(matches) >= 199):
            print(url)
            pdb.set_trace()
        for match in matches:
            match_data = match.findAll("td")
            if(len(match_data) <= 9):
                continue 
            date = match_data[9].text
            match_dict = match_dict_orig.copy()
            score = match_data[1].text
            match_dict['score'] = int(score.split('/')[0])
            if("/" in score):
                match_dict['fow'] = int(score.split('/')[-1])
                
            match_dict['rpo'] = float(match_data[3].text)
            match_dict['year'] = int(match_data[9].text.split(' ')[-1])
            match_dict['month'] = match_data[9].text.split(' ')[-2].lower()
            if(match_data[5].text not in self.result):
                continue
            match_dict['result'] = self.result[match_data[5].text]
            self.data[date + str(team) + "_" + str(opp)] = match_dict

    def save_data(self):

        for r in self.opp:
            o = self.opp[r]
            l = [self.data[y] for y in self.data if self.data[y]['opp'] == o]
            print(o, len(l))
            for k in self.host:
                h = self.host[k]
                lt = [y for y in l if y['host'] == h]
                print(o, h, len(lt))
        
        f = open("data_full.csv", "w")
        f.write("team" + ",")
        f.write("opp" + ",")
        f.write("host" + ",")
        f.write("year" + ",")
        f.write("month" + ",")
        f.write("toss" + ",")
        f.write("day_match" + ",")
        f.write("bat_first" + ",")
        f.write("format" + ",")
        f.write("fow" + ",")
        f.write("score" + ",")
        f.write("rpo" + ",")
        f.write("result" + "\n")
        
        
        for match_date in self.data:
            match = self.data[match_date]
            f.write(match['team'] + ",")
            f.write(match['opp'] + ",")
            f.write(match['host'] + ",")
            f.write(str(match['year']) + ",")
            f.write(match['month'] + ",")
            f.write(str(match['toss']) + ",")
            f.write(str(match['day_match']) + ",")
            f.write(str(match['bat_first']) + ",")
            f.write(str(match['format']) + ",")
            f.write(str(match['fow']) + ",")
            f.write(str(match['score']) + ",")
            f.write(str(match['rpo']) + ",")
            f.write(str(match['result']) + "\n")

            f.write(match['opp'] + ",")
            f.write(match['team'] + ",")
            f.write(match['host'] + ",")
            f.write(str(match['year']) + ",")
            f.write(match['month'] + ",")
            f.write(str(1 - match['toss']) + ",")
            f.write(str(match['day_match']) + ",")
            f.write(str(1 - match['bat_first']) + ",")
            f.write(str(match['format']) + ",")
            f.write(str(match['fow']) + ",")
            f.write(str(match['score']) + ",")
            f.write(str(match['rpo']) + ",")
            f.write(str(1 - match['result']) + "\n")
            
            
            
            
            
    
    def generate_data_thread(self, opp, host):
        for team in tqdm(self.team, leave = False):
            if(team <= opp):
                continue
            for day_match in tqdm(self.day_match, leave=False):
                for toss in self.toss:
                    for bat_first in self.bat_first:
                        for format in self.format:
                            self.get_data(host, format, day_match, toss, bat_first, opp, team)

    def generate_data(self):

        self.data = Manager().dict()
        thread_list = []
        #iterate over all data
        for opp in tqdm(self.opp):
            for host in tqdm(self.host):
                #generate the data
                process = multiprocessing.Process(target = self.generate_data_thread, 
                    args = (opp, host))

                #append the threads
                thread_list.append(process)
                process.start()
        
        #join to the threads
        for thread in thread_list:
            thread.join()
  
        self.save_data()

if __name__ == '__main__':

    data = DataScrapper(HOSTS, OPP)
    data.generate_data()
