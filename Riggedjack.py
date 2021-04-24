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

@bot.command()
async def play(ctx, *args):
    await accountExists(ctx)
    deck = await deckCreation(constants.deck)
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','r') as f:
        stuff = json.load(f)

    menu = discord.Embed(
        description = f"""WELCOME <@{ctx.author.id}> TO THE TABLE
            2:3 PAYOUT ON BLACKJACK
            DEALER STANDS ON 17
        
        """,
        colour = discord.Colour.purple()
        )
    menu.set_author(name=f"{ctx.author.name} ", icon_url=ctx.author.avatar_url)
    ui = await ctx.send(embed=menu)
    await asyncio.sleep(3)
    
    dealerHand = []
    playerHand = []
    dealerValue = 0
    playerValue = 0
    deck,dealerHand,dealerValue = await dealerDraw(deck,dealerHand,dealerValue)
    for i in range(2):
        deck,playerHand,playerValue = await playerDraw(deck,playerHand,playerValue)

    table = discord.Embed(
        description = f"""<@{ctx.author.id}>
        
        Dealer Hand: {dealerHand} Dealer Value: {dealerValue}                                               
        Player Hand: {playerHand} Player Value: {playerValue}
        
        """,
        colour = discord.Colour.purple()
        )
    table.set_author(name=f"{ctx.author.name} ", icon_url=ctx.author.avatar_url)    
    await ui.edit(embed=table)
    await ui.add_reaction(constants.hit)
    await ui.add_reaction(constants.stand)
    await ui.add_reaction(constants.double)
    await playerTurn(ctx)

# PLAYER TURN TO HIT/STAND/DOUBLE
async def playerTurn(ctx):

    try:
        reaction, user = await bot.wait_for('reaction_add', check=lambda react,user: user==ctx.author and str(react.emoji) == f'<{constants.hit}>', timeout = 30.0)
    except asyncio.TimeoutError:
        print('timeout')
    else:
        print("nice")

# DEALER DRAW CARDS
async def dealerDraw(deck,dealerHand,dealerValue):
    dealerValue += constants.deckValues[deck[0]]
    dealerHand.append(deck[0])
    deck.pop(0)
    return deck,dealerHand,dealerValue

# PLAYER DRAW CARDS
async def playerDraw(deck,playerHand,playerValue):
    playerValue += constants.deckValues[deck[0]]
    playerHand.append(deck[0])
    deck.pop(0)
    return deck,playerHand,playerValue

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

# SHUFFLE CARDS INTO A DECK FOR USE
async def deckCreation(deck):
    bigDeck = deck*4 
    deck = []
    for i in range(len(bigDeck)):
        card = random.randint(0,len(bigDeck)-1)
        deck.append(bigDeck[card])
        bigDeck.pop(card)
    return deck

# NOT IN USE CURRENTLY
async def invalidArguments(ctx):
    await ctx.send(f'<@{ctx.author.id}> Invalid arguments do -help for a list of commands')





if __name__ == "__main__":
    with open(constants.tokenPath,"r") as token:
        token=token.read()
        bot.run(token)