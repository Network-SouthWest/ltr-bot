#########  Import Libraries  ##########
import os
import asyncio
from colorama import Fore, Back, Style
import discord
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime
from discord.ext import commands, tasks
from time import sleep
from random import randint
from flask import Flask, request, render_template, jsonify
import threading #to run flask in background
import signal #shutdown
import re #anticrack
import toml #init


#########  Variables define  #########
global dev_mode
dev_mode = False
''' DEVELOPMENT DEBUG MESSAGES -- TURN OFF WHEN IN RELEASE '''

with open('ltr_config.toml', 'r') as f:
    config = toml.load(f)
f.close()

#########  Initialise  ########

TOKEN = config["keys"]["discord_token"]

global status_quote
global old_status_quote
global last_polled
last_polled = 0
status_quote = "Subscribe to LTR Trains!"
old_status_quote = "Subscribe to LTR Trains!"

intents = discord.Intents.default()
intents.message_content = True #needed to read messages
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='*',intents=intents,activity=discord.Activity(type=discord.ActivityType.watching,name=status_quote))
load_dotenv()

now = datetime.now()
uptime_start = now.strftime("%d/%m/%y %H:%M:%S")

#########  Web Server Init  ########
app = Flask(__name__)
     


@app.route('/status', methods=['GET', 'POST'])
def bot_status():
    if request.method == 'POST':
        status_quote = request.form['Bot Status']
        return f"Bot status quote set to: {status_quote}, will update within 15 minutes, POST request received"
    return render_template('status.html')

@app.route('/')
def index():
     return render_template("index.html")

@app.route('/home')
def home():
     return render_template("index.html")

@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    if request.method == 'POST':
        name = request.form['confirmation']
        if name == "yes":
            print("Shutting Down")
            sleep(2)
            os.kill(os.getpid(), signal.SIGINT)
             
    return render_template('shutdown.html')


#########  Code  ###########


def printdev(x):
    if dev_mode == True:
        print(x)

@tasks.loop(minutes=5)
async def rotate_status():
    if True:#status_quote != old_status_quote:
        
        global last_polled
        global status_quote
        
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_quote))
        #print("Status Changed:\n"+old_status_quote+"-->"+status_quote)
        #old_status_quote = status_quote
        
        now = datetime.now()
        day = now.strftime("%A")
        hour=int(now.strftime("%H"))
        
        
        message=["<@"+str(config['ltr']['usr_id_panto'])+"> <@"+str(config['ltr']['usr_id_smallmac'])+"> Time to close bidding!!!!!!\n-# you can use /bidding_war_end in the bidding war channel to change permissions",
                 "<@"+str(config['ltr']['usr_id_panto'])+"> <@"+str(config['ltr']['usr_id_smallmac'])+"> Time to open up bidding!!!!!!\n-# you can use /bidding_war_start in the bidding war channel to change permissions",
                 "## Bids are closed! Please react to your favourite bids <:LTRT:1358179657203056707>. <@&"+str(config['ltr']['role_biddingwarpings'])+">"]
       
        if hour > last_polled and hour == 18:
            if day == "Friday":
                print("end")
                #channel_id = config['ltr']['bidding_war_items'] #bidding war items ticket
                #channel = await bot.fetch_channel(channel_id)
                #message = await channel.send(message[0])
                
                channel_id = config['ltr']['bidding_war'] #bidding war items ticket
                
                
                channel = await bot.fetch_channel(channel_id)
                server = await bot.fetch_guild(config['ltr']['server'])
                try:
                    perms = channel.overwrites_for(server.default_role)
                    perms.send_messages=False
                    await channel.set_permissions(server.default_role, overwrite=perms)
                except Exception as e:
                    print(Fore.RED+Style.BRIGHT+"everybody panic it went wrong ",e,Fore.RESET,Style.NORMAL)
                message = await channel.send(message[2])
                print(Fore.CYAN + "BIDDING HAS ENDED" + Fore.RESET)
                
            elif day == "Sunday":
                print("start")
                channel_id = config['ltr']['bidding_war_items'] #bidding war items ticket
                channel = await bot.fetch_channel(channel_id)
                message = await channel.send(message[1])
                print(Fore.CYAN + "Its Sunday My Dudes. Its Bidding Time." + Fore.RESET)
        last_polled=int(now.strftime("%H"))
        
        
        
        


def ltr_verify(interaction):
    print(interaction.guild.id)
    if interaction.guild.id == config["ltr"]["server"] or interaction.guild.id == config["test"]["server"]:
        return True
    else:
        return False


def executed(interaction,command,extra=""):
    user = interaction.user
    now = datetime.now()
    time = now.strftime("%d/%m/%y %H:%M:%S")
    print(Fore.GREEN+str(command)+" executed by ",user,"at",time,"Message ID:",interaction.id,Fore.RESET,extra)


# Custom styling

GUILD_ID = str(config["bot"]["support_server"]) #support
GUILD_ID_2 = str(config["ltr"]["server"]) #ltr

API = "https://discord.com/api/v10"
HEADERS = {"Authorization": f"Bot {TOKEN}"}

import requests

requests.patch(
    f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/@me",
    headers={"Authorization": f"Bot {TOKEN}"},
    json={"display_name_font_id": 6, "display_name_effect_id": 2, "display_name_colors": [615993,615993,615993,14875981,14875981]})
sleep(1.5)
requests.patch(
    f"https://discord.com/api/v10/guilds/{GUILD_ID_2}/members/@me",
    headers={"Authorization": f"Bot {TOKEN}"},
    json={"display_name_font_id": 6, "display_name_effect_id": 2, "display_name_colors": [615993,615993,615993,14875981,14875981]})


@bot.event
async def on_ready():
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global commands")
    except Exception as e:
        print(f"Global sync failed: {e}")
        
    print(Fore.CYAN+" _   _____ ____   "+Fore.RESET+" ____        _   ")
    print(Fore.CYAN+"| | |_   _|  _ \\  "+Fore.RESET+"| __ )  ___ | |_ ")
    print(Fore.CYAN+"| |   | | | |_) | "+Fore.RESET+"|  _ \\ / _ \\| __|")
    print(Fore.CYAN+"| |___| | |  _ <  "+Fore.RESET+"| |_) | (_) | |_ ")
    print(Fore.CYAN+"|_____|_| |_| \\_\\ "+Fore.RESET+"|____/ \\___/ \\__|\n\n")
    
    
    
    
    rotate_status.start()
    
    print(Fore.BLUE+Style.BRIGHT)
    print(f'{bot.user.name} has connected to Discord!')
    #print(Fore.GREEN+"Commands:"+Fore.RESET)
    #print([cmd.name for cmd in bot.commands])
    print(Fore.RESET+"Connected to:")
    for guild in bot.guilds:
        print(guild.name,guild.id)
    print(Fore.YELLOW+"Ready\n"+Fore.RESET)
    print(Style.NORMAL)



async def add_role(role_id,guild,user_arr):

    for l in user_arr:
        member = guild.get_member(int(l)) #self explanatory really
        if member is None:
            member = await guild.fetch_member(int(l))
    
        if member:
            role = guild.get_role(role_id) #Fetch Winner Role 1562761400776925234
        else:
            print(Fore.Red+"add_role error: role isnt a thing apparently. start screaming."+Fore.RESET) #Screaming Intensifies
        if role:
            await member.add_roles(role) #Add ye role 
            print(member, "has been added to role",role_id, end=" ")
        else:
            print(Fore.Red+"Uhhh role isnt a thing apparently."+Fore.RESET) #Screaming Intensifies
    #print("egg")

async def remove_role(role_id,guild,user_arr):

    for l in user_arr:
        member = guild.get_member(int(l)) #self explanatory really
        if member is None:
            member = await guild.fetch_member(int(l))
    
        if member:
            role = guild.get_role(role_id) #Fetch Winner Role 1562761400776925234
        else:
            print(Fore.Red+"add_role error: role isnt a thing apparently. start screaming."+Fore.RESET) #Screaming Intensifies
        if role:
            await member.remove_roles(role) #remove ye role 
            print(member, "has been removed from role",role_id, end=" ")
        else:
            print(Fore.Red+"Uhhh role isnt a thing apparently."+Fore.RESET) #Screaming Intensifies


async def bidding_war_submissions(submission):
    #submission format = "user_id,submission"
    file = open("bid_submissions.txt","rt")
    data = []
    for i in file:
        if len(i) > 2:
            data.append(i.strip("\n"))
    file.close()

    submissions = 0
    winners = 0

    submissions = int(data[0].split("/")[0])+1
    winners = int(data[0].split("/")[1])
    

    #print(submissions,winners)
    data[0] = (f"{submissions}/{winners}\n")
    #print("data",data)
    data.append("\n"+submission+"\n")

    file = open("bid_submissions.txt","wt")
    for b in data:
        file.write(b+"\n")
    file.close()
    print(submissions,winners,submissions==winners)
    if submissions == winners:
        # START BIDDING WAR
        print(Fore.GREEN+"start bidding war"+Fore.RESET)


        #start coding hereee.
        channel = await bot.fetch_channel(1488983500551098398)#test 1543878894422069298)
        file= open("bid_submissions.txt","rt")
        data = []
        print(data)
        
        

        for i in file:
            if len(i) > 2:
                data.append(i.strip("\n"))
        print(data)
        data.pop(0)
        
        msg = "# Bidding War; Round n+1\n**Items for auction:**\n\n"
        for n in data:
            msg = msg+" - "+n.split(",")[1]+"\n"

        bidding_quotes=["On your marks, get set, bake!","Wigan NorthWestern","Welcome aboard this avanti west coast service to bidingham new street","Its dark in here",
                        "With great power comes great electricity bill","If there is a hole there is a goal","Shuddup skiiiiiii","To confuse your enemy first you must confuse yourself",
                        "UwU",":3 prr","Better to poo in the sink than to sink in the poo","greggs","sausage roll","TPWS and AWS Operational","The bluetooth device is ready to pair",
                        "Leaton :uh_oh:","T R A C T O R","Mega thrash, Mega Bash","If you can prove that this footer has been used twice you get to pick the replacement text here",
                        "You are going to brazil","fuh you firstbus","Arriva","TfL offers their condolences","Network SouthEast","Do robots dream of electric sheep?",
                        "Tax Fraud","This service has been cancelled due to leaves on the line","This service has been cancelled due to a brake fault",
                        "This brake fault has been cancelled due to a service","This service is for E L E P H A N T and Castle","Ghost Trains",
                        "You'll be going nowhere","Error 418 I'm a teapot'","Pardon you said","kettle","may your pillow be cool on both sides","Clubcard Accepted",
                        "E","This auction was brought to you by raid shadow legends","Goodness gracious me","The animatronics get a little bit quirky at night"]
        
        msg+="\nFor rules, see pinned messages\n-# "+bidding_quotes[randint(0,len(bidding_quotes)-1)]+"\n|| <@&1488987567692058744>  ||"
        #msg = "Imagine I have done a thing."
        await channel.send(msg)
        
         
        guild = await bot.fetch_guild(1355092715179737099)
        perms = channel.overwrites_for(guild.default_role)
        perms.send_messages=True
        await channel.set_permissions(guild.default_role, overwrite=perms)
    
        response = "Bidding has started, Let the bidding begin!"
        await channel.send(response)


def bidding_war_winners(winners):
    file = open("bid_submissions.txt","wt") # OVERWRITE
    winner_count = len(winners)
    file.write(f"0/{winner_count}\n")
    file.close()

    #UN ADDED



@bot.event
async def on_message(message):
    
    gif_war = [config["ltr"]["gif_war"],config["test"]["gif_war"]] 
    bidding_war = [config["ltr"]["bidding_war"],config["test"]["bidding_war"]]   
    
    if not message.guild and message.author.id != config["bot"]["user_id"]:
        channel_id = config["bot"]["logs_channel"] #bot-logs channel in support server
        channel = await bot.fetch_channel(channel_id)
        await channel.send("LTR Bot DM")
        await channel.send(str(message.author)+"\n"+str(message.content))

    banned_bots = ["heist","quotubi"]
    
    channel_gallery = config["ltr"]["gallery"]
    channel_staff_room = config["ltr"]["staff_room"] #LTR
    server_ltr = config["ltr"]["server"]
    role_ltr_mod = config["ltr"]["role_mod"]
    channel_gif_war = config["ltr"]["gif_war"]
    channel_bidding_war = config["ltr"]["bidding_war"]
    
    #print(message.guild)
    ltr = False
    try:
        ltr = (message.guild.id == config["ltr"]["server"])
    except:
        ltr = (str(message.guild) == "LTRtrains")
    #print(message,message.content)
    if message.guild.id == (config["test"]["server"]) or (ltr == True ):
        
        bypass = "None"
        exempt_roles = [config["ltr"]["role_networker"],config["ltr"]["role_ltrbot"],config["ltr"]["role_biddingwarcontrols"],config["ltr"]["role_mod"],config["test"]["role_fakemod"]] # Networker Bot, LTR Bot,Bidding War Controls, Mod [MODERATOR ROLE MUST ALWAYS BE LAST] , spoof ltr mod
        role_name = ["Bot","Bot","Bid","Mod","Mod"]
        try:
            for i in message.author.roles:
                #printdev(i)
                if i.id in exempt_roles: #Mod
                    bypass = role_name[exempt_roles.index(i.id)]
                    #printdev("bypass: "+str(bypass))
                #printdev(i.id)
        except Exception as e:
            bypass = "None"
            printdev(Fore.RED+"ERROR    "+str(e)+Fore.RESET)
                
        #print(message.author.bot)
        if ( message.author.bot == False) or (message.author.bot == "False"):
            if not message.attachments and not "https://" in message.content and (message.channel.id in gif_war) and not ( bypass in ["Mod","Bot"]) and not message.content == "Only gifs/images may be sent in this channel.": # and message.author == discord.client.User:
                await message.delete()
                
                channel = await bot.fetch_channel(message.channel.id)
                await channel.send("Only gifs/images may be sent in this channel.", delete_after=3.0)
                print(Fore.YELLOW+"LTR: Deleted non media message in gif war"+Fore.RESET)
                    
            
          
        
            image_extentions= [".jpeg",".png",".jpg",".svg",".webp",".tiff",".psd",".raw",".bmp",".heif"]
        
            if message.channel.id == channel_gallery :
                for ext in image_extentions:
                    isimage = message.content.lower().split("?")[0].endswith(ext)
                    if isimage == True:
                        break
            
                if not message.attachments and (not isimage) and not ( bypass in ["Mod","Bot"]) : #and message.author == discord.client.User:
                    channel_id = channel_gallery
                    channel = await bot.fetch_channel(channel_id)
                    del_content = message.content
                    del_auth_nick = message.author.nick
                    try:
                        message_og = await channel.fetch_message(message.reference.message_id)
                        thread = await channel.create_thread(name=str(del_content),message=message_og)
                        await thread.send(str(del_auth_nick)+' said; '+str(del_content))
                    except Exception:
                        print("non reply")
                    
                    
                    await message.delete()
                    
                    await channel.send("Only photos may be sent in this channel.", delete_after=3.0)
                    
                    print("LTR: Deleted non media message in photo gallery")
                    
                    
                    
                    
            #print(message.author.name,message)
            if message.author.name in banned_bots and message.author.bot == True:
                print(Fore.RED+"Message from "+str(message.author.name)+" deleted. Reason: Banned bot."+Fore.RESET)
                await message.delete()
                
            if message.channel.id in bidding_war and message.author.bot == False:
                
                if bypass == "None" and message.author.id != 1248524299657285668:
                    bid = message.content
            
                    bid = bid.lower()
            
                    res = "i bid"

                    p = "^" + res
                    if re.search(p, bid):
                        pass
                    else:
                        print("Invalid Bid, must start with \"I Bid\"")
                        await message.delete()
                        channel_id = config["ltr"]["bidding_war"] #bidding war channel
                        channel = await bot.fetch_channel(channel_id)
                        message = await channel.send("I bid that **bids must start with \"I bid.\"**", delete_after=3.0)
                print(bypass,"this better be bid when its meant to")
                if bypass == "Bid":# or True: #Put bidding war controls role here, trust.
                    bid = message.content
                    bid = bid.lower()
            
                
                    # Verificactions here
                    announcement = False #contains # Bidding War; Round
                    end = False
                
                    announcement = "# bidding war; round" in bid
                    end = "winners" in bid
                
                    winners=[]
                
                    if announcement and end:
                        x = re.findall("- <@.*>", bid) # Fetch all winners.
                
                        if len(x) > 0:
                            #print("bidding war end")
                
                            for j in x:
                                #print(j)
                                k = j.split(" ")[1].strip("<@").strip(">") #Extract the user ID of the winners. FIRST mention of each line.
                                #print(k)
                                winners.append(k) #Adds to array cuz you need to
                        print(Fore.CYAN+"Bidding War Winners: ",Fore.RESET,winners) # Cheeky bit of logs action here
                        guild = message.guild
                                
                        bidding_war_winners(winners) # Update TXT file
                                
                        #1562761400776925234) # test Winner Role
                        await add_role(1562773248008126464,guild,winners)
                
                        # test 1562769865847078932 Send message to tell people to submit items.1562773548723081297
                        channel_id = 1562773548723081297 #Bidding Winners
                        channel = await bot.fetch_channel(channel_id)
                        # Long ahh message
                        msg="## YOU HAVE WON :tada: :tada: :tada: \nCongratulations on winning. Please place what you wish to put up for bidding here.\n Please use the format: ``I submit: your item here``\n-# Once you send this message and it is processed successfully, you will be removed from this channel. <@&1562761400776925234>"
                        await channel.send(msg)
                        
            # THATS RIGHT ITS TIME TO YOINKITY SPLOINKETY THESE BIDS EH?
            if (message.channel.id == 1562769865847078932 or message.channel.id == 1562773548723081297) and message.author.bot == False: #you should add the ltr one that doesent exist lol
                # boom
                item = message.content.lower()
                if "i submit:" in item:
                    item = item.split(":")[1]
                    print(item)
                    user = message.author
                    guild = message.guild
                    await bidding_war_submissions(f"{user.id},{item}")
                
                    channel_id = 1562773548723081297 #Bidding Winners
                    channel = await bot.fetch_channel(channel_id)
                    await channel.send(f"Item submitted for auction. <@{user.id}> you will be violenly expelled from this channel shortly.")
                    sleep(3)
                    await remove_role(1562773248008126464,guild,[user.id])
    
    

def perms_verify(role,interaction):
    bypass = "None"
    exempt_roles = [config["ltr"]["role_networker"],config["ltr"]["role_biddingwarcontrols"],config["ltr"]["role_mod"]] # Networker Bot,Bidding War Controls, Mod [MODERATOR ROLE MUST ALWAYS BE LAST]
    role_name = ["Bot","Bid","Mod"]
    try:
        for i in interaction.user.roles:
            if i.id in exempt_roles: #Mod
                #print(i.id)
                bypass = role_name[exempt_roles.index(i.id)]
                #print(bypass)
    except Exception as e:
        bypass = "None"
        print(e)

    if role == "Mod":
        if "Mod" in bypass:
            return True
    elif role == "Bid":
        if "Bid" in bypass or "Mod" in bypass:
            return True
    else:
        return False

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi **{member.name}**, welcome to the LTR Trains Discord Server!'
    )
    rules = ["## Please carefully read the following server rules:","😃 1. Be cool, kind, and civil. **Treat all members with respect** and express your thoughts in a constructive manner.",
             "📇 2. **Use an appropriate name and avatar.** Avoid special characters, emoji, obscenities, and impersonation.\n-# (this includes rules 6, 7 and 8)\n-# (usernames must be distinct from others, and easy to moderate)",
             "📨 3. **Do not spam**. Avoid excessive messages, images, formatting, emoji, commands, and pings (except ⁠spam-stuff ofc)\n-# this applies to ads too, only once a week for the same ad!\n-# pinging 'everyone' or 'here' will result in an automatic 1 hour timeout (dont try it!)",
             "🛡 4. **Avoid personal information.** Protect your privacy and the privacy of others.",
             "🤕 5.**No harassment, abuse, or bullying. We have zero-tolerance for harming others.**",
             "🗯 6. **No racist, sexist, anti-LGBTQ+, or otherwise offensive content.** We have zero-tolerance for hate speech.\n-# (this applies to usernames and statuses)",
             "🏛 7. **No political or religious topics.** These complex subjects result in controversial and offensive posts, please take this elsewhere.\n-# (this applies to usernames and statuses) (excluding exclusively transportation related politics)",
             "🚨 8. **No sexual, inappropriate, pornographic or otherwise inappropriate content.** We do not condone illegal or suspicious discussions and activity. \n-# (this applies to usernames and statuses)",
             "🗂 9. **Please use the correct channels where possible**, Keep links, media, and convo to the topic of the channel!\n-# AI content is only allowed in ⁠AI slop https://discord.com/channels/1355092715179737099/1406968049306963968",
             "🚓 10. **No mini modding**, if you arent a mod, dont moderate! please open a ticket if you want help",
             "🤔 11. **Rules are subject to common sense.** These rules are not comprehensive and use of loopholes to violate the spirit of these rules is still subject to moderation."]
    msg = ""
    for i in rules:
        msg += i+"\n\n"
    await member.dm_channel.send(msg)
    
@bot.tree.command(name="helloworld", description="run a test command")
@app_commands.guild_install()
@app_commands.allowed_contexts(dms=False,guilds=True,private_channels=True)
async def testcommand(interaction: discord.Interaction):
    executed(interaction,"Hello World") #prints to logs
    
    response = "I am indeed being tested"
    await interaction.response.send_message(response)




#@commands.has_permissions(manage_channels=True)
@bot.tree.command(name='bidding_war_end', description="Ends Bidding War - Needs Bidding War Controls")
@app_commands.guild_install()
@app_commands.allowed_contexts(dms=False,guilds=True,private_channels=True)
async def bidding_war_end(interaction: discord.Interaction):
    if ltr_verify(interaction) == True and interaction.channel_id == config["ltr"]["bidding_war"] and perms_verify("Bid",interaction):
        
        executed(interaction,"Bidding War End") #prints to logs
    
        perms = interaction.channel.overwrites_for(interaction.guild.default_role)
        perms.send_messages=False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=perms)
    
        #ltr(interaction)
        response = "Bidding has ended, please react to your favourite bids!"
        await interaction.response.send_message(response)
    
    
@bot.tree.command(name='bidding_war_start')
@app_commands.allowed_contexts(dms=False,guilds=True,private_channels=True)
@app_commands.guild_install()
#@commands.has_permissions(manage_channels=True)
async def bidding_war_start(interaction: discord.Interaction):
    print(ltr_verify(interaction),interaction.channel_id == config["ltr"]["bidding_war"],perms_verify("Bid",interaction))
    if ltr_verify(interaction) == True and interaction.channel_id == config["ltr"]["bidding_war"] and perms_verify("Bid",interaction):
        executed(interaction,"Bidding War Start") #prints to logs
    
        perms = interaction.channel.overwrites_for(interaction.guild.default_role)
        perms.send_messages=True
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=perms)
    
        response = "Bidding has started, Let the bidding begin!"
        await interaction.response.send_message(response)


def run_flask():
    app.run(debug=False,use_reloader=False,host="0.0.0.0")

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()
#print(Fore.RED + "Flask server disabled, uncomment to run again once fixed ⚠️")
(Fore.GREEN + "Flask server Enabled, comment to disable again")
bot.run(TOKEN)
