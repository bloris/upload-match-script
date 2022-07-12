class User(object):
    def __init__(self, name, profileIconId, elo, win, lose):
        self.name = name
        self.profileIconId = profileIconId
        self.elo = elo
        self.tier = self.getTier(elo)
        self.win = win
        self.lose = lose

    @staticmethod
    def from_dict(source):
        # [START_EXCLUDE]
        user = User(source[u'name'], source[u'profileIconId'], source[u'elo'], source[u'win'], source[u'lose'])

        return user

    def to_dict(self):
        # [START_EXCLUDE]
        user = {
            u'name': self.name,
            u'profileIconId': self.profileIconId,
            u'elo': self.elo,
            u'tier': self.tier,
            u'win': self.win,
            u'lose': self.lose,
        }

        return user

    def __repr__(self):
        return(
            f'User(\
                name={self.name}, \
                profileIconId={self.profileIconId}, \
                elo={self.elo}, \
                tier={self.tier}, \
                win={self.win}, \
                lose={self.lose}\
            )'
        )
    

    def getTier(self,elo):
        if elo >= 2100:
            return 'Grandmaster'
        elif elo >= 1900:
            return 'Master'
        elif elo >= 1700:
            return 'Diamond'
        elif elo >= 1500:
            return 'Platinum'
        elif elo >= 1300:
            return 'Gold'
        elif elo >= 1100:
            return 'Silver'
        elif elo >= 900:
            return 'Bronze'
        else:
            return 'Iron'
        return 'Iron'