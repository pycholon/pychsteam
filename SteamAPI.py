import json
import urllib
import urllib.parse
import urllib.request
import urllib.error


# todo http通信がかかるので、try/exceptを使いたい
class GetInfo:
    """
    connect steam api with urllib using api key.
    """
    ON = 1

    def __init__(self, key):
        self.API_KEY = key

    def getOwnedGames(self, steamid) -> list:
        query_dict = {
            "key": self.API_KEY,
            "steamid": steamid,
            "format": "json",
            "include_appinfo": self.ON
        }
        query_string = urllib.parse.urlencode(query_dict)
        base = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?"
        readobj = urllib.request.urlopen(base + query_string)
        response = json.load(readobj)
        games = response["response"]["games"]
        return games

    def getFriendlist(self, steamid) -> list:
        query_dict = {
            "key": self.API_KEY,
            "steamid": steamid,
            "format": "json",
            "relationship": "friend"
        }
        query_string = urllib.parse.urlencode(query_dict)
        base = "http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?"
        readobj = urllib.request.urlopen(base + query_string)
        response = json.load(readobj)
        friends = response["friendslist"]["friends"]
        return friends

    def getPlayerSummaries(self, *steamids) -> list:
        """
        listを渡す時は、getPlayerSummaries(*list)とする
        return list
        """
        query_dict = {
            "key": self.API_KEY,
            "steamids": steamids,
            "format": "json",
        }
        query_string = urllib.parse.urlencode(query_dict)
        base = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?"
        readobj = urllib.request.urlopen(base + query_string)
        response = json.load(readobj)
        summaries = response["response"]["players"]
        return summaries

    def getAppDetail(self, appid):
        """
        return appdetail
        本来は複数問い合わせできるべきAPIだが、バグで複数id動かないので一つづつforで回すしかない
        """
        # todo *appid化?
        query_dict = {
            "appids": appid
        }
        query_string = urllib.parse.urlencode(query_dict)
        base = "http://store.steampowered.com/api/appdetails/?"
        readobj = urllib.request.urlopen(base + query_string)
        response = json.load(readobj)
        if response[str(appid)]["success"]:
            appdetail = response[str(appid)]["data"]
            return appdetail
        else:
            print("error, can't get appid%s's detail" % appid)
