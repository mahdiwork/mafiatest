import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, WebAppInfo
from telebot.util import antiflood 
from telebot.apihelper import ApiTelegramException
import random
import threading
import logging
import database
import random
from pprint import pprint
from Utils import Game, Group, bot, send_message, edit_message_text, Message, Player, edit_message_reply_markup, Settings
import os 


userStep = {}
dict_messages_main = {}
dict_messages_general = {}
players_dict = {}
group_dict = {}
game_dict = {}
dict_mid_for_answer = {}
dict_admin_group = {}
file_path_main = os.path.join('Game_Mode', 'main_fa.ini')
file_path_general = os.path.join('Game_Mode','general_fa.ini')
master_cid = 74862
main_admin = 748626808
groups_admin = []


main_command = {
r'robot\_setting'       : 'تنظیمات ربات',
}

#------------------------------------------------------------def--------------------------------------------------------------
def read_ini_file(file_path, dict_text):
    current_key = None
    with open(file_path, 'r' ,encoding='utf-8') as file:
        for line in file:
            line = line.rstrip()
            if '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                dict_text[key] = value.strip('"')
                current_key = key
            elif current_key is not None :
                if '[' not in line:
                    dict_text[current_key] += '\n' + line.strip('"')

def create_tag(user):
    return f'[{user.name}](tg://user?id={user.id})'

def is_block(cid):
    check_blocked = database.select_blocked_users_by_cid(cid)
    if check_blocked:
        return True
    else:
        return False

def is_group_block(group_id):
    check_blocked = database.select_blocked_groups_by_group_id(group_id)
    if check_blocked:
        return True
    else:
        return False

def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        userStep[uid] = 0
        return 0

def show_number_for_time_config(type_, chosen, group_id):
    list_times = [60, 90, 120, 180, 300]
    markup = InlineKeyboardMarkup(row_width=3)
    list_markup = []
    for time in list_times:
        if time == chosen:
            list_markup.append(InlineKeyboardButton(f'{time} ✅',callback_data=f'choossetime_{type_}_{time}_{group_id}'))
        else:
            list_markup.append(InlineKeyboardButton(f'{time}',callback_data=f'choossetime_{type_}_{time}_{group_id}'))
    markup.add(*list_markup)
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_{type_}_{group_id}'))
    return markup

def active_or_inactive(type_, chosen, group_id):
    markup = InlineKeyboardMarkup()
    if chosen == 'active':
        markup.add(InlineKeyboardButton(dict_messages_main['onr'] + ' ✅',callback_data=f'activeorinactive_{type_}_active_{group_id}'))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['onr'],callback_data=f'activeorinactive_{type_}_active_{group_id}'))

    if chosen == 'inactive':
        markup.add(InlineKeyboardButton(dict_messages_main['offr'] + ' ✅',callback_data=f'activeorinactive_{type_}_inactive_{group_id}'))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['offr'],callback_data=f'activeorinactive_{type_}_inactive_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_{type_}_{group_id}'))
    return markup

def choose_the_number_of_hunter_save_days(type_, chosen, group_id):
    markup = InlineKeyboardMarkup(row_width=3)
    list_days = [1, 2, 3]
    list_markup = []
    for day in list_days:
        if day == chosen:
            list_markup.append(InlineKeyboardButton(f'{day} ✅',callback_data=f'huntersavedays_{type_}_{day}_{group_id}'))
        else:
            list_markup.append(InlineKeyboardButton(f'{day}',callback_data=f'huntersavedays_{type_}_{day}_{group_id}'))
    markup.add(*list_markup)
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_{type_}_{group_id}'))
    return markup

def choose_game_mode(type_, chosen, group_id):
    markup = InlineKeyboardMarkup()
    if chosen == 'selective':
        markup.add(InlineKeyboardButton(dict_messages_main['Players'] + ' ✅',callback_data=f'choosegamemode_{type_}_selective_{group_id}'))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['Players'],callback_data=f'choosegamemode_{type_}_selective_{group_id}'))

    if chosen == 'normal':
        markup.add(InlineKeyboardButton(dict_messages_main['Normal'] + ' ✅',callback_data=f'choosegamemode_{type_}_normal_{group_id}'))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['Normal'],callback_data=f'choosegamemode_{type_}_normal_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_{type_}_{group_id}'))
    return markup


def choose_show_roles_end_game(type_, chosen, group_id):
    markup = InlineKeyboardMarkup()
    if chosen == 'all':
        markup.add(InlineKeyboardButton(dict_messages_main['all'] + ' ✅',callback_data=f'chooseshowroles_{type_}_all_{group_id}'))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['all'],callback_data=f'chooseshowroles_{type_}_all_{group_id}'))

    if chosen == 'live':
        markup.add(InlineKeyboardButton(dict_messages_main['onlyUp'] + ' ✅',callback_data=f'chooseshowroles_{type_}_live_{group_id}'))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['onlyUp'],callback_data=f'chooseshowroles_{type_}_live_{group_id}'))

    if chosen == 'nothing':
        markup.add(InlineKeyboardButton(dict_messages_main['rolNo'] + ' ✅',callback_data=f'chooseshowroles_{type_}_nothing_{group_id}'))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['rolNo'],callback_data=f'chooseshowroles_{type_}_nothing_{group_id}'))

    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_{type_}_{group_id}'))
    return markup


def InlineKeyboardMarkup_config_time(group_id): # دکمه های اصلی بخش تنظیم تایم
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['config_time_NightTimer'],callback_data=f'timeconfig_NightTimer_{group_id}'),InlineKeyboardButton(dict_messages_main['config_time_DayTimer'],callback_data=f'timeconfig_daytimer_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_time_VotingTimer'],callback_data=f'timeconfig_votingtimer_{group_id}'),InlineKeyboardButton(dict_messages_main['config_time_JoinTimer'],callback_data=f'timeconfig_jointimer_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_time_ExtendTimer'],callback_data=f'timeconfig_extendtimer_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_main_{group_id}'))
    return markup


def InlineKeyboardMarkup_config_roles(group_id):# دکمه های اصلی بخش تنظیم نقش
    markup = InlineKeyboardMarkup(row_width=2)
    list_roles = database.select_all_roles()
    list_markup = []
    type_sub_group = database.select_geoup_by_group_id(group_id)[0]['subscription_type']
    for role in list_roles:
        if role['role_status'] == 'on':
            if role['role_type'] == 'paid':
                if type_sub_group == 'free':
                    list_markup.append(InlineKeyboardButton(role['role_name'] + " 💰", callback_data=f"roleconfig_paid_{group_id}_{role['code_role']}"))
                    continue
            check_closed = database.select_closed_roles_for_groups_by_group_id(group_id, role['code_role'])
            if check_closed:
                list_markup.append(InlineKeyboardButton(role['role_name'] + " ❌", callback_data=f"roleconfig_open_{group_id}_{role['code_role']}"))
            else:
                list_markup.append(InlineKeyboardButton(role['role_name'] + " ✅", callback_data=f"roleconfig_close_{group_id}_{role['code_role']}"))
    markup.add(*list_markup)
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_main_{group_id}'))
    return markup

def InlineKeyboardMarkup_config_game(group_id): # دکمه های اصلی بخش تنظیم بازی
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['config_game_cultHunterExposeRole'],callback_data=f'gameconfig_hunterexposerole_{group_id}'), InlineKeyboardButton(dict_messages_main['config_game_cultHunterCountNightShow'],callback_data=f'gameconfig_huntercountnight_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_game_Voting_secretly'],callback_data=f'gameconfig_votingsecretly_{group_id}'), InlineKeyboardButton(dict_messages_main['config_game_CountSecretVoting'],callback_data=f'gameconfig_countsecretvoting_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_game_PlayerNameSecretVoting'],callback_data=f'gameconfig_PlayerNameSecretVoting_{group_id}'), InlineKeyboardButton(dict_messages_main['config_game_MuteDie'],callback_data=f'gameconfig_MuteDie_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_main_{group_id}'))
    return markup

def InlineKeyboardMarkup_config_group(group_id): # دکمه های اصلی بخش تنظیم گروه
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['config_group_gameMode'],callback_data=f'groupconfig_gameMode_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_group_ExposeRole'],callback_data=f'groupconfig_ExposeRole_{group_id}'), InlineKeyboardButton(dict_messages_main['config_group_ExposeRoleOn'],callback_data=f'groupconfig_ExposeRoleOn_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_group_Flee'],callback_data=f'groupconfig_Flee_{group_id}'), InlineKeyboardButton(dict_messages_main['config_group_Extend'],callback_data=f'groupconfig_Extend_{group_id}'))
    # markup.add(InlineKeyboardButton(dict_messages_main['config_group_Roles'],callback_data=f'groupconfig_Roles_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'],callback_data=f'backconfig_main_{group_id}'))
    return markup

def InlineKeyboardMarkup_config_block(group_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['list_block_users'], callback_data=f'blockconfig_list_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['new_blocked'], callback_data=f'blockconfig_new_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'backconfig_main_{group_id}'))
    return markup

def InlineKeyboardMarkup_config_main(group_id): # دکمه های اصلی تنظیمات
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['Config_time'], callback_data=f'config_time_{group_id}'),InlineKeyboardButton(dict_messages_main['config_roles'],callback_data=f'config_roles_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_games'], callback_data=f'config_games_{group_id}'),InlineKeyboardButton(dict_messages_main['config_group'],callback_data=f'config_group_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['user_block'], callback_data=f'config_block_{group_id}'))
    markup.add(InlineKeyboardButton(dict_messages_main['config_end'], callback_data=f'config_end_{group_id}'))
    return markup

def InlineKeyboardMarkup_main():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(dict_messages_main['webapp'], web_app=WebAppInfo(url='https://almaslink.ir/comming_soon/'))) 
    markup.add(KeyboardButton(dict_messages_main['dis_roles'], web_app=WebAppInfo(url='https://irweb.site/mafia_roles'))) 
    # markup.add('حساب کاربری 👤')
    # markup.add('فرشگاه 🛒', 'خرید سکه 💰')
    return markup

def InlineKeyboardMarkup_mainadmin():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['mng_roles'], callback_data="mngroles"))
    markup.add(InlineKeyboardButton(dict_messages_main['list_all_groups'], callback_data="listallgroups"))
    markup.add(InlineKeyboardButton(dict_messages_main['info_user_btn'], callback_data="mainadmin_infouser"))    
    return markup

def InlineKeyboardMarkup_edit_group(group_id):
    markup = InlineKeyboardMarkup()
    check_blocked_group = database.select_blocked_groups_by_group_id(group_id)
    if check_blocked_group:
        markup.add(InlineKeyboardButton(dict_messages_main['config_Unblock'], callback_data=f"mainadmin_Unblock_{group_id}"))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['config_Block'], callback_data=f"mainadmin_block_{group_id}"))

    check_sub = database.select_geoup_by_group_id(group_id)[0]
    if check_sub['subscription_type'] == 'free':
        markup.add(InlineKeyboardButton(dict_messages_main['groupfree'], callback_data=f"mainadmin_paid_{group_id}"))
    else:
        markup.add(InlineKeyboardButton(dict_messages_main['groupmoney'], callback_data=f"mainadmin_free_{group_id}")) 

    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f"mainadmin_backlistgroups"))
    return markup

def replykebord_communication_admin():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(dict_messages_main['support_btn'])
    return markup


def message_settings_role(role, cid, mid):
    dict_info_role = database.select_role_by_role(role)[0]
    markup = InlineKeyboardMarkup()
    if  dict_info_role['role_type'] == 'free':
        role_type = dict_messages_main['free']
        markup.add(InlineKeyboardButton(dict_messages_main['type'].format(role_type), callback_data=f"mainadmin_typerole_{role}_paid"))
    else:
        role_type = dict_messages_main['paid']
        markup.add(InlineKeyboardButton(dict_messages_main['type'].format(role_type), callback_data=f"mainadmin_typerole_{role}_free"))
   
    if  dict_info_role['role_status'] == 'on':
        role_status = dict_messages_main['onr']
        markup.add(InlineKeyboardButton(dict_messages_main['status'].format(role_status), callback_data=f"mainadmin_statusrole_{role}_off"))
    else:
        role_status = dict_messages_main['offr']
        markup.add(InlineKeyboardButton(dict_messages_main['status'].format(role_status), callback_data=f"mainadmin_statusrole_{role}_on"))
    text = dict_messages_main['info_role'].format(dict_info_role['role'],
                                                  dict_info_role['role_name'],
                                                  dict_info_role['role_grouping'],
                                                  int(dict_info_role['becoming_cult']*100),
                                                  role_type,
                                                  role_status)
    

    markup.add(InlineKeyboardButton(dict_messages_main['change_becoming_cult'], callback_data=f"mainadmin_becomingcult_{role}_{int(dict_info_role['becoming_cult']*100)}"))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data="mainadmin_backlistroles")) 
    edit_message_text(text, cid, mid, reply_markup=markup)


def message_becoming_cult(role, cid, mid, becoming_cult):
    dict_info_role = database.select_role_by_role(role)[0]
    print(dict_info_role)

    if  dict_info_role['role_type'] == 'free':
        role_type = dict_messages_main['free']
    else:
        role_type = dict_messages_main['paid']
   
    if  dict_info_role['role_status'] == 'on':
        role_status = dict_messages_main['onr']
    else:
        role_status = dict_messages_main['offr']

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['becoming_cult'], callback_data="mainadmin_none"))
    markup.add(InlineKeyboardButton("- 5", callback_data=f"mainadmin_changebecomcult_{role}_-5"), InlineKeyboardButton(becoming_cult, callback_data="mainadmin_none"), InlineKeyboardButton("+ 5", callback_data=f"mainadmin_changebecomcult_{role}_+5"))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f"mainadmin_role_{role}")) 
    text = dict_messages_main['info_role'].format(dict_info_role['role'],
                                                  dict_info_role['role_name'],
                                                  dict_info_role['role_grouping'],
                                                  int(dict_info_role['becoming_cult']*100),
                                                  role_type,
                                                  role_status)
    

    edit_message_text(text, cid, mid, reply_markup=markup)



def gen_markup_broadcast_timer(current_timer, forward):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Start Broadcasting', callback_data='BroadcastStart'), InlineKeyboardButton('Cancel', callback_data='BroadcastCancel'))
    if current_timer >= 48:
        markup.add(InlineKeyboardButton("Permanent post", callback_data='Broadcast3'))
    else:
        markup.add(InlineKeyboardButton('- 3', callback_data='Broadcast'+str(current_timer-3)),InlineKeyboardButton('+ 3', callback_data='Broadcast'+str(current_timer+3)))
        markup.add(InlineKeyboardButton(str(current_timer) + ' Hours post', callback_data='Broadcast100'))
    markup.add(InlineKeyboardButton(f"Forwarding: {'On' if forward else 'Off'}", callback_data='BroadcastForwardOff' if forward else 'BroadcastForwardOn'))
    return markup


def check_group_in_dict(group_id, m):
    if group_id not in group_dict:
        list_info = database.select_geoup_by_group_id(group_id)
        if list_info:
            dict_info = list_info[0]
            instance_group = Group(group_id, dict_info['title'], dict_info['username'], dict_info['cid_admin_added_bot'])
            group_dict.setdefault(group_id,instance_group)
        else:
            title = m.chat.title
            username = m.chat.username
            instance_group = Group(group_id, title, username, 0)
            database.insert_groups(group_id, title, username, 0)
            database.insert_group_settings(group_id)
            group_dict.setdefault(group_id,instance_group)
            print(group_dict)



#-------------------------------------------------------------------listener--------------------------------------------------------------
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        # print(m)
        if m.content_type == 'text':
            print(str(m.chat.first_name) +
                  " [" + str(m.chat.id) + "]: " + m.text)
        elif m.content_type == 'photo':
            print(str(m.chat.first_name) +
                  " [" + str(m.chat.id) + "]: " + "New photo recieved")
        elif m.content_type == 'document':
            print(str(m.chat.first_name) +
                  " [" + str(m.chat.id) + "]: " + 'New Document recieved')

bot.set_update_listener(listener)

#-------------------------------------------------------------------content_types--------------------------------------------------------------
@bot.message_handler(content_types='new_chat_members')
def handle_new_chat_members(m):
    group_id = m.chat.id
    for new_member in m.new_chat_members:
        if new_member.id == bot.get_me().id:
            if group_id not in group_dict:
                title = m.chat.title
                username = m.chat.username
                cid_admin_added_bot = m.from_user.id
                instance_group = Group(group_id, title, username, cid_admin_added_bot)
                database.insert_groups(group_id, title, username, cid_admin_added_bot)
                database.insert_group_settings(group_id)
                group_dict.setdefault(group_id,instance_group)
                print(group_dict)


@bot.message_handler(content_types='left_chat_member')
def handle_left_chat_member(m):
    left_member = m.left_chat_member
    if left_member.id == bot.get_me().id:
        group_id = m.chat.id


#------------------------------------------------------------------commends-----------------------------------------------------------
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if m.chat.type in ['private']:
        name = m.chat.first_name
        username = "@" + str(m.chat.username)
        if is_block(cid): 
            Message(dict_messages_main['msg_blocked_user'], Player(cid, name), replykebord_communication_admin()).send_message()
            return
        database.insert_users(cid, username, name)

        
        if m.text.endswith('start') == False:
            group_id = int(m.text.split(' ')[-1])
            if cid not in players_dict:
                check_blocked = database.select_blocked_users_from_group(cid, group_id)
                if check_blocked:
                    bot.send_message(cid, dict_messages_main['msg_user_blocked'])
                
                else:
                    name = m.chat.first_name
                    player = game_dict[group_dict[group_id]].add_playar(cid, name)
                    if player:
                        players_dict[cid] = player
                        print(players_dict)
            else:
                player = players_dict[cid]
                g_id = player.game.group.id
                if g_id == group_id:
                    Message(dict_messages_general['lastingame2'],player, InlineKeyboardMarkup_main()).send_message()
                    # bot.send_message(cid, dict_messages_general['lastingame2'], reply_markup=InlineKeyboardMarkup_main())
                else:
                    Message(dict_messages_general['LastInGame'],player, InlineKeyboardMarkup_main()).send_message()
                    # bot.send_message(cid, dict_messages_general['LastInGame'], reply_markup=InlineKeyboardMarkup_main())

        else:
            Message(dict_messages_main['StartBot'],Player(cid,name), InlineKeyboardMarkup_main()).send_message()
            if cid == master_cid:
                pass
            elif cid == main_admin:
                text = ''
                if cid == main_admin:
                    text += 'main command\n'
                    for command in main_command:
                        text += '/' + command + " : " + main_command[command] +"\n"

                Message(text, Player(cid, 'mainadmin')).send_message()
           

@bot.message_handler(commands=['help'])
def command_start(m):
    cid = m.chat.id
    if m.chat.type in ['private']:
        name = m.chat.first_name
        Message(dict_messages_main['help_bot'],Player(cid,name), InlineKeyboardMarkup_main()).send_message()

    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(dict_messages_main['open_robot'],url=f"https://t.me/{bot.get_me().username}"))
        Message(dict_messages_main['help_bot_group'],Player(cid,"name"), markup).send_message()

            

@bot.message_handler(commands=['robot_setting'])
def command_robot_setting(m):
    if m.chat.type in ['private']:
        cid = m.chat.id
        name = m.from_user.first_name
        if cid == main_admin:
            Message(dict_messages_main['msg_settings'], Player(cid,name), InlineKeyboardMarkup_mainadmin()).send_message()
            
        else:
            Message(dict_messages_main['Default_message'],Player(cid,name), InlineKeyboardMarkup_main()).send_message()


@bot.message_handler(commands=['startgame'])
def command_start_normalgame(m):
    if m.chat.type in ['group' , 'supergroup']:
        group_id = m.chat.id
        if is_group_block(group_id):
            Message(dict_messages_main['blocked_group'], Player(group_id, "group")).send_message()
            return
        check_group_in_dict(group_id, m)
        if group_dict[group_id] in game_dict:
            send_message(group_id,dict_messages_main['gameactive'])
            return
        cid = m.from_user.id
        name = m.from_user.first_name
        instance_settings = Settings(group_dict[group_id])
        instance_game = Game(group_dict[group_id],instance_settings,[],'normal')
        instance_settings.get_info_from_databade()
        
        game_dict[group_dict[group_id]] = instance_game
        instance_game.start()

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(dict_messages_general['joinToGame'],url=f"https://t.me/{bot.get_me().username}?start={group_id}"))
        message_start_game = Message(dict_messages_general['startAtGame_Normal'].format(f'[{name}](tg://user?id={cid})'),group_dict[group_id],markup, mid_for_copy=random.choice([140,142]))
        message_start_game.send_message()
        game_dict[group_dict[group_id]].add_message_start_game(message_start_game)

        message_list_player = Message('#players:\n',group_dict[group_id])
        message_list_player.send_message()
        # bot.pin_chat_message(group_id, message_list_player.message_id)
        game_dict[group_dict[group_id]].add_message_list_player(message_list_player)

    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()


@bot.message_handler(commands=['config'])
def command_config(m):
    if m.chat.type in ['group' , 'supergroup']:
        user_id = m.from_user.id
        group_id = m.chat.id
        check_group_in_dict(group_id, m)
        try:
            chat_member = bot.get_chat_member(group_id, user_id)
            status = chat_member.status
            if status in ['administrator', 'creator']:
                Message(dict_messages_main['whoconfig'],Player(user_id,m.chat.first_name),InlineKeyboardMarkup_config_main(group_id)).send_message()
                Message(dict_messages_main['ConfigSendPrvaite'],group_dict[group_id]).send_message(m.message_id)
                # Message(dict_messages_main['ConfigSendPrvaite'],group_dict[group_id]).reply_message(m)
            else:
                Message(dict_messages_main['YouNotAdminGp'],group_dict[group_id]).send_message(m.message_id)
                # Message(dict_messages_main['YouNotAdminGp'],group_dict[group_id]).reply_message(m)
        except Exception as e:
            logging.exception(f' Error in command_config Exception: ' + str(e))
            bot.send_message(master_cid, f'Warning: Error in command_config Exception: ' + str(e))


    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()


@bot.message_handler(commands=['extend'])
def command_config(m):
    if m.chat.type in ['group' , 'supergroup']:
        group_id = m.chat.id
        check_group_in_dict(group_id, m)
        if group_dict[group_id] in game_dict:
            user_id = m.from_user.id
            dict_settings = database.select_group_settings_by_group_id(group_id)[0]
            if game_dict[group_dict[group_id]].check_the_stage_to_extend_time():

                text = m.text
                if len(text.split(' ')) == 2 and text.split(' ')[1].replace('-','').isdigit():
                    time_for_extend = int(text.split(' ')[1])
                    if dict_settings['adding_time_by_player'] == 'inactive':
                        chat_member = bot.get_chat_member(group_id, user_id)
                        status = chat_member.status
                        if status in ['administrator', 'creator']:
                            print(time_for_extend)
                            extend_time = dict_settings['extra_time_to_vote']
                            if time_for_extend < 0:
                                game_dict[group_dict[group_id]].extend_time(time_for_extend)
                            elif time_for_extend > extend_time:
                                game_dict[group_dict[group_id]].extend_time(extend_time)
                            else:
                                game_dict[group_dict[group_id]].extend_time(time_for_extend)

                        else:
                            Message(dict_messages_main['AllowExtendForAdmin'],group_dict[group_id]).send_message()
                    else:
                        extend_time = dict_settings['extra_time_to_vote']
                        if time_for_extend < 0:
                            game_dict[group_dict[group_id]].extend_time(time_for_extend)
                        elif time_for_extend > extend_time:
                            game_dict[group_dict[group_id]].extend_time(extend_time)
                        else:
                            game_dict[group_dict[group_id]].extend_time(time_for_extend)
                else:
                    Message(dict_messages_main['incorrectextendtime'], group_dict[group_id]).send_message()
            else:
                Message(dict_messages_main['gamenotinmembership'], group_dict[group_id]).send_message()
        else:
            Message(dict_messages_general['GameNotCreate'],group_dict[group_id]).send_message()
    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()

@bot.message_handler(commands=['killgame'])
def command_config(m): 
    if m.chat.type in ['group' , 'supergroup']:
        group_id = m.chat.id
        user_id = m.from_user.id
        check_group_in_dict(group_id, m)
        chat_member = bot.get_chat_member(group_id, user_id)
        status = chat_member.status
        if status in ['administrator', 'creator']:
            if group_dict[group_id] in game_dict:
                list_players = game_dict[group_dict[group_id]].list_players()
                if len(list_players) > 0:
                    for player in list_players:
                        del players_dict[player.id]
                del game_dict[group_dict[group_id]]
                Message(dict_messages_main['KillGame'].format(f'[{m.from_user.first_name}](tg://user?id={user_id})'),group_dict[group_id]).send_message()
            else:
                Message(dict_messages_main['NotGameForKill'],group_dict[group_id]).send_message()
        else:
            Message(dict_messages_main['NotAllowForUser'],group_dict[group_id]).send_message()
    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()


@bot.message_handler(commands=['players'])
def command_config(m): 
    if m.chat.type in ['group' , 'supergroup']:
        group_id = m.chat.id
        user_id = m.from_user.id
        check_group_in_dict(group_id, m)
        if group_dict[group_id] in game_dict:
            instans_game = game_dict[group_dict[group_id]]
            message_list_player_id = instans_game.return_message_list_player().message_id
            Message(dict_messages_general['playerList'], group_dict[group_id]).send_message(message_list_player_id)
        else:
            Message(dict_messages_main['NotGameForplayers'],group_dict[group_id]).send_message()
    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()

@bot.message_handler(commands=['flee'])
def command_config(m): 
    if m.chat.type in ['group' , 'supergroup']:
        mid = m.message_id
        group_id = m.chat.id
        user_id = m.from_user.id
        check_group_in_dict(group_id, m)
        if group_dict[group_id] in game_dict:
            if game_dict[group_dict[group_id]].flee_player(user_id):
                del players_dict[user_id]
            else:
                Message(dict_messages_main['NotAllowFleeInGame'],group_dict[group_id]).send_message(mid)
        else:
            Message(dict_messages_main['NotGameForflee'],group_dict[group_id]).send_message(mid)
    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()


@bot.message_handler(commands=['smite'])
def command_config(m): 
    if m.chat.type in ['group' , 'supergroup']:
        group_id = m.chat.id
        user_id = m.from_user.id
        check_group_in_dict(group_id, m)
        chat_member = bot.get_chat_member(group_id, user_id)
        status = chat_member.status
        if status in ['administrator', 'creator']:
            if group_dict[group_id] in game_dict:
                list_players = game_dict[group_dict[group_id]].list_players()
                list_players_alive = []
                for player in list_players:
                    if player.alive:
                        list_players_alive.append(player)

                if len(list_players_alive) > 0:
                    markup = InlineKeyboardMarkup()
                    for player in list_players_alive:
                        markup.add(InlineKeyboardButton(str(player.name), callback_data=f"smite_{player.id}"))
                    markup.add(InlineKeyboardButton(dict_messages_main['cancele_ok'], callback_data="smite_cancel"))

                    Message(dict_messages_main['messagesmite'], group_dict[group_id], markup).send_message()
                else:
                    Message(dict_messages_main['ziroplayerforsmite'], group_dict[group_id]).send_message()

            else:
                Message(dict_messages_main['NotGameForsmite'],group_dict[group_id]).send_message()
        else:
            Message(dict_messages_main['NotAllowForUser'],group_dict[group_id]).send_message()
    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()

@bot.message_handler(commands=['chatid'])
def command_config(m): 
    if m.chat.type in ['group' , 'supergroup']:
        mid = m.message_id
        group_id = m.chat.id
        check_group_in_dict(group_id, m)
        Message(f'**{group_id}**',group_dict[group_id]).send_message(mid)
    else:
        cid = m.chat.id
        name = m.from_user.first_name
        Message(dict_messages_main['SendToGroup'],Player(cid,name)).send_message()

#---------------------------------------------------------callback_main_admin---------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("listallgroups") and call.message.chat.id == main_admin)
def callback_list_all_groups(call):
    cid = call.message.chat.id
    mid=call.message.message_id
    list_dict_groups = database.select_all_GroupsTable()
    if len(list_dict_groups) == 0:
        bot.answer_callback_query(call.id, dict_messages_main['answer_none_group'])
        return
    
    markup = InlineKeyboardMarkup()
    for group in list_dict_groups:
        markup.add(InlineKeyboardButton(str(group['title']), callback_data=f"mainadmin_group_{group['group_id']}"))
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data="mainadmin_back"))
    edit_message_text(dict_messages_main['settings_group'], cid, mid, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("mngroles") and call.message.chat.id == main_admin)
def list_all_roles(call):
    cid = call.message.chat.id
    mid=call.message.message_id 
    markup = InlineKeyboardMarkup(row_width=2)
    list_roles = database.select_all_roles()
    list_markup = []
    for role in list_roles:
        list_markup.append(InlineKeyboardButton(role['role_name'], callback_data=f"mainadmin_role_{role['role']}"))
    markup.add(*list_markup)
    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data="mainadmin_back"))
    edit_message_text(dict_messages_main['setting_role'], cid, mid, reply_markup=markup)




@bot.callback_query_handler(func=lambda call: call.data.startswith("mainadmin") and call.message.chat.id == main_admin)
def callback_mainadmin(call):
    cid = call.message.chat.id
    mid=call.message.message_id
    data=call.data.split("_")
    if data[1] == "back":
        edit_message_text(dict_messages_main['msg_settings'], cid, mid, reply_markup=InlineKeyboardMarkup_mainadmin())

    elif data[1] == "backlistgroups":
        callback_list_all_groups(call)

    elif data[1] == "backlistroles":
        list_all_roles(call)
    
    elif data[1] == 'group':
        group_id = int(data[2])
        dict_group = database.select_geoup_by_group_id(group_id)[0]
        edit_message_text(dict_messages_main['show_details_group'].format(dict_group['title'], dict_group['username'], dict_group['number_of_game']), cid, mid, reply_markup=InlineKeyboardMarkup_edit_group(group_id))
        
    elif data[1] == "block":
        group_id = int(data[2])
        database.insert_blocked_groups(group_id)
        bot.answer_callback_query(call.id, dict_messages_main['msg_block_group'])
        edit_message_reply_markup(cid, mid, reply_markup=InlineKeyboardMarkup_edit_group(group_id))

    elif data[1] == "Unblock":
        group_id = int(data[2])
        database.delete_row_blocked_groups(group_id)
        bot.answer_callback_query(call.id, dict_messages_main['msg_unblock_group'])
        edit_message_reply_markup(cid, mid, reply_markup=InlineKeyboardMarkup_edit_group(group_id))

    elif data[1] == 'paid':
        group_id = int(data[2])
        database.update_GroupsTable('subscription_type', 'paid', group_id)
        bot.answer_callback_query(call.id, dict_messages_main['msg_money_group'])
        edit_message_reply_markup(cid, mid, reply_markup=InlineKeyboardMarkup_edit_group(group_id))

    elif data[1] == 'free':
        group_id = int(data[2])
        database.update_GroupsTable('subscription_type', 'free', group_id)
        bot.answer_callback_query(call.id, dict_messages_main['msg_free_group'])
        edit_message_reply_markup(cid, mid, reply_markup=InlineKeyboardMarkup_edit_group(group_id))


    elif data[1] == 'infouser':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(dict_messages_main['cancel'], callback_data="mainadmin_cancel"))
        edit_message_text(dict_messages_main['msg_info_user'], cid, mid, reply_markup= markup)
        userStep[cid] = 1

    elif data[1] == 'blockuser':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(dict_messages_main['user_unblock'], callback_data=f"mainadmin_unblockuser_{data[2]}"))
        bot.answer_callback_query(call.id, dict_messages_main['ok_block_user'])
        database.insert_blocked_users(int(data[2]))
        edit_message_reply_markup(cid, mid, reply_markup=markup)

    elif data[1] == 'unblockuser':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(dict_messages_main['user_block'], callback_data=f"mainadmin_blockuser_{data[2]}"))
        bot.answer_callback_query(call.id, dict_messages_main['ok_unblock_user'])
        database.insert_blocked_users(int(data[2]))
        edit_message_reply_markup(cid, mid, reply_markup=markup)


    elif data[1] == 'answer':
        userStep[cid] = 3
        dict_mid_for_answer.setdefault(cid,[])
        dict_mid_for_answer[cid] = [int(data[3]), int(data[2])]
        bot.delete_message(cid, mid)
        Message(dict_messages_main['send_answer'], Player(cid,'mainadmin')).send_message()

    elif data[1] == 'cancel':
        # Message()
        userStep[cid] = 0
        bot.delete_message(cid, mid)
        Message(dict_messages_main['msg_settings'], Player(cid,'mainadmin'), InlineKeyboardMarkup_mainadmin()).send_message()

    elif data[1] == 'role':
        role = data[2]
        message_settings_role(role, cid, mid)
    
    elif data[1] == 'typerole':
        role_type = data[3]
        role = data[2]
        database.update_roles('role_type', role_type, role)
        message_settings_role(role, cid, mid)

    elif data[1] == 'statusrole':
        role_status = data[3]
        role = data[2]
        database.update_roles('role_status', role_status, role)
        message_settings_role(role, cid, mid)

    elif data[1] == 'becomingcult':
        role = data[2]
        becoming_cult = data[3]
        message_becoming_cult(role, cid, mid, becoming_cult)

    elif data[1] == 'changebecomcult':
        role = data[2]
        becoming_cult = int(data[3])
        print('becoming_cult',becoming_cult)
        dict_info_role = database.select_role_by_role(role)[0]
        if dict_info_role['becoming_cult'] == 0:
            bot.answer_callback_query(call.id, dict_messages_main['min_becoming_cult'])
        elif int(dict_info_role['becoming_cult']*100) == 100:
            bot.answer_callback_query(call.id, dict_messages_main['max_becoming_cult'])
        else:
            new_becoming_cult = (dict_info_role['becoming_cult']*100) + becoming_cult
            print(new_becoming_cult)
            database.update_roles('becoming_cult', new_becoming_cult/100, role)
            message_becoming_cult(role, cid, mid, int(new_becoming_cult))








    elif data[1] == 'none':
        bot.answer_callback_query(call.id, dict_messages_main['becoming_cult'])


#-----------------------------------------------------callback---------------------------------------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("target"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    data=call.data.split("_")
    mid=call.message.message_id

    if data[1] == 'night':
        id_target = int(data[2])
        name_target = data[3]
        instans_player = players_dict[cid]
        instans_player.set_target(id_target)
        list_team = game_dict[group_dict[players_dict[cid].game.group.id]].get_teammates(players_dict[cid])
        if list_team:
            for player in list_team:
                if player.id != cid:
                    if player.grouping == 'wolf' and player.role not in ['enchanter','WolfJadogar']:
                        if instans_player.role == 'WhiteWolf':
                            text = dict_messages_general['msg_wolf_white'].format(create_tag(instans_player), create_tag(instans_player.target))
                            Message(text, player).send_message()             
                        else:
                            text = dict_messages_general['eatUser'].format(create_tag(instans_player), create_tag(instans_player.target))
                            Message(text, player).send_message()
                    elif player.grouping == 'cult':
                        if instans_player.role == 'Franc':
                            text = dict_messages_general['save_franc'].format(create_tag(instans_player), create_tag(instans_player.target))
                            Message(text, player).send_message()
                        else:
                            text = dict_messages_general['CultistVotedConvert'].format(create_tag(instans_player), create_tag(instans_player.target))
                            Message(text, player).send_message()


        bot.edit_message_text(dict_messages_general['SelectOk'].format(name_target), cid, mid)
    
    elif data[1] == 'day':
        if data[2] == 'Solh':
            instans_player = players_dict[cid]
            instans_game = instans_player.game
            instans_game.cancel_of_voting(instans_player)
            bot.edit_message_text(dict_messages_main['cancel_voting'], cid, mid)

        elif data[2] == 'ahangar':
            instans_player = players_dict[cid]
            instans_game = instans_player.game
            instans_game.silver_spread(instans_player)
            bot.edit_message_text(dict_messages_main['cancel_wolf_attak'], cid, mid)

        elif data[2] == 'voteagain':
            instans_player = players_dict[cid]
            instans_game = instans_player.game
            instans_game.def_vote_again(instans_player)
            bot.edit_message_text(dict_messages_main['vote_again'], cid, mid)


        elif data[2] == 'notify':
            instans_player = players_dict[cid]
            instans_game = instans_player.game
            instans_game.declaring_role_kadkhoda(instans_player)
            bot.edit_message_text(dict_messages_main['msg_notify'], cid, mid)

        elif data[2] == 'voteruler':
            instans_player = players_dict[cid]
            instans_game = instans_player.game
            instans_game.vote_ruler(instans_player)
            bot.edit_message_text(dict_messages_main['msg_voteruler'], cid, mid)

        elif data[2] == 'KhabGozar':
            instans_player = players_dict[cid]
            instans_game = instans_player.game
            instans_game.cancel_night(instans_player)
            bot.edit_message_text(dict_messages_main['msg_cancel_night'], cid, mid)

        elif data[2] == 'no':
            bot.delete_message(cid, mid)

        else:
            id_target = int(data[2])
            instans_player = players_dict[cid]
            name_target = data[3]
            instans_game = instans_player.game
            if instans_player.role == 'tofangdar':
                game_check = instans_game.shot_tofangdar(instans_player,id_target)
                print(game_check)
                if game_check == 'end game':
                    list_players = instans_game.players
                    if len(list_players) > 0:
                        for player in list_players:
                            if player.id in players_dict:
                                del players_dict[player.id]
                    del game_dict[group_dict[instans_game.group.id]]
            
            elif instans_player.role == 'kentvampire':
                game_check = instans_game.shot_kentvampire(instans_player,players_dict[id_target])
                print(game_check)
                if game_check == 'end game':
                    list_players = instans_game.players
                    if len(list_players) > 0:
                        for player in list_players:
                            if player.id in players_dict:
                                del players_dict[player.id]
                    del game_dict[group_dict[instans_game.group.id]]


            bot.edit_message_text(dict_messages_general['SelectOk'].format(name_target), cid, mid)

    elif data[1] == 'second':
        id_target = int(data[2])
        name_target = data[3]
        instans_player = players_dict[cid]
        instans_target = players_dict[id_target]

        instans_player.set_second_target(instans_target)
        bot.edit_message_text(dict_messages_general['SelectOk'].format(name_target), cid, mid)

# @bot.callback_query_handler(func=lambda call: call.data.startswith("targetday"))
# def edite_infi_cust(call):
#     cid = call.message.chat.id
#     data=call.data.split("_")
#     mid=call.message.message_id
#     id_target = int(data[2])
#     name_target = data[3]
#     instans_player = players_dict[cid]
#     instans_player.set_target(id_target)

#     list_team = game_dict[group_dict[players_dict[cid].game.group.id]].get_teammates(players_dict[cid])
#     bot.edit_message_text(dict_messages_general['SelectOk'].format(name_target), cid, mid)
@bot.callback_query_handler(func=lambda call: call.data.startswith("rulervoting"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    data=call.data.split("_")
    mid=call.message.message_id
    id_vote = int(data[1])
    name_vote = data[2]

    instans_player = players_dict[cid]
    instans_player.set_vote(id_vote)

    Message(dict_messages_general['RulerVoteMessage'].format(create_tag(instans_player),create_tag(instans_player.vote)), group_dict[instans_player.game.group.id]).send_message()
    bot.edit_message_text(dict_messages_general['SelectOk'].format(create_tag(instans_player.vote)), cid, mid, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith("voting"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    data=call.data.split("_")
    mid=call.message.message_id
    id_vote = int(data[1])
    name_vote = data[2]

    instans_player = players_dict[cid]
    instans_player.set_vote(id_vote)

    instans_info_database = instans_player.game.settings
    print(instans_info_database.voting_secret)
    if instans_info_database.voting_secret == 'active':
        if instans_info_database.number_vote_voting_secret == 'active':
            number_players_voted = 0
            for player in instans_player.game.players:
                if player.vote != None:
                    number_players_voted += 1
            Message(dict_messages_main['voteusersecret'].format(number_players_voted, len(instans_player.game.players)), group_dict[instans_player.game.group.id]).send_message()
    else:
        Message(dict_messages_general['voteUser'].format(create_tag(instans_player),create_tag(instans_player.vote)), group_dict[instans_player.game.group.id]).send_message()

    bot.edit_message_text(dict_messages_general['SelectOk'].format(create_tag(instans_player.vote)), cid, mid, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith("loving"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    data=call.data.split("_")
    mid=call.message.message_id
    id_vote = int(data[1])
    name_vote = data[2]    
    instans_player = players_dict[cid]
    lover = players_dict[id_vote]
    instans_game = instans_player.game
    instans_game.choice_lover(instans_player, lover)
    # bot.edit_message_text(dict_messages_general['SelectOk'].format(create_tag(lover)), cid, mid, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith("pattern"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    data=call.data.split("_")
    mid=call.message.message_id
    id_vote = int(data[1])
    name_vote = data[2]
    
    instans_player = players_dict[cid]
    pattern = players_dict[id_vote]
    instans_player.choice_pattern(pattern)
    bot.edit_message_text(dict_messages_general['SelectOk'].format(create_tag(pattern)), cid, mid, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith("fire"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    mid=call.message.message_id        
    instans_player = players_dict[cid]
    instans_player.order_to_fire()
    bot.edit_message_text(dict_messages_general['ordertofire'], cid, mid)



@bot.callback_query_handler(func=lambda call: call.data.startswith("config"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    group_id = int(data[2])

    if type_callback == 'time':
        # Message('ادیت',Player(cid, name)).edit_message_reply_markup()
        edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_time(group_id))

    elif type_callback == 'roles':
        edit_message_text(dict_messages_main['msg_for_manag_roles'], cid, mid, reply_markup=InlineKeyboardMarkup_config_roles(group_id))
        # edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_roles(group_id))

    elif type_callback == 'games':
        edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_game(group_id))

    elif type_callback == 'group':
        edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_group(group_id))

    elif type_callback == 'block':
        bot.edit_message_reply_markup(cid, mid, reply_markup=InlineKeyboardMarkup_config_block(group_id))

    elif type_callback == 'end':
        edit_message_text(dict_messages_main['endedconfig'], cid,mid)




@bot.callback_query_handler(func=lambda call: call.data.startswith("blockconfig")) # بلاک کردن کاربر گروه توسط ادمین گروه
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    group_id = int(data[2])
    dict_database = database.select_group_settings_by_group_id(group_id)[0]
    if type_callback == 'list':
        list_block = database.select_blocked_users_from_group_by_groupid(group_id)
        if list_block:
            markup = InlineKeyboardMarkup()
            for user in list_block:
                dict_info_user = database.select_users_by_cid(user['cid'])[0]
                markup.add(InlineKeyboardButton(dict_info_user['name'], callback_data=f'blockconfig_unblock_{group_id}_{user["cid"]}'))
            markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{group_id}'))
            bot.edit_message_text(dict_messages_main['msg_block_user'],cid, mid, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, dict_messages_main['ans_no_block'])

    elif type_callback == 'new':
        userStep[cid] = 4
        dict_admin_group.setdefault(cid, 0)
        dict_admin_group[cid] = group_id
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{group_id}'))
        bot.edit_message_text(dict_messages_main['msg_for_block_user_group'], cid, mid, reply_markup = markup)

    elif type_callback == 'unblock':
        bot.answer_callback_query(call.id, dict_messages_main['user_group_unblocked'])


        uid = int(data[3])
        database.delete_blocked_users_from_group(group_id, uid)

        list_block = database.select_blocked_users_from_group_by_groupid(group_id)
        if list_block:
            markup = InlineKeyboardMarkup()
            for user in list_block:
                dict_info_user = database.select_users_by_cid(user['cid'])[0]
                markup.add(InlineKeyboardButton(dict_info_user['name'], callback_data=f'blockconfig_unblock_{group_id}_{user["cid"]}'))
            markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{group_id}'))
            bot.edit_message_text(dict_messages_main['msg_block_user'],cid, mid, reply_markup=markup)
        else:
            bot.edit_message_text(dict_messages_main['whoconfig'], cid, mid, reply_markup=InlineKeyboardMarkup_config_block(group_id))
            # bot.answer_callback_query(call.id, dict_messages_main['ans_no_block'])


    elif type_callback == 'back':
        userStep[cid] = 0
        bot.edit_message_text(dict_messages_main['whoconfig'], cid, mid, reply_markup=InlineKeyboardMarkup_config_block(group_id))

 


@bot.callback_query_handler(func=lambda call: call.data.startswith("timeconfig")) # نمایش زمان ها بر اساس تایپ انتخاب شده
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    group_id = int(data[2])
    dict_database = database.select_group_settings_by_group_id(group_id)[0]
    if type_callback == 'NightTimer':
        # edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, dict_database['nitht_time'] ,group_id))
        edit_message_text(dict_messages_main['timeNightTimer'], chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, dict_database['nitht_time'] ,group_id))  
    
    elif type_callback == 'daytimer':
        edit_message_text(dict_messages_main['timeDayFaq'], chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, dict_database['day_time'] ,group_id)) 

    elif type_callback == 'votingtimer':
        edit_message_text(dict_messages_main['lynchTimerFq'], chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, dict_database['voting_time'] ,group_id)) 
   
    elif type_callback == 'jointimer':
        edit_message_text(dict_messages_main['timeJoinTimer'], chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, dict_database['time_to_join'] ,group_id)) 

    elif type_callback == 'extendtimer':
        edit_message_text(dict_messages_main['maxTimesetting'], chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, dict_database['extra_time_to_vote'] ,group_id)) 

@bot.callback_query_handler(func=lambda call: call.data.startswith("choossetime")) # انتخاب زمان مورد نظر
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    time_selected = int(data[2])
    group_id = int(data[3])

    if type_callback == 'NightTimer':
        database.update_group_settings('nitht_time', time_selected, group_id)
        # edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, time_selected, group_id))

    elif type_callback == 'daytimer':
        database.update_group_settings('day_time', time_selected, group_id)
        # edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, time_selected, group_id))

    elif type_callback == 'votingtimer':
        database.update_group_settings('voting_time', time_selected, group_id)
        # edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, time_selected, group_id))

    elif type_callback == 'jointimer':
        database.update_group_settings('time_to_join', time_selected, group_id)
        # edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, time_selected, group_id))

    elif type_callback == 'extendtimer':
        database.update_group_settings('extra_time_to_vote', time_selected, group_id)
        # edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, time_selected, group_id))

    edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=show_number_for_time_config(type_callback, time_selected, group_id))



@bot.callback_query_handler(func=lambda call: call.data.startswith("roleconfig")) # تنظیم نقش ها برای فعال بودن یا نبودن
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    group_id = int(data[2])
    role_code = int(data[3])
    if type_callback == 'close':
        database.insert_closed_roles_for_groups(group_id, role_code)
        edit_message_reply_markup(cid, mid, reply_markup=InlineKeyboardMarkup_config_roles(group_id))
        bot.answer_callback_query(call.id, dict_messages_main['closed_role'])


    elif type_callback == 'open':
        database.delete_closed_roles_for_groups_by_group_id(group_id, role_code)
        edit_message_reply_markup(cid, mid, reply_markup=InlineKeyboardMarkup_config_roles(group_id))
        bot.answer_callback_query(call.id, dict_messages_main['open_role'])

    elif type_callback == 'paid':
        bot.answer_callback_query(call.id, dict_messages_main['msg_paid_role'])

    





@bot.callback_query_handler(func=lambda call: call.data.startswith("gameconfig")) # تنظیم بازی
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    group_id = int(data[2])
    dict_database = database.select_group_settings_by_group_id(group_id)[0]

    if type_callback == 'hunterexposerole':
        edit_message_text(dict_messages_main['Hunting_shekar'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['expose_shekar'] ,group_id))

    elif type_callback == 'huntercountnight':
        edit_message_text(dict_messages_main['Hunting_shekar_day'], chat_id=cid, message_id=mid, reply_markup=choose_the_number_of_hunter_save_days(type_callback, dict_database['expose_shekar_day'] ,group_id))

    elif type_callback == 'votingsecretly':
        edit_message_text(dict_messages_main['SecretVoteEnable'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['voting_secret'] ,group_id))

    elif type_callback == 'countsecretvoting':
        edit_message_text(dict_messages_main['type_hide_vote_end'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['number_vote_voting_secret'] ,group_id))

    elif type_callback == 'PlayerNameSecretVoting':
        edit_message_text(dict_messages_main['type_hide_vote_show_userName'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['name_vote_voting_secret'] ,group_id))

    elif type_callback == 'MuteDie':
        edit_message_text(dict_messages_main['MuteDieConfig'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['silence_after_deeth'] ,group_id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("groupconfig")) # تنظیم گروپ
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    group_id = int(data[2])
    dict_database = database.select_group_settings_by_group_id(group_id)[0]

    if type_callback == 'gameMode':
        edit_message_text(dict_messages_main['chnageGameMode'], chat_id=cid, message_id=mid, reply_markup=choose_game_mode(type_callback, dict_database['type_game'] ,group_id))

    elif type_callback == 'ExposeRole':
        edit_message_text(dict_messages_main['HowToshowRol'], chat_id=cid, message_id=mid, reply_markup=choose_show_roles_end_game(type_callback, dict_database['show_role_end_game'] ,group_id))

    elif type_callback == 'ExposeRoleOn':
        edit_message_text(dict_messages_main['efshaNaqshSetting'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['show_role_after_deeth'] ,group_id))

    elif type_callback == 'Flee':
        edit_message_text(dict_messages_main['allowFleeAtGame'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['escape_player'] ,group_id))

    elif type_callback == 'Extend':
        edit_message_text(dict_messages_main['extendForPlayer'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['adding_time_by_player'] ,group_id))

    # elif type_callback == 'Roles':
    #     edit_message_text(dict_messages_main['Roles'], chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, dict_database['manege_roles'] ,group_id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("choosegamemode")) # انتخاب مود بازی 
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    mode_selected = data[2]
    group_id = int(data[3])

    database.update_group_settings('type_game', mode_selected, group_id)
    edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=choose_game_mode(type_callback, mode_selected ,group_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith("chooseshowroles")) # انتخاب حالت نمایش نقش ها در انتهای بازی
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    mode_selected = data[2]
    group_id = int(data[3])

    database.update_group_settings('show_role_end_game', mode_selected, group_id)
    edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=choose_show_roles_end_game(type_callback, mode_selected ,group_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith("huntersavedays")) # انتخاب تعداد روز سیو شکارچی در بازی
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    daye_selected = int(data[2])
    group_id = int(data[3])

    database.update_group_settings('expose_shekar_day', daye_selected, group_id)
    edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=choose_the_number_of_hunter_save_days(type_callback, daye_selected ,group_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith("activeorinactive")) # انتخاب حالت مورد نظر
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    mode_selected = data[2]
    group_id = int(data[3])

    # تنظیمات بخش نقش ها
    # if type_callback == 'fool':
    #     database.update_group_settings('role_fool', mode_selected, group_id)

    # elif type_callback == 'hypocrite':
    #     database.update_group_settings('role_monafeq', mode_selected, group_id)

    # elif type_callback == 'cult':
    #     database.update_group_settings('role_cult', mode_selected, group_id)

    # elif type_callback == 'Lucifer':
    #     database.update_group_settings('role_lucifer', mode_selected, group_id)


    # تنظیمات بخش گیم
    if type_callback == 'hunterexposerole':
        database.update_group_settings('expose_shekar', mode_selected, group_id)

    elif type_callback == 'huntercountnight':
        database.update_group_settings('expose_shekar_day', mode_selected, group_id)

    elif type_callback == 'votingsecretly':
        database.update_group_settings('voting_secret', mode_selected, group_id)

    elif type_callback == 'countsecretvoting':
        database.update_group_settings('number_vote_voting_secret', mode_selected, group_id)

    elif type_callback == 'PlayerNameSecretVoting':
        database.update_group_settings('name_vote_voting_secret', mode_selected, group_id)

    elif type_callback == 'MuteDie':
        database.update_group_settings('silence_after_deeth', mode_selected, group_id)


    # تنظیم بخش گروه
    elif type_callback == 'ExposeRoleOn':
        database.update_group_settings('show_role_after_deeth', mode_selected, group_id)
    elif type_callback == 'Flee':
        database.update_group_settings('escape_player', mode_selected, group_id)
    elif type_callback == 'Extend':
        database.update_group_settings('adding_time_by_player', mode_selected, group_id)
    # elif type_callback == 'Roles':
    #     database.update_group_settings('manege_roles', mode_selected, group_id)
    edit_message_reply_markup(chat_id=cid, message_id=mid, reply_markup=active_or_inactive(type_callback, mode_selected ,group_id))



@bot.callback_query_handler(func=lambda call: call.data.startswith("smite"))
def edite_infi_cust(call):
    group_id = call.message.chat.id
    cid = call.from_user.id
    mid=call.message.message_id
    data=call.data.split("_")
    

    chat_member = bot.get_chat_member(group_id, cid)
    status = chat_member.status
    if status in ['administrator', 'creator']:
        if data[1] == 'cancel':
            bot.delete_message(group_id,mid)
            return
        uid = int(data[1])
        if uid in players_dict:
            bot.edit_message_text(dict_messages_main['smite_user_ok'].format(create_tag(players_dict[uid])), group_id, mid, parse_mode='Markdown')
            instans_game = game_dict[group_dict[group_id]]
            check_end_game = instans_game.fired_player(players_dict[uid])
            if check_end_game == 'end game':
                list_players = instans_game.players
                if len(list_players) > 0:
                    for player in list_players:
                        if player.id in players_dict:
                            del players_dict[player.id]
                del game_dict[instans_game.group.id]
            else:
                del players_dict[uid]
        else:
            bot.answer_callback_query(call.id, dict_messages_main['already_canceled'])
            # Message(dict_messages_main['already_canceled'], group_dict[group_id]).send_message()
    else:
        bot.answer_callback_query(call.id, dict_messages_main['NotAllowForUser'])
        # Message(dict_messages_main['NotAllowForUser'], group_dict[group_id]).send_message()




@bot.callback_query_handler(func=lambda call: call.data.startswith("backconfig"))
def edite_infi_cust(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    type_callback = data[1]
    
    print(data)
    if type_callback == 'main':  # برگشت به صفحه اول
        group_id = int(data[2])
        edit_message_text(dict_messages_main['whoconfig'], cid, mid, reply_markup=InlineKeyboardMarkup_config_main(group_id))

    elif type_callback in ['NightTimer', 'daytimer', 'votingtimer', 'jointimer', 'extendtimer']: # برگشت به صفحه تنظیمات تایم
        group_id = int(data[2])
        edit_message_text(dict_messages_main['whoconfig'], chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_time(group_id))

    # elif type_callback in ['fool', 'hypocrite', 'cult', 'Lucifer']: # برگشت به صفحه تنظیمات نقش
    #     group_id = int(data[2])
    #     edit_message_text(dict_messages_main['whoconfig'], chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_roles(group_id))

    elif type_callback in ['hunterexposerole', 'huntercountnight', 'votingsecretly', 'countsecretvoting', 'PlayerNameSecretVoting', 'MuteDie']: # برگشت به صفحه تنظیمات گیم
        group_id = int(data[2])
        edit_message_text(dict_messages_main['whoconfig'], chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_game(group_id))

    elif type_callback in ['gameMode','ExposeRole', 'ExposeRoleOn', 'Flee', 'Extend']: # برگشت به صفحه تنظیمات گیم
        group_id = int(data[2])
        edit_message_text(dict_messages_main['whoconfig'], chat_id=cid, message_id=mid, reply_markup=InlineKeyboardMarkup_config_group(group_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith("all_role"))
def edit_all_role(call):
    cid = call.message.chat.id
    name = call.message.chat.first_name
    mid=call.message.message_id
    data=call.data.split("_")
    group_id = int(data[3])

    instans_game = game_dict[group_dict[group_id]]
    dict_all_role = {}

#---------------------------------------------------------------text--------------------------------------------------
@bot.message_handler(func=lambda m: m.text == dict_messages_main['support_btn'])
def support(m):
    cid = m.chat.id
    name = m.chat.first_name
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(dict_messages_main['cancel'])
    userStep[cid] = 2
    Message(dict_messages_main['support_msg'], Player(cid, name), markup).send_message()

@bot.message_handler(func=lambda m: m.text == dict_messages_main['cancel'])
def support(m):
    cid = m.chat.id
    name = m.chat.first_name



#----------------------------------------------------------------user step--------------------------------------------------------
@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 1)
def get_msg(m):
    cid = m.chat.id
    if m.forward_from:
        uid = m.forward_from.id
        list_dict_info_user = database.select_users_by_cid(uid)
        if list_dict_info_user:
            dict_info = list_dict_info_user[0]
            markup = InlineKeyboardMarkup()
            check_blocked = database.select_blocked_users_by_cid(uid)
            if check_blocked:
                markup.add(InlineKeyboardButton(dict_messages_main['user_unblock'], callback_data=f"mainadmin_unblockuser_{dict_info['cid']}"))
            else:
                markup.add(InlineKeyboardButton(dict_messages_main['user_block'], callback_data=f"mainadmin_blockuser_{dict_info['cid']}"))
            Message(dict_messages_main['info_user'].format(
                dict_info['username'],
                dict_info['name'],
                dict_info['cid'],
                dict_info['nickname'],
                dict_info['emoji'],
                dict_info['inventory'],
                dict_info['XP'],
                dict_info['power_soul']
            ), Player(cid, 'mainadmin'), markup).send_message()
        else:
            Message(dict_messages_main['no_user_by_cid'], Player(cid, 'mainadmin')).send_message()

    else:
        text = m.text
        if text[0] == '@':
            list_dict_info_user = database.select_users_by_username(text)
            if list_dict_info_user:
                dict_info = list_dict_info_user[0]
                markup = InlineKeyboardMarkup()
                check_blocked = database.select_blocked_users_by_cid(dict_info['cid'])
                if check_blocked:
                    markup.add(InlineKeyboardButton(dict_messages_main['user_unblock'], callback_data=f"mainadmin_unblockuser_{dict_info['cid']}"))
                else:
                    markup.add(InlineKeyboardButton(dict_messages_main['user_block'], callback_data=f"mainadmin_blockuser_{dict_info['cid']}"))
                Message(dict_messages_main['info_user'].format(
                    dict_info['username'],
                    dict_info['name'],
                    dict_info['cid'],
                    dict_info['nickname'],
                    dict_info['emoji'],
                    dict_info['inventory'],
                    dict_info['XP'],
                    dict_info['power_soul']
                ), Player(cid, 'mainadmin'), markup).send_message()
            else:
                Message(dict_messages_main['no_user_by_username'], Player(cid, 'mainadmin')).send_message()
        else:
            Message(dict_messages_main['notcorect_format'], Player(cid, 'mainadmin')).send_message()
            


@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 2)
def get_msg(m):
    cid = m.chat.id
    name = m.chat.first_name
    text = m.text
    mid = m.message_id
    check_username = m.chat.username
    if check_username:
        username = "@" + check_username
    else:
        username = check_username
    msg = bot.forward_message(main_admin, cid, mid)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(dict_messages_main['answer_for_user'], callback_data=f"mainadmin_answer_{msg.message_id}_{cid}"))
    if msg.forward_from:
        Message(dict_messages_main['send_msg_for_admim_for'].format(username,name,cid,text), Player(main_admin, 'mainadmin'), markup).send_message(msg.message_id)
    else:
        Message(dict_messages_main['send_msg_for_admin'].format(username,name,cid,text), Player(main_admin, 'mainadmin'), markup).send_message(msg.message_id)

    # bot.reply_to(msg, dict_messages_main['send_msg_for_admin'].format(username,name,cid,text))
    
    Message(dict_messages_main['ok_send_msg_for_admin'], Player(cid, 'mainadmin')).send_message(msg.message_id)


@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 3)
def get_msg(m):
    cid = m.chat.id
    name = m.chat.first_name
    text = m.text
    userStep[cid] = 0

    if m.reply_to_message:
        mid = m.message_id
        text = m.text 
        uid = m.json['reply_to_message']['forward_from']['id']
        umid = m.reply_to_message.message_id - 1
        send_message(chat_id= uid, text= text, reply_to_message_id = umid)
        Message(dict_messages_main['ok_send_msg_for_user'], Player(cid, 'mainadmin')).send_message()
    else:
        send_message(chat_id= dict_mid_for_answer[cid][0], text= text, reply_to_message_id = dict_mid_for_answer[cid][1])
        dict_mid_for_answer.pop(cid)
        Message(dict_messages_main['ok_send_msg_for_user'], Player(cid, 'mainadmin')).send_message()
    # Message(dict_messages_main[''])



@bot.message_handler(func=lambda m: get_user_step(m.chat.id) == 4)
def get_msg(m):
    cid = m.chat.id
    name = m.chat.first_name
    text = m.text
    if m.forward_from:
        uid = m.forward_from.id
        list_dict_info_user = database.select_users_by_cid(uid)
        if list_dict_info_user:
            dict_info = list_dict_info_user[0]
            markup = InlineKeyboardMarkup()
            check_blocked = database.select_blocked_users_from_group(dict_info['cid'], dict_admin_group[cid])
            if check_blocked:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{dict_admin_group[cid]}'))
                Message(dict_messages_main['user_group_blocked'], Player(cid, 'admin'), markup).send_message() 
            else:
                userStep[cid] = 0
                database.insert_blocked_users_from_group(dict_admin_group[cid],  dict_info['cid'])
                Message(dict_messages_main['yes_block_user_group'], Player(cid, 'admin')).send_message() 
                Message(dict_messages_main['whoconfig'], Player(cid, 'admin'), InlineKeyboardMarkup_config_block(dict_admin_group[cid])).send_message() 
                    

        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{dict_admin_group[cid]}'))
            Message(dict_messages_main['no_user_by_cid'], Player(cid, 'admin'), markup).send_message()



    else:
        text = m.text
        if text[0] == '@':
            list_dict_info_user = database.select_users_by_username(text)
            if list_dict_info_user:
                dict_info = list_dict_info_user[0]
                markup = InlineKeyboardMarkup()
                check_blocked = database.select_blocked_users_from_group(dict_info['cid'], dict_admin_group[cid])
                if check_blocked:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{dict_admin_group[cid]}'))
                    Message(dict_messages_main['user_group_blocked'], Player(cid, 'admin'), markup).send_message() 

                else:
                    userStep[cid] = 0
                    database.insert_blocked_users_from_group(dict_admin_group[cid],  dict_info['cid'])
                    Message(dict_messages_main['yes_block_user_group'], Player(cid, 'admin')).send_message() 
                    Message(dict_messages_main['whoconfig'], Player(cid, 'admin'), InlineKeyboardMarkup_config_block(dict_admin_group[cid])).send_message() 
                    

            else:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{dict_admin_group[cid]}'))
                Message(dict_messages_main['no_user_by_username'], Player(cid, 'admin'), markup).send_message()
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(dict_messages_main['CanceleBtn'], callback_data=f'blockconfig_back_{dict_admin_group[cid]}'))
            Message(dict_messages_main['notcorect_format'], Player(cid, 'admin'), markup).send_message()


#----------------------------------------------------------------all message in private--------------------------------------------------------
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def all_message(m):
    cid = m.chat.id
    text = m.text
    name = m.chat.first_name
    mid = m.message_id
    if cid in players_dict:
        list_team = game_dict[group_dict[players_dict[cid].game.group.id]].get_teammates(players_dict[cid]) 
        if list_team:
            bot.delete_message(cid,m.message_id)
            for player in list_team:
                Message(f'{name} : {text}', player).send_message()
        

@bot.message_handler(func=lambda message: message.chat.type in ['group' , 'supergroup'])
def all_message(m):
    print('okkkkk')
    group_id = m.chat.id
    user_id = m.from_user.id
    text = m.text
    name = m.chat.first_name
    if user_id in players_dict:
        print('hast')
        if players_dict[user_id].alive == False:
            if players_dict[user_id].game.settings.silence_after_deeth == 'active':
                bot.delete_message(group_id,m.message_id)


@bot.message_handler(func=lambda message: True)
def all_message(m):
    group_id = m.chat.id
    # user_id = m.from_user.id
    print(group_id)
#------------------------------------------------------------------------thread-------------------------------------------------------------
def check_and_notify_thread():
    while True:
        for key_game in list(game_dict.keys()):
            game = game_dict[key_game]
            time_method_execution = game.next_action_time()
            text_action = game.next_action()
            if text_action == 'start_game':
                diff = time_method_execution - time.time()
                if diff <= 45 and game.meld_45_sec:
                    game.meld_45_sec = False
                    game.ann_remaining_time(45)
                elif diff <= 30 and game.meld_30_sec:
                    game.meld_30_sec = False
                    game.ann_remaining_time(30)
                elif diff <= 15 and game.meld_15_sec:
                    game.meld_15_sec = False
                    game.ann_remaining_time(15)



            if time_method_execution <= time.time():
                game_check = game.run_action()
                if game_check == False:
                    list_players = game.players
                    if len(list_players) > 0:
                        for player in list_players:
                            if player.id in players_dict:
                                del players_dict[player.id]
                    del game_dict[key_game]
                
                elif game_check == 'end game':
                    list_players = game.players
                    if len(list_players) > 0:
                        for player in list_players:
                            if player.id in players_dict:
                                del players_dict[player.id]
                    del game_dict[key_game]

        threading.Event().wait(2)


check_thread = threading.Thread(target=check_and_notify_thread)
check_thread.start()






read_ini_file(file_path_main, dict_messages_main)
read_ini_file(file_path_general, dict_messages_general)
bot.infinity_polling()

