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
    game_dur = int(dict_obj['json_ob'][0]['TIME_PLAYED'])
    win1, win2 = dict_obj['json_ob'][0]['WIN'], dict_obj['json_ob'][5]['WIN']
    game_creation = 1000*(os.path.getmtime(path))#int(datetime.datetime.now().timestamp()*1000)

    new_data = {'gameId' : match_id, 'gameDuration' : game_dur,'gameCreation':game_creation,
            'teams':[{'win':win1},{'win':win2}],'participants':[],
            'participantIdentities': []}

    for i,v in enumerate(dict_obj['json_ob']):
        tmp_dict = {}
        stats = {}
        stats['kills'] = int(v['CHAMPIONS_KILLED'])
        stats['deaths'] = int(v['NUM_DEATHS'])
        stats['assists'] = int(v['ASSISTS'])
        stats['champLevel'] = int(v['LEVEL'])
        stats['goldEarned'] = int(v['GOLD_EARNED'])
        stats['totalMinionsKilled'] = int(v['MINIONS_KILLED'])
        stats['neutralMinionsKilled'] = int(v['NEUTRAL_MINIONS_KILLED'])
        stats['item0'] = int(v['ITEM0'])
        stats['item1'] = int(v['ITEM1'])
        stats['item2'] = int(v['ITEM2'])
        stats['item3'] = int(v['ITEM3'])
        stats['item4'] = int(v['ITEM4'])
        stats['item5'] = int(v['ITEM5'])
        stats['item6'] = int(v['ITEM6'])
        stats['visionWardsBoughtInGame'] = int(v['VISION_WARDS_BOUGHT_IN_GAME'])
        stats['perk0'] = int(v['PERK0'])
        stats['perkSubStyle'] = int(v['PERK_SUB_STYLE'])
        tmp_dict['name'] = v['NAME']
        tmp_dict['championId'] = int(key_ch[v['SKIN'].lower()])
        tmp_dict['stats'] = stats
        new_data['participants'].append(tmp_dict)
        new_data['participantIdentities'].append({'player':{'summonerName':v['NAME']}})

    return new_data