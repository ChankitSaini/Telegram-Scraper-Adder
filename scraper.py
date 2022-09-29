import os, sys
import configparser
import csv
import time
from time import sleep
import datetime


from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import UserStatusRecently, ChannelParticipantsAdmins, UserStatusLastMonth, UserStatusLastWeek, UserStatusOffline, UserStatusOnline

re="\033[1;31m"
gr="\033[1;32m"
cy="\033[1;36m"

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)

def banner():
    print(f"""
{re}╔╦╗┌─┐┬  ┌─┐{re}╔═╗  ╔═╗┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
{re} ║ ├┤ │  ├┤ {re}║ ╦  ╚═╗│  ├┬┘├─┤├─┘├┤ ├┬┘
{re} ╩ └─┘┴─┘└─┘{re}╚═╝  ╚═╝└─┘┴└─┴ ┴┴  └─┘┴└─

              Version : 1.01
 {re}Thanks to me
   www.chankit.me
        """)

cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('clear')
    banner()
    print(re+"[!] run python3 setup.py first !!\n")
    sys.exit(1)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    os.system('clear')
    banner()
    client.sign_in(phone, input(gr+'[+] Enter the code: '+re))
 
os.system('clear')
banner()
chats = []
last_date = None
chunk_size = 200
groups=[]
 
result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)
 
for chat in chats:
    try:
        if chat.megagroup== True:
            groups.append(chat)
    except:
        continue
 
print(gr+'[+] Choose a target_group to scrape members :'+re)
i=0
for g in groups:
    print(gr+'['+cy+str(i)+']' + ' - ' + g.title)
    i+=1
 
print('')
g_index = input(gr+"[+] Enter a Number : "+re)
target_group=groups[int(g_index)]
 
print(gr+'[+] Fetching Members...')
time.sleep(1)
choice = int(input(f"\nHow would you like to obtain the users?\n\n[0] All users\n[1] Active Users(online today and yesterday)\n[2] Users active in the last week\n[3] Users active in the last month\n[4] Non-active users(not active in the last month) \n\nYour choice: "))
members = []
members = client.iter_participants(target_group, aggressive=True)

channel_full_info = client(GetFullChannelRequest(target_group))
cont = channel_full_info.full_chat.participants_count

def write(target_group,member):
    if member.username:
        username = member.username
    else:
        username = ''
    if isinstance(member.status,UserStatusOffline):
        writer.writerow([username, member.id, member.access_hash, target_group.title, target_group.id,member.status.was_online])
    else:
        writer.writerow([username, member.id, member.access_hash, target_group.title, target_group.id,type(member.status).__name__])

admin_choice = input(f"Would you like to have admins on a separate CSV file? [y/n] ")
if admin_choice == "y" or admin_choice == "Y":
    with open("admins.csv", "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user id', 'access hash', 'target_group', 'target_group id','status'])
        for member in client.iter_participants(target_group, filter=ChannelParticipantsAdmins):    
            if not member.bot:
                write(target_group,member)
f.close()
print(f"")

time.sleep(1)
with open("members.csv", "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username', 'user id', 'access hash', 'target_group', 'target_group id','status'])
    if choice == 0:
        try:
            for index,member in enumerate(members):
                print(f"{index+1}/{cont}", end="\r")
                if index%100 == 0:
                    sleep(3)
                if not member.bot:
                    write(target_group,member)                   
        except Exception as e:
            print("\nThere was a FloodWaitError, but check members.csv. More than 95%% of members should be already added.")
    elif choice == 1:
        try:
            for index,member in enumerate(members):
                print(f"{index+1}/{cont}", end="\r")
                if index%100 == 0:
                    sleep(3)
                if not member.bot:
                    if isinstance(member.status, (UserStatusRecently,UserStatusOnline)):
                        write(target_group,member)
                    elif isinstance(member.status,UserStatusOffline):
                        d = member.status.was_online                    
                        today_user = d.day == today.day and d.month == today.month and d.year == today.year
                        yesterday_user = d.day == yesterday.day and d.month == yesterday.month and d.year == yesterday.year
                        if today_user or yesterday_user:
                            write(target_group,member)
        except Exception as e:
            print(f"There was an error occured please forward it to @ChankitSaini \nError: {e}")
    elif choice == 2:
        try:
            for index,member in enumerate(members):
                print(f"{index+1}/{cont}", end="\r")
                if index%100 == 0:
                    sleep(3)
                if not member.bot:
                    if isinstance(member.status, (UserStatusRecently,UserStatusOnline,UserStatusLastWeek)):
                        write(target_group,member)
                    elif isinstance(member.status,UserStatusOffline):
                        d = member.status.was_online
                        for i in range(0,7):
                            current_day = today - datetime.timedelta(days=i)
                            correct_user = d.day == current_day.day and d.month == current_day.month and d.year == current_day.year
                            if correct_user:
                                write(target_group,member)
        except Exception as e:
            print(f"There was an error occured please forward it to @ChankitSaini \nError: {e}")
    elif choice == 3:
        try:
            for index,member in enumerate(members):
                print(f"{index+1}/{cont}", end="\r")
                if index%100 == 0:
                    sleep(3)
                if not member.bot:
                    if isinstance(member.status, (UserStatusRecently,UserStatusOnline,UserStatusLastWeek,UserStatusLastMonth)):
                        write(target_group,member)
                    elif isinstance(member.status,UserStatusOffline):
                        d = member.status.was_online
                        for i in range(0,30):
                            current_day = today - datetime.timedelta(days=i)
                            correct_user = d.day == current_day.day and d.month == current_day.month and d.year == current_day.year
                            if correct_user:
                                write(target_group,member)
        except Exception as e:
            print(f"There was an error occured please forward it to @ChankitSaini \nError: {e}")
    elif choice == 4:
        try:
            all_users = []
            active_users = []
            for index,member in enumerate(members):
                print(f"{index+1}/{cont}", end="\r")
                all_users.append(member)
                if index%100 == 0:
                    sleep(3)
                if not member.bot:
                    if isinstance(member.status, (UserStatusRecently,UserStatusOnline,UserStatusLastWeek,UserStatusLastMonth)):
                        active_users.append(member)
                    elif isinstance(member.status,UserStatusOffline):
                        d = member.status.was_online
                        for i in range(0,30):
                            current_day = today - datetime.timedelta(days=i)
                            correct_user = d.day == current_day.day and d.month == current_day.month and d.year == current_day.year
                            if correct_user:                            
                                active_users.append(member)
            for member in all_users:
                if member not in active_users:
                    write(target_group,member)
        except Exception as e:
            print(f"There was an error occured please forward it to @ChankitSaini \nError: {e}")
                
f.close()
print(gr+'[+] Members scraped successfully. Join @NeuroticAssociation on Telegram')
