import discord, asyncio, os, json, sys, re, datetime, time
from discord.ext import commands
from random import *
from urllib import parse
from urllib.request import urlopen

token = "Nzg0MjcwNTk2MTQ5MzQ2MzA0.X8m26Q.VIRuyE8qnJElI0sWg36wojnsFaM"
#token = "NzgzNjkyODU5MzM2ODE4NzA4.X8ec2Q.vSz2BlHSgL_x8biAVXvr7qXZPiM"
bot = commands.Bot(command_prefix='?!', help_command=None)

def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

@bot.event
async def on_ready():
    ch = 0
    for g in bot.guilds:
        ch += 1
    print("=========================")
    print("다음으로 로그인 합니다 : ")
    print(bot.user.name)
    print("로그인 성공!")
    print("=========================")      
    list_name = ['?!help / ?!patch', '?!invite to invite the bot!', f'Working on {ch} servers', 'm!help (music bot commend)']
    await bt(list_name)


def save_data():
    open('data.json', mode='w', encoding='utf-8').write(json.dumps(messages))

msg = None
try:
    messages = json.loads(open('data.json', mode='r', encoding='utf-8').read())
except Exception as E:
    print("Data file was errored!")
    raise E

'''try:
    recover = json.loads(open('recover.json', mode='r', encoding='utf-8').read())
except Exception as E:
    recover = []
    open('recover.json', mode='w', encoding='utf-8').write("[]")'''

channels = {}
delayChan = {}
delayWorkingChan = set()
deleteWorkingChan = set()

try:
    channels = json.loads(open('reactions.json', mode='r', encoding='utf-8').read())
except:
    open('reactions.json', mode='w').write(json.dumps({}))


async def bt(games):        
    await bot.wait_until_ready()

    while not bot.is_closed():
        for g in games:
            await bot.change_presence(status = discord.Status.online, activity = discord.Game(g))
            await asyncio.sleep(5)

@bot.command()
async def ping(ctx):
    la = bot.latency
    await ctx.send(":ping_pong:  **Pong!** " + f'{str(round(la * 1000))}ms')
    
@bot.command()
async def getstick(ctx):
    print(messages.keys())
    if str(ctx.channel.id) in messages.keys():
        embed = discord.Embed(title=f"Stickied Message Info", description=f"**Channel** {ctx.channel.mention}")
        if re.compile('discord.Embed\(title=".*", description=".*", color=[0-9]+\)').match(messages[str(ctx.channel.id)][1]):
            Emb = eval(messages[str(ctx.channel.id)][1].split('///')[0])
            embed.description += f'\n**Type** Embed'
            embed.description += f'\n**Title** {Emb.title}'
            embed.description += f'\n**Description** {Emb.description}'
            embed.description += f'\n**Color** {Emb.color}'
            try:
                embed.description += f'\n**Image** {messages[str(ctx.channel.id)][1].split("///")[1]}'
            except IndexError:
                pass
        else:
            embed.description += f'\n**Type** Text'
            embed.description += f'\n**Text** {messages[str(ctx.channel.id)][1]}'
        embed.description += f'\n**Delay** {messages[str(ctx.channel.id)][3]}'
        await ctx.author.send(embed=embed)
    else:
        await ctx.author.send(embed=discord.Embed(title="No stickied text in channel"))

@bot.command()
async def stick(ctx, *others):
    global messages
    run = True
    while(run == True):
        run = False
        if ctx.author.permissions_in(ctx.channel).manage_messages:
            if len(ctx.message.content.split(' ', maxsplit=2)) <= 2:
                await ctx.send(embed=discord.Embed(title="Syntax", description="\n\n`?!stick text <message to stick> [delay=<delay>]`\n`?!stick embed <title>///<desc>///<#color> [img=<url>] [delay=<delay>]`\n\n`?!stick text <접착할 메시지> [delay=<지연>]`\n`?!stick embed <제목>///<설명>///<#색상> [img=<링크>] [delay=<지연>]`", color=0x03a9ab))
            else:
                try:
                    delay = ctx.message.content.split(' delay=', maxsplit=1)[1]
                    print(delay)
                    delay = float(delay)
                except IndexError as E:
                    delay = 1
                    delayChan[ctx.channel.id] = 0
                except:
                    await ctx.send(embed=discord.Embed(title="", description="%s is not a valid number" % delay))
                    break                        
                if ctx.message.content.split(' ', maxsplit=2)[1] == ('text'):
                    content = ctx.message.content.split(' ', maxsplit=2)[2].split(' img=')[0].split(' delay=')[0]
                    if messages.get(str(ctx.channel.id)) == None:
                        messages[str(ctx.channel.id)] = [None, content, [], delay]
                    else:
                        messages[str(ctx.channel.id)][1] = content
                        messages[str(ctx.channel.id)][3] = delay
                    try:
                        await ctx.send(embed=discord.Embed(title="%s was set to channel #%s's stickied message" % (messages[str(ctx.channel.id)][1], ctx.channel.name), description="%s (이)가 채널 %s의 접착 메시지로 설정되었습니다" % (messages[str(ctx.channel.id)][1], ctx.channel.mention), color=0x03a9ab))
                    except discord.errors.HTTPException:
                        await ctx.send(embed=discord.Embed(title="%s was set to channel #%s's stickied message" % (messages[str(ctx.channel.id)][1][0:211] + "...", ctx.channel.name), description="%s (이)가 채널 %s의 접착 메시지로 설정되었습니다" % (messages[str(ctx.channel.id)][1][0:211] + "...", ctx.channel.mention), color=0x03a9ab))
                elif ctx.message.content.split(' ', maxsplit=2)[1] == ('embed'):
                    try:
                        img = ctx.message.content.split('///', maxsplit=2)[2].split(' img=', maxsplit=1)[1].split(' delay=')
                        if 'http' in img[1]: img = img[1]
                        else: img = img[0]
                    except IndexError:
                        img = ""
                    try:
                        title = ctx.message.content.split(' ', maxsplit=2)[2].split('///', maxsplit=2)[0].replace("\n", "\\n")
                    except:
                        title = ""
                    try:
                        desc = ctx.message.content.split(' ', maxsplit=2)[2].split('///', maxsplit=2)[1].replace("\n", "\\n")
                    except:
                        desc = ""
                    try:
                        color = ctx.message.content.split(' ', maxsplit=2)[2].split('///', maxsplit=2)[2].split(' ')[0]
                        if color.startswith('#'):
                            color = int(color[1:len(color)], 16)
                        else:
                            color = int(color, 16)
                        if color > 16777215:
                            raise ValueError("Not a valid color")
                        if color == 16777215:
                            color = 16777214
                    except IndexError:
                        color = 0x00aaaa
                    except ValueError:
                        if color == "":
                            color = 0x00aaaa
                        else:
                            await ctx.send(embed=discord.Embed(title="", description="%s is not a valid color" % ctx.message.content.split(' ', maxsplit=2)[2].split('///', maxsplit=2)[2], color=0x03a9ab))
                            break
                    if messages.get(str(ctx.channel.id)) == None:
                        messages[str(ctx.channel.id)] = [None, "discord.Embed(title=\"%s\", description=\"%s\", color=%d)///%s" % (title, desc, color, img), [], delay]
                    else:
                        messages[str(ctx.channel.id)][1] = "discord.Embed(title=\"%s\", description=\"%s\", color=%d)///%s" % (title, desc, color, img)
                        messages[str(ctx.channel.id)][3] = delay
                    await ctx.send(embed=discord.Embed(title="An embed was set to channel #%s's stickied message" % ctx.channel.name, description="임베드 (이)가 채널 %s의 접착 메시지로 설정되었습니다" % ctx.channel.mention, color=0x03a9ab))
                else:
                    await ctx.send(embed=discord.Embed(title="Syntax", description="\n\n`?!stick text <message to stick> [delay=<delay>]`\n`?!stick embed <title>///<desc>///<#color> [img=<url>] [delay=<delay>]`\n\n`?!stick text <접착할 메시지> [delay=<지연>]`\n`?!stick embed <제목>///<설명>///<#색상> [img=<링크>] [delay=<지연>]`", color=0x03a9ab))
        else:
            await ctx.send(embed=discord.Embed(title="You don't have message manage permission on this channel", description="이 채널에서의 메시지 관리 권한이 없습니다", color=0x03a9ab))

@bot.command(aliases = ["stickstop"])
async def stopstick(ctx, *others):
    message = ctx.message
    if message.author.permissions_in(message.channel).manage_messages:
        try:
            messages.pop(str(message.channel.id))
            await ctx.send(embed=discord.Embed(title="Channel #%s's stickied message was removed" % (message.channel.name), description="채널 %s의 접착 메시지가 삭제되었습니다" % (message.channel.mention), color=0x03a9ab))
        except KeyError:
            await ctx.send(embed=discord.Embed(title="No existing stickied message on channel #%s" % (message.channel.name), description="채널 %s에 접착 메시지가 없습니다" % (message.channel.mention), color=0x03a9ab))
        save_data()
    else:
        await ctx.send(embed=discord.Embed(title="You don't have message manage permission on this channel", description="이 채널에서의 메시지 관리 권한이 없습니다", color=0x03a9ab))

@bot.command()
async def vote(ctx, *others): #vote
    message = ctx.message
    if message.author.permissions_in(message.channel).manage_messages:
        #await message.delete()
        qjsgh = 0
        vote = message.content[7:].split("/")
        embed = discord.Embed(title='Topic - [' + vote[0] + ']', color=0x62c1cc)
        for i in range(1, len(vote)):
            qjsgh += 1
            embed.add_field(name=qjsgh, value=vote[i], inline=False)
        choose = await ctx.send(embed=embed)
        qjsgh = 0
        
        for i in range(1, len(vote)):
            qjsgh += 1
            if qjsgh == 1:
                await choose.add_reaction('1️⃣')
            else:
                if qjsgh == 2:
                    await choose.add_reaction('2️⃣')
                else:
                    if qjsgh == 3:
                        await choose.add_reaction('3️⃣')
                    else:
                        if qjsgh == 4:
                            await choose.add_reaction('4️⃣')
                        else:    
                            if qjsgh == 5:
                                await choose.add_reaction('5️⃣')
                            else:    
                                if qjsgh == 6:
                                    await choose.add_reaction('6️⃣')
                                else:
                                    if qjsgh == 7:
                                        await choose.add_reaction('7️⃣')
                                    else:
                                        if qjsgh == 8:
                                            await choose.add_reaction('8️⃣')
                                        else:
                                            if qjsgh == 9:
                                                await choose.add_reaction('9️⃣')
                                            else:    
                                                if qjsgh == 10:
                                                    await choose.add_reaction('')
                                                else:
                                                    await choose.add_reaction('')
    else:
        await ctx.send(embed=discord.Embed(title="You don't have message manage permission on this channel", description="이 채널에서의 메시지 관리 권한이 없습니다", color=0x03a9ab))           

@bot.command(aliases = ["lucky"])
async def luck(ctx, *others):
    message = ctx.message
    dw = randint(1, 12)
    if dw == 1:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... ZERO / 10 ", color=0x03a9ab))
    if dw == 2:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... ZERO / 10 ", color=0x03a9ab))
    if dw == 3:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 1 / 10 ", color=0x03a9ab))
    if dw == 4:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 2 / 10 ", color=0x03a9ab))
    if dw == 5:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 3 / 10 ", color=0x03a9ab))
    if dw == 6:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 4 / 10 ", color=0x03a9ab))
    if dw == 7:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 5 / 10 ", color=0x03a9ab))
    if dw == 8:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 6 / 10 ", color=0x03a9ab))
    if dw == 9:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 7 / 10 ", color=0x03a9ab))
    if dw == 10:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 8 / 10 ", color=0x03a9ab))
    if dw == 11:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 9 / 10 ", color=0x03a9ab))
    if dw == 12:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Luck is..... 10 / 10 拾", color=0x03a9ab))         

@bot.command(aliases = ["dailylucky"])
async def dailyluck(ctx, *others):
    message = ctx.message
    nowDate = to_integer(datetime.date.today())
    seed(a=int(message.author.id)+int(nowDate))
    dw = randrange(1,11)
    if dw == 0:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Today's Luck is..... ZERO / 10", color=0x03a9ab))
    else:
        await ctx.send(embed=discord.Embed(title="Lucky Test", description="Your Today's Luck is..... %s / 10" % dw, color=0x03a9ab))
                                                
@bot.command()
async def emoji_log(ctx, *others):
    message = ctx.message
    if message.author.permissions_in(message.channel).manage_messages:
        args = message.content.split(' ')
        emoji_channel = str(bot.get_channel(int(args[1][2:-1])).id)
        log_channel = str(bot.get_channel(int(args[2][2:-1])).id)
        channels[emoji_channel] = log_channel
        open('reactions.json', mode='w').write(json.dumps(channels))
        print(channels)

        await ctx.send(embed=discord.Embed(title="#%s's message un-reactions will be logged in #%s" % (bot.get_channel(int(emoji_channel)).name, bot.get_channel(int(log_channel)).name)))
    else:
        await ctx.send(embed=discord.Embed(title="You don't have message manage permission on this channel", description="이 채널에서의 메시지 관리 권한이 없습니다", color=0x03a9ab))

@bot.command()
async def emoji_log_remove(ctx, *others):
    message = ctx.message
    if message.author.permissions_in(message.channel).manage_messages:
        args = message.content.split(' ')
        args[1] = args[1][2:-1]
        if args[1] in channels.keys():
            await ctx.send(embed=discord.Embed(title="#%s's message reactions will no longer be logged in #%s" % (bot.get_channel(int(args[1])), bot.get_channel(int(channels[args[1]])))))
            del channels[args[1]]
            open('reactions.json', mode='w').write(json.dumps(channels))
            print(channels)
        else:
            await ctx.send(embed=discord.Embed(title="There's no emoji logging in #%s" % (bot.get_channel(int(args[1])))))
    else:
        await ctx.send(embed=discord.Embed(title="You don't have message manage permission on this channel", description="이 채널에서의 메시지 관리 권한이 없습니다", color=0x03a9ab))

@bot.command()
async def invite(ctx, *others): #초대
    embed = discord.Embed(title="Invite me!", description="https://discord.com/api/oauth2/authorize?client_id=784270596149346304&permissions=70569024&scope=bot ", color=0x00ff03)
    await ctx.author.send(embed=embed)

@bot.command()
async def help(ctx, *others):  #도움말        
    embed = discord.Embed(title="Command list", description="Check about how to use sticky bot / 봇의 사용법을 확인하세요.", color=0x00ff03)
    embed.add_field(name="Korean", value="https://docs.google.com/document/d/18CF4OrAoykKx9lLdGmGMmwhBhovAWZ8ws1_d-ESUw_E/edit?usp=sharing", inline=False)
    embed.add_field(name="English", value="https://docs.google.com/document/d/1tAZ0c-stGEtdXyb6zjCFKC-PBxrR9AADhuI3b_xtukI/edit?usp=sharing", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def patch(ctx, *others): #패치노트
    if ctx.author.permissions_in(ctx.channel).manage_messages:
        embed = discord.Embed(title="Patch Note", description="Check about Patch Note / 패치노트를 확인합니다.", color=0x00ff03)
        embed.add_field(name="Link (KOR/ENG)", value="https://docs.google.com/document/d/1eF7eRCoFbkDGTpRbx-ZvsAWTatkRsIfXJVKmqRCi_eI/edit?usp=sharing", inline=False)            
        await ctx.send(embed=embed)
    else:
        await ctx.channel.send(embed=discord.Embed(title="Only mods can view Patch Note", description="관리자만 패치노트 확인이 가능합니다.", color=0x03a9ab)) 			

@bot.event
async def on_message(message):
    id = message.author.id
    global messages
    working = []
    
    if id == 455343602898305034: #소유주 전용 명령어
        if message.content == ('?!stop'): #봇 종료
            await message.channel.send(embed=discord.Embed(title=" Stopping the bot", description="", color=0x03a9ab))
            sys.exit(0)

        if message.content == ('?!restart'): #봇 재시작
            await message.channel.send(embed=discord.Embed(title="⏪ Restarting the bot", description="", color=0x03a9ab))
            os.system('start.bat')
            sys.exit(0)

    if message.author == bot.user:
        return

    '''global recover
    if message.channel.id not in recover:
        messagesThis = await message.channel.history().flatten()
        ThereIsBotMessage = False
        for i in messagesThis:
            if i.embeds == [] and i.author == bot.user and i.content != "" and not(i.content.startswith(":ping_pong:")):
                if messages.get(str(i.channel.id)) == None:
                    messages[str(i.channel.id)] = [None, i.content]
                else:
                    messages[str(i.channel.id)][1] = i.content
                await i.channel.send(embed=discord.Embed(title="The sticky message text was recovered.\nuse ?!stickstop to delete the message if you dont want it to be recovered."))
                break
        recover.append(message.channel.id)
        open('recover.json', mode='w', encoding='utf-8').write(json.dumps(recover))
    '''
    #print(messages)

    while messages.get(str(message.channel.id)) != None:
        if message.content.startswith('?!stick'): break
        if message.content.startswith('?!stop'): break
        if delayChan.get(message.channel.id) == None:
            delayChan[message.channel.id] = 0
        if len(messages[str(message.channel.id)]) < 4:
            messages[str(message.channel.id)].append(1)

        if time.time() - delayChan[message.channel.id] < messages[str(message.channel.id)][3]:
            delayChan[message.channel.id] = time.time()
        
        if message.channel.id in delayWorkingChan:
            break
        else:
            delayWorkingChan.add(message.channel.id)
            while time.time() - delayChan[message.channel.id] < messages[str(message.channel.id)][3]:
                await asyncio.sleep(0.5)
            delayWorkingChan.remove(message.channel.id)
        if message.channel.id in deleteWorkingChan:
            break
        deleteWorkingChan.add(message.channel.id)
        if messages[str(message.channel.id)][0] != None:
            if not message.channel.id in working:
                working.append(message.channel.id)
                try:
                    messages[str(message.channel.id)][2]
                except IndexError:
                    messages[str(message.channel.id)].append([])
                try:
                    msg = await message.channel.fetch_message(messages[str(message.channel.id)][0])
                    await msg.delete()
                except discord.errors.NotFound:
                    pass
                while len(messages[str(message.channel.id)][2]) > 0:
                    for i in messages[str(message.channel.id)][2]:
                        try:
                            try:
                                msg = await message.channel.fetch_message(i)
                                await msg.delete()
                                messages[str(message.channel.id)][2].remove(msg.id)
                            except discord.errors.NotFound:
                                messages[str(message.channel.id)][2].remove(i)
                        except ValueError:
                            continue
                
            else:
                return None
            working.remove(message.channel.id)
        try:
            if re.compile('discord.Embed\(title=".*", description=".*", color=[0-9]+\)').match(messages[str(message.channel.id)][1]):
                Emb = eval(messages[str(message.channel.id)][1].split('///')[0])
                try:
                    img = messages[str(message.channel.id)][1].split('///')[1]
                    Emb.set_thumbnail(url=img)
                except IndexError:
                    pass
                
                msg = await message.channel.send(embed = Emb)
            else:
                msg = await message.channel.send(messages[str(message.channel.id)][1])
            try:
                messages[str(message.channel.id)][2].append(msg.id)
                messages[str(message.channel.id)][0] = msg.id
            except IndexError:
                messages[str(message.channel.id)].append([])
                messages[str(message.channel.id)][2].append(msg.id)
        except Exception as E:
            await message.channel.send(E)
        save_data()
        deleteWorkingChan.remove(message.channel.id)
        delayChan[message.channel.id] = time.time()
        break
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.channel_id) in channels.keys():
        username = bot.get_user(payload.user_id)
        user_unknown = 0
        if username == None:
            username = "__An unknown user__"
            user_unknown = 1
        
        if user_unknown == 0:
            Embed1 = discord.Embed(title="%s un-reacted on a message in #%s" % (username, bot.get_channel(payload.channel_id).name), description="%s" % payload.emoji, color=0xffff00)
            Embed1.set_footer(text = 'ID: %d' % payload.user_id)
        else:
            Embed1 = discord.Embed(title="%s un-reacted on a message in #%s" % (username, bot.get_channel(payload.channel_id).name), color=0xffff00)
            Embed1.set_footer(text = 'ID: %d' % payload.user_id)
            Embed1.add_field(name="%s" % payload.emoji, value="\"__An unknown user__\" usually occurs when the user has never chatted on the server while dashboard is running" , inline=True)
        Embed1.timestamp = datetime.datetime.utcnow()

        await bot.get_channel(int(channels[str(payload.channel_id)])).send(embed=Embed1)
        
@bot.command()
async def setdelay(ctx, seconds: int):
    if ctx.author.permissions_in(ctx.channel).manage_messages:
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!")
    else:
        await ctx.send(embed=discord.Embed(title="You don't have message manage permission on this channel", description="이 채널에서의 메시지 관리 권한이 없습니다", color=0x03a9ab))
        
bot.run(token)
