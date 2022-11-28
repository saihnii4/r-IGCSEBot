async def refreshKeywords():
    global keywords
    channel = client.get_channel(929910420326727730)
    messages = await channel.history(limit=500).flatten()
    keywords = {message.content.splitlines()[0].lower() : "\n".join(message.content.splitlines()[1:]) for message in messages}

async def refreshReactionRoles():
    global reactionroleiiiiiis
    channel = client.get_channel(932454877915910144)
    messages = await channel.history(limit=500).flatten()
    reactionroles = {int(message.content.splitlines()[0]) : {i.split()[0]: int(i.split()[1]) for i in message.content.splitlines()[1:]} for message in messages}
    return reactionroles

async def removeUser(userid):
    req = requests.delete(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY})
    return True

async def getRepNew(userid):
    req = requests.get(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY})
    return int(req.json().get("value","0"))

async def addRepNew(userid):
    rep = await getRepNew(userid)
    req = requests.put(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY}, data=str(rep+1))
    return rep+1

async def changeRepNew(userid, rep):
    req = requests.put(f"https://api.kvstore.io/collections/rep_leaderboard/items/{userid}", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY}, data=str(rep))
    return True

async def getLeaderboardNew(offset=0):
    req = requests.get(f"https://api.kvstore.io/collections/rep_leaderboard/items?offset={offset}&limit=100", headers={"Content-Type" : "text/plain", "kvstoreio_api_key" : API_KEY})
    leaderboard = {}
    for item in req.json():
        leaderboard[int(item['key'])] = int(item['value'])
    if len(leaderboard) == 100:
        leaderboard = {**leaderboard, **(await getLeaderboardNew(offset+100))}
    return {k: v for k, v in sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)} # Descending sort by rep

async def lowLikelihood(message):
    role = discord.utils.get(message.guild.roles, name="Discord Mod")
    await message.reply(f"My automatic evaluation has returned that the likelihood of the message being spam is low. Please wait for {role.mention} to review the message.")

async def spamMessage(message, reporter):
    user = message.author
    bot = message.guild.get_member(861445044790886467)
    mod_role = discord.utils.get(message.guild.roles, id=578170681670369290)
    await message.reply(f"{message.author.mention} has been muted for sending scam messages. (Reported by {reporter.mention})\nIf this action was done in error, {mod_role.mention} will review the mute and revoke it if necessary")
    ban_msg_channel = client.get_channel(690267603570393219)
    last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
    role = discord.utils.get(message.guild.roles, id=787670627967959087)
    await user.add_roles(role)
    case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1 # Increment previous case number
    ban_msg = f"""Case #{case_no} | [Mute]
Username: {user.name}#{user.discriminator} ({user.id})
Reporter: {reporter.mention}
Reason: Spamming messages in channels"""
    await ban_msg_channel.send(ban_msg)
    log_channel = client.get_channel(792775200394575882)
    await log_channel.send(content=f"Reporter: {reporter.mention}\n\nTranscript of message sent by {user.mention}:\n\n{message.content}")

    for channel in message.guild.text_channels: # Delete any other instances of the spam message sent
        fetchMessage = await channel.history(limit=10).flatten()
        if fetchMessage:
            for m in fetchMessage:
                if m.content == message.content:
                    try:
                        await m.delete()
                    except:
                        pass