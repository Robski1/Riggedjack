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
async def profile(ctx, *args):
    await accountExists(ctx)
    user = ctx.author
    if len(args) > 0:
        try:
            user = await bot.fetch_user(args[0].strip("<@!>"))
            if user not in os.listdir(constants.userSavePath):
                await makeSave(user)
        except:
            await ctx.send('cannot find user')
            return None
    with open (f'{constants.userSavePath}{user.id}.txt','r') as f:
        stuff = json.load(f)
    embed = discord.Embed(
        description = f'`PROFILE`',
        colour = discord.Colour.purple()
        )
    embed.set_author(name=f'{user.name} ', icon_url=user.avatar_url)
    embed.add_field(name='Balance: ',value=f"{stuff['account']['balance']}")
    embed.add_field(name='Wins: ',value=f"{stuff['account']['wins']}")
    embed.add_field(name='Losses: ',value=f"{stuff['account']['losses']}")
    embed.add_field(name='Blackjacks: ',value=f"{stuff['account']['blackJacks']}")
    embed.add_field(name='Busts: ',value=f"{stuff['account']['busts']}")
    embed.add_field(name='Total Games: ',value=f"{stuff['account']['totalGames']}")
    embed.add_field(name='Win Percentage: ',value=f"{stuff['account']['winPercent']}%")
    embed.add_field(name='Membership: ',value=f"{stuff['account']['membership']}")
    await ctx.send(embed=embed)
    
@bot.command()
async def play(ctx, *args):
    await accountExists(ctx)
# LOAD DECK AND PLAYER PROFILE
    deck = await deckCreation(constants.deck)
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','r') as f:
        stuff = json.load(f)
# TABLE START SCREEN
    menu = discord.Embed(
        description = f"""WELCOME <@{ctx.author.id}> TO THE TABLE""",
        colour = discord.Colour.purple()
        )
    menu.set_author(name=f"{ctx.author.name} ", icon_url=ctx.author.avatar_url)
    menu.set_image(url='https://i.imgur.com/m5m7lza.png')
    ui = await ctx.send(embed=menu)
    await asyncio.sleep(7)
#GAME LOGIC
    gameEnd = False
    while gameEnd == False:
        PlayerTurn = True
        DealerTurn = False
        hasDouble = False
        roundEnd = False
        dealerHand = []
        playerHand = []
        dealerValue = 0
        playerValue = 0

    # DEAL STARTING HANDS
        deck,playerHand,playerValue = await playerDraw(deck,playerHand,playerValue) #order : players -> dealer(FU) -> players -> dealer(FD)
        deck,dealerHand,dealerValue = await dealerDraw(deck,dealerHand,dealerValue)
        deck,playerHand,playerValue = await playerDraw(deck,playerHand,playerValue)
        # >>>>> dealer face down <<<<< #

        while roundEnd == False:
            await updateTable(ctx,dealerHand,dealerValue,playerHand,playerValue,ui,PlayerTurn,hasDouble)
            if DealerTurn:
                deck,dealerHand,dealerValue = await dealerDraw(deck,dealerHand,dealerValue)
                DealerTurn = False
                PlayerTurn = True
                continue
            if hasDouble:
                PlayerTurn = False
                DealerTurn = True
                continue
            if PlayerTurn:
                choice = await playerTurn(ctx,deck,playerHand,playerValue)
                if choice == 'hit':
                    deck,playerHand,playerValue = await playerDraw(deck,playerHand,playerValue)
                if choice == 'stand':
                    None
                if choice == 'double':
                    deck,playerHand,playerValue = await playerDraw(deck,playerHand,playerValue)
                    hasDouble = True
                PlayerTurn = False
                DealerTurn = True
                continue
        if len(deck) <= 60:
            await reshuffleDeckScreen(ctx,ui)
            deck = await deckCreation(constants.deck)

#FUNCTIONS
# RESHUFFLE DECK SCREEN
async def reshuffleDeckScreen(ctx,ui):
    table = discord.Embed(
        description = f"""<@{ctx.author.id}>
        PLEASE WAIT WHILE THE DEALER RESHUFFLES THE DECK
        """,
        colour = discord.Colour.purple()
        )
    table.set_author(name=f"{ctx.author.name} ", icon_url=ctx.author.avatar_url)    
    await ui.edit(embed=table)
    await asyncio.sleep(7)

# UPDATE THE TABLE
async def updateTable(ctx,dealerHand,dealerValue,playerHand,playerValue,ui,PlayerTurn,hasDouble):
    table = discord.Embed(
        description = f"""<@{ctx.author.id}>
        
        Dealer Hand: {dealerHand} Dealer Value: {dealerValue}                                               
        Player Hand: {playerHand} Player Value: {playerValue}
        
        """,
        colour = discord.Colour.purple()
        )
    table.set_author(name=f"{ctx.author.name} ", icon_url=ctx.author.avatar_url)    
    await ui.edit(embed=table)

    if hasDouble:
        await ui.clear_reactions()
        return
    if PlayerTurn:
        await ui.clear_reactions()
    await ui.add_reaction(constants.hit)
    await ui.add_reaction(constants.stand)
    await ui.add_reaction(constants.double)

# PLAYER TURN TO HIT/STAND/DOUBLE
async def playerTurn(ctx,deck,playerHand,playerValue):
    try:
        reaction, user = await bot.wait_for('reaction_add', check=lambda react,user: user==ctx.author and str(react.emoji) in [f'<{constants.hit}>',f'<{constants.stand}>',f'<{constants.double}>'], timeout = 120.0)
    except asyncio.TimeoutError:
        print('timeout')
        await timeoutGame()
    else:
        if str(reaction) == f'<{constants.hit}>':
            return 'hit'
        if str(reaction) == f'<{constants.stand}>':
            return 'stand'
        if str(reaction) == f'<{constants.double}>':
            return 'double'

# TIMEOUT
async def timeoutGame():
    None

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
    if type(ctx) == discord.ext.commands.context.Context:
        user = ctx.author
    else:
        user = ctx
    stuff = {}
    stuff['account'] = {}
    stuff['account'].update({
        'accountName' : f'{user.name}',
        'accountId' : f'{user.id}',
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
    
    with open (f'{constants.userSavePath}{user.id}.txt','w') as f:
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

# DIFFRENCE IN TIME FROM COMMAND AND LAST CLAIM
async def dateDiffInSeconds(date1, date2):
    timedelta = date2 - date1
    return timedelta.days * 24 * 3600 + timedelta.seconds

# CONVERTING SECONDS INTO READABLE TIME
async def daysHoursMinutesSecondsFromSeconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return (days, hours, minutes, seconds)

# CALCULATES TIME UNTIL NEXT CLAIM
async def nextDailyClaim(ctx):
    with open (f'{constants.userSavePath}{ctx.author.id}.txt','r') as f:
        stuff = json.load(f)
    now = datetime.now()
    lastClaim = datetime.strptime(stuff['account']['lastDailyClaimTime'],'%H:%M:%S')
    dateFormat = await daysHoursMinutesSecondsFromSeconds(await dateDiffInSeconds(now, lastClaim))
    await ctx.send(f"<@{ctx.author.id}> You can do -daily in {dateFormat[1]} hours {dateFormat[2]} minutes {dateFormat[3]} seconds")
    
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

# NOT IN USE CURRENTLY - INVALID ARGUMENTS
async def invalidArguments(ctx):
    await ctx.send(f'<@{ctx.author.id}> Invalid arguments do -help for a list of commands')

if __name__ == "__main__":
    with open(constants.tokenPath,"r") as token:
        token=token.read()
        bot.run(token)