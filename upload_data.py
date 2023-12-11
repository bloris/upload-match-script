import json
import datetime

import numpy as np
import scipy.stats


from encryptId import encrypt
from user import User
from match import UserMatch, Match
from database import firebaseDB
from secret import api_key, get_changed_name
from parse_rofl import parse_rofl
  
class AutoScript:
    def __init__(self):
        self.db = firebaseDB()
        self.api_key = api_key()

    def getData(self,path):
        if ".json" in path:
            self.data = self.getJson(path)
        elif ".rofl" in path:
            self.data = parse_rofl(path)

        self.data['gameId'] = str(self.data["gameId"])

        if self.db.isMatchExist(self.data['gameId']):
            print("Match Already Exist")
            return False
        self.allUser = self.db.getAllUser()
        self.userDict = self.makeUser()
        self.userPuuidList = list(self.userDict.keys())
        self.match = [self.data['gameId'], Match(self.data['gameId'],self.userPuuidList,self.data['teams'][0]['win'] == 'Win',
            datetime.datetime.fromtimestamp(self.data['gameCreation']/1000),self.data['gameDuration'])]
        self.userMatch = self.makeMatchList()

        return True

    def putData(self):
        response = self.db.putData(self.userDict,self.match,self.userMatch)
        # if response:
        #     print("Success")
        # else:
        #     print("Fail")

    def getJson(self,path):
        with open(path,"r") as st_json:
            data = json.load(st_json)
        return data

    def makeUser(self):
        userDict = {}
        changedName = get_changed_name()
        for i in range(10):
            summoner = self.data['participantIdentities'][i]['player']
            name = summoner['summonerName']
            if name in changedName.keys():
                name = changedName[name]
            #print(name)
            user_data = encrypt(self.api_key,name)
            puuid = user_data['puuid']

            if puuid in self.allUser.keys():
                user = self.allUser[puuid]
            else:
                user = User(puuid,user_data['name'],user_data['profileIconId'],1300,0,0)
            user.name = user_data['name']
            user.profileIconId = user_data['profileIconId']
            userDict[puuid] = user
        self.allUser.update(userDict)
        return userDict

    def makeMatchList(self):
        userMatchList = {}
        matchId = self.data['gameId']
        for i in range(10):
            stat = self.data['participants'][i]
            userMatchList[self.userPuuidList[i]]=UserMatch(matchId,stat['championId'],0,stat['stats']['perk0'],stat['stats']['perkSubStyle'],
            stat['stats']['kills'],stat['stats']['deaths'],stat['stats']['assists'],
            stat['stats']['totalMinionsKilled']+stat['stats']['neutralMinionsKilled'],
            0,[stat['stats']['item0'],stat['stats']['item1'],stat['stats']['item2'],stat['stats']['item3'],
            stat['stats']['item4'],stat['stats']['item5'],stat['stats']['item6']],stat['stats']['visionWardsBoughtInGame'],
            stat['stats']['champLevel'], stat['stats']['goldEarned'],
            datetime.datetime.fromtimestamp(self.data['gameCreation']/1000),False)

        return userMatchList

    def updateElo(self):
        all_elo = [v.elo for _,v in self.allUser.items()]
        avg_elo, std_elo = np.mean(all_elo), np.std(all_elo)

        supportList = [i[0] for i in sorted([[k,v.cs] for k,v in self.userMatch.items()],key=lambda x:x[1])[:2]]
        eloList = [v.elo for k,v in self.userDict.items()]

        score = []
        for k,v in self.userMatch.items():
            if k in supportList:
                score.append(v.score(True))
            else:
                score.append(v.score())

        responsibilityFactor = 10 #낮아질수록 상위 플레이어의 책임이 커짐
        outperformThreshold = 40 #캐리 점수, 져도 점수를 거의 잃지 않으며 이를 넘길경우 소량 증가함

        weightedPercentile = [pow(scipy.stats.norm(avg_elo, std_elo).cdf(elo), 1/responsibilityFactor) for elo in eloList]
        weightedPercentile = list(map(lambda x:0.5 if np.isnan(x) else x, weightedPercentile))
        t1Score, t2Score = sum(score[:5]),sum(score[5:])
        t1Elo, t2Elo = sum(eloList[:5]),sum(eloList[5:])
        killList = [v.kill for v in self.userMatch.values()]
        t1Kill, t2Kill = sum(killList[:5]), sum(killList[5:])

        t1TotalWeightedPercentile, t2TotalWeightedPercentile = sum(weightedPercentile[:5]), sum(weightedPercentile[5:])

        deltaCombatScore = []
        for i in range(5):
            expectedScore = t1Score*weightedPercentile[i]/t1TotalWeightedPercentile
            deltaCombatScore.append(score[i] - expectedScore)

        for i in range(5,10):
            expectedScore = t2Score*weightedPercentile[i]/t2TotalWeightedPercentile
            deltaCombatScore.append(score[i] - expectedScore)

        elo_change_sum = Match.determineK(t1Score,t2Score)
        ea = 1.0 / (1.0 + pow(10.0, (t2Elo - t1Elo) / 400.0))

        s = 1 if self.data['teams'][0]['win'] == 'Win' else 0
        teamOneEloChange = round(elo_change_sum * (s - ea))
        teamTwoEloChange = -teamOneEloChange

        for i in range(5):
            if teamOneEloChange >= 0:
                eloList[i] += int((teamOneEloChange / 5) * (1 + deltaCombatScore[i] / outperformThreshold)+0.5)
            else:
                eloList[i] += int((teamOneEloChange / 5) * (1 - deltaCombatScore[i] / outperformThreshold)+0.5)

        for i in range(5,10):
            if teamTwoEloChange >= 0:
                eloList[i] += int((teamTwoEloChange / 5) * (1 + deltaCombatScore[i] / outperformThreshold)+0.5)
            else:
                eloList[i] += int((teamTwoEloChange / 5) * (1 - deltaCombatScore[i] / outperformThreshold)+0.5)

        eloChange = [eloList[i] - self.userDict[self.userPuuidList[i]].elo for i in range(10)]

        for i in range(10):
            puuid = self.userPuuidList[i]
            killTotal = t1Kill if i < 5 else t2Kill
            if i < 5:
                win = True if s == 1 else False
            else:
                win = True if s == 0 else False
            self.userDict[puuid].elo = eloList[i]
            self.userDict[puuid].update_tier()
            self.userMatch[puuid].eloChange = eloChange[i]
            self.userMatch[puuid].killP = int(100 * (self.userMatch[puuid].kill+self.userMatch[puuid].assist) / killTotal + 0.5)
            self.userMatch[puuid].win = win
            if win:
                self.userDict[puuid].win += 1
            else:
                self.userDict[puuid].lose += 1

    def printCurrent(self):
        for v in self.userDict.values():
            print(v)
        print()
        print(self.match[1])
        print()
        for v in self.userMatch.values():
            print(v)

