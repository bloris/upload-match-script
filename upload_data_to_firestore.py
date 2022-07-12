import json
import datetime

import numpy as np
import scipy.stats


from encryptId import encrypt
from user import User
from match import UserMatch, Match
from database import dbInit
from secret import api_key
  
class AutoScript:
    def __init__(self,path):
        self.db = dbInit()
        self.api_key = api_key()
        if ".json" in path:
            self.data = self.getJson(path)
        self.allUser = self.getAllUser()
        self.userDict = self.makeUser()
        self.userPuuidList = list(self.userDict.keys())
        self.match = Match(self.userPuuidList,self.data['teams'][0]['win'] == 'Win',
            datetime.datetime.fromtimestamp(self.data['gameCreation']/1000))
        self.userMatch = self.makeMatchList()

    def getJson(self,path):
        with open(path,"r") as st_json:
            data = json.load(st_json)
        return data

    def makeUser(self):
        userDict = {}
        changedName = {
            "감염된게음성인가":"깨물기 없다 앙",
            "옥산동 제어와드": "오산동 제어와드",
            "림0I": "LuLu랄라",
        }
        for i in range(10):
            summoner = self.data['participantIdentities'][i]['player']
            name = summoner['summonerName']
            if name in changedName.keys():
                name = changedName[name]
            user_data = encrypt(self.api_key,name)
            puuid = user_data['puuid']

            if puuid in self.allUser.keys():
                user = self.allUser[puuid]
            else:
                user = User(user_data['name'],user_data['profileIconId'],1300,0,0)
            userDict[puuid] = user
        self.allUser.update(userDict)
        return userDict

    def getAllUser(self):
        allUser = {}
        docr_ref = self.db.collection(u'users').stream()
        for doc in docr_ref:
            allUser[doc.id] = User.from_dict(doc.to_dict())
        return allUser

    def makeMatchList(self):
        userMatchList = {}
        for i in range(10):
            stat = self.data['participants'][i]
            userMatchList[self.userPuuidList[i]]=(UserMatch(stat['championId'],0,stat['stats']['perk0'],stat['stats']['perkSubStyle'],
            stat['stats']['kills'],stat['stats']['deaths'],stat['stats']['assists'],
            stat['stats']['totalMinionsKilled']+stat['stats']['neutralMinionsKilled'],
            0,[stat['stats']['item0'],stat['stats']['item1'],stat['stats']['item2'],stat['stats']['item2'],
            stat['stats']['item4'],stat['stats']['item5'],stat['stats']['item6']],stat['stats']['visionWardsBoughtInGame'],
            datetime.datetime.fromtimestamp(self.data['gameCreation']/1000)))

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
            self.userDict[self.userPuuidList[i]].elo = eloList[i]
            self.userMatch[self.userPuuidList[i]].eloChange = eloChange[i]

    def printCurrent(self):
        for v in self.userDict.values():
            print(v)
        print()
        print(self.match)
        print()
        for v in self.userMatch.values():
            print(v)

autoScript = AutoScript("../end/4783411518.json")
autoScript.printCurrent()
autoScript.updateElo()
autoScript.printCurrent()


# db = dbInit()
# data = getJson("../end/4783411518.json")

# allUser = getAllUser()
# userDict = makeUser(data,api_key(),allUser)
# allUser.update(userDict)

# autoScript = AutoScript()

# userPuuidList = list(userDict.keys())
# match = Match(userPuuidList,data['teams'][0]['win'] == 'Win',datetime.datetime.fromtimestamp(data['gameCreation']/1000))

# userMatch = makeMatchList(userPuuidList,data)

# all_elo = [v.elo for _,v in allUser.items()]
# avg_elo, std_elo = np.mean(all_elo), np.std(all_elo)

# supportList = [i[0] for i in sorted([[k,v.cs] for k,v in userMatch.items()],key=lambda x:x[1])[:2]]
# eloList = [v.elo for k,v in userDict.items()]

# score = []
# for k,v in userMatch.items():
#     if k in supportList:
#         score.append(v.score(True))
#     else:
#         score.append(v.score())

# responsibilityFactor = 10 #낮아질수록 상위 플레이어의 책임이 커짐
# outperformThreshold = 40 #캐리 점수, 져도 점수를 거의 잃지 않으며 이를 넘길경우 소량 증가함


# print(avg_elo, std_elo)
# weightedPercentile = [pow(scipy.stats.norm(avg_elo, std_elo).cdf(elo), 1/responsibilityFactor) for elo in eloList]
# weightedPercentile = list(map(lambda x:0.5 if np.isnan(x) else x, weightedPercentile))
# t1Score, t2Score = sum(score[:5]),sum(score[5:])
# t1Elo, t2Elo = sum(eloList[:5]),sum(eloList[5:])

# t1TotalWeightedPercentile, t2TotalWeightedPercentile = sum(weightedPercentile[:5]), sum(weightedPercentile[5:])

# deltaCombatScore = []
# for i in range(5):
#     expectedScore = t1Score*weightedPercentile[i]/t1TotalWeightedPercentile
#     deltaCombatScore.append(score[i] - expectedScore)

# for i in range(5,10):
#     expectedScore = t2Score*weightedPercentile[i]/t2TotalWeightedPercentile
#     deltaCombatScore.append(score[i] - expectedScore)

# elo_change_sum = Match.determineK(t1Score,t2Score)
# ea = 1.0 / (1.0 + pow(10.0, (t2Elo - t1Elo) / 400.0))

# s = 1 if data['teams'][0]['win'] == 'Win' else 0
# teamOneEloChange = round(elo_change_sum * (s - ea))
# teamTwoEloChange = -teamOneEloChange

# for i in range(10):
#     print(userDict[userPuuidList[i]].name,score[i],eloList[i])

# for i in range(5):
#     if teamOneEloChange >= 0:
#         eloList[i] += int((teamOneEloChange / 5) * (1 + deltaCombatScore[i] / outperformThreshold)+0.5)
#     else:
#         eloList[i] += int((teamOneEloChange / 5) * (1 - deltaCombatScore[i] / outperformThreshold)+0.5)

# for i in range(5,10):
#     if teamTwoEloChange >= 0:
#         eloList[i] += int((teamTwoEloChange / 5) * (1 + deltaCombatScore[i] / outperformThreshold)+0.5)
#     else:
#         eloList[i] += int((teamTwoEloChange / 5) * (1 - deltaCombatScore[i] / outperformThreshold)+0.5)

# eloChange = [eloList[i] - userDict[userPuuidList[i]].elo for i in range(10)]

# for i in range(10):
#     userDict[userPuuidList[i]].elo = eloList[i]
#     userMatch[userPuuidList[i]].eloChange = eloChange[i]

# for k,v in userDict.items():
#     print(v)
# print()
# print(match)
# print()
# for k,v in userMatch.items():
#     print(v)


#{'participantId': 3, 'teamId': 100, 'championId': 876, 
# 'spell1Id': 14, 'spell2Id': 4, 'stats': {'participantId': 3, 
# 'win': True, 'item0': 4637, 'item1': 6653, 'item2': 1029, 'item3': 0, 'item4': 3020, 'item5': 0, 'item6': 3340, 
# 'kills': 4, 'deaths': 4, 'assists': 7, 'largestKillingSpree': 3, 'largestMultiKill': 2, 'killingSprees': 1, 
# 'longestTimeSpentLiving': 642, 'doubleKills': 1, 'tripleKills': 0, 'quadraKills': 0, 'pentaKills': 0, 
# 'unrealKills': 0, 'totalDamageDealt': 91496, 'magicDamageDealt': 65845, 'physicalDamageDealt': 6615, 
# 'trueDamageDealt': 19035, 'largestCriticalStrike': 0, 'totalDamageDealtToChampions': 16879, 
# 'magicDamageDealtToChampions': 13605, 'physicalDamageDealtToChampions': 402, 'trueDamageDealtToChampions': 2870, 
# 'totalHeal': 2985, 'totalUnitsHealed': 1, 'damageSelfMitigated': 9009, 'damageDealtToObjectives': 3587, 
# 'damageDealtToTurrets': 3587, 'visionScore': 11, 'timeCCingOthers': 26, 'totalDamageTaken': 16275, 
# 'magicalDamageTaken': 4933, 'physicalDamageTaken': 10828, 'trueDamageTaken': 514, 'goldEarned': 9989, 
# 'goldSpent': 8450, 'turretKills': 2, 'inhibitorKills': 1, 'totalMinionsKilled': 142, 'neutralMinionsKilled': 0, 
# 'neutralMinionsKilledTeamJungle': 0, 'neutralMinionsKilledEnemyJungle': 0, 'totalTimeCrowdControlDealt': 301, 
# 'champLevel': 15, 'visionWardsBoughtInGame': 2, 'sightWardsBoughtInGame': 0, 'wardsPlaced': 9, 'wardsKilled': 1, 
# 'firstBloodKill': False, 'firstBloodAssist': False, 'firstTowerKill': False, 'firstTowerAssist': False, 
# 'firstInhibitorKill': False, 'firstInhibitorAssist': False, 'combatPlayerScore': 0, 'objectivePlayerScore': 0, 
# 'totalPlayerScore': 0, 'totalScoreRank': 0, 'wasAfk': False, 'leaver': False, 'gameEndedInEarlySurrender': False, 
# 'gameEndedInSurrender': False, 'causedEarlySurrender': False, 'earlySurrenderAccomplice': False, 
# 'teamEarlySurrendered': False, 'playerScore0': 0, 'playerScore1': 0, 'playerScore2': 0, 'playerScore3': 0, 
# 'playerScore4': 0, 'playerScore5': 0, 'playerScore6': 0, 'playerScore7': 0, 'playerScore8': 0, 'playerScore9': 0, 
# 'perk0': 8010, 'perk0Var1': 105, 'perk0Var2': 0, 'perk0Var3': 0, 'perk1': 9111, 'perk1Var1': 773, 'perk1Var2': 220, 
# 'perk1Var3': 0, 'perk2': 9105, 'perk2Var1': 18, 'perk2Var2': 30, 'perk2Var3': 0, 'perk3': 8014, 'perk3Var1': 291, 
# 'perk3Var2': 0, 'perk3Var3': 0, 'perk4': 8139, 'perk4Var1': 977, 'perk4Var2': 0, 'perk4Var3': 0, 'perk5': 8135, 
# 'perk5Var1': 1896, 'perk5Var2': 4, 'perk5Var3': 0, 'perkPrimaryStyle': 8000, 'perkSubStyle': 8100, 'statPerk0': 5005, 
# 'statPerk1': 5008, 'statPerk2': 5002}, 'timeline': {'participantId': 3, 'creepsPerMinDeltas': {'10-20': 5.8, '
# 0-10': 5.300000000000001}, 'xpPerMinDeltas': {'10-20': 529.6, '0-10': 431.0}, 'goldPerMinDeltas': {'10-20': 388.4, '0-10': 215.8}, 
# 'damageTakenPerMinDeltas': {'10-20': 795.9000000000001, '0-10': 275.6}, 'role': 'SOLO', 'lane': 'MIDDLE'}}