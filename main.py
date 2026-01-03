import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import time
from dotenv import load_dotenv
load_dotenv()

def load_data():
    if not os.path.exists("economy.json"):
        with open("economy.json", "w") as f:
            json.dump({}, f)

    with open("economy.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        try:
            guild = discord.Object(id=1455675638852751486)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e:
            print(f'Error syncing commands {e}')


        guild = discord.Object(id=1455675638852751486)
        await self.tree.sync(guild=guild)
        print("Commands synced")

    # Events
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith('Hello'):
            await message.channel.send(f'Hi there {message.author}')

        if message.content.startswith('G'):
            await message.channel.send(f'Good Gamers {message.author}')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1455675638852751486)

# /cmds
@client.tree.command(name="about", description="Get the bot information.", guild=GUILD_ID)
async def say(interaction: discord.Interaction):
    embed = discord.Embed(title="About Ninjeff", description="Ninjeff is a Discord bot that belongs to the Jeff community. It was completely coded by pingedgrimz.", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

# /tournament
# -------------------------
# TOURNAMENT ENTRY (10K FEE)
# -------------------------

class TournamentEntry(discord.ui.View):
    MAX_ENTERIES = 16

    def __init__(self):
        super().__init__(timeout=None)
        self.entries: list[int] = []  # instance list

    @discord.ui.button(label="Enter Tournament", style=discord.ButtonStyle.green)
    async def enter_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        data = load_data()
        user_id = str(interaction.user.id)

        # Ensure user exists in economy file
        if user_id not in data:
            data[user_id] = {"wallet": 0, "daily": 0}
            save_data(data)

        # Already entered?
        if interaction.user.id in self.entries:
            return await interaction.response.send_message(
                "You already entered in the tournament.",
                ephemeral=True
            )

        # Tournament full?
        if len(self.entries) >= self.MAX_ENTERIES:
            return await interaction.response.send_message(
                "The roster for the tournament is complete.",
                ephemeral=True
            )

        # Check money
        if data[user_id]["wallet"] < 10000:
            return await interaction.response.send_message(
                "You need **$10,000** to enter this tournament.",
                ephemeral=True
            )

        # Deduct entry fee
        data[user_id]["wallet"] -= 10000
        save_data(data)

        # Add user to tournament
        self.entries.append(interaction.user.id)

        # Public announcement
        await interaction.channel.send(
            f"{interaction.user.mention} has paid **$10,000** and entered the tournament!"
        )

        # Disable button if full
        if len(self.entries) >= self.MAX_ENTERIES:
            button.disabled = True
            await interaction.message.edit(view=self)

        # Private confirmation
        await interaction.response.send_message("You have been entered!", ephemeral=True)


# -------------------------
# CONFIRM HOST BUTTON
# -------------------------

class TournamentButton(discord.ui.View):
    REQUIRED_ROLE_ID = 1455677149330538627  # change to your staff role ID

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm Host", style=discord.ButtonStyle.blurple)
    async def announce_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        # Permission check
        if self.REQUIRED_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )

        role_mention = "<@&1456583616934051922>"  # change to your ping role

        # Banner embed
        embed1 = discord.Embed(color=discord.Color.blue())
        embed1.set_image(url="https://cdn.discordapp.com/attachments/1455998327714742486/1455998635836969053/Jeff_community_tournaments_banner..png?ex=695966e5&is=69581565&hm=c3adc97d64ba51eaa02beae2d957724a39df5513c6af9391181906216c4a382a&")  # put your real banner URL here

        # Announcement embed
        embed2 = discord.Embed(
            title="Tournament Announcement",
            description="A new tournament has been declared!",
            color=discord.Color.blue()
        )
        embed2.set_image(url="https://cdn.discordapp.com/attachments/1455998327714742486/1456548768160813178/Jeff_community_logo..png?ex=69596cff&is=69581b7f&hm=111cf4d97b1c8e0d0d6a5b659201d2557b214392767cf1557176262fca7db4fd&")
        embed2.add_field(name="Max players:", value="```16 players```", inline=True)
        embed2.add_field(name="Winning prize:", value="```1,000 V-Bucks```", inline=True)

        # 1. Private confirmation (ephemeral)
        await interaction.response.send_message(
            "Tournament has been hosted!",
            ephemeral=True
        )

        # 2. Public message in channel (NOT a reply, mention OUTSIDE embed)
        await interaction.channel.send(
            content=role_mention,
            embeds=[embed1, embed2],
            view=TournamentEntry()
        )


# -------------------------
# /host COMMAND
# -------------------------

@client.tree.command(name="host", description="Launch a tournament.", guild=GUILD_ID)
async def host(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Click the button below to launch the tournament:",
        view=TournamentButton(),
        ephemeral=True
    )

# /status
@client.tree.command(name="status", description="Get the current status of the bot.", guild=GUILD_ID)
async def say(interaction: discord.Interaction):
    embed=discord.Embed(title="Bot Status")
    embed.add_field(name="🧠 Memory Usage", value="81.80 MB", inline=True)
    embed.add_field(name="⚙️ CPU Usage", value="51.6%", inline=True)
    embed.add_field(name="⏱️ Uptime", value="00:14:03", inline=True)
    embed.add_field(name="🐍 Python Version", value="3.12.7", inline=True)
    embed.add_field(name="📦 discord.py Version", value="2.6.4", inline=True)
    embed.add_field(name="🖥️ OS", value="Windows", inline=True)
    await interaction.response.send_message(embed=embed)

# /links
@client.tree.command(name="links", description="Get useful links for Jeff community.", guild=GUILD_ID)
async def say(interaction: discord.Interaction):
    embed = discord.Embed(title="Useful Links", color=discord.Color.blue())
    embed.set_image(url="https://cdn.discordapp.com/attachments/1455998327714742486/1456548768160813178/Jeff_community_logo..png?ex=6958c43f&is=695772bf&hm=ffe11329fdbc62594316900dffa9027aa44f845d1c54ae90ed6c3b391f790c28&")
    embed.add_field(name="Merch", value="[OFJ Merch](https://ofj.creator-spring.com/?_ga=2.121664520.2032860827.1766889703-571559999.1766889495&_gl=1*1qae5x1*_gcl_au*MTk2MjkyMjIzLjE3NjY4ODk3MDMuNTA1MjkzOTczLjE3NjY5MDQzOTguMTc2NjkwNTY5MQ..*_ga*NTcxNTU5OTk5LjE3NjY4ODk0OTU.*_ga_G3GKJFR6Z9*czE3NjY5MDQyNjQkbzIkZzEkdDE3NjY5MDY3ODkkajQ2JGwwJGgyODg0MTM0MTc)", inline=False)
    embed.add_field(name="Discord", value="[Discord Invite](https://discord.gg/9Vf3z9vFCm)")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# /balance
@client.tree.command(name="balance", description="Check your balance.", guild=GUILD_ID)
async def balance(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)
    balance = data.get(user_id, {}).get("wallet", 0)
    await interaction.response.send_message(f"{interaction.user.mention}, you have **${balance}**.")

# /work
@client.tree.command(name="work", description="Work to earn money.", guild=GUILD_ID)
async def work(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)

    earnings = random.randint(50, 200)

    if user_id not in data:
        data[user_id] = {"wallet": 0, "daily": 0}
    data[user_id]["wallet"] += earnings
    save_data(data)
    await interaction.response.send_message(
        f"{interaction.user.mention} worked and earned **${earnings}**!")

# daily
@client.tree.command(name="daily", description="Claim your daily reward.", guild=GUILD_ID)
async def daily(interaction: discord.Interaction):
    data = load_data()
    user_id = str(interaction.user.id)

    if user_id not in data:
        data[user_id] = {"wallet": 0, "daily": 0}

    last_claim = data[user_id]["daily"]
    now = time.time()

    if now - last_claim < 86400:
        remaining = int(86400 - (now - last_claim))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        return await interaction.response.send_message(
            f"You already claimed your daily reward. Come back in **{hours}h {minutes}m**."
        )

    reward = random.randint(200, 500)
    data[user_id]["wallet"] += reward
    data[user_id]["daily"] = now
    save_data(data)
    await interaction.response.send_message(
        f"{interaction.user.mention} claimed **${reward}** their daily reward!")

client.run(os.getenv("TOKEN"))