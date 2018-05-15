import json
import SteamAPI
import random
from environment import Env

API_KEY = Env.STEAM_API_KEY
steamAPI = SteamAPI.GetInfo(API_KEY)


class Player:
    """
    Attributes
    -----------
    personaname : str
        The user's username.
    steamid : str
        The user's steam ID.
    ownedgames : list ->  GameList?
        The user's owned games
        [{Game:object, appid:100, name:kamige}, {}, {}, {} ]
    friends : list
        [{"steamid": str ,"relationship": str ,"friend_since": int },{},{},,,]

    """

    def __init__(self, *, steamid=None):
        self.steamid = steamid
        self.ownedgames = None
        self.friends = None
        self.friendsdict = None
        self.personaname = None

    # [{Game:object, appid:100, name:kamige}, {}, {}, {} ]
    def update_ownedgames(self):
        games = steamAPI.getOwnedGames(self.steamid)
        self.ownedgames = [{**agame, **{"obj": build_game(appid=agame["appid"])}} for agame in games]
        return self.ownedgames
        # todo fix Player.owned game -> GameList or new attribute like ".easy_game_list" or new class PGameList

    def get_details(self):
        summary = steamAPI.getPlayerSummaries(self.steamid)
        for k, v in summary[0].items():
            setattr(self, k, v)
        return True


    def get_friends(self):
        ffs = steamAPI.getFriendlist(self.steamid)
        friends_ids = [friend["steamid"] for friend in ffs]
        friends = steamAPI.getPlayerSummaries(*friends_ids)
        self.friendsdict = {player["personaname"]: player["steamid"] for player in friends}
        # todo もっと整理を　こんなにattributeいる？？dictじゃなくてobjectでもよくね？FriendListクラスつくる？

    def arefriends(self, *steamids):
        upperdict = {key.upper(): self.friendsdict[key] for key in
                     self.friendsdict.keys()}  # return [ALLFRIENDNAME1, ALLFRIENDNAME2,...]
        friends_idlist = []
        for name in steamids:
            if name.upper() in upperdict.keys():
                v = upperdict[name.upper()]
                friends_idlist.append(v)
        return friends_idlist
    # todo 大文字小文字の区別をなくすためだけにここまでいるか不明　re やstr.casefoldを検討

class MainPlayer(Player):
    def __init__(self, steamid):
        super().__init__(steamid=steamid)
        self.get_details()


class Game:
    def __init__(self, *, appid, name=None):
        self.appid = appid
        self.name = name
        self._isdetailed = False

    def get_details(self):
        dic = steamAPI.getAppDetail(self.appid)
        for k, v in dic.items():
            setattr(self, k, v)
        self._isdetailed = True


class GameList:
    """
    a class that contains multiple Game object.
    mostly same as list.
    """


    def __init__(self, games: list):
        self.contents = games
        self._isdetailed = False

    def setlist(self, klist: list):
        self.contents = klist

    def choice(self):
        if self.contents:
            ranid = random.choice(self.contents)
            jsond = steamAPI.getAppDetail(ranid)
            choosen_game = build_game(json=jsond)
            return choosen_game

    def shuffle(self):
        self.contents = random.sample(self.contents, len(self.contents))

    def build_categories(self, categorynumb) -> "new GameList":
        newlist = []
        for game in self.contents:
            categories = getattr(game, "categories", None)
            if categories:
                for category in categories:
                    if categorynumb in category.keys():
                        newlist.append(game)
            else:
                continue
        return newlist

class PlayerGameList(GameList):
    pass


# mapping functions --------------------------------------------------------------------------------------------------
def build_player(steamid) -> Player:
    pl = Player(steamid=steamid)
    return pl
    # todo 簡素すぎて必要ない


def build_playerslist(*steamids) -> list:
    plist = [Player(steamid=ids) for ids in steamids]
    return plist
    # todo 簡素すぎて必要ない


def build_game(*, appid=None, json=None) -> Game:
    g = None
    if json or appid is not None:
        if json is not None:
            g = Game(appid=json["steam_appid"])
            for k, v in json.items():
                setattr(g, k, v)
        elif appid is not None:
            g = Game(appid=appid)
    else:
        print("no game error")
        return g
    # todo 整理とraise error


# utility functions --------------------------------------------------------------------------------------------------
def searchfriends(*checks: str, center) -> list:
    friendids = center.arefriends(*checks)
    playerlist = build_playerslist(*friendids) + [center]
    return playerlist


def search_kyoutuugames(*players) -> GameList:
    setlist = [{agame["appid"] for agame in player.ownedgame} for player in players]
    kyoutuu = setlist[0].intersection(*setlist[1:])
    kyotu_game = GameList(list(kyoutuu))
    return kyotu_game


def main(center: MainPlayer = None, *checklist: str) -> GameList:
    center.get_friends()
    players = searchfriends(*checklist, center=center)
    for player in players:
        player.update_ownedgames()
    kyoutuu_game = search_kyoutuugames(*players)
    return kyoutuu_game


if __name__ == '__main__':
    MY_ID = Env.MY_STEAM_ID
    samplenames = ["sample1", "sample2"]
    center = MainPlayer(MY_ID)
    f = main(center, *samplenames)
    r = f.choice()
    print(vars(r))
