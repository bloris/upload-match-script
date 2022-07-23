class Match(object):
    def __init__(self,users,win,matchDate,gameDuration):
        self.users = users
        self.win = win
        self.matchDate = matchDate
        self.gameDuration = gameDuration
    
    @staticmethod
    def from_dict(source):
        match = Match(source[u'users'],source[u'win'],source[u'matchDate'],source[u'gameDuration'])

        return match

    def to_dict(self):
        match = {
            u'users': self.users,
            u'win': self.win,
            u'matchDate': self.matchDate,
            u'gameDuration': self.gameDuration
        }
        return match
    
    def __repr__(self):
        return(
            f'User(\
                users={self.users}, \
                win={self.win}, \
                matchDate={self.matchDate}, \
                gameDuration={self.gameDuration}, \
            )'
        )
    
    @staticmethod
    def determineK(t1_score, t2_score):
        buckets = [{'lo': 0.00, 'hi': 0.25, 'k': 300}, # 팀 점수 차이 큼
                        {'lo': 0.25, 'hi': 0.50, 'k': 260},  # 
                        {'lo': 0.50, 'hi': 0.80, 'k': 220},  # 
                        {'lo': 0.80, 'hi': 1.01, 'k': 200}] # 팀 점수 차이 적음
        defaultK = 200
        
        decisiveness = min(t1_score, t2_score) / max(t1_score, t2_score)
        for b in buckets:
            if decisiveness >= b['lo'] and decisiveness < b['hi']:
                return b['k']
            
        return defaultK
class UserMatch(object):
    def __init__(self,champ,eloChange,mainPerk,subPerk,kill,death,assist,cs,killP,item,ward,champLevel,goldEarned,win,matchDate) -> None:
        self.champ = champ
        self.eloChange = eloChange
        self.mainPerk = mainPerk
        self.subPerk = subPerk
        self.kill = kill
        self.death = death
        self.assist = assist
        self.cs = cs
        self.killP = killP
        self.item = item
        self.ward = ward
        self.champLevel = champLevel
        self.goldEarned = goldEarned
        self.matchDate = matchDate
        self.win = win
    
    def score(self,support = False):
        return self.kill * 2 - self.death + self.assist + (0.08*self.cs) + (self.assist if support else 0)

    @staticmethod
    def from_dict(source):
        # [START_EXCLUDE]
        userMatch = UserMatch(source[u'champ'], source[u'eloChange'], source[u'mainPerk'], source[u'subPerk'], source[u'kill'], 
        source[u'death'], source[u'assist'], source[u'cs'], source[u'killP'], source[u'item'], source[u'ward'],
        source[u'champLevel'],source[u'goldEarned'], source[u'matchDate'], source[u'win'])

        return userMatch

    def to_dict(self):
        match = {
            u'champ': self.champ,
            u'eloChange': self.eloChange,
            u'mainPerk': self.mainPerk,
            u'subPerk' : self.subPerk,
            u'kill' : self.kill,
            u'death' : self.death,
            u'assist' : self.assist,
            u'cs' : self.cs,
            u'killP' : self.killP,
            u'item' : self.item,
            u'ward' : self.ward,
            u'champLevel' : self.champLevel,
            u'goldEarned' : self.goldEarned,
            u'matchDate' : self.matchDate,
            u'win' : self.win,
        }

        return match

    def __repr__(self):
        return(
            f'UserMatch(\
                champ={self.champ}, \
                eloChange={self.eloChange}, \
                mainPerk={self.mainPerk}, \
                subPerk={self.subPerk}, \
                kill={self.kill}, \
                death={self.death}, \
                assist={self.assist}, \
                cs={self.cs}, \
                killP={self.killP}, \
                item={self.item}, \
                ward={self.ward},\
                win={self.win} \
            )'
        )

