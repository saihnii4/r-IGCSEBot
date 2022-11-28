from nextcord.ext import commands
import nextcord as discord

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.listeners = {
            998759935196270614: self.voting_system
        }

    @commands.Cog.listener()
    async def on_socket_raw_recieve(self, *args, **kwargs):
        print(*args, **kwargs)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction, user):
        print(reaction, user)
        if user.bot: return
        hooks = self.listeners.get(reaction.message_id)
        for hook in hooks:
            await hook(reaction, user, **dict(reaction))

    async def voting_system(self, reaction, user):
        print(type(user))

