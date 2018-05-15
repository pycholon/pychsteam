import asyncio
import discord
import top
from environment import Env

client = discord.Client()
token = Env.DISCORD_TOKEN_1
asyncio.set_event_loop(asyncio.new_event_loop())


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    # そのserver上で自身を指定するiam; memberクラスを取得
    iam = discord.utils.get(message.server.members, name=client.user.name)
    global mainplayer
    global myid

    if message.content.startswith("おはよう"):
        if client.user != message.author:
            m = "おはようございます" + message.author.name + "さん！"
            await client.send_message(message.channel, m)

    elif message.content.startswith("myid"):
        if client.user != message.author:
            s = message.content.split("myid")
            myid = s[1]
            mainplayer = top.MainPlayer(steamid=myid)
            m = "あなたのsteamIDを" + myid + "に設定しました \n 名前は" + mainplayer.personaname + "となります"
            await client.send_message(message.channel, m)

    elif message.content.startswith("S"):
        if client.user != message.author:
            if mainplayer is not None:
                v = message.content[2:]
                await client.send_message(message.channel, "さがしてます")
                b = v.split(",")
                gamelist = top.main(mainplayer, *b)
                game = gamelist.choice()
                m = game.name + "はいかがでしょうか"
                await client.send_message(message.channel, m)
                pass
            else:
                await client.send_message(message.channel, "myidでsteamidを設定してください")

    elif message.content == "kill":
        client.close()
        client.logout()
        print("killed.")


def choice_ourgame(obj: top.GameList, categoryid=1) -> top.Game:
    agame = obj.choice()
    agame.get_details()
    categories = getattr(agame, "categories")
    calist = [each for each in categories if each.get("id") == categoryid]
    return calist
    # todo sagoyutyuu
    # todo filter関数について調べる

myid = None
mainplayer = None
# mainplayer = top.MainPlayer(steamid=Env.MY_STEAM_ID)

client.run(token)
