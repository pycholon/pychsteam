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
    owned_games : list [{"obj":Game, "appid": int, "name": str, "playtime_forever": int}]
        The user's owned games
    friends_list_rough : list [{"steamid": str, "relationship": str, "friend_since": int}]
        Easy-list of friends, for ids.
    friends_detailed : list[Player]
        list that contains Player object.
    """

    def __init__(self, *, steamid=None):
        self.steamid = steamid
        self.owned_games = None
        self.friends_list_rough = None
        self.friends_detailed = None
        self.personaname = None
        self._isdetailed = False
        # todo もっと整理を　こんなにattributeいる？？dictじゃなくてobjectでもよくね？FriendListクラスつくる？
        # todo ownedgameをnamedtupleにしてもいいかも

    # [{Game:object, appid:100, name:kamige}, {}, {}, {} ]
    def update_owned_games(self):
        games = steamAPI.getOwnedGames(self.steamid)
        self.owned_games = [{**agame, **{"obj": build_game(appid=agame["appid"])}} for agame in games]
        return self.owned_games
        # todo fix Player.owned game -> GameList or new attribute like ".easy_game_list" or new class PGameList

    def get_details(self):
        summary = steamAPI.getPlayerSummaries(self.steamid)
        for k, v in summary[0].items():
            setattr(self, k, v)
        self._isdetailed = True

    def get_friends(self):
        self.friends_list_rough = steamAPI.getFriendlist(self.steamid)

    def get_friends_detailed(self):
        if self.friends_list_rough is None:
            self.get_friends()
        raw = steamAPI.getPlayerSummaries(*self.friends_list_rough["steamid"])
        # self.friend_detailed = ...
    # todo sagyoutyuu

    def are_friends(self, *names: str) -> "list of Player":
        d = [obj for obj in self.friends_detailed if getattr(obj, "personaname") in names]
        return d


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
            choosen_game = build_game(data=jsond)
            return choosen_game

    def shuffle(self):
        self.contents = random.sample(self.contents, len(self.contents))

    def build_new_with_categories(self, *, category_number=None):
        newlist = []
        for game in self.contents:
            categories = getattr(game, "categories", None)  # -> [{},{},{}]
            if categories:
                for each in categories:
                    if category_number in each["id"]:
                        newlist.append(game)
            else:
                continue
        newgamelist = GameList(newlist)
        return newgamelist
    # todo fix


class PlayerGameList(GameList):
    pass


# mapping functions --------------------------------------------------------------------------------------------------
def build_player(steamid) -> Player:
    pl = Player(steamid=steamid)
    return pl
    # todo 簡素すぎて必要ない?


def build_playerslist(*steamids) -> list:
    plist = [Player(steamid=ids) for ids in steamids]
    return plist
    # todo 簡素すぎて必要ない?


def build_game(*, appid=None, data=None) -> Game:
    g = None
    if data or appid is not None:
        if data is not None:
            g = Game(appid=data["steam_appid"])
            for k, v in data.items():
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
        player.update_owned_games()
    kyoutuu_game = search_kyoutuugames(*players)
    return kyoutuu_game


if __name__ == '__main__':
    MY_ID = Env.MY_STEAM_ID
    samplenames = ["sample1", "sample2"]
    center = MainPlayer(MY_ID)
    f = main(center, *samplenames)
    r = f.choice()
    print(vars(r))


"""
   def get_friends(self):
        self.friendlist = steamAPI.getFriendlist(self.steamid)
        #friends_ids = [friend["steamid"] for friend in self.friendlist]
        #friends_details = steamAPI.getPlayerSummaries(*friends_ids)
        #self.friendsdict = {player["personaname"]: player["steamid"] for player in friends_details}
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
"""