import json
import os
import datetime
from riotwatcher import LolWatcher
from secret import api_key

def parse_rofl(path):
    lol_watcher = LolWatcher(api_key())
    my_region = 'kr'

    versions = lol_watcher.data_dragon.versions_for_region(my_region)
    champions_version = versions['n']['champion']

    ch_data = lol_watcher.data_dragon.champions(champions_version,locale = versions['l'])
    
    key_ch = {}

    for i in ch_data['data'].values():
        key_ch[i['id'].lower()] = int(i['key'])
    

    with open(path, "r",encoding = 'utf-8',errors = 'ignore') as st:
        contents = st.readlines()
    idx = 0
    for i,l in enumerate(contents):
        if '"statsJson":"[' in l:
            idx = i
            break
    test = contents[idx].split('"statsJson":"[')[1].split(']')[0].replace('\\','')
    dict_obj = {'json_ob':eval(test)}

    match_id = path[:-5].split('-')[1]
    game_dur = dict_obj['json_ob'][0]['TIME_PLAYED']
    win1, win2 = dict_obj['json_ob'][0]['WIN'], dict_obj['json_ob'][5]['WIN']
    game_creation = int(datetime.datetime.now().timestamp()*1000)

    new_data = {'MatchId' : match_id, 'gameDuration' : game_dur,'gameCreation':game_creation,
            'teams':[{'win':win1},{'win':win2}],'participants':[],
            'participantIdentities': []}
    
    for i,v in enumerate(dict_obj['json_ob']):
        tmp_dict = {}
        stats = {}
        stats['kills'] = int(v['CHAMPIONS_KILLED'])
        stats['deaths'] = int(v['NUM_DEATHS'])
        stats['assists'] = int(v['ASSISTS'])
        stats['totalMinionsKilled'] = int(v['MINIONS_KILLED'])
        stats['neutralMinionsKilled'] = int(v['NEUTRAL_MINIONS_KILLED'])
        stats['item0'] = v['ITEM0']
        stats['item1'] = v['ITEM1']
        stats['item2'] = v['ITEM2']
        stats['item3'] = v['ITEM3']
        stats['item4'] = v['ITEM4']
        stats['item5'] = v['ITEM5']
        stats['item6'] = v['ITEM6']
        stats['visionWardsBoughtInGame'] = v['VISION_WARDS_BOUGHT_IN_GAME']
        stats['perk0'] = v['PERK0']
        stats['perkSubStyle'] = v['PERK_SUB_STYLE']
        tmp_dict['name'] = v['NAME']
        tmp_dict['championId'] = key_ch[v['SKIN'].lower()]
        tmp_dict['stats'] = stats
        new_data['participants'].append(tmp_dict)
        new_data['participantIdentities'].append({'player':{'summonerName':v['NAME']}})

    return new_data#json.dumps(new_data)

if __name__ == '__main__':
    path = '../end'
    for p in os.listdir(path):
        if ".rofl" in p:
            data = parse_rofl("../end/" + p)
    # path = 'KR-5457721894.rofl'
    # data = parse_rofl(path)
    # with open('./testrofl4.json','w') as f:
    #     f.write(data)