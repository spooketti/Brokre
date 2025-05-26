from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ui import View, Select, Button
from discord import app_commands
from discord.ext import commands #idk how important this one is
import os
import json

load_dotenv()
token = os.getenv("TOKEN")


intents = discord.Intents.all()
client = commands.Bot(command_prefix="no", intents=intents)
brogreID = discord.Object(id=915051802276294676)

@client.event
async def on_ready():
  try:
    synched = await client.tree.sync(guild=brogreID)
    print(f"Synched {len(synched)} commands")
  except:
    print("sucks")

class TableSetup(discord.ui.Modal, title="Table Setup"):
    tableName = discord.ui.TextInput(label="Table Name", placeholder="Brokre Poker Table Name")
    smallBlind = discord.ui.TextInput(
        label="Small Blind",
        style=discord.TextStyle.short,
        placeholder="Small Blind",
        required=True,
        max_length=5
    )
    bigBlind = discord.ui.TextInput(
        label="Big Blind",
        style=discord.TextStyle.short,
        placeholder="Big Blind",
        required=True,
        max_length=5
    )
    maxPlayers = discord.ui.TextInput(
        label="Max Players",
        style=discord.TextStyle.short,
        placeholder="Leave Blank For Uncapped Players",
        required=False,
        max_length=1
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if( (int)(self.maxPlayers) <= 0):
                raise Exception("invalid")
            self.maxPlayers = (int)(self.maxPlayers)
        except:
            self.maxPlayers = "Uncapped"
            
        embed = discord.Embed(
        title=f"{interaction.user.display_name} Has Created Table, {self.tableName}!",
        description= f"<:brokre:1376477769570975744>Small Blind: {self.smallBlind} \n <:brokre:1376477769570975744>Big Blind: {self.bigBlind}\n  Max Players: {self.maxPlayers}",
        color=discord.Color.brand_red() 
    )
        await interaction.response.send_message(
             embed=embed,view=TableControl(self.tableName)
        )

@client.tree.command(name="start", guild=brogreID)
async def start(interaction: discord.Interaction):
    await interaction.response.send_modal(TableSetup())

@client.tree.command(name="profile", guild=brogreID)
async def profile(interaction: discord.Interaction):
    playerData = {}
    with open("players.json", 'r',encoding="utf-8") as file:
        playerData = json.load(file)

    if not interaction.user.name in playerData:
        with open("players.json","w",encoding="utf-8") as file:
            await interaction.response.send_message("You don't have an account so one was created for you")
            playerData[interaction.user.name] = {"chips":1000,"wins":0,"losses":0}
            file.seek(0)
            file.truncate()
            json.dump(playerData,file,indent=4)
            return

    embed = discord.Embed(
        title="Your Profile",
        description=f"Name: {interaction.user.name} \n <:brokre:1376477769570975744>Chips: {playerData[interaction.user.name]['chips']}",
        color=discord.Color.blue() 
    )
    embed.set_footer(text="footer")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)  

    await interaction.response.send_message(embed=embed, view=EmbedControl("Join Table, joinTable"))

class EmbedControl(View):
    def __init__(self,primaryLabel,primaryID,parentData):
        super().__init__(timeout=None)  

        self.add_item(Button(label=primaryLabel, style=discord.ButtonStyle.primary, custom_id=primaryID))

class TableControl(View):
    def __init__(self, tableName):
        super().__init__(timeout=None)  
        self.tableName = tableName

        joinButton = Button(label="Join Table", style=discord.ButtonStyle.primary)
        joinButton.callback = self.wrap_callback(joinTable)
        self.add_item(joinButton)

    def wrap_callback(self, func):
        async def callback(interaction: discord.Interaction):
            await func(interaction, self.tableName)
        return callback

@client.event
async def on_interaction(interaction: discord.Interaction):
    switch = {
        "joinTable":joinTable
    }
    result = switch.get(interaction.data.get("custom_id"))
    if result:
        await result(interaction)
    else: 
        await interaction.response.send_message(interaction.data, ephemeral=False)

async def joinTable(interaction: discord.Interaction, tableName):
    await interaction.response.send_message(f"{interaction.user.name} has joined table {tableName}", ephemeral=False)
    

# @client.command()
# async def menu(ctx):
#     await ctx.send("menu:", view=DropdownView())

# class DropdownMenu(Select):
#     def __init__(self):
#         options = [
#             discord.SelectOption(label="Option 1", description="option a"),
#             discord.SelectOption(label="Option 2", description="option b"),
#             discord.SelectOption(label="Option 3", description="option c"),
#         ]
#         super().__init__(placeholder="wtf", min_values=1, max_values=1, options=options)

#     async def callback(self, interaction: discord.Interaction):
#         await interaction.response.send_message(f"You selected: **{self.values[0]}**", ephemeral=True)

# class DropdownView(View):
#     def __init__(self):
#         super().__init__()
#         self.add_item(DropdownMenu())

  
client.run(token)