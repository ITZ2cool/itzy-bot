import discord
from discord.ext import commands
import random, json, os
from datetime import datetime

import os
TOKEN= os.getenv("MTUxMjQ5MjMxMDkxNzgxMjIyNA.GT0V_o.m6mBXJ0eirZJBnmYGklZufDJpjDW-pTBlMAEoU")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

cards = [
    {"id":"YEJI-001","name":"Yeji","rarity":"Common","image":"https://i.pinimg.com/736x/21/cf/37/21cf374eb4548717e7cce87f1b790b4e.jpg"},
    {"id":"LIA-001","name":"Lia","rarity":"Common","image":"https://i.pinimg.com/736x/39/b7/8e/39b78e3a90c37bf151582ff7e060e9f2.jpg"},
    {"id":"RYUJIN-001","name":"Ryujin","rarity":"Rare","image":"https://i.pinimg.com/736x/f9/de/ac/f9deac7af75ba4a6a3c9f36bfcc862e7.jpg"},
    {"id":"CHAER-001","name":"Chaeryeong","rarity":"Epic","image": "https://i.pinimg.com/736x/9c/7a/2c/9c7a2c09d7f119b4ea3af6d6ed700518.jpg"},
    {"id":"YUNA-001","name":"Yuna","rarity":"Legendary","image": "https://i.pinimg.com/736x/43/2f/8f/432f8f66fe75d437ffebb711396e7283.jpg"},
]

def load_json(name):
    if not os.path.exists(name):
        return {}
    with open(name,"r") as f:
        return json.load(f)

def save_json(name,data):
    with open(name,"w") as f:
        json.dump(data,f,indent=4)

def rarity_pull():
    roll=random.randint(1,100)
    if roll<=70:
        pool=[c for c in cards if c["rarity"]=="Common"]
    elif roll<=90:
        pool=[c for c in cards if c["rarity"]=="Rare"]
    elif roll<=99:
        pool=[c for c in cards if c["rarity"]=="Epic"]
    else:
        pool=[c for c in cards if c["rarity"]=="Legendary"]
    return random.choice(pool)
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print("ITZY Bot Online")
    
rarity_colors = {
    "Common": "⚪",
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡"
}
@bot.command()
async def hello(ctx):
    await ctx.send("ITZY Bot is working 💖")

@bot.command()
async def daily(ctx):
    db=load_json("economy.json")
    u=str(ctx.author.id)
    if u not in db:
        db[u]={"coins":0,"last_daily":""}
    today=datetime.utcnow().strftime("%Y-%m-%d")
    if db[u]["last_daily"]==today:
        await ctx.send("Already claimed today.")
        return
    db[u]["coins"]+=100
    db[u]["last_daily"]=today
    save_json("economy.json",db)
    await ctx.send("You got 100 coins!")

@bot.command()
async def balance(ctx):
    db=load_json("economy.json")
    u=str(ctx.author.id)
    if u not in db:
        db[u]={"coins":0,"last_daily":""}
        save_json("economy.json",db)
    await ctx.send(f"Balance: {db[u]['coins']} coins")

@bot.command()
async def drop(ctx):
    inv = load_json("inventory.json")
    u = str(ctx.author.id)

    inv.setdefault(u, [])

    card = rarity_pull()
    inv[u].append(card)
    save_json("inventory.json", inv)

    emoji = rarity_colors.get(card["rarity"], "⚪")

    embed = discord.Embed(
        title=f"{emoji} {card['name']}",
        description=f"ID: {card['id']}\nRarity: {card['rarity']}"
    )

    if card["image"].startswith("http"):
        embed.set_image(url=card["image"])

    await ctx.send(embed=embed)
    
@bot.command()
async def test(ctx):
    await ctx.send("test works")

@bot.command()
async def inventory(ctx):
    inv = load_json("inventory.json")
    u = str(ctx.author.id)

    cards = inv.get(u, [])

    if not isinstance(cards, list) or len(cards) == 0:
        await ctx.send("No cards yet.")
        return

    embed = discord.Embed(
        title="🎴 Your ITZY Collection",
        color=discord.Color.purple()
    )

    for c in cards:
        if not isinstance(c, dict):
            continue

        name = c.get("name", "Unknown")
        rarity = c.get("rarity", "?")

        embed.add_field(
            name=name,
            value=f"Rarity: {rarity}",
            inline=False
        )

    await ctx.send(embed=embed)
@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def collection(ctx):
    inv=load_json("inventory.json")
    u=str(ctx.author.id)
    owned=len(set(c["id"] for c in inv.get(u,[])))
    await ctx.send(f"🏆 {owned}/{len(cards)} unique cards collected")

bot.run(TOKEN)
