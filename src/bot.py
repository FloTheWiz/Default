import time
from datetime import datetime 

import discord
from discord.ext import commands

from colorama import init, Fore, Style

init(autoreset=True)

# Default mentions
allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True) 

# Intents, for more info: https://discordpy.readthedocs.io/en/latest/intents.html
intents = discord.Intents(
    voice_states=True,
    messages=True,
    reactions=True,
    message_content=True,
    guilds=True,
    members=True
)

class Bot(commands.Bot):
    def __init__(self, config: dict) -> None:
        self._prefix = config.get('prefix', '!!')
        super().__init__(
            command_prefix=commands.when_mentioned_or(self._prefix), # Defaults to '!!'
            description=config.get('description', "Somebody didn't change their description!"),
            intents = intents,
            allowed_mentions = allowed_mentions
        )

        self.config = config
        self.boot_start = time.time()
        
        self._cogs = config.get('cogs', [])
        self._uptime = datetime.now()

        self._version = config.get('version', '1.0.0') # version_str
        
        self._activity = config.get('activity', 'Somebody didn\'t change their activity!')
        
        self.log_colors = {
                "INFO": Fore.CYAN,
                "ERROR": Fore.RED,
                "WARNING": Fore.YELLOW,
                "SUCCESS": Fore.GREEN,  
            }
    @property
    def owner(self) -> discord.User:
        """(usually) Me :3"""
        return self.bot_app_info.owner

    def log(self, message: str, level: str = "INFO"):
        """Gross but handy Utility function

        Args:
            message (str): A string, can be formatted
            level (str, optional): Level of panic.More levels can be defined above. Defaults to "INFO".
        """
        level = level.upper() # Just in case.
        color = self.log_colors.get(level, Fore.CYAN)
        print(f"{Fore.BLUE} {self.user}{Style.RESET_ALL} | {color}[{level:7}]{Style.RESET_ALL}{Fore.WHITE} {message}{Style.RESET_ALL}")

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            self.log(f"Command not found: {ctx.message.content}", "WARNING")
            return

        self.log(f"Error in command {ctx.command}: {error}", "ERROR")
        await ctx.send(f"An error occurred: {error}")

    async def on_ready(self) -> None:
        """The reason I want to put this on github is so I can avoid ever writing this again.
        If anybody knows a better, crossplatform method than just formatting ANSI, let me know."""
        
        self.log(f"Username: {self.log_colors["INFO"]}{self.user}{Style.RESET_ALL} | discord.py version: {self.log_colors["INFO"]}{discord.__version__}{Style.RESET_ALL}", "INFO")
        self.log(f"Guilds: {self.log_colors["INFO"]}{len(self.guilds)}{Style.RESET_ALL} | Users: {self.log_colors["INFO"]}{len(self.users)}{Style.RESET_ALL} | Prefix: {self.log_colors["INFO"]}{self._prefix}{Style.RESET_ALL}", "INFO")
        self.log(f"Invite Link: {self.log_colors["INFO"]}https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=52288&scope=bot%20applications.commands{Style.RESET_ALL}", "INFO")
        self.log(f"Ready: {self.log_colors["SUCCESS"]}{self.user}{Style.RESET_ALL} (ID: {self.log_colors["SUCCESS"]}{self.user.id}{Style.RESET_ALL})", "SUCCESS")
    
    async def startup(self) -> None:
        """
        Cog syncing and boot time
        """
        await self.wait_until_ready()
        await self.tree.sync()
        self.log("Ready and Tree Synced", "SUCCESS")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=self._activity))
        # Calculate boot time 
        done = round(time.time() - self.boot_start, 2)
        
        # Assign Different levels to different colors
        if done < 30: # Under 30 Seconds is good, especially for a bigger bot
            self.log(f"Booted in: {self.log_colors["SUCCESS"]}{done} {Style.RESET_ALL}seconds", "SUCCESS")
        elif done < 60: # Under 1 Minute
            self.log(f"Booted in: {self.log_colors["WARNING"]}{done} {Style.RESET_ALL}seconds", "WARNING")
        else: # Over 1 Minute
            self.log(f"Booted in: {self.log_colors["ERROR"]}{done} {Style.RESET_ALL} seconds", "ERROR")
        
    async def setup_hook(self) -> None:
        """Initialize cogs. May Offset to a class for CogHandler """
        for cog in self._cogs:
            try:
                self.log(f'Loading: {self.log_colors["INFO"]}{cog}{Style.RESET_ALL}', "INFO")
                await self.load_extension(cog)
            except Exception as e:
                self.log(f"Failed to load cog {self.log_colors["ERROR"]}{cog}: {e}{Style.RESET_ALL}", "ERROR")
            finally:
                self.log(f"Loaded: {self.log_colors["SUCCESS"]}{cog}{Style.RESET_ALL}", "SUCCESS")
        self.loop.create_task(self.startup())
        