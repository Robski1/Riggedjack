from imports import *
bot = commands.Bot(command_prefix = '-', case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('-help'))
    print('Bot is online ')
    
@bot.command()
async def help(ctx, *args):
    await accountExists(ctx)
    embed = discord.Embed(
        description = '`THIS IS A HELP PAGE`',
        colour = discord.Colour.purple()
        )
    embed.set_author(name=f"{ctx.author.name} ", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx, *args):
    await accountExists(ctx)
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','r') as f:
        stuff = json.load(f)
    daily = stuff['account']['daily']
    lastClaim = stuff['account']['lastDailyClaimTime']
    if daily:
        chips = random.randint(500,2000)
        embed = discord.Embed(
            description = f'YOU GAINED {chips} CHIPS',
            colour = discord.Colour.purple()
            )
        embed.set_author(name=f"{ctx.author.name} ", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        await addChips(ctx, chips, daily)
    else:
        await nextDailyClaim(ctx)

# CREATE ACCOUNT
async def makeSave(ctx):
    stuff = {}
    stuff['account'] = {}
    stuff['account'].update({
        'accountName' : f'{ctx.author.name}',
        'accountId' : f'{ctx.author.id}',
        'membership' : 'coming soon',
        'balance' : 100000,
        'totalGames' : 0,
        'wins' : 0,
        'losses' : 0,
        'winPercent' : 0,
        'blackJacks' : 0,
        'busts' : 0,
        'daily' : True,
        'lastDailyClaimTime' : '00:00:00'
    })
    stuff['settings'] = {}
    stuff['settings'].update({
        'deckCount' : 2
    })
    
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','w') as f:
        json.dump(stuff,f, indent=4)

# CHECK IF ACCOUNT EXISTS, IF NOT CREATE ONE
async def accountExists(ctx):
    if f'{ctx.author.id}.txt' not in os.listdir(constants.userSavePath):
        await makeSave(ctx)
    else:
        return True

# ADDS CHIPS TO ACCOUNT
async def addChips(ctx, chips, daily):
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','r') as f:
        stuff = json.load(f)
        stuff['account']['balance'] += chips
    if daily:
        now = datetime.now()
        now = now.strftime('%H:%M:%S')
        stuff['account']['daily'] = False
        stuff['account']['lastDailyClaimTime'] = now
        with open (f'{constants.userSavePath}{ctx.author.id}.txt','w') as f:
            json.dump(stuff,f, indent=4)
        await wait1day(ctx)
    else:
        with open (f'{constants.userSavePath}{ctx.author.id}.txt','w') as f:
            json.dump(stuff,f, indent=4)

#CALCULATES TIME UNTIL NEXT CLAIM
async def nextDailyClaim(ctx):
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','r') as f:
        stuff = json.load(f)
    await ctx.send(f"<@{ctx.author.id}> You can do -daily when it is {stuff['account']['lastDailyClaimTime']}")
    
# WAIT A DAY FOR DAILY TO RESET
async def wait1day(ctx):
    await asyncio.sleep(86,400)
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','r') as f:
        stuff = json.load(f)
        stuff['account']['daily'] = True
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','w') as f:
        json.dump(stuff,f, indent=4)




if __name__ == "__main__":
    with open(constants.tokenPath,"r") as token:
        token=token.read()
        bot.run(token)