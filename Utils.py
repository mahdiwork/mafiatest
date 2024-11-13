import configparser
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, WebAppInfo
import telebot
from telebot.util import antiflood 
from telebot.apihelper import ApiTelegramException
import random
import logging
import time
import database
import os

TOKEN = '7608893026:AAEarXN8Cc8Y27gJNoEAwCQqjjIlwPuZa0o' #'7018847010:AAEMTrqs7mZRwxyaXE_XUgbyYPYzl_Twt3M' # 
bot = telebot.TeleBot(TOKEN, num_threads=1)

master_cid = 748626808
channel_id_description = -1002194828730

logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# config = configparser.ConfigParser()
# config.read('Game_Mode\general_fa.ini')

# def read_ini_file(file_path):
#     ini_data = {}
#     with open(file_path, 'r' ,encoding='utf-8') as file:
#         for line in file:
#             line = line.strip()
#             if line and not line.startswith(';') and '=' in line:
#                 key, value = map(str.strip, line.split('=', 1))
#                 ini_data[key] = value
#     return ini_data


def read_ini_file(file_path):
    ini_data = {}
    current_key = None
    with open(file_path, 'r' ,encoding='utf-8') as file:
        for line in file:
            line = line.rstrip()
            if '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                ini_data[key] = value.strip('"')
                current_key = key
            elif current_key is not None:
                if '[' not in line:
                    ini_data[current_key] += '\n' + line.strip('"')
    return ini_data

def format_seconds(seconds):
    min = seconds // 60
    rem_seconds = seconds % 60
    return f'{min:02}:{rem_seconds:02}'

def InlineKeyboardMarkup_main():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('مینی اپ 📱', web_app=WebAppInfo(url='https://almaslink.ir/comming_soon/'))) 
    markup.add(KeyboardButton("راهنما 📖", web_app=WebAppInfo(url='https://irweb.site/mafia_roles'))) 
    # markup.add('حساب کاربری 👤')
    # markup.add('فرشگاه 🛒', 'خرید سکه 💰')
    return markup


class Player: # کلاس پلیر های بازی
    def __init__(self, id, name, game = None):
        self.id = id
        self.name = name
        self._role = None
        self.status = False
        self.where = None
        self._home = [self] 
        self._alive = True
        self._target = None
        self.game = game  # Game
        self._grouping = None
        self.love = None
        self.save_Shahzade = True
        self.becoming_love = True

        self.number_of_shot = None

        self._save_fereshte = False
        self.save_WhiteWolf = False
        self.save_Phoenix = False
        self.save_Franc = False
        self.bewitched = False

        self._becoming_cult = 0
        self._kill_cult = None
        self._new_cult = None
        self._messages = []
        self.list_targets = []
        self.role_name = None
        self.vote = None
        self.new_WolfGorgine = None

        self.pattern = None
        self.is_pattern = None

        self.oil_spraying = False
        self.set_fire = False

        self.first_eat = False

        self.can_there_solh = True
        self.can_there_spreadsilver = True
        self.can_vote_agian = True
        self.notify_kadkhoda = True
        self.can_Ruler_vote = True
        self.can_KhabGozar = True

        self.second_target = None
        self.fake_role = None

        self.list_announced_roles = []
        self.list_lovers = []

        self.is_prisoner = True

        self.message_target_kalantar = None

    def __hash__(self):
        return hash(self.id)

    @property
    def messages(self):
        return self._messages
    @messages.setter
    def messages(self, messages):
        self._messages.append(messages)


    @property
    def new_cult(self):
        return self._new_cult
    @new_cult.setter
    def new_cult(self, new_cult):
        self._new_cult = new_cult

    @property
    def kill_cult(self):
        return self._kill_cult
    @kill_cult.setter
    def kill_cult(self, kill_cult):
        self._kill_cult = kill_cult

    @property
    def becoming_cult(self):
        return self._becoming_cult
    @becoming_cult.setter
    def becoming_cult(self, becoming_cult):
        self._becoming_cult = becoming_cult

    @property
    def save_fereshte(self):
        return self._save_fereshte
    @save_fereshte.setter
    def save_fereshte(self, save_fereshte):
        self._save_fereshte = save_fereshte

    @property
    def alive(self):
        return self._alive
    @alive.setter
    def alive(self, alive):
        self._alive = alive


    @property
    def role(self):
        return self._role
    @role.setter
    def role(self, role):
        self._role = role

    @property
    def target(self):
        return self._target
    @target.setter
    def target(self, target):
        self._target = target

    @property
    def grouping(self):
        return self._grouping
    @grouping.setter
    def grouping(self, grouping):
        self._grouping = grouping 

    @property
    def home(self):
        return self._home
    @home.setter
    def home(self, home):
        self._home = home 

    def initial_state(self):
        self.messages.clear()
        self.where = None
        self.home = [self]
        self.target = None
        self.fake_role = None
        self.save_fereshte = False
        self.save_WhiteWolf = False
        self.save_Franc = False

    def initial_state_second(self):
        self.messages.clear()
        self.where = None
        self.home = [self]
        self.target = None
        self.second_target = None
        self.save_fereshte = False
        self.save_WhiteWolf = False
        self.save_Franc = False


    def fallling_in_love_Sweetheart(self, target):
        if target.love != None:
            target.love.love = None
            target.love.you_were_killed(target)
            target.messages = Message(self.create_message('MsgSweetHeartLastLoveDead', [target.love]), target)
            target.love.messages = Message(self.create_message('MsgPlayerDeadLastLove'), target.love)
            target.game.group.messages = Message(self.create_message('MsgGroupDeadLastLove').format(self.create_tag(target.love), self.game.roleannouncement(target.love)), target.game.group)
        
        if self.love != None:
            self.love.love = None
            self.love.you_were_killed(self)
            self.love.messages = Message(self.create_message('MsgPlayerDeadLastLove'), self.love)
            self.game.group.messages = Message(self.create_message('MsgGroupDeadLastLove').format(self.create_tag(self.love), self.game.roleannouncement(self.love)), self.game.group)
            self.messages = Message(self.create_message('MsgSweetHeartLastLoveDead', [self.love]), self)
        

        # if self.love == None:
        self.becoming_love = False
        self.love = target
        target.love = self
        # self.messages = Message(self.create_message('MsgLoveSweetHeart', [target]), self)

        # else:
        #     self.love.love = None
        #     self.love.you_were_killed(self)
        #     self.love.messages = Message(self.create_message('MsgPlayerDeadLastLove'), self.love)
        #     self.game.group.messages = Message(self.create_message('MsgGroupDeadLastLove').format(self.create_tag(self.love), self.game.roleannouncement(self.love)), self.game.group)
        #     self.messages = Message(self.create_message('MsgLoveSweetHeart', [target]), self)
        #     self.messages = Message(self.create_message('MsgSweetHeartLastLoveDead', [self.love]), self)
        #     self.love = target
        #     target.love = self


    def returned_to_none_vote(self):
        self.vote = None

    def fall_in_love(self, love):
        self.love = love

    def order_to_fire(self):
        self.set_fire = True

    def change_role_rosta(self):
        self.role = 'rosta'
        self.becoming_cult = 1

    def change_role_pishgo(self, PishRezerv, type):
        if type == 'changerole':
            PishRezerv.messages = Message(self.create_message('ChangeRolePishgo', [self]), PishRezerv)
        elif type == 'kill':
            PishRezerv.messages = Message(self.create_message('ApprenticeNowSeer', [self]), PishRezerv)
        PishRezerv.role = 'pishgo'
        PishRezerv.becoming_cult = 0.4

    def change_role_vampier(self):
        if self.role == 'pishgo':
            self.check_for_exist_PishRezerv()
            
        self.role = 'Vampire'
        self.grouping = 'vampire'
        self.role_name = self.game.dict_game_texts['role_Vampire_n']
        # self.new_cult = True

    def change_role_cult(self):
        if self.role == 'pishgo':
            self.check_for_exist_PishRezerv()

        self.role = 'ferqe'
        self.grouping = 'cult'
        self.role_name = self.game.dict_game_texts['role_ferqe_n']
        self.new_cult = True

    def change_role_WolfGorgine(self):
        if self.role == 'pishgo':
            self.check_for_exist_PishRezerv()

        self.role = 'WolfGorgine'
        self.becoming_cult = 0
        self.grouping = 'wolf'
        self.role_name = self.game.dict_game_texts['role_WolfGorgine_n']
        self.new_WolfGorgine = True

    def change_role_WolfGorgine_WhiteWolf(self):
        self.role = 'WolfGorgine'
        self.grouping = 'wolf'
        self.role_name = self.game.dict_game_texts['role_WolfGorgine_n']

    def check_for_exist_PishRezerv(self):
        for player in self.game.players:
            if player.alive:
                if player.role == 'PishRezerv':
                    self.change_role_pishgo('changerole')


    def not_go_anywhare(self):
        self.where = None
        if self.target != None:
            try:
                self.target.home.remove(self)
            except:
                send_message(master_cid, f'باز هم ارور not_go_anywhare رو داریم نمیدونم چرا')
        else:
            self.home.remove(self)

    def set_target(self,id_target):
        if self.role == 'PesarGij' and random.random() < 0.5:
            list_player = []
            for player in self.game.players:
                if player != self:
                    if player.id != id_target:
                        list_player.append(player)
            random_vote = random.choice(list_player)
            self.night_action(random_vote)
        else:
            for player in self.game.players:
                if player.id == id_target:
                    self.night_action(player)

    def set_second_target(self, target):
        self.second_target = target 

    def choice_pattern(self, pattern):
        self.pattern = pattern
        pattern.is_pattern = self

    def set_vote(self,id_vote_me):
        for player in self.game.players:
            if player.id == id_vote_me:
                self.vote = player
                

    def change_status(self):
        if self.status:
            self.status = False
        else:
            self.status = True

    def assign_role(self, role_entrance, role_name, grouping, becoming_cult):
        self.role = role_entrance
        self.grouping = grouping
        self.role_name = role_name
        self.becoming_cult = becoming_cult
        if role_entrance == 'purevampire':
            self.active=False
        elif role_entrance == 'tofangdar':
            self.number_of_shot = 2
    def notification_assign_role(self): # ارسال پیام ابتدای بازی برای هر پلیر
        # تیم روستا
        if self.role == 'rosta':
            self.messages = Message(self.create_message('role_rosta'), self)

        if self.role == 'shekar':
            self.messages = Message(self.create_message('role_shekar'), self, mid_for_copy=2)

        elif self.role == 'kalantar':
            self.messages = Message(self.create_message('role_kalantar'), self, mid_for_copy=22)
            for player in self.game.players:
                if player.role == "Bloodthirsty":
                    self.messages = Message(self.create_message('role_kalantarBloodInHome'), self)
                    
        elif self.role == 'pishgo':
            self.messages = Message(self.create_message('role_pishgo'), self, mid_for_copy=14)

        elif self.role == 'tofangdar':
            self.messages = Message(self.create_message('role_tofangdar'), self, mid_for_copy=20)

        elif self.role == 'fereshte':
            self.messages = Message(self.create_message('role_Fereshte'), self, mid_for_copy=24)

        elif self.role == 'rishSefid':
            self.messages = Message(self.create_message('role_rishSefid'), self, mid_for_copy=58)

        elif self.role == 'Knight':
            self.messages = Message(self.create_message('role_Knight'), self, mid_for_copy=26)

        elif self.role == 'PishRezerv':
            self.messages = Message(self.create_message('role_PishRezerv'), self, mid_for_copy=6)

        elif self.role == 'Solh':
            self.messages = Message(self.create_message('role_Solh'), self, mid_for_copy=54)

        elif self.role == 'Ahangar':
            self.messages = Message(self.create_message('role_Ahangar'), self, mid_for_copy=62)

        elif self.role == 'karagah':
            self.messages = Message(self.create_message('role_karagah'), self, mid_for_copy=16)

        elif self.role == 'faheshe':
            self.messages = Message(self.create_message('role_faheshe'), self, mid_for_copy=30)

        elif self.role == 'trouble':
            self.messages = Message(self.create_message('role_trouble'), self, mid_for_copy=40)

        elif self.role == 'ahmaq':
            self.messages = Message(self.create_message('role_ahmaq'), self, mid_for_copy=14)

        elif self.role == 'Kadkhoda':
            self.messages = Message(self.create_message('role_Kadkhoda'), self, mid_for_copy=34)

        elif self.role == 'Ruler':
            self.messages = Message(self.create_message('role_Ruler'), self, mid_for_copy=36)

        elif self.role == 'Mast':
            self.messages = Message(self.create_message('role_Mast'), self, mid_for_copy=44)

        elif self.role == 'NefrinShode':
            self.messages = Message(self.create_message('role_NefrinShode'), self, mid_for_copy=46)

        elif self.role == 'Khaen':
            self.messages = Message(self.create_message('role_Khaen'), self, mid_for_copy=48)

        elif self.role == 'KhabGozar':
            self.messages = Message(self.create_message('role_KhabGozar'), self, mid_for_copy=52)

        elif self.role == 'Gorgname':
            self.messages = Message(self.create_message('role_Gorgname'), self, mid_for_copy=56)

        elif self.role == 'PesarGij':
            self.messages = Message(self.create_message('role_PesarGij'), self, mid_for_copy=64)

        elif self.role == 'Augur':
            self.messages = Message(self.create_message('role_Augur'), self, mid_for_copy=10)

        elif self.role == 'elahe':
            self.messages = Message(self.create_message('role_elahe'), self, mid_for_copy=50)

        elif self.role == 'ngativ':
            self.messages = Message(self.create_message('role_ngativ'), self, mid_for_copy=8)

        elif self.role == 'Chemist':
            self.messages = Message(self.create_message('role_Chemist'), self, mid_for_copy=28)

        elif self.role == 'Shahzade':
            self.messages = Message(self.create_message('role_Shahzade'), self, mid_for_copy=60)

        elif self.role == 'Sweetheart':
            self.messages = Message(self.create_message('role_Sweetheart'), self, mid_for_copy=38)

        elif self.role == 'Vahshi':
            self.messages = Message(self.create_message('role_Vahshi'), self, mid_for_copy=82)


        # تیم گرگ ها
        elif self.role == 'WolfAlpha':
            self.messages = Message(self.create_message('role_WolfAlpha'), self, mid_for_copy=68)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_wolf_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'WolfGorgine':
            self.messages = Message(self.create_message('role_WolfGorgine'), self, mid_for_copy=74)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_ferqe_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'Wolfx':
            self.messages = Message(self.create_message('role_Wolfx'), self, mid_for_copy=72)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_ferqe_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'WhiteWolf':
            self.messages = Message(self.create_message('role_WhiteWolf'), self, mid_for_copy=78)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_ferqe_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'WolfTolle':
            self.messages = Message(self.create_message('role_WolfTolle'), self, mid_for_copy=78)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_ferqe_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'Honey':
            self.messages = Message(self.create_message('role_Honey'), self, mid_for_copy=90)

        elif self.role == 'enchanter':
            self.messages = Message(self.create_message('role_enchanter'), self, mid_for_copy=86)

        elif self.role == 'WolfJadogar':
            self.messages = Message(self.create_message('role_WolfJadogar'), self, mid_for_copy=88)


        # تیم قاتل
        elif self.role == 'Qatel':
            self.messages = Message(self.create_message('role_Qatel'), self, mid_for_copy=122)
            Archer = None
            for ply in self.game.players:
                if ply.role == 'Archer':
                    Archer = ply
            if Archer != None:
                self.messages = Message(self.create_message('role_QatelIfArcher', [Archer]), self)

        elif self.role == 'Archer':
            self.messages = Message(self.create_message('role_Archer'), self, mid_for_copy=124)
            Qatel = None
            for ply in self.game.players:
                if ply.role == 'Qatel':
                    Qatel = ply
            if Qatel != None:
                self.messages = Message(self.create_message('role_archeriqatel', [Qatel]), self)
            
            


        # تیم فرقه ها
        elif self.role == 'ferqe':
            self.messages = Message(self.create_message('role_ferqe'), self, mid_for_copy=114)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_wolf_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'Royce':
            self.messages = Message(self.create_message('role_Royce'), self, mid_for_copy=116)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_ferqe_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'Franc':
            self.messages = Message(self.create_message('role_franc'), self, mid_for_copy=120)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_ferqe_team'].format(self.game.text_get_teammates(self)), self)


        # تیم آتش
        elif self.role == 'Firefighter':
            self.messages = Message(self.create_message('role_Firefighter'), self, mid_for_copy=100)
            for ply in self.game.players:
                if ply.role == 'IceQueen':
                    self.messages = Message(self.game.dict_game_texts['role_FirefighterIce'].format(self.create_tag(ply)), self)


        elif self.role == 'IceQueen':
            self.messages = Message(self.create_message('role_IceQueen'), self, mid_for_copy=102)
            for ply in self.game.players:
                if ply.role == 'Firefighter':
                    self.messages = Message(self.game.dict_game_texts['role_IceQueenFire'].format(self.create_tag(ply)), self)

        # تیم ومپایر
        elif self.role == 'Vampire':
            self.messages = Message(self.create_message('role_Vampire'), self, mid_for_copy=96)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_wolf_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'Bloodthirsty':
            self.messages = Message(self.create_message('role_Bloodthirsty'), self, mid_for_copy=92)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_wolf_team'].format(self.game.text_get_teammates(self)), self)

        elif self.role == 'kentvampire':
            self.messages = Message(self.create_message('role_kentvampire'), self, mid_for_copy=94)
            if self.game.text_get_teammates(self):
                self.messages = Message(self.game.dict_game_texts['role_wolf_team'].format(self.game.text_get_teammates(self)), self)




        
        
        
        self.send_message_()


    def send_message_(self):
        for msg in self.messages:
            msg.send_message()
        self.messages.clear()
        

    def you_were_killed(self,attacker, status='novoting'):  # پس از مشخص شدن کشته شدن نقش
        self.alive = False
        Message(self.create_message('to_die'), self).send_message()
        if self.love != None:
            Message(self.create_message('LoverDied').format(self.create_tag(self), self.create_tag(self.love), self.game.roleannouncement(self.love)), self.game.group).send_message()
            self.love.love = None
            self.love.you_were_killed(self) 
        if self.is_pattern != None:
            if self.is_pattern.alive:
                list_wolf = []
                for player in self.game.players:
                    if player.alive:
                        if player.grouping == 'wolf':
                            list_wolf.append(player)
                if len(list_wolf) > 0:
                    sampel_wolf = None
                    for wolf in list_wolf:
                        Message(self.create_message('OlgoChangedTo', [self, self.is_pattern]), wolf).send_message()
                        sampel_wolf = wolf
                    Message(self.create_message('OlgoChangedToTeam').format(self, self.game.text_get_teammates(sampel_wolf)), self.is_pattern).send_message()
                    self.is_pattern.change_role_WolfGorgine()
                else:
                    self.is_pattern.change_role_WolfGorgine()
                    Message(self.create_message('OlgoChangedToTone', [self]), self.is_pattern).send_message()

        print(f"{self.name} ({self.role}) has died.")
        if self.role == 'shekar':
            self._shekar_die(attacker)

        elif self.role == "pishgo":
            self._pishgo_die(attacker)

        elif self.role == 'kalantar':
            self._kalantar_die(attacker, status)

        elif self.role == 'tofangdar':
            self._tofangdar_die(attacker)

        elif self.role == 'fereshte':
            self._fereshte_die(attacker)

        elif self.role == 'rishSefid':
            if attacker.role == 'tofangdar':
                attacker.change_role_rosta()
                self.game.group.messages = Message(self.create_message('GunnerShotWiseElder',[attacker, self]), self.game.group)
        
        elif self.role == 'Knight':
            pass

        elif self.role == 'PishRezerv':
            pass
        elif self.role == 'Solh':
            pass
        elif self.role == 'Ahangar':
            pass
        elif self.role == 'karagah':
            pass
        elif self.role == 'faheshe':
            pass
        elif self.role == 'trouble':
            pass
        elif self.role == 'ahmaq':
            pass
        elif self.role == 'Kadkhoda':
            pass
        elif self.role == 'Ruler':
            if self.game.Ruler_vote == self:
                self.game.Ruler_vote = False
                Message(self.create_message('RulerIsDead'), self.game.group).send_message()
        elif self.role == 'NefrinShode':
            pass
        elif self.role == 'Khaen':
            pass
        elif self.role == 'KhabGozar':
            pass
        elif self.role == 'Gorgname':
            pass
        elif self.role == 'PesarGij':
            pass
        elif self.role == 'Augur':
            pass
        elif self.role == 'elahe':
            pass
        elif self.role == 'ngativ':
            pass
        elif self.role == 'Chemist':
            pass
        elif self.role == 'Sweetheart':
            pass
        elif self.role == 'Vahshi':
            pass
            # if attacker.role == 'Qatel':
            #     self.messages = Message(self.create_message(self.game.dict_game_texts['HarlotFuckKiller'], [attacker]), self)
            # elif attacker.grouping == 'wolf'  and attacker.role not in ['enchanter','WolfJadogar']:
            #     self.messages = Message(self.create_message(self.game.dict_game_texts['HarlotFuckWolf'], [attacker]), self)
                
        
        elif self.role == 'WolfAlpha':
            self._WolfAlpha_die(attacker)
        elif self.role == "WolfGorgine":
            self._WolfGorgine_die(attacker)
        elif self.role == 'WhiteWolf':
            pass
        elif self.role == 'Wolfx':
            pass
        elif self.role == 'enchanter':
            for player in self.game.players:
                if player.bewitched:
                    player.bewitched = False
                    Message(self.create_message(self.create_message('ClearEnchanter')), player).send_message()
        elif self.role == 'WolfJadogar':
            pass
        elif self.role == 'Honey':
            pass
        elif self.role == 'WolfTolle':
            self.game.target_again = True
            self.game.attack_again = True

        elif self.role == 'Qatel':
            self._Qatel_die(attacker)
        
        # گروه آتش
        elif self.role == 'Firefighter':
            pass
        elif self.role == 'icequeen':
            pass


        elif self.role == 'darkknight':
            self._darkknight_die(attacker)


        # گروه آتش
        elif self.role == 'ferqe':
            pass
        elif self.role == 'Royce':
            self._Royce_die(attacker)
        elif self.role == 'Franc':
            pass



        # ومپایر 
        elif self.role == 'Vampire':
            pass

        elif self.role == 'Bloodthirsty':
            self.game.is_vampire_imprisoned = False
            self.gmae.conversion_power_vampire = True
            for player in self.game.players:
                if player.grouping == 'vampire':
                    if player.alive:
                        player.messages= Message(self.create_message('VampireDeadLastFind',[self]), player)
        
        elif self.role == 'kentvampire':
            pass
    
    def night_action(self, target):
        # گروه روستا
        if self.role == 'shekar':
            self._shekar_night_action(target)
        elif self.role == "pishgo":
            self._pishgo_night_action(target)
        elif self.role == "kalantar":
            self._kalantar_night_action(target)
        elif self.role == "tofangdar":
            self._tofangdar_night_action(target)
        elif self.role == 'fereshte':
            self._fereshte_night_action(target)
        elif self.role == 'Knight':
            self._Knight_night_action(target)
        elif self.role == 'faheshe':
            target.home.append(self)
            self.home.remove(self)
            self.where = target
            self.target = target
        elif self.role == 'ahmaq':
            self.target = target
        elif self.role == 'ngativ':
            self.target = target
        elif self.role == 'karagah':
            self.target = target
        elif self.role == 'Chemist':
            target.home.append(self)
            self.home.remove(self)
            self.where = target
            self.target = target
        # elif self.role == 'Spy':
        #     self._Spy_night_action(target)


        # گروه گرگ
        elif self.role == 'WolfAlpha':
            self._WolfAlpha_night_action(target)
        elif self.role == "WolfGorgine":
            self._WolfGorgine_night_action(target)
        elif self.role == 'WhiteWolf':
            target.home.append(self)
            self.home.remove(self)
            self.where = target
            self.target = target
        elif self.role == 'Wolfx':
            target.home.append(self)
            self.home.remove(self)
            self.where = target
            self.target = target
        elif self.role == 'WolfTolle':
            target.home.append(self)
            self.home.remove(self)
            self.where = target
            self.target = target
        elif self.role == 'enchanter':
            self.target = target

        elif self.role == 'WolfJadogar':
            self.target = target

        elif self.role == 'Honey':
            self.target = target

        # گروه قاتل
        elif self.role == 'Qatel':
            target.home.append(self)
            self.home.remove(self)
            self.where=target
            self.target = target

        elif self.role == 'Archer':
            target.home.append(self)
            self.home.remove(self)
            self.where=target
            self.target = target
        
        # گروه آتش
        elif self.role == 'Firefighter':
            self.target = target
        elif self.role == 'icequeen':
            self.target = target
           

        # گروه ومپایر
        elif self.role == 'Vampire':
            target.home.append(self)
            self.home.remove(self)
            self.where = target
            self.target = target

        elif self.role == 'Bloodthirsty':
            target.home.append(self)
            self.home.remove(self)
            self.where = target
            self.target = target

        elif self.role == 'kentvampire':
            # target.home.append(self)
            # self.home.remove(self)
            # self.where = target
            self.target = target


        elif self.role == 'darkknight':
            self._darkknight_night_action(target)


        # گروه فرقه
        elif self.role == 'ferqe':
            target.home.append(self)
            self.home.remove(self)
            self.where=target
            self.target = target

        elif self.role == 'Royce':
            target.home.append(self)
            self.home.remove(self)
            self.where=target
            self.target = target

        elif self.role == 'Franc':
            target.home.append(self)
            self.home.remove(self)
            self.where=target
            self.target = target

    # پس از مرگ
    def _shekar_die(self, attacker):
        pass

    def _pishgo_die(self, attacker):
        for player in self.game.players:
            if player.alive:
                if player.role == 'PishRezerv':
                    self.change_role_pishgo(player, 'kill')
                    
    
    def _kalantar_die(self, attacker, status):
        self.game.is_vampire_imprisoned = False
        if attacker.grouping == 'vampire':
            if attacker.alive:
                if random.random() < 0.5:
                    attacker.you_were_killed(self)
                    self.game.group.messages = Message(self.create_message('VampireDeadByKalan',[self,attacker]), self.game.group)


        elif attacker.role=='WolfGorgine' and random.random() < 0.5:
            list_WolfGorgine=[]
            for playar in self.list_players:
                if playar.group=='Wolf':
                    if playar.alive:
                        list_WolfGorgine.append(playar)

            if list_WolfGorgine:    
                choise = random.choice(list_WolfGorgine)
                choise.you_were_killed(self)
                self.game.group.messages = Message(self.create_message('HunterShotWolfMulti').format(self.create_tag(self), self.create_tag(attacker), self.game.roleannouncement(attacker)), self.game.group)

        else:
            self.game.time_next_action_saved = self.game.time_next_action - time.time()
            self.game.time_next_action = time.time() + 20

            self.game.action_saved = self.game.action
            self.game.action = 'shotkalantar'

            if status == 'voting':
                self.game.action_killed_kalantar = 'voting'
                text = self.game.dict_game_texts['HunterLynchedChoice']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    if player != self:
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name,callback_data=f'kalantar_{player.id}_{player.name}'))
                markup.add(InlineKeyboardButton(self.create_message('noshot'), callback_data=f'kalantar_noshot'))
                target_message = Message(text, self, markup)
                self.message_target_kalantar = target_message
                target_message.send_message()


                # print("""باید بتونه انتخاب کنه کیو میخواد تارگت کنه و بکشه""")
                # return 'revenge_kalantar'
            

    def _tofangdar_die(self, attacker):
        pass

    def _fereshte_die(self, attacker):
        if attacker.grouping == 'gorg':
            self.messages = self.game.dict_game_texts['GuardWolf']




    def _WolfAlpha_die(self, attacker):
        pass
    def _WolfGorgine_die(self, attacker):
        pass


    def _Qatel_die(self, attacker):
        pass

    def _commonvampire_die(self, attacker):
        pass
    def _purevampire_die(self, attacker):
        pass

    def _darkknight_die(self, attacker):
        pass

    def _hamzad_die(self, attacker):
        pass
    
    def _Royce_die(self, attacker):
        self.game.target_again = True
        self.game.invited_again = True
        # list_cult = []
        # for player in self.game.players:
        #     if player != self:
        #         if player.grouping == "cult":
        #             list_cult.append(player)
        # if len(list_cult) > 0:

        



    def _shekar_night_action(self, target):
        """شکارچی اقدام شبانه خود را انجام می‌دهد."""
        target.home.append(self)
        self.home.remove(self)
        self.target = target
        self.where = target

    def _pishgo_night_action(self, target):
        """پیشگو اقدام شبانه خود را انجام می‌دهد."""
        self.target = target

    def _kalantar_night_action(self, target):
        """کلانتر در شب عملیاتی ندارد"""
        pass

    def _tofangdar_night_action(self, target):
        """تفنگدار در شب عملیاتی ندارد"""
        pass

    def _fereshte_night_action(self, target):
        target.home.append(self)
        self.home.remove(self)
        self.where=target
        self.target = target

    def _Knight_night_action(self, target):
        target.home.append(self)
        self.home.remove(self)
        self.where=target
        self.target = target

    def _WolfAlpha_night_action(self, target):
        target.home.append(self)
        self.home.remove(self)
        self.where=target
        self.target = target


    def _WolfGorgine_night_action(self, target):
        """گرگینه اقدام شبانه خود را انجام می‌دهد."""
        target.home.append(self)
        self.home.remove(self)
        self.where = target
        self.target = target


    def _commonvampire_night_action(self, target):
        pass
    def _purevampire_night_action(self, target):
        pass

    def _darkknight_night_action(self, target):
        pass

    def _hamzad_night_action(self, target):
        pass


    # def get_teammates(self):
    #     list_grouping = []
    #     for player in self.game.players:
    #         if player.grouping == self.grouping:
    #             if player.id != self.id:
    #                 list_grouping.append(player)
    #     if len(list_grouping) == 0:
    #         return False
    #     else:
    #         return list_grouping 

    def create_tag(self,user):
        return f'[{user.name}](tg://user?id={user.id})'
        
    def create_message(self,name_message,list_user_for_tag=[]):
        if len(list_user_for_tag) == 0:
            return self.game.dict_game_texts[name_message]
        
        elif len(list_user_for_tag) == 1:
            self.game.dict_game_texts[name_message].format(self.create_tag(list_user_for_tag[0]))

        elif len(list_user_for_tag) == 2:
            self.game.dict_game_texts[name_message].format(self.create_tag(list_user_for_tag[0],list_user_for_tag[1]))

    # def election(self, target):
    #     """انتخاب هدف شبانه توسط گروه مافیا."""
    #     if self.role == "WolfGorgine":
    #         self.home.append(target)
    #         print(f"{self.name} has voted to target {target.name}.")

class Settings:
    def __init__(self, group):
        self.group = group

        self.time_night = None
        self.day_time = None
        self.time_vote = None
        self.time_join = None

        self.expose_shekar = None
        self.expose_shekar_day = None

        self.voting_secret = None
        self.number_vote_voting_secret = None
        self.name_vote_voting_secret = None
        self.silence_after_deeth = None
        self.show_role_end_game = None
        self.show_role_after_deeth = None
        self.adding_time_by_player = None

    def get_info_from_databade(self):
        dict_info = database.select_group_settings_by_group_id(self.group.id)[0]
        self.time_night =                   dict_info['nitht_time']
        self.day_time =                     dict_info['day_time']
        self.time_vote =                    dict_info['voting_time']
        self.time_join =                    dict_info['time_to_join']

        self.expose_shekar =                dict_info['expose_shekar']
        self.expose_shekar_day =            dict_info['expose_shekar_day']

        self.voting_secret =                dict_info['voting_secret']
        self.number_vote_voting_secret =    dict_info['number_vote_voting_secret']
        self.name_vote_voting_secret =      dict_info['name_vote_voting_secret']
        self.silence_after_deeth =          dict_info['silence_after_deeth']
        self.show_role_end_game =           dict_info['show_role_end_game']
        self.show_role_after_deeth =        dict_info['show_role_after_deeth']
        self.adding_time_by_player =        dict_info['adding_time_by_player']



class Group:
    def __init__(self, id, title, username, cid_admin_added_bot):
        self.id = id
        self.title = title
        self.username = username
        self.cid_admin_added_bot = cid_admin_added_bot
        self._messages = []

    def __hash__(self):
        return hash(self.id)

    @property
    def messages(self):
        return self._messages
    @messages.setter
    def messages(self, messages):
        self._messages.append(messages)

    def send_message(self):
        for msg in self.messages:
            msg.send_message()
        self.messages.clear()

class Game: # کلاس گیم (برای ساخت و اجرای هر بازی)
    def __init__(self, group, settings ,players, game_mode):
        self.group = group
        self.settings = settings
        self.game_mode=game_mode
        self.players = players
        self.active=False
        self.dict_messages_send = {}
        self.dict_game_texts = read_ini_file(os.path.join('Game_Mode','general_fa.ini'))
        self.message_list_player = None
        self.message_start_game = None
        self.day = 1

        self.invited_again = False
        self.target_again = False
        self.attack_again = False

        self.send_message_for_expose_shekar = False

        self.action_saved = None
        self.time_next_action_saved = None
        self.action_killed_kalantar = None
        self.choice_target_kalantar = False

        self.action = None
        self.time_next_action = None
        self.dict_message_choice_target = {}
        self.dict_message_choice_target_day = {}
        self.dict_message_choice_vote = {}
        self.dict_message_loving = {}

        self.one_min_announcement = True
        self.ten_sec_announcement = True

        self.voting_status = True
        self.wolves_can_attack = True
        self.vote_again = False
        self.Ruler_vote = False
        self.night_status = True

        self.is_vampire_imprisoned = True
        self.conversion_power_vampire = False


        self.meld_45_sec = True
        self.meld_30_sec = True
        self.meld_15_sec = True
        self.msgs_for_ann_time = []

        self.active_membership = True

    def flee_player(self, id_player): # متد انصراف از بازی
        if self.next_action() == 'start_game':
            player_for_delete = None
            for player in self.players:
                if player.id == id_player:
                    player_for_delete = player
            self.players.remove(player_for_delete)
            Message(self.create_message('okFlee', [player_for_delete]) + self.dict_game_texts['FleeCoutPlayer'].format(len(self.players)), self.group).send_message()
            return True
        else:
            return False
        
    def fired_player(self, player):
        if self.next_action() == 'start_game':
            self.players.remove(player)
            self.edit_message_list_player()
            Message(self.create_message('smite_user_ok', [player]), self.group).send_message()
        else:
            player.alive = False
            player.status = 'smite'
            self.send_list_players_in_group()
            check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
            if check_win:
                return 'end game'
            




    def get_teammates(self, target_player): # متد دریافت هم تیمی ها
        list_grouping = []
        if target_player.grouping == 'village':
            return False
        if target_player.role in ['enchanter','WolfJadogar']:
            return False
        if self.next_action() != 'check_night':
            return False
        for player in self.players:
            if player.grouping == target_player.grouping:
                # if player.id != self.id:
                if player.alive:
                    list_grouping.append(player)
        if (len(list_grouping)-1) == 0:
            return False
        else:
            return list_grouping 

    def list_players(self):
        return self.players

    def extend_time(self,extra_time):
        if extra_time < 0:
            self.time_next_action += extra_time   
            total_time = int(self.time_next_action - time.time())
            if total_time > 0:
                Message(self.dict_game_texts['ExtendToTimeManfi'].format(extra_time,format_seconds(total_time)), self.group).send_message()
            else:
                Message(self.dict_game_texts['ExtendToTimeManfi'].format(extra_time,'00:00'),self.group).send_message()

        elif (self.time_next_action - time.time()) + extra_time > self.settings.time_join :
            self.time_next_action = self.settings.time_join + time.time()
            total_time = int(self.time_next_action - time.time())
            Message(self.dict_game_texts['ExtendToTime'].format(extra_time,format_seconds(total_time)), self.group).send_message()

        else:
            self.time_next_action += extra_time  
            total_time = int(self.time_next_action - time.time())
            Message(self.dict_game_texts['ExtendToTime'].format(extra_time,format_seconds(total_time)), self.group).send_message()

        remain_time = self.time_next_action - time.time()
        if remain_time > 45:
            self.meld_45_sec = True 
        else:
            self.meld_45_sec = False 

        if remain_time > 30:
            self.meld_30_sec = True
        else:
            self.meld_30_sec = False

        if remain_time > 15:
            self.meld_15_sec = True
        else:
            self.meld_15_sec = False


    def check_the_stage_to_extend_time(self):
        if self.next_action() == 'start_game':
            return True
        else:
            return False

    def next_action(self):
        return self.action
    
    def next_action_time(self):
        return self.time_next_action

    def run_action(self):
        text_action = self.next_action()
        if text_action != None:
            if text_action == 'start_game':
                return self.start_game()
            
            elif text_action == 'time_to_join_game':
                return self.time_to_join_game()

            elif text_action == 'check_night':
                return self.check_night()

            elif text_action == 'target_again':
                return self.def_target_again()
            
            elif text_action == 'voting':
                return self.voting()
            
            elif text_action == 'check_voting':
                return self.check_voting()
            
            elif text_action == 'shotkalantar':
                return self.check_shotkalantar()

    def start(self):
        self.active=True
        self.action = 'start_game'
        self.time_next_action = time.time() + self.settings.time_join

    def time_to_join_game(self):
        print(self.action)
        time_now = time.time()
        print(55 <self.time_next_action - time_now < 60 , self.one_min_announcement)
        if 55 <self.time_next_action - time_now < 60 and self.one_min_announcement:
            self.one_min_announcement = False
            print(self.dict_game_texts['OnlyJoinTheGameTime'].format(self.dict_game_texts['minuts']))
            Message(self.dict_game_texts['OnlyJoinTheGameTime'].format(self.dict_game_texts['minuts']), self.group).send_message()
        elif 5 <self.time_next_action - time_now < 10 and self.ten_sec_announcement:
            self.ten_sec_announcement = False
            print(self.dict_game_texts['OnlyJoinTheGameTime'].format(self.dict_game_texts['Secend'].format(10)))
            Message(self.dict_game_texts['OnlyJoinTheGameTime'].format(self.dict_game_texts['Secend'].format(10)), self.group).send_message()
        elif self.time_next_action - time_now <= 0 :
            return self.start_game()

    def start_game(self):
        self.active_membership = False
        check_res = self.chack_number_player()
        if check_res == 'not enough':
            self.remove_join_button()
            Message(self.dict_game_texts['NotStartGameForPlayer'],self.group).send_message()
            # حذف بازی و پلیر ها از دیکشنری های فایل main 
            return False
        self.remove_join_button()
        self.playing_roles()
        self.send_notification_for_player()
        self.send_start_notification_in_group()
        self.send_list_players_in_group()
        self.start_night()


# شروع حلقه
    def start_night(self):  # شروع شب
        if self.night_status:
            self.action = ''
            self.send_night_notification_in_group() # ارسال پیام شب شدن در گروه
            # self.send_list_players_in_group()  # ارسال لیست بازیکنان
            self.checking_shekarchi_in_game() # چک کردن وجود شکارچی در بازی و در صورت وجود و تایید ادمین اعلام نقشش
            self.sending_night_actions()  # ارسال لیست تارگت ها برای نقش هایی که توانایی تارگت شب زدن دارند
            if self.day == 1:
                self.send_list_for_elahe()
                self.send_list_for_Vahshi()
            
            if self.target_again:
            # if self.invited_again:
                self.action = "target_again"
                self.time_next_action = time.time() + (self.settings.time_night/2)

            else:
                self.action = 'check_night'
                self.time_next_action = time.time() + self.settings.time_night
        else:
            self.action = ''
            self.send_notification_cancel_night()
            self.start_dey()

    def def_target_again(self): # تارگت دوباره
        again = False
        if self.invited_again:
            if len(self.check_cult_alive()) > 0: # چک کردن وجود فرقه زنده
                self.check_message_choice_target_for_cult()
                self.send_list_target_again_invited()
                again = True

        if self.target_again:
            if len(self.check_wolf_alive()) > 0: # چک کردن وجود گرگ زنده
                self.check_message_choice_target_for_wolf()
                self.send_list_target_again_attack()
                again = True

        if again:
            self.action = 'check_night'
            self.time_next_action = time.time() + (self.settings.time_night/2)
        else:
            self.target_again = False
            self.attack_again = False
            self.invited_again = False
            self.action = 'check_night'
            self.time_next_action = time.time() + (self.settings.time_night/2)

    def check_night(self): # چک کردن اتفاقات شب
        self.wolves_can_attack = True
        self.action = ''
        self.check_message_choice_target() # چک کردن اینکه نقش ها رای داده اند یا نه و در صورت رای ندادن حذف پیام انتخاب رای
        if self.day == 1:
            self.check_elahe()
            self.check_Vahshi()
        self.check_night_target() # چک کردن تارگت های هر نقش
        self.send_events() # ارسال اتفاقات
        self.return_the_initial_state() # برگشتن به حالت اولیه نقش ها
        if self.target_again:
            self.target_again = False
            self.attack_again = False
            self.invited_again = False
            self.converting_second_targer_to_first()
            self.check_night_target() # چک کردن تارگت های هر نقش
            self.send_events() # ارسال اتفاقات
            self.return_the_initial_state_second() # برگشتن به حالت اولیه نقش ها

        check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
        if check_win:
            return 'end game'
        self.start_dey()


    def start_dey(self): # شروع روز
        self.declaring_role_to_Augur() # اعلا نقش به رمال  در صورت وجود ذر بازی
        self.send_dey_notification_in_group() # ارسال پیام های مربوط به شروع روز
        self.send_list_players_in_group()
        self.sending_day_actions()     # ارسال لیست تارگت ها برای نقش هایی که توانایی تارگت زدن در روز را دارند
        check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
        if check_win:
            return 'end game'
        self.action = 'voting'
        self.time_next_action = time.time() + self.settings.day_time


    # def check_day(self): # چک کردن اتفاقات روز
    #     self.action = ''
    #     self.check_message_choice_target_day() # چک کردن اینکه نقش ها رای داده اند یا نه و در صورت رای ندادن حذف پیام انتخاب رای
    #     self.check_day_target() # چک کردن تارگت های هر نقش
    #     self.send_events() # ارسال اتفاقات
    #     self.return_the_initial_state_day() # برگشتن به حالت اولیه نقش ها
    #     check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
    #     if check_win:
    #         return 'end game'
    #     self.voting()

    def voting(self): # شروع رای گیری
        self.check_message_choice_target_day() # چک کردن اینکه نقش ها رای داده اند یا نه و در صورت رای ندادن حذف پیام انتخاب رای
        check_exist_voting = self.chech_voting_status()
        if check_exist_voting:
            if self.Ruler_vote == False:
                self.send_voting_notification_in_group() # ارسال پیام شروع رای گیری در گروه
                self.sending_voting_dey() # ارسال دکمه های رای دادن برای بازیکنان
                self.action = 'check_voting'
                self.time_next_action = time.time() + self.settings.time_vote
            else:
                self.send_voting_notification_ruler()
                self.sending_voting_ruler()
                self.action = 'check_voting'
                self.time_next_action = time.time() + self.settings.time_vote
        else:
            self.send_cancel_voting_notification_in_group() # ارسال پیام لغو شدن رای گیری در گروه
            self.day += 1
            self.start_night()

    def check_voting(self): # چک رای 
        self.check_message_choice_voting()
        self.actions_vote()  # اعمال رای گیری روز
        self.votes_returned_to_none()  # بازگشت آرا بازیکنان به none
        self.send_list_players_in_group()
        check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
        if check_win:
            return 'end game'
        check_voteagain = self.check_vote_again()# در صورتی که دختر دردسر ساز رای دوباره را فعال کرده باشد اجرا میشود
        if check_voteagain:
            self.voting()
        else:
            self.day += 1
            self.start_night()
# پایان حلقه 

    def shotkalantar(self, kalantar ,target):
        self.action = ''
        self.choice_target_kalantar = True
        target.you_were_killed(kalantar)
        
        if self.action_killed_kalantar == 'voting':
            Message(self.create_message('HunterKilledFinalLynched').format(self.create_tag(kalantar), self.create_tag(target), self.roleannouncement(target)), self.group).send_message()
        else:
            if self.action_saved == 'check_night':
                self.group.messages = Message(self.create_message('HunterKilledFinalShot').format(self.create_tag(kalantar), self.create_tag(target), self.roleannouncement(target)), self.group)
            else: 
                Message(self.create_message('HunterKilledFinalShot').format(self.create_tag(kalantar), self.create_tag(target), self.roleannouncement(target)), self.group).send_message()

        if self.action_saved != 'check_night':
            check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
            if check_win:
                return 'end game'
        
        self.action = self.action_saved
        self.time_next_action = time.time() + self.time_next_action_saved
        

    def noshotkalantar(self, kalantar):
        self.action = ''
        self.choice_target_kalantar = True
        if self.action_killed_kalantar == 'voting':
            Message(self.create_message('HunterSkipChoiceLynched',[kalantar]), self.group).send_message()
        else:
            if self.action_saved == 'check_night':
                self.group.messages = Message(self.create_message('HunterSkipChoiceShot',[kalantar]), self.group)
            else:
                Message(self.create_message('HunterSkipChoiceShot',[kalantar]), self.group).send_message()

        self.action = self.action_saved
        self.time_next_action = time.time() + self.time_next_action_saved

    def check_shotkalantar(self):
        self.action = ''
        if self.choice_target_kalantar == False:
            for ply in self.players:
                if ply.role == 'kalantar':
                    msg = ply.message_target_kalantar
                    msg.edit_message_text(self.dict_game_texts['endTime'])

        for ply in self.players:
            if ply.role == 'kalantar':
                if self.action_killed_kalantar == 'voting':
                    Message(self.create_message('HunterNoChoiceLynched',[ply]), self.group).send_message()
                else:
                    if self.action_saved == 'check_night':
                        self.group.messages = Message(self.create_message('HunterNoChoiceShot',[ply]), self.group)                
                    else:
                        Message(self.create_message('HunterNoChoiceShot',[ply]), self.group).send_message()
        self.action = self.action_saved
        self.time_next_action = time.time() + self.time_next_action_saved



    def ann_remaining_time(self, time):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(self.dict_game_texts['joinToGame'],url=f"https://t.me/{bot.get_me().username}?start={self.group.id}"))
        msg = Message(self.dict_game_texts['OnlyJoinTheGameTime'].format(self.dict_game_texts['Secend'].format(time)), self.group, markup)
        self.msgs_for_ann_time.append(msg)
        msg.send_message()

    def converting_second_targer_to_first(self):
        for player in self.players:
            if player.second_target != None:
                player.target = player.second_target

    def send_list_target_again_invited(self):
        for player_target in self.players:
            if player_target.grouping == "cult":
                if player_target.alive:
                    Message(self.create_message('RoyceDead'), player_target).send_message()
                    text = self.dict_game_texts['AskConvert']
                    markup = InlineKeyboardMarkup()
                    for player in self.players:
                        # if player != player_target:
                        if player.grouping != player_target.grouping:
                            if player.alive == True:
                                markup.add(InlineKeyboardButton(player.name, callback_data=f'target_second_{player.id}_{player.name}'))
                    target_message = Message(text,player_target,markup)
                    target_message.send_message()
                    self.dict_message_choice_target[player_target] = target_message

    def send_list_target_again_attack(self):
        for player_target in self.players:
            if player_target.grouping == "wolf":
                if player_target.alive:
                    # Message(self.create_message('RoyceDead'), player_target).send_message()
                    text = self.dict_game_texts['HowWasEatUser']
                    markup = InlineKeyboardMarkup()
                    for player in self.players:
                        # if player != player_target:
                        if player.grouping != player_target.grouping:
                            if player.alive == True:
                                markup.add(InlineKeyboardButton(player.name, callback_data=f'target_second_{player.id}_{player.name}'))
                    target_message = Message(text,player_target,markup)
                    target_message.send_message()
                    self.dict_message_choice_target[player_target] = target_message

    def check_cult_alive(self):
        list_cult_alive = []
        for player in self.players:
            if player.alive:
                if player.grouping == "cult":
                    list_cult_alive.append(player)
        return list_cult_alive

    def check_wolf_alive(self):
        list_wolf_alive = []
        for player in self.players:
            if player.alive:
                if player.grouping == "wolf":
                    list_wolf_alive.append(player)
        return list_wolf_alive

    def check_elahe(self):
        for ply in self.players:
            if ply.role == 'elahe':
                if len(ply.list_lovers) == 2:
                    ply.list_lovers[0].fall_in_love(ply.list_lovers[1])
                    ply.list_lovers[1].fall_in_love(ply.list_lovers[0])

                    Message(self.create_message('CupidChosen2', [ply.list_lovers[1]]), ply.list_lovers[0]).send_message()
                    Message(self.create_message('CupidChosen2', [ply.list_lovers[0]]), ply.list_lovers[1]).send_message()
                else:
                    list_ply = []
                    for player in self.players:
                        if player != 'Sweetheart':
                            list_ply.append(player)
                    random_list_role = random.sample(list_ply, 2)
                    random_list_role[0].fall_in_love(random_list_role[1])
                    random_list_role[1].fall_in_love(random_list_role[0])

                    Message(self.create_message('CupidChosen2', [random_list_role[1]]), random_list_role[0]).send_message()
                    Message(self.create_message('CupidChosen2', [random_list_role[0]]), random_list_role[1]).send_message()

    def check_Vahshi(self):
        for ply in self.players:
            if ply.role == 'Vahshi':
                if ply.pattern == None:
                    list_ply = []
                    for plye in self.players:
                        if plye.role != 'Vahshi':
                            list_ply.append(plye)
                    
                    random_role = random.choice(list_ply)
                    ply.choice_pattern(random_role)
                Message(self.create_message('NewWCRoleModel', [ply.pattern]), ply).send_message()
                


    def send_list_for_Vahshi(self):
        for ply in self.players:
            if ply.role == 'Vahshi':
                text = self.dict_game_texts['vahshi_L']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    if player.role != 'Vahshi':
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name, callback_data=f'pattern_{player.id}_{player.name}'))    
                love_message = Message(text, ply, markup)
                love_message.send_message()
                self.dict_message_loving.setdefault(ply, love_message)        

    def send_list_for_elahe(self):
        for ply in self.players:
            if ply.role == 'elahe':
                text = self.dict_game_texts['elahe_L']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    if player.alive == True:
                        if player.role != 'Sweetheart':
                            markup.add(InlineKeyboardButton(player.name, callback_data=f'loving_{player.id}_{player.name}'))    
                love_message = Message(text, ply, markup)
                love_message.send_message()
                self.dict_message_loving.setdefault(ply, love_message)


    def choice_lover(self, elahe, lover):
        if lover in elahe.list_lovers:
            elahe.list_lovers.remove(lover)
        else:
            elahe.list_lovers.append(lover)

        if len(elahe.list_lovers) == 2:
            text = self.create_message('loving_ok', [elahe.list_lovers[0],elahe.list_lovers[1]])
            self.dict_message_loving[elahe].edit_message_text(text)    
        
        else:
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player.alive == True:
                    if player.role != 'Sweetheart':
                        if player in elahe.list_lovers:
                            markup.add(InlineKeyboardButton(player.name + " ✅", callback_data=f'loving_{player.id}_{player.name}'))  
                        else:
                            markup.add(InlineKeyboardButton(player.name, callback_data=f'loving_{player.id}_{player.name}'))    
            self.dict_message_loving[elahe].edit_message_reply_markup(markup)        
        


    def declaring_role_to_Augur(self):
        for player in self.players:
            if player.role == 'Augur':
                list_role_in_game = []
                for ply in self.players:
                    list_role_in_game.append(ply.role)
                list_role_not_in_game = []

                list_all_roles = []
                for r in database.select_all_roles():
                    if r['role_status'] == 'on':
                        check_closed = database.select_closed_roles_for_groups_by_group_id(self.group.id, r['code_role'])
                        if check_closed == []:
                            list_all_roles.append(r)

                for role in list_all_roles:
                    if role['role'] not in list_role_in_game and role['role'] not in player.list_announced_roles:
                        list_role_not_in_game.append(role)
                if len(list_role_not_in_game) > 0:
                    role_selected = random.choice(list_role_not_in_game)
                    player.list_announced_roles.append(role_selected['role'])

                    Message(self.create_message('AugurSees').format(role_selected['role_name']), player).send_message()
                elif len(list_role_not_in_game) == 0:
                    Message(self.create_message('AugurSeesNothing'), player).send_message()

                

    def cancel_night(self, KhabGozar):
        self.night_status = False
        KhabGozar.can_KhabGozar = False
        Message(self.create_message('SandmanSleepAll', [KhabGozar]), self.group).send_message()

    def send_notification_cancel_night(self):
        self.night_status = True
        Message(self.create_message('SandmanNight'), self.group).send_message()

    def send_voting_notification_ruler(self):
        Message(self.create_message('RulerMessageVoteNow').format(self.settings.time_vote), self.group).send_message()
        
    def sending_voting_ruler(self):
        text = self.dict_game_texts['howVote']
        markup = InlineKeyboardMarkup()
        for player in self.players:
            if player != self.Ruler_vote:
                if player.alive == True:
                    markup.add(InlineKeyboardButton(player.name,callback_data=f'rulervoting_{player.id}_{player.name}'))    
        vote_message = Message(text,self.Ruler_vote,markup)
        vote_message.send_message()
        self.dict_message_choice_vote.setdefault(self.Ruler_vote ,vote_message)


    def declaring_role_kadkhoda(self, kadkhoda):
        kadkhoda.notify_kadkhoda = False
        Message(self.create_message('MayorReveal', [kadkhoda]), self.group).send_message()

    def remove_join_button(self):
        bot.edit_message_reply_markup(self.message_start_game.receiver.id, self.message_start_game.message_id)
        for msg in self.msgs_for_ann_time:
            bot.edit_message_reply_markup(msg.receiver.id, msg.message_id)

    def check_vote_again(self):
        if self.vote_again:
            self.vote_again = False
            Message(self.create_message('troubleGroupMessageS'), self.group).send_message()
            return True
        else:
            return False

    def def_vote_again(self, trouble):
        trouble.can_vote_agian = False
        self.vote_again = True
        Message(self.create_message('troubleGroupMessage', [trouble]), self.group).send_message()

    def vote_ruler(self, Ruler):
        Ruler.can_Ruler_vote = False
        self.Ruler_vote = Ruler
        Message(self.create_message('RulerNowRul', [Ruler]), self.group).send_message()

    def cancel_of_voting(self, Solh):
        Solh.can_there_solh = False
        self.voting_status = False
        Message(self.create_message('PacifistNoLynch'), self.group).send_message()

    def chech_voting_status(self):
        if self.voting_status:
            return True
        else:
            self.voting_status = True
            return False

    def send_cancel_voting_notification_in_group(self):
        Message(self.create_message('PacifistNoLynchNow'), self.group).send_message()

    def silver_spread(self, Ahangar):
        Ahangar.can_there_spreadsilver = False
        self.wolves_can_attack = False
        Message(self.create_message('BlacksmithSpreadSilver', [Ahangar]), self.group).send_message()

    def actions_vote(self):
        if self.Ruler_vote != False:
            if self.Ruler_vote.vote != None:
                self.Ruler_vote.vote.you_were_killed(self.Ruler_vote, 'voting')
                Message(self.dict_game_texts['RulerKillPl'].format(self.create_tag(self.Ruler_vote.vote), self.roleannouncement(self.Ruler_vote.vote)), self.group).send_message()
            else:
                Message(self.create_message('RuleTimeEnd'), self.group).send_message()
            self.Ruler_vote = False
            return
        
        list_vote = []
        dict_vote = {}
        for playar in self.players:
            if playar.alive == True:
                if playar.vote != None:
                    if playar.role == 'Kadkhoda' and playar.notify_kadkhoda == False:
                        list_vote.append(playar.vote.id)
                        list_vote.append(playar.vote.id)
                        dict_vote.setdefault(playar.vote, [])
                        dict_vote[playar.vote].append(playar)
                    else:
                        list_vote.append(playar.vote.id)
                        dict_vote.setdefault(playar.vote, [])
                        dict_vote[playar.vote].append(playar)
        
        if len(list_vote)==0:
            Message(self.create_message('no_kill'), self.group).send_message()
            return

        if self.settings.voting_secret == 'active':
            if self.settings.name_vote_voting_secret == 'active':
                final_text = ''
                for ply in dict_vote:
                    names_of_voters = ''
                    for voter in dict_vote[ply]:
                        names_of_voters += self.create_tag(voter) + '\n'
                    final_text += self.dict_game_texts['listendvote'].format(len(dict_vote[ply]), self.create_tag(ply), names_of_voters) + '\n'
                Message(final_text, self.group).send_message()
                
            else:
                final_text = ''
                for ply in dict_vote:
                    final_text += self.dict_game_texts['listendvotesecret'].format(len(dict_vote[ply]), self.create_tag(ply)) + '\n'
                Message(final_text, self.group).send_message()
        else:
            final_text = ''
            for ply in dict_vote:
                names_of_voters = ''
                for voter in dict_vote[ply]:
                    names_of_voters += self.create_tag(voter) + '\n'
                final_text += self.dict_game_texts['listendvote'].format(len(dict_vote[ply]), self.create_tag(ply), names_of_voters) + '\n'
            Message(final_text, self.group).send_message()

        frequency = {}
        for item in list_vote:
            if item in frequency:
                frequency[item] += 1
            else:
                frequency[item] = 1

        max_count = 0
        for count in frequency.values():
            if count > max_count:
                max_count = count

        most_frequent_items = [item for item, count in frequency.items() if count == max_count]
        if len(most_frequent_items) > 1:
            Message(self.create_message('no_kill'),self.group).send_message()
        else:
            for i in self.players:
                if i.id == most_frequent_items[0]:
                    if i.role == "Shahzade" and i.save_Shahzade:
                        i.save_Shahzade = False
                        Message(self.create_message('KillShahzade', [i]) ,self.group).send_message()
                    else:
                        # i.alive = False
                        Message(self.dict_game_texts['killed_user'].format(self.create_tag(i), self.roleannouncement(i)), self.group).send_message()
                        i.you_were_killed(i, 'voting')
                        


            # print(f"مقدار با بیشترین تکرار: {most_frequent_items[0]}, تعداد تکرار: {max_count}")

    def check_message_choice_voting(self):
        for player in self.dict_message_choice_vote:
            if player.vote == None:
                self.dict_message_choice_vote[player].edit_message_text(self.dict_game_texts['endTime'])
        # for playar in self.players:
        #     if playar.vote == None:
        #         self.dict_message_choice_vote[playar].edit_message_text(self.dict_game_texts['endTime'])
        #         # Message(self.dict_game_texts['endTime'], playar)


    def votes_returned_to_none(self):
        self.dict_message_choice_vote.clear()
        for playar in self.players:
            if playar.alive == True:
                playar.returned_to_none_vote()



    def sending_voting_dey(self):
        for player in self.players:
            if player.alive == True:
                self.list_voting_for_player(player)

    def list_voting_for_player(self, player_me):
        text = self.dict_game_texts['howVote']
        markup = InlineKeyboardMarkup()
        for player in self.players:
            if player != player_me:
                if player.alive == True:
                    markup.add(InlineKeyboardButton(player.name,callback_data=f'voting_{player.id}_{player.name}'))    
        vote_message = Message(text,player_me,markup)
        vote_message.send_message()
        self.dict_message_choice_vote.setdefault(player_me ,vote_message)



    def add_message_start_game(self,message):
        self.message_start_game = message 

    def add_message_list_player(self,message):
        self.message_list_player = message 

    def return_message_list_player(self):
        return self.message_list_player

    def edit_message_list_player(self):
        text = '#players:\n'
        for player in self.players:
            text += self.create_tag(player) + '\n'
        self.message_list_player.edit_message_text(text)

    def add_playar(self, id, name):
        if self.game_mode=="normal":
            if len(self.players) <= 20:
                if self.active_membership:
                    #name = '' # نام کاربری از دیتابیس برداشته میشود
                    player = Player(id, name, self)
                    self.players.append(player)
                    player.change_status()
                    message = Message(self.dict_game_texts['JoinTheGame'].format(self.group.title),player, InlineKeyboardMarkup_main()) # لینک کردن گروه
                    message.send_message()
                    self.edit_message_list_player()
                    Message(self.create_message('add_player_game',[player]), self.group).send_message()
                    return player
                else:
                    return False
            # بقیه دسته بندی ها
            else:
                return 'number complated'




    def check_message_choice_target(self): # پاک کردن پیام های انتخاب تارگت که در پی وی ارسال شده اند
        for player in self.dict_message_choice_target:
            if player.alive == True:
                if player.grouping == 'cult':
                    if self.invited_again:
                        if player.second_target == None:
                            self.dict_message_choice_target[player].edit_message_text(self.dict_game_texts['endTime'])   
                    else:
                        if player.target == None:
                            self.dict_message_choice_target[player].edit_message_text(self.dict_game_texts['endTime'])
                else:
                    if player.target == None:
                        self.dict_message_choice_target[player].edit_message_text(self.dict_game_texts['endTime'])

    def check_message_choice_target_day(self): # پاک کردن پیام های انتخاب تارگت که در پی وی ارسال شده اند
        if len(self.dict_message_choice_target_day) > 0:
            for player in self.dict_message_choice_target_day:
                # if player.target_day == True:
                if player.alive == True:
                    if player.target == None:
                        self.dict_message_choice_target_day[player].edit_message_text(self.dict_game_texts['endTime'])    

    def check_message_choice_target_for_cult(self): # پاک کردن پیام های انتخاب تارگت که در پی وی ارسال شده اند برای فرقه ها
        for player in self.dict_message_choice_target:
            if player.grouping == 'cult':
                if player.alive == True:
                    if player.target == None:
                        self.dict_message_choice_target[player].edit_message_text(self.dict_game_texts['endTime'])

    def check_message_choice_target_for_wolf(self): # پاک کردن پیام های انتخاب تارگت که در پی وی ارسال شده اند برای گرگ ها
        for player in self.dict_message_choice_target:
            if player.grouping == 'wolf':
                if player.alive == True:
                    if player.target == None:
                        self.dict_message_choice_target[player].edit_message_text(self.dict_game_texts['endTime'])


    def sending_night_actions(self): #ارسال کار هایی که بازیکنان باید انجام دهند
        for player in self.players:
            if player.alive == True:
                if player.new_WolfGorgine == True:
                    Message(self.create_message('BittenTurned'), player).send_message()
                    player.new_WolfGorgine = None
                self.list_target_for_player(player)

    def sending_day_actions(self):
        for player in self.players:
            if player.alive == True:
                self.list_target_day_for_player(player)
                

    def return_the_initial_state(self):
        self.dict_message_choice_target.clear()
        self.group.messages.clear()
        for player in self.players:
            player.initial_state()

    def return_the_initial_state_second(self):
        self.dict_message_choice_target.clear()
        self.group.messages.clear()
        for player in self.players:
            player.initial_state_second()

    def return_the_initial_state_day(self):
        self.dict_message_choice_target_day.clear()
        self.group.messages.clear()
        for player in self.players:
            player.initial_state()

    def analysis_of_events_and_review_of_winning(self):
        list_role_players = []
        list_wolf = []
        list_cult = []
        list_village = []
        list_Qatel = []
        list_vampire = []

        for player in self.players:
            if player.alive == True:
                list_role_players.append([player.role, player])
                if player.grouping == 'Qatel':
                    list_Qatel.append([player.role, player])
                if player.grouping == 'wolf':
                    list_wolf.append([player.role, player])
                if player.grouping == 'cult':
                    list_cult.append([player.role, player])
                if player.grouping == 'village':
                    list_village.append([player.role, player])
                if player.grouping == 'vampire':
                    list_vampire.append([player.role, player])

        number_all = len(list_role_players)
        number_village = len(list_village)
        number_vampire = len(list_vampire)
        number_wolf = len(list_wolf)
        number_cult = len(list_cult)
        number_Qatel = len(list_Qatel)
        print('number_all',number_all,number_village)

        # if 'Qatel' in list_role_players:
        #     if number_all == 1:
        #         Message(self.dict_game_texts['winner_qatel'],self.group).send_message()
        #         self.send_list_winner_in_group('Qatel')
        #         return True
            
        #     elif number_all == 2:
        #         if 
        #         else:
        #             for i in self.players:
        #                 if i.alive == True:
        #                     if i.role != 'Qatel'

        if number_wolf == 0:
            for player in self.players:
                if player.role == 'Khaen':
                    if player.alive:
                        player.change_role_WolfGorgine()
                        Message(self.create_message('TraitorTurnWolf'), player).send_message()

        if number_wolf == 1:
            if list_wolf[0][1].role == 'WhiteWolf':
                for player in self.players:
                    if player.role == 'Khaen':
                        if player.alive:
                            player.change_role_WolfGorgine()
                            Message(self.create_message('TraitorTurnWolf'), player).send_message()
                else:
                    list_wolf[0][1].change_role_WolfGorgine_WhiteWolf()
                    Message(self.create_message('WhiteWolfDeadAllWolf'), list_wolf[0][1]).send_message()

        if len(list_Qatel)>0:
            if len(list_Qatel) == number_all:
                Message(self.dict_game_texts['winner_qatel'],self.group).send_message()
                self.send_list_winner_in_group('Qatel')
                return True

            if len(list_Qatel) == 1 and number_all == 2:
                for i in list_role_players:
                    if i[1].grouping != 'Qatel':
                        if i[1].role == 'kalantar':
                            for b in list_role_players:
                                b[1].alive = False
                            Message(self.dict_game_texts['SKHunterEnd'],self.group).send_message() # همه باختن
                            self.send_list_winner_in_group('hich')
                            return True

                # for c in list_role_players:
                #     if c[1].grouping != 'Qatel':
                #         c[1].alive =False
                # Message(self.dict_game_texts['winner_qatel'],self.group).send_message()
                # self.send_list_winner_in_group('Qatel')
                # return True
            
            if (len(list_Qatel)+1) == number_all:
                Message(self.dict_game_texts['winner_qatel'],self.group).send_message()
                self.send_list_winner_in_group('Qatel')
                return True


        if number_all == number_village:
            Message(self.dict_game_texts['winner_rosta'],self.group , mid_for_copy=random.choice([136,137,138])).send_message()
            self.send_list_winner_in_group('village')
            return True

        if number_Qatel == 0:
            if number_wolf / number_all >= 0.5:
                Message(self.dict_game_texts['winner_wolf'],self.group, mid_for_copy=random.choice([144,145])).send_message()
                self.send_list_winner_in_group('wolf')
                return True

            if number_vampire / number_all >= 0.5:
                Message(self.dict_game_texts['win_vampire'],self.group).send_message()
                self.send_list_winner_in_group('vampire')
                return True

            if number_all == number_cult:
                Message(self.dict_game_texts['winner_ferqeTeem'],self.group).send_message()
                self.send_list_winner_in_group('cult')
                return True 
        
        



    

    def check_night_target(self): 
        list_ferqe = []    
        list_wolf = [] 
        list_vampire = [] 
        list_wolf_target = []
        list_ferqe_target = []
        list_vampire_target = []
        list_none_target = []
        for ply in self.players:
            if ply.grouping == 'vampire':
                list_vampire.append(ply)

        for player in self.players:
            if player.target == None:
                list_none_target.append(player)

            elif player.role == 'fereshte': # فرشته
                self.implementation_action_fereshte(player,player.target)    

            elif player.grouping == 'wolf' and player.role not in ['enchanter','WolfJadogar','WhiteWolf']:
                list_wolf_target.append(player.target)
                list_wolf.append(player)

            elif player.grouping == 'cult':
                if player.role != 'Franc':
                    list_ferqe_target.append(player.target)
                    list_ferqe.append(player)

            elif player.grouping == 'vampire':
                list_vampire_target.append(player.target)
                # list_vampire.append(player)

        for player in self.players: # فرانک
            if player.role == 'IceQueen':
                self.implementation_action_Franc(player) 

        for player in self.players: # ملکه یخ
            if player.role == 'IceQueen':
                self.implementation_action_IceQueen(player) 

        for player in self.players: # عجوزه
            if player.role == 'Honey':
                self.implementation_action_Honey(player) 

        for player in self.players: # پیشگو
            if player.role == 'pishgo':
                self.implementation_action_pishgo(player) 

        for player in self.players: # کاراگاه
            if player.role == 'karagah':
                self.implementation_action_karagah(player) 

        for player in self.players: # پیشگوی نگاتیو
            if player.role == 'ngativ':
                self.implementation_action_ngativ(player) 

        for player in self.players: # پادشاه آتش
            if player.role == 'Firefighter':
                if player.set_fire:
                    self.burning_oiled_houses(player) 

        for player in self.players: # احمق
            if player.role == 'ahmaq':
                self.implementation_action_ahmaq(player)

        for player in self.players: # ناتاشا
            if player.role == 'faheshe':
                self.implementation_action_faheshe(player) 

        for player in self.players: # گرگ سفید
            if player.role == 'WhiteWolf':
                self.implementation_action_WhiteWolf(player) 

        for player in self.players: # قاتل
            if player.role == 'Qatel':
                self.implementation_action_Qatel(player)          

        if len(list_wolf_target)>0:
            wolf_target = self.final_target_wolfs(list_wolf_target)
            self.where_do_wolf(wolf_target)
            self.implementation_action_gorg(list_wolf,wolf_target)
        else:
            wolf_target = None

        if len(list_ferqe_target)>0:
            ferqe_target = self.final_target_ferqe(list_ferqe_target)
            self.where_do_ferqe(ferqe_target)
            self.implementation_action_ferqe(list_ferqe,ferqe_target)
        else:
            ferqe_target = None

        if len(list_vampire_target)>0: # گروه ومپایر
            ferqe_target = self.final_target_vampier(list_vampire_target)
            self.where_do_vampier(ferqe_target)
            self.implementation_action_vampier(list_vampire,ferqe_target)
        else:
            ferqe_target = None

        for player in self.players: # کماندار
            if player.role == 'Archer':
                self.implementation_action_Archer(player)   

        for player in self.players: # شکارچی
            if player.role == 'shekar':
                self.implementation_action_shekar(player)       

        for player in self.players: # پادشاه آتش
            if player.role == 'Firefighter':
                self.implementation_action_Firefighter(player)    

        for player in self.players: # شوالیه
            if player.role == 'Knight':
                self.implementation_action_Knight(player)    


        for player in self.players: # کنت ومپایر
            if player.role == 'kentvampire':
                self.implementation_action_kentvampire(player)   

        for player in self.players: # شیمیدان
            if player.role == 'Chemist':
                self.implementation_action_Chemist(player)  

        for player in self.players: # افسونگر
            if player.role == 'enchanter':
                self.implementation_action_enchanter(player)   
        for player in self.players: # جادوگر
            if player.role == 'WolfJadogar':
                self.implementation_action_WolfJadogar(player) 

    def send_events(self):
        for playar in self.players:
            for msg in playar.messages:
                msg.send_message()
        for msg_group in self.group.messages:
            msg_group.send_message()
        # for player in self.players:
        #     # if player.grouping == 'wolf':
        #     #     if wolf_target == None:
        #     #         # if len(player.home)>1:
        #     #         #     for i in player.home:
        #     #         #         if i.role == 'Qatel':

        #     if player.grouping == 'Qatel':
        #         if player.role == 'Qatel':
        #             if player.target != None:
        #                 dict_target = {}
        #                 for i in player.target.home:
        #                     dict_target.setdefault(i.grouping,[])
        #                     dict_target[i.grouping].append(i) 
        #             else: 
        #                 if len(player.home) > 1:
        #                     dict_target = {}
        #                     for i in player.home:
        #                         dict_target.setdefault(i.grouping,[])
        #                         dict_target[i.grouping].append(i)  

        #             for group in dict_target:
        #                 if group == 'village':
        #                     for ply in group:
        #                         ply.you_were_killed(player)
        #                         dict_messages_sent[self.group]=
        #                 else: 
        #                     random.choice(group).you_were_killed(player)


    # def check_day_target(self):
    #     list_none_target = []
    #     for player in self.players:
    #         if player.target == None:
    #             list_none_target.append(player)
    #         elif player.role == 'tofangdar': # تفنگدار
    #             self.implementation_action_day_tofangdar(player,player.target)    
                                





    def playing_roles(self):
        # درصد ها بر اساس تعداد بازیکنان و نوع بازی مشخص میشود که از هر گروه چند نفر باشند
        dict_vallage = {}
        dict_wolf = {}
        dict_Qatel = {}
        dict_cult = {}
        dict_fire = {}
        dict_Vampire = {}
        if self.game_mode == 'normal':
            # if len(self.players) == 3:
            #     if random.random()<0.5:
            #         dict_vallage = self.roles_village(2)
            #         # dict_cult = self.roles_cult(1) 
            #         # dict_wolf = self.roles_cult(2) 
            #         dict_Qatel = self.roles_wolf(1)
            #     else:
            #         dict_vallage = self.roles_village(2)
            #         # dict_wolf = self.roles_cult(2) 
            #         dict_Qatel = self.roles_wolf(1)

            if len(self.players) == 5:
                if random.random()<0.3:
                    dict_vallage = self.roles_village(4)
                    dict_wolf = self.roles_wolf(1) 
                else:
                    dict_vallage = self.roles_village(4)
                    dict_wolf = self.roles_wolf(1)  

            elif len(self.players) <= 10:
                num = len(self.players)
                dict_vallage = self.roles_village(num-3)
                dict_wolf = self.roles_wolf(2)
                dict_Qatel = self.roles_Qatel(1) 

            elif len(self.players) <= 15:
                num = len(self.players)
                dict_vallage = self.roles_village(num-5)
                dict_wolf = self.roles_wolf(2)
                dict_cult = self.roles_cult(2)
                dict_fire = self.roles_Qatel(1)

            elif len(self.players) > 15:
                num = len(self.players)
                dict_vallage = self.roles_village(num-6)
                dict_wolf = self.roles_wolf(3)
                dict_cult = self.roles_cult(2)
                dict_fire = self.roles_Qatel(1)
                # dict_Vampire = self.roles_Vampire(2)   

        print(dict_vallage)

        dict_all_roles = dict_vallage | dict_wolf | dict_cult | dict_Qatel | dict_fire | dict_Vampire
        print(dict_all_roles)
        for playar in self.players:
            random_role = random.choice(list(dict_all_roles.keys()))
            playar.assign_role(random_role, dict_all_roles[random_role][1], dict_all_roles[random_role][0], dict_all_roles[random_role][2])
            del dict_all_roles[random_role]

    def final_target_vampier(self,list_target):
        frequency = {}
        for item in list_target:
            if item in frequency:
                frequency[item] += 1
            else:
                frequency[item] = 1

        max_count = max(frequency.values())
        most_frequent_items = [key for key, value in frequency.items() if value == max_count]
        if len(most_frequent_items)==1:
            return most_frequent_items[0]
        else:
            return random.choice(most_frequent_items) 


    def final_target_ferqe(self,list_target):
        frequency = {}
        for item in list_target:
            if item in frequency:
                frequency[item] += 1
            else:
                frequency[item] = 1

        max_count = max(frequency.values())
        most_frequent_items = [key for key, value in frequency.items() if value == max_count]
        if len(most_frequent_items)==1:
            return most_frequent_items[0]
        else:
            return random.choice(most_frequent_items)   


    def final_target_wolfs(self,list_target):
        frequency = {}
        for target in list_target:
            if target in frequency:
                frequency[target] += 1
            else:
                frequency[target] = 1

        max_count = max(frequency.values())
        most_frequent_items = [key for key, value in frequency.items() if value == max_count]
        if len(most_frequent_items)==1:
            return most_frequent_items[0]
        else:
            for player in self.players:
                if player.role == 'WolfAlpha' and player.target in most_frequent_items:
                    return player.target
                else:
                    return random.choice(most_frequent_items)


    def where_do_wolf(self,target):
        for player in self.players:       
            if player.grouping == 'wolf' and player.role not in ['enchanter','WolfJadogar','WhiteWolf']:
                if player.target != target:
                    player.not_go_anywhare()
                    
    def where_do_ferqe(self,target):
        for player in self.players:       
            if player.grouping == 'cult':
                if player.role != "Franc":
                    if player.target != target:
                        player.not_go_anywhare()        

    def where_do_vampier(self,target):
        for player in self.players:       
            if player.grouping == 'vampire':
                if player.target != target:
                    player.not_go_anywhare()             
            

    def roles_village(self ,number):
        # اعمال و درصدی که باید انجام شود و بر اساس نوع بازی دیکشنری نقش ها ارسال شود
        if self.game_mode == 'normal':
            print('number',number)
            dict_roles = {}
            type_sub_group = database.select_geoup_by_group_id(self.group.id)[0]['subscription_type']
            list_roles = database.select_roles_by_grouping('village')
            for role in list_roles:
                if role['role_status'] == 'on':
                    check_closed = database.select_closed_roles_for_groups_by_group_id(self.group.id, role['code_role'])
                    if check_closed == []:
                        if type_sub_group == 'free':
                            if role['role_type'] == 'paid':
                                continue
                        dict_roles[role['role']] = [role['role_grouping'], role['role_name'], role['becoming_cult']]
                        
            if len(dict_roles) > number:
                if 'pishgo' in dict_roles:
                    dict_roles.pop('kalantar')
                    dict_roles.pop('Sweetheart')
                    dict_roles.pop('elahe')
                    dict_roles.pop('Chemist')
                    dict_roles.pop('Vahshi')
                    if len(self.players) <= 10:
                        dict_roles.pop('shekar')

                    list_roles_r = list(dict_roles)

                    if len(self.players) > 10:
                        list_roles_r.remove('shekar')
                    list_roles_r.remove('pishgo')
                    if len(self.players) > 10:
                        random_roles = random.sample(list_roles_r , number-2)
                    else:
                        random_roles = random.sample(list_roles_r , number-1)
                    random_roles.append('pishgo')
                    if len(self.players) > 10:
                        random_roles.append('shekar')
                else:
                    random_roles = random.sample(list(dict_roles), number)
                return {role: dict_roles[role] for role in random_roles}
            else:
                return dict_roles

    
    def roles_wolf(self ,number):
        # اعمال و درصدی که باید انجام شود و بر اساس نوع بازی دیکشنری نقش ها ارسال شود
        if self.game_mode == 'normal':
            dict_roles = {}
            type_sub_group = database.select_geoup_by_group_id(self.group.id)[0]['subscription_type']
            list_roles = database.select_roles_by_grouping('wolf')
            for role in list_roles:
                if role['role_status'] == 'on':
                    check_closed = database.select_closed_roles_for_groups_by_group_id(self.group.id, role['code_role'])
                    if check_closed == []:
                        if type_sub_group == 'free':
                            if role['role_type'] == 'paid':
                                continue
                        dict_roles[role['role']] = [role['role_grouping'], role['role_name'], role['becoming_cult']]
            if len(dict_roles) > number:
                dict_roles.pop('WhiteWolf') 
                dict_roles.pop('WolfTolle') 
                if len(self.players) >= 8:
                    random_roles = random.sample(list(dict_roles), number)
                    # random_roles.append('WolfGorgine')
                    # random_roles.append('WolfAlpha')
                else:
                    random_roles = random.sample(list(dict_roles), number)
                    # random_roles.append('WolfGorgine')
                return {role: dict_roles[role] for role in random_roles}
            else:
                return dict_roles
            

    def roles_cult(self ,number):
        # اعمال و درصدی که باید انجام شود و بر اساس نوع بازی دیکشنری نقش ها ارسال شود
        if self.game_mode == 'normal':
            dict_roles = {}
            type_sub_group = database.select_geoup_by_group_id(self.group.id)[0]['subscription_type']
            list_roles = database.select_roles_by_grouping('cult')
            for role in list_roles:
                if role['role_status'] == 'on':
                    check_closed = database.select_closed_roles_for_groups_by_group_id(self.group.id, role['code_role'])
                    if check_closed == []:
                        if type_sub_group == 'free':
                            if role['role_type'] == 'paid':
                                continue
                        dict_roles[role['role']] = [role['role_grouping'], role['role_name'], role['becoming_cult']]
            if len(dict_roles) > number:
                dict_roles.pop('Franc')
                random_roles = random.sample(list(dict_roles), number)
                return {role: dict_roles[role] for role in random_roles}
            else:
                return dict_roles


            # return {'ferqe':['cult',self.dict_game_texts['role_ferqe_n'], 1],
            #         'Royce':['cult',self.dict_game_texts['role_Royce_n'], 1]}   
 
    def roles_Qatel(self ,number):
        if self.game_mode == 'normal':
            dict_roles = {}
            type_sub_group = database.select_geoup_by_group_id(self.group.id)[0]['subscription_type']
            list_roles = database.select_roles_by_grouping('Qatel')
            for role in list_roles:
                if role['role_status'] == 'on':
                    check_closed = database.select_closed_roles_for_groups_by_group_id(self.group.id, role['code_role'])
                    if check_closed == []:
                        if type_sub_group == 'free':
                            if role['role_type'] == 'paid':
                                continue
                        dict_roles[role['role']] = [role['role_grouping'], role['role_name'], role['becoming_cult']]
            if len(dict_roles) > number:
                dict_roles.pop('Archer')
                random_roles = random.sample(list(dict_roles), number)

                return {role: dict_roles[role] for role in random_roles}
            else:
                return dict_roles
            

    def roles_Vampire(self ,number):
        if self.game_mode == 'normal':
            dict_roles = {}
            type_sub_group = database.select_geoup_by_group_id(self.group.id)[0]['subscription_type']
            list_roles = database.select_roles_by_grouping('vampire')
            for role in list_roles:
                if role['role_status'] == 'on':
                    check_closed = database.select_closed_roles_for_groups_by_group_id(self.group.id, role['code_role'])
                    if check_closed == []:
                        if type_sub_group == 'free':
                            if role['role_type'] == 'paid':
                                continue
                        dict_roles[role['role']] = [role['role_grouping'], role['role_name'], role['becoming_cult']]
            if len(dict_roles) > number:
                random_roles = random.sample(list(dict_roles), number-1)
                random_roles.append('Vampire')

                return {role: dict_roles[role] for role in random_roles}
            else:
                return dict_roles



    def roles_fire(self,number):
        # اعمال و درصدی که باید انجام شود و بر اساس نوع بازی دیکشنری نقش ها ارسال شود
        if self.game_mode == 'normal':
            return {'Firefighter':['fire',self.dict_game_texts['role_Firefighter_n'], 0],
                    'Archer':['fire',self.dict_game_texts['role_Archer_n'], 0]}    

    def implementation_action_Honey(self, Honey):
        if Honey.target != None:
            Honey.targer.fake_role = 'WolfGorgine'


    def implementation_action_IceQueen(self, IceQueen):
        if IceQueen.target != None:
            IceQueen.target.initial_state()
            


    def implementation_action_Franc(self, Franc):
        if Franc.target != None:
            if self.is_there_cult():
                Franc.target.save_Franc = True
                # if Franc.target.oil_spraying:
                #     Franc.target.oil_spraying = False
                #     Franc.messages = Message(self.create_message('AngelInHomeForAngel', [Franc.target]),Franc)

            else:
                Franc.target.you_were_killed(Franc)
                self.group.messages = Message(self.create_message('FrancKillGroupMessage').format(self.create_tag(Franc.target), self.roleannouncement(Franc.target)), self.group)
                Franc.target.messages = Message(self.create_message('FrancKillPlayerMessage'), Franc.target)
                
                

    def implementation_action_pishgo(self, pishgo):
        if pishgo.target != None:
            if pishgo.target.fake_role == None:
                if pishgo.target.role == 'Wolfx':
                    pishgo.messages = Message(self.dict_game_texts['Searsee'].format(self.create_tag(pishgo.target), "شاهزاده🤴🏻"), pishgo)  
                elif pishgo.target.role == 'Gorgname':
                    pishgo.messages = Message(self.dict_game_texts['Searsee'].format(self.create_tag(pishgo.target), "گرگینه🐺"), pishgo)
                elif pishgo.target.role == 'Khaen':
                    if random.random() < 0.5:
                        pishgo.messages = Message(self.dict_game_texts['Searsee'].format(self.create_tag(pishgo.target), "روستایی‌ساده👨🏻"), pishgo) 
                    else:
                        pishgo.messages = Message(self.dict_game_texts['Searsee'].format(self.create_tag(pishgo.target), "گرگینه🐺"), pishgo) 
                else:
                    pishgo.messages = Message(self.dict_game_texts['Searsee'].format(self.create_tag(pishgo.target), pishgo.target.role_name), pishgo) 

            else:
                if pishgo.target.fake_role == 'WolfGorgine':
                    pishgo.messages = Message(self.dict_game_texts['Searsee'].format(self.create_tag(pishgo.target), "گرگینه🐺"), pishgo) 

    def implementation_action_karagah(self, karagah):
        if karagah.target != None:
            if karagah.target.fake_role == None:
                karagah.messages = Message(self.create_message('DetectiveSnoop').format(self.create_tag(karagah.target), karagah.target.role_name), karagah)  
                if karagah.target.grouping == "wolf":
                    if random.random() < 0.4:
                        for player in self.players:
                            if player.grouping == "wolf":
                                player.messages = Message(self.create_message('KaragahSForWolf', [karagah]), player)
            else:
                karagah.messages = Message(self.create_message('DetectiveSnoop').format(self.create_tag(karagah.target), "گرگینه🐺"), karagah)


    def implementation_action_Chemist(self, Chemist):
        if Chemist.target != None:
            if Chemist.target.alive:
                if Chemist.target.role == 'Sweetheart':
                    Chemist.target.fallling_in_love_Sweetheart(Chemist) 
                    Chemist.target.messages = Message(self.create_message('MsgLoveSweetHeart', [Chemist]), Chemist.target)
                    Chemist.messages = Message(self.create_message('msgforchemi', [Chemist.target]), Chemist)
                    return

                elif Chemist.target.role == "Qatel":
                    Chemist.you_were_killed(Chemist.target)
                    Chemist.messages = Message(self.create_message('ChemistSK', [Chemist.target]), Chemist) 
                    Chemist.target.messages = Message(self.create_message('ChemistVisitYouSK', [Chemist]), Chemist.target)
                    self.group.messages = Message(self.create_message('ChemistSKPublic',[Chemist]), self.group)

                else:
                    if random.random() <= 0.5:
                        Chemist.target.you_were_killed(Chemist)
                        Chemist.messages = Message(self.create_message('ChemistSuccess', [Chemist.target]), Chemist) 
                        Chemist.target.messages = Message(self.create_message('ChemistVisitYouSuccess'), Chemist.target)
                        self.group.messages = Message(self.create_message('ChemistSuccessPublic').format(self.create_tag(Chemist.target), self.roleannouncement(Chemist.target)), self.group) 
                    else:
                        Chemist.you_were_killed(Chemist.target)
                        Chemist.messages = Message(self.create_message('ChemistFail', [Chemist.target]), Chemist) 
                        Chemist.target.messages = Message(self.create_message('ChemistVisitYouFail', [Chemist]), Chemist.target)
                        self.group.messages = Message(self.create_message('ChemistFailPublic',[Chemist]), self.group) 

            else:
                Chemist.messages = Message(self.create_message('ChemistTargetDead', [Chemist.target]), Chemist)
            
    def implementation_action_ngativ(self, ngativ):
        list_player_live = []
        if ngativ.target != None:
            check = False
            for ply in self.players:
                if ply != ngativ:
                    if ply != ngativ.target:
                        if ply not in ngativ.list_announced_roles:
                            if ply.alive:
                                list_player_live.append(ply)
                                check = True
            if check:
                print(list_player_live)
                random_role = random.choice(list_player_live)
                print(random_role)
                ngativ.list_announced_roles.append(random_role)
                # ngativ.messages = Message(self.create_message('NegSeerSees', [random_role]), ngativ)  
                ngativ.messages = Message(self.dict_game_texts['NegSeerSees'].format(self.create_tag(ngativ.target), self.roleannouncement(random_role)), ngativ)  
            else:
                ngativ.messages = Message(self.create_message('No_role'), ngativ)  


          
    def implementation_action_ahmaq(self, ahmaq):
        if ahmaq.target != None:
            list_roles = []
            for ply in self.players:
                if ply != ahmaq:
                    list_roles.append(ply)
            random_role = random.choice(list_roles)
            ahmaq.messages = Message(self.dict_game_texts['Searsee'].format(self.create_tag(ahmaq.target), random_role.role_name), ahmaq)  

    def implementation_action_faheshe(self,faheshe):
        if faheshe.target != None:
            if faheshe.target.role == 'Sweetheart':
                faheshe.target.fallling_in_love_Sweetheart(faheshe) 
                faheshe.target.messages = Message(self.create_message('MsgLoveSweetHeart', [faheshe]), faheshe.target)
                faheshe.messages = Message(self.create_message('MsgPlayerFHLoved', [faheshe.target]), faheshe)
                return

            if faheshe.target.grouping == 'wolf' and faheshe.target.role not in ['enchanter', 'WolfJadogar']:
                faheshe.you_were_killed(faheshe.target)
                faheshe.messages = Message(self.create_message('HarlotFuckWolf', [faheshe.target]), faheshe)
                self.group.messages = Message(self.create_message('HarlotEaten', [faheshe]), self.group)

            elif faheshe.target.role == 'Qatel':
                faheshe.you_were_killed(faheshe.target)
                faheshe.messages = Message(self.create_message('HarlotFuckKiller', [faheshe.target]),faheshe)
                self.group.messages = Message(self.create_message('FahesheInKiller', [faheshe]), self.group)

            elif faheshe.target.grouping == 'cult':
                faheshe.messages = Message(self.create_message('HarlotDiscoverCult', [faheshe.target]),faheshe)

            elif faheshe.target.role == 'Bloodthirsty':
                if random.random() < 0.5:
                    faheshe.change_role_vampier()
                    faheshe.messages = Message(self.create_message('bloodConvertNatasha', [faheshe.target]),faheshe)
                    for ply in self.players:
                        if ply.grouping == 'vampire':
                            if ply.alive:
                                ply.messages = Message(self.create_message('bloodConvertMessageNatasha', [faheshe, faheshe.target]), ply)
                else:
                    faheshe.you_were_killed(faheshe.target)
                    faheshe.messages = Message(self.create_message('BloodKillNatashaMessage', [faheshe.target]),faheshe)
                    self.group.messages = Message(self.create_message('BloodKillNatasha', [faheshe]), self.group)
                    

            else:
                faheshe.messages = Message(self.create_message('HarlotVisitNonWolf', [faheshe.target]),faheshe) 
                faheshe.target.messages = Message(self.create_message('HarlotVisitYou'),faheshe.target)


    def implementation_action_fereshte(self,fereshte,target):
        
        if fereshte.target.role == 'Sweetheart':
            fereshte.target.fallling_in_love_Sweetheart(fereshte) 
            fereshte.target.messages = Message(self.create_message('MsgLoveSweetHeart', [fereshte]), fereshte.target)
            fereshte.messages = Message(self.create_message('msgforfereshte', [fereshte.target]), fereshte)
            return

        elif target.grouping == 'wolf' and target.role not in ['enchanter','WolfJadogar']:
            if random.random() < 0.5:
                fereshte.you_were_killed(target)
                fereshte.messages = Message(self.create_message('GuardWolf'),fereshte)
                self.group.messages = Message(self.create_message('GAGuardedWolf',[fereshte]),self.group)
            else:  
                fereshte.messages = Message(self.create_message('GuardEmptyHouse',[target]),fereshte)


        elif target.role == 'Qatel': # قاتل رو سیو بده
            fereshte.you_were_killed(target)
            fereshte.messages = Message(self.create_message('GuardKiller'),fereshte)
            self.group.messages = Message(self.create_message('GAGuardedKiller',[fereshte]),self.group)

        elif fereshte.target.role == 'Bloodthirsty':
            if random.random() < 0.5:
                fereshte.change_role_vampier()
                fereshte.messages = Message(self.create_message('bloodConvertFereshte', [fereshte.target]),fereshte)
                for ply in self.players:
                    if ply.grouping == 'vampire':
                        if ply.alive:
                            ply.messages = Message(self.create_message('bloodConvertMessage', [fereshte, fereshte.target]), ply)
            else:
                fereshte.you_were_killed(fereshte.target)
                fereshte.messages = Message(self.create_message('BloodKillAngelMessage', [fereshte.target]),fereshte)
                self.group.messages = Message(self.create_message('BloodKillAngel', [fereshte]), self.group)

        else:
            target.save_fereshte = True
            if target.oil_spraying:
                target.oil_spraying = False
                fereshte.messages = Message(self.create_message('AngelInHomeForAngel', [target]),fereshte)


    def implementation_action_WhiteWolf(self, WhiteWolf):
        if WhiteWolf.target != None:
            WhiteWolf.target.save_WhiteWolf = True

    def implementation_action_Qatel(self, Qatel):
        if Qatel.target != None:

            if Qatel.target.role == 'Sweetheart':
                Qatel.target.fallling_in_love_Sweetheart(Qatel) 
                Qatel.messages = Message(self.create_message('MsgPlayerSKLoved', [Qatel.target]), Qatel)
                Qatel.target.messages = Message(self.create_message('msgforswit', [Qatel]),Qatel.target)
                return

            elif Qatel.target.save_WhiteWolf:
                Qatel.messages = Message(self.create_message('WhiteGourdKillerMessage',[Qatel.target]), Qatel)
                Qatel.target.messages = Message(self.create_message('WolfMessageGourdWhiteWolf'), Qatel.target)
                for ply in self.players:
                    if ply.role == 'WhiteWolf':
                        ply.messages = Message(self.create_message('WhiteGourdKiller', [Qatel.target]), ply)
                return

            elif Qatel.target.save_Franc:
                Qatel.messages = Message(self.create_message('FrancGourdKillerMessage',[Qatel.target]), Qatel)
                Qatel.target.messages = Message(self.create_message('PlayerMessageFrancS'), Qatel.target)
                for ply in self.players:
                    if ply.role == 'Franc':
                        ply.messages = Message(self.create_message('KillerICult', [Qatel.target]), ply)
                return

            elif Qatel.target.save_fereshte == False: # در هر صورت تارگت را میکشد
                if Qatel.target.role == 'Ahangar':
                    Qatel.target.you_were_killed(Qatel)
                    Qatel.target.messages = Message(self.create_message('SerialKillerKilledYouTow'), Qatel.target)
                    self.group.messages = Message(self.create_message('BlacksmithKilled', [Qatel.target]), self.group)
           
                elif Qatel.target.role == 'Mast':
                    Qatel.target.you_were_killed(Qatel)
                    Qatel.target.messages = Message(self.create_message('SerialKillerKilledYouTow'), Qatel.target)
                    self.group.messages = Message(self.create_message('DrunkKilled', [Qatel.target]), self.group)

                else:
                    Qatel.target.you_were_killed(Qatel)
                    Qatel.target.messages = Message(self.create_message('SerialKillerKilledYouTow') ,Qatel.target)
                    self.group.messages = Message(self.dict_game_texts['DefaultKilled'].format(self.create_tag(Qatel.target), self.roleannouncement(Qatel.target)),self.group)

            else:
                Qatel.messages =  Message(self.create_message('GuardBlockedKiller',[Qatel.target]), Qatel)
                Qatel.target.messages = Message(self.create_message('GuardSavedYou'), Qatel.target)

                for i in self.players:
                    if i.role == 'fereshte':
                        i.messages = Message(self.create_message('GuardSaved',[Qatel.target]), i)
            
            list_wolf_in_home_target = []
            list_ferqe_in_home_target = []
            list_rosta_in_home_target = []

            for i in Qatel.target.home:
                if i != Qatel.target:
                    if i.grouping == 'wolf' and i.role not in ['enchanter','WolfJadogar']:
                        if i.alive == True:
                            list_wolf_in_home_target.append(i)

                    elif i.grouping == 'cult':
                        if i.alive == True:
                            list_ferqe_in_home_target.append(i)

                    elif i.grouping == 'village':
                        if i.alive == True:
                            list_rosta_in_home_target.append(i)

            if len(list_wolf_in_home_target) != 0:  # اینجا باید درست بشه
                victim=random.choice(list_wolf_in_home_target)       
                victim.you_were_killed(Qatel)
                self.group.messages = Message(self.dict_game_texts['SerialKillerKilledWolf'].format(self.create_tag(victim),self.roleannouncement(victim)), self.group)


            if len(list_ferqe_in_home_target) != 0:
                victim=random.choice(list_ferqe_in_home_target)
                victim.you_were_killed(Qatel)
                self.group.messages = Message(self.dict_game_texts['SerialKillerKilledferqe'].format(self.create_tag(victim),self.roleannouncement(victim)), self.group)

            if len(list_rosta_in_home_target) != 0:
                for b in list_rosta_in_home_target:
                    if b.role == 'faheshe':
                        b.you_were_killed(Qatel)
                        self.group.messages = Message(self.create_message('HarlotFuckedKilledPublic', [b, Qatel.target]), self.group)
                    # else:
                    #     b.you_were_killed(Qatel)
                    #     self.group.messages = Message(self.dict_game_texts['SerialKillerKilledWolf'].format(self.create_tag(victim),self.roleannouncement(victim)),self.group)



    def implementation_action_gorg(self,list_gorg,target):
        list_gorg_alive = []
        for gorg in list_gorg:
            if gorg.alive == True:
                print('wooolf', gorg.role)
                list_gorg_alive.append(gorg)
        if list_gorg_alive == []:
            list_gorg_alive = list_gorg
        if target.alive == True:
            if len(list_gorg_alive) > 0:
                random_wolf = random.choice(list_gorg_alive)
                if target.role == 'Sweetheart':
                    if target.love != None:
                        if target.love.grouping == 'wolf':
                            target.you_were_killed(random.choice(list_gorg_alive))
                            self.group.messages = Message(self.dict_game_texts['wolfEat'].format(self.create_tag(target), self.roleannouncement(target)), self.group)
                            target.messages = Message(self.create_message('eat_you'), target) 
                            return
                        else:
                            target.fallling_in_love_Sweetheart(random_wolf) 
                            random_wolf.messages = Message(self.create_message('MsgWolfPlayerLoverWolfs', [target]), random_wolf)
                            list_gorg_alive.remove(random_wolf)
                            for wolf in list_gorg_alive:
                                wolf.messages = Message(self.create_message('MsgWolfs', [target]), wolf)
                            target.messages = Message(self.create_message('msgforswit', [random_wolf]), target)
                            return
                    else:
                        target.fallling_in_love_Sweetheart(random_wolf) 
                        random_wolf.messages = Message(self.create_message('MsgWolfPlayerLoverWolfs', [target]), random_wolf)
                        list_gorg_alive.remove(random_wolf)
                        for wolf in list_gorg_alive:
                            wolf.messages = Message(self.create_message('MsgWolfs', [target]), wolf)
                        target.messages = Message(self.create_message('msgforswit', [random_wolf]), target)
                        return



            if target.save_Franc:
                for wolf in list_gorg:
                    wolf.messages = Message(self.create_message('FrancGourdWolfMessageGroup',[target]), wolf)
                target.messages = Message(self.create_message('PlayerMessageFrancS'), target)
                for ply in self.players:
                    if ply.role == 'Franc':
                        ply.messages = Message(self.create_message('WolfAttackCult', [target]), ply)
                return






            if target.save_fereshte == False:
                if target.role == 'Qatel':
                    if len(list_gorg_alive) > 0:
                        victim=random.choice(list_gorg_alive) #کشته شدن یک گرگ به صورت رندوم به دلیل حمله به قاتل 
                        victim.you_were_killed(target) 
                        self.group.messages = Message(self.dict_game_texts['SerialKillerKilledWolf'].format(self.create_tag(victim), self.roleannouncement(victim)) ,self.group)# ارسال پیام کشته شدن گرگ توسط قاتل با انتخاب اشتباه گرگ

                elif target.role == 'rishSefid':
                    if target.first_eat == False:
                        target.first_eat = True
                        for wolf in list_gorg:
                            wolf.messages = Message(self.create_message('EatRishSefidTotal',[target]), wolf)
                        target.messages = Message(self.create_message('EatRishSefidWolf'), target)
                    else:
                        target.you_were_killed(random.choice(list_gorg_alive)) 
                        self.group.messages = Message(self.dict_game_texts['wolfEat'].format(self.create_tag(target), self.roleannouncement(target)), self.group)
                        target.messages = Message(self.create_message('eat_you'), target)

                elif target.role == 'enchanter':
                    target.you_were_killed(random.choice(list_gorg_alive)) 
                    self.group.messages = Message(self.create_message('EatenEnchanter',[target]), self.group)
                    target.messages = Message(self.create_message('eat_you'), target)

                elif target.role == 'WolfJadogar':
                    target.you_were_killed(random.choice(list_gorg_alive)) 
                    self.group.messages = Message(self.create_message('SorcererEaten',[target]), self.group)
                    target.messages = Message(self.create_message('eat_you'), target)

                elif target.role == 'Mast':
                    self.wolves_can_attack = False
                    target.you_were_killed(random.choice(list_gorg_alive)) 
                    self.group.messages = Message(self.create_message('RoleMast_eat',[target]), self.group)
                    target.messages = Message(self.create_message('eat_you'), target)
                    for player in self.players:
                        if player.alive:
                            if player.grouping == 'wolf':
                                player.messages = Message(self.create_message('mastEatWolfGR', [target]), player) 

                elif target.role == 'NefrinShode':
                    target.change_role_WolfGorgine()
                    for player in self.players:
                        if player.alive:
                            if player.grouping == 'wolf':
                                player.messages = Message(self.create_message('eat_nefrinForWolf', [target]), player) 
                    target.messages = Message(self.create_message('eat_nefrin'), target)
                    target.messages = Message(self.create_message('WolfTeam').format(self.text_get_teammates(target)), target)


                elif target.role == 'Bloodthirsty':
                    random_wolf = random.choice(list_gorg_alive)
                    if random.random() < 0.5:
                        random_wolf.change_role_vampier()
                        random_wolf.messages = Message(self.create_message('bloodConvertFereshte', [target]),random_wolf)
                        for ply in self.players:
                            if ply.grouping == 'vampire':
                                if ply.alive:
                                    ply.messages = Message(self.create_message('bloodConvertMessage', [random_wolf, target]), ply)
                    else:
                        random_wolf.you_were_killed(target)
                        random_wolf.messages = Message(self.create_message('BloodKillAngelMessage', [target]),random_wolf)
                        self.group.messages = Message(self.create_message('BloodKillAngel', [random_wolf]), self.group)

                else:
                    wolves_kill = False
                    WolfAlpha = False
                    for player in self.players:
                        if player.role == 'WolfAlpha':
                            if player.alive:
                                WolfAlpha = player
                    if WolfAlpha != False:
                        if target.bewitched:
                            becomewolf = 0.5
                        else:
                            becomewolf = 0.2
                        if random.random() < becomewolf: # اگه آلفا گازش بگیره
                            target.change_role_WolfGorgine()
                            WolfAlpha.messages = Message(self.create_message('PlayerBittenWolf',[target]), WolfAlpha)
                            for ply in self.players:
                                if ply.grouping == 'wolf' and ply.role not in ['enchanter','WolfJadogar']:
                                    if ply.alive:
                                        if ply != target:
                                            ply.messages = Message(self.create_message('PlayerBittenWolves',[target, WolfAlpha]) ,ply)
                            target.messages = Message(self.create_message('PlayerBitten'), target)

                        else:
                            wolves_kill = True

                    elif target.bewitched:
                        if random.randint() < 0.3:
                            target.change_role_WolfGorgine()
                            for ply in self.players:
                                if ply.grouping == 'wolf' and ply.role not in ['enchanter','WolfJadogar']:
                                    if ply.alive:
                                        if ply != target:
                                            ply.messages = Message(self.create_message('EnchanterPlayerBitten',[target]), ply)
                            target.messages = Message(self.create_message('EnchanterPlayerBittenOk'), target)
                        else:
                            wolves_kill = True

                    else:
                        wolves_kill = True

                    if wolves_kill:
                        if target.role == 'PishRezerv':
                            target.you_were_killed(random.choice(list_gorg_alive))
                            self.group.messages = Message(self.create_message('ApprenticeSeerEaten', [target]), self.group)
                            target.messages = Message(self.create_message('eat_you'), target)    

                        elif target.role == 'ahmaq':
                            target.you_were_killed(random.choice(list_gorg_alive))
                            self.group.messages = Message(self.create_message('RoleAhmag_eat', [target]), self.group)
                            target.messages = Message(self.create_message('eat_you'), target)  

                        elif target.role == 'karagah':
                            target.you_were_killed(random.choice(list_gorg_alive))
                            self.group.messages = Message(self.create_message('roleKaragh_eat', [target]), self.group)
                            target.messages = Message(self.create_message('eat_you'), target)   

                        else:
                            target.you_were_killed(random.choice(list_gorg_alive))
                            self.group.messages = Message(self.dict_game_texts['wolfEat'].format(self.create_tag(target), self.roleannouncement(target)), self.group)
                            target.messages = Message(self.create_message('eat_you'), target) 
                # elif target.role == 'kalantar':
                #     target.you_were_killed(list_gorg)


            
            else:
                # self.group.messages = Message(self.create_message('is_angelWolf',[target]),self.group)
                target.messages = Message(self.create_message('GuardSavedYou'),target)
                for i in self.players:
                    if i.role == 'fereshte':
                        i.messages = Message(self.create_message('GuardSaved',[target]),i)
            



            if target.alive == False:
                for ply in target.home:
                    if ply.role == 'faheshe' and target != ply:
                        ply.you_were_killed(random.choice(list_gorg_alive))
                        self.group.messages = Message(self.create_message('HarlotFuckedVictimPublic', [ply, target]),self.group)
        else:
            for ply in self.players:
                if ply.grouping == 'wolf' and ply.role not in ['enchanter','WolfJadogar']:
                    ply.messages = Message(self.create_message('dedaftervisitwolf',[target]),ply)



    def implementation_action_ferqe(self,list_ferqe,target):
        if target.grouping == 'cult':
            print("خئدش فرقست عزیزم")
            return
        list_ferqe_alive = []
        for ferqe in list_ferqe:
            if ferqe.alive == True:
                list_ferqe_alive.append(ferqe)

        if len(list_ferqe_alive) == 0:
            return
        elif len(list_ferqe_alive) == 1:
            list_ferqe_alive_ = list_ferqe_alive
        else:
            list_ferqe_alive_ = []
            for i in list_ferqe_alive:
                if i.role != 'Royce':
                    list_ferqe_alive_.append(i)

        new_cult = None
        for ferqe in list_ferqe_alive_:
            if ferqe.new_cult == True:
                new_cult = ferqe
            # if ferqe.alive == True:
            #     list_ferqe_alive.append(ferqe)
        
        if new_cult == None:
            # if len(list_ferqe_alive) == 0:
            #     ferqe_caller = random.choice(list_ferqe)
            # else:
            ferqe_caller = random.choice(list_ferqe_alive_)
        else:
            ferqe_caller = new_cult

        ferqe_caller.new_cult = False # دیگه فرقه جدید حساب نمیشه

        print('ferqe_caller', ferqe_caller.role, ferqe_caller.role_name)
        if target.alive == True:
            if target.becoming_cult != 0: # فرقه میشود یا نه
                if target.role == 'Sweetheart':
                    if target.love != None:
                        if target.love.grouping == 'cult':
                            for cult in self.players:
                                if cult.grouping == 'cult':
                                    if cult.alive:
                                        cult.messages = Message(self.create_message('CultJoin',[target]),cult)
                            target.change_role_cult()
                            target.messages = Message(self.create_message('CultConvertYou'), target)
                            target.messages = Message(self.create_message('role_ferqe_team').format(self.text_get_teammates(ferqe_caller)), target)
                            return

                        else:
                            target.fallling_in_love_Sweetheart(ferqe_caller)
                            if len(list_ferqe) > 1:
                                ferqe_caller.messages = Message(self.create_message('MsgPlayerCultsLoved', [target]), ferqe_caller)
                            else:
                                ferqe_caller.messages = Message(self.create_message('MsgPlayerCultLoved', [target]), ferqe_caller)
                            for cult in list_ferqe_alive:
                                cult.messages = Message(self.create_message('MsgPlayerLoveCultsMessage', [ferqe_caller, target]),cult)
                            target.messages = Message(self.create_message('msgforswit', [ferqe_caller]), target)
                            return

                    else:
                        target.fallling_in_love_Sweetheart(ferqe_caller)
                        if len(list_ferqe) > 1:
                            ferqe_caller.messages = Message(self.create_message('MsgPlayerCultsLoved', [target]), ferqe_caller)
                        else:
                            ferqe_caller.messages = Message(self.create_message('MsgPlayerCultLoved', [target]), ferqe_caller)
                        for cult in list_ferqe_alive:
                            cult.messages = Message(self.create_message('MsgPlayerLoveCultsMessage', [ferqe_caller, target]),cult)
                        target.messages = Message(self.create_message('msgforswit', [ferqe_caller]), target)
                        return

                if target.role == 'fereshte' or target.role == 'faheshe' and target.where != None: # نقش هایی که ممکن است خانه نباشند
                    for cult in self.players:
                        if cult.grouping == 'cult':
                            if cult == ferqe_caller:
                                cult.messages = Message(self.create_message('CultVisitEmptyOne',[target]), cult)
                            else:
                                if cult.alive:
                                    cult.messages = Message(self.create_message('CultVisitEmpty',[ferqe_caller, target]), cult)
                    return

                if random.random() <= target.becoming_cult:# اگر دعوت را قبول کرد
                    for cult in self.players:
                        if cult.grouping == 'cult':
                            if cult.alive:
                                cult.messages = Message(self.create_message('CultJoin',[target]),cult)
                    target.change_role_cult()
                    target.messages = Message(self.create_message('CultConvertYou'), target)
                    target.messages = Message(self.create_message('role_ferqe_team').format(self.text_get_teammates(ferqe_caller)), target)



                else: # دعوت رو قبول نکرد
                    if target.role == 'kalantar':
                        if random.random() <= 0.25:
                            self.group.messages = Message(self.create_message('CultConvertHunter',[ferqe_caller,target]), self.group)
                        else:
                            for cult in self.players:
                                if cult.grouping == 'cult':
                                    if cult == ferqe_caller:
                                        cult.messages = Message(self.create_message('CultVisitAttempOne',[target]), cult)
                                    else:
                                        if cult.alive:
                                            cult.messages = Message(self.create_message('CultVisitAttemp',[ferqe_caller, target]), cult)
                            target.messages = Message(self.create_message('CultAttempt'),target) 

                    else:
                        for cult in self.players:
                            if cult.grouping == 'cult':
                                print(cult.role, ferqe_caller.role,target.role)
                                if cult == ferqe_caller:
                                    cult.messages = Message(self.create_message('CultVisitAttempOne',[target]),cult)
                                else:
                                    if cult.alive:
                                        cult.messages = Message(self.create_message('CultVisitAttemp',[ferqe_caller, target]), cult)

                        target.messages = Message(self.create_message('CultAttempt'), target) 

            else: # تارگت فرقه را میکشد یا نه
                if target.grouping == 'wolf' and target.role not in ['enchanter','WolfJadogar']:
                    if ferqe_caller.alive == True:
                        ferqe_caller.you_were_killed(target)
                        self.group.messages = Message(self.create_message('CultConvertWolfPublic',[ferqe_caller]), self.group)
                    else:
                        pass
                        # خود فرقه قبلا مرده و چه پیامی باید ارسال بشه؟


                 # فرقه ومپایر دعوت کنه
                # elif target.grouping == 'vampire':
                #     if ferqe_caller.alive:
                #         if random.random() < 0.5:
                        
                #         else:

                        
                #     else:
                #         pass
                    
                elif target.role == 'Qatel':
                    if ferqe_caller.alive == True:
                        ferqe_caller.you_were_killed(target)
                        self.group.messages = Message(self.create_message('CultConvertKillerPublic',[ferqe_caller]), self.group)
                    else:
                        pass
                        # خود فرقه قبلا مرده و چه پیامی باید ارسال بشه؟

                elif target.role == 'shekar':
                    if ferqe_caller.alive == True:
                        ferqe_caller.you_were_killed(target)
                        self.group.messages = Message(self.create_message('CultConvertKillerPublic',[ferqe_caller, target]), self.group)
                    else:
                        pass      


                elif target.role == 'Bloodthirsty':
                    # random_wolf = random.choice(list_gorg_alive)
                    if ferqe_caller.alive:
                        if random.random() < 0.5:
                            ferqe_caller.change_role_vampier()
                            ferqe_caller.messages = Message(self.create_message('PlayerMessageConvertToVampire', [target]),ferqe_caller)
                            for ply in self.players:
                                if ply.alive:
                                    if ply.grouping == 'vampire':
                                        ply.messages = Message(self.create_message('VampireMessageCultConvert', [ferqe_caller]), ply)
                                    elif ply.grouping == 'cult':
                                        ply.messages = Message(self.create_message('BloodthirstyCultMessageConvert', [ferqe_caller, target]), ply)
                        else:
                            ferqe_caller.you_were_killed(target)
                            ferqe_caller.messages = Message(self.create_message('cult_caller_vampire', [target]),ferqe_caller)
                            self.group.messages = Message(self.create_message('GroupMessageDeadCult', [ferqe_caller]), self.group)


        else: # کشته  شده بود
            for cult in self.players:
                if cult.grouping == 'cult':
                    if cult == ferqe_caller:
                        cult.messages = Message(self.create_message('CultVisitDeadOne', [target]), cult)
                    else:
                        if cult.alive:
                            cult.messages = Message(self.create_message('CultVisitDead', [ferqe_caller, target]), cult)

    def implementation_action_vampier(self,list_vampire,target):
        if target != None:
            # choesed_vampire = random.choice(list_vampire)
            Bloodthirsty = None
            for vampire in list_vampire:
                if vampire.role == 'Bloodthirsty':
                    Bloodthirsty = vampire
            
            if target.save_Franc:
                for vampire in list_vampire:
                    vampire.messages = Message(self.create_message('FrancGourdVampireMessageGroup',[target]), vampire)
                target.messages = Message(self.create_message('PlayerMessageFrancS'), target)
                for ply in self.players:
                    if ply.role == 'Franc':
                        ply.messages = Message(self.create_message('VampireCult', [target]), ply)
                return


            if self.is_vampire_imprisoned:
                list_vampire = []
                Bloodthirsty = ''
                for vampire in list_vampire:
                    if vampire.role != 'Bloodthirsty':
                        list_vampire.append(vampire)
                    else:
                        Bloodthirsty = vampire

                choesed_vampire = random.choice(list_vampire)

                if target.role == 'kalantar' and Bloodthirsty.alive:
                    target.you_were_killed(choesed_vampire)
                    choesed_vampire.messages = Message(self.create_message('FindeVampire',[target]),choesed_vampire)
                    Bloodthirsty.messages = Message(self.create_message('FindeVampireBloodMessage',[choesed_vampire]),Bloodthirsty)
                    list_team = list_vampire.remove(choesed_vampire)
                    if len(list_team) > 0:
                        for vamp in list_team:
                            vamp.messages = Message(self.create_message('FindeVampireTeam',[choesed_vampire ,target]),vamp)

                elif target.grouping == 'wolf':
                    choesed_vampire.you_were_killed(target)
                    choesed_vampire.messages = Message(self.create_message('VampireDeadWolf',[target]),choesed_vampire)
                    self.group.messages = Message(self.create_message('VampireDeadWolfGroupMessage',[choesed_vampire]), self.group)
                    list_team = list_vampire.remove(choesed_vampire)
                    if len(list_team) > 0:
                        for vamp in list_team:
                            vamp.messages = Message(self.create_message('VampireDeadWolfTeam',[choesed_vampire ,target]), vamp)
                
                elif target.role == 'shekar':
                    choesed_vampire.you_were_killed(target)
                    choesed_vampire.messages = Message(self.create_message('VampireDeadCH',[target]),choesed_vampire)
                    self.group.messages = Message(self.create_message('VampireDeadCHGroupMessage',[choesed_vampire]), self.group)
                    list_team = list_vampire.remove(choesed_vampire)
                    if len(list_team) > 0:
                        for vamp in list_team:
                            vamp.messages = Message(self.create_message('VampireDeadCHTeam',[choesed_vampire ,target]), vamp)

                elif target.role == 'Qatel':
                    choesed_vampire.you_were_killed(target)
                    choesed_vampire.messages = Message(self.create_message('VampireDeadByKiller',[target]),choesed_vampire)
                    target.messages = Message(self.create_message('VampireConKiller', [choesed_vampire]), target)
                    self.group.messages = Message(self.create_message('VampireDeadByKillerGroupMessage',[choesed_vampire]), self.group)
                    list_team = list_vampire.remove(choesed_vampire)
                    if len(list_team) > 0:
                        for vamp in list_team:
                            vamp.messages = Message(self.create_message('VampireDeadByKillerTeam',[target, choesed_vampire]), vamp)
                else:
                    intrandom = random.random()
                    if intrandom < 0.5:
                        target.you_were_killed(choesed_vampire)
                        choesed_vampire.messages = Message(self.create_message('vampier_one_kill_target',[target]),choesed_vampire)
                        target.messages = Message(self.create_message('eat_Vampire'), target)
                        self.group.messages = Message(self.create_message('VampireKillPlayer').format(self.create_tag(target), self.roleannouncement(target)), self.group)
                        list_team = list_vampire.remove(choesed_vampire)
                        if len(list_team) > 0:
                            for vamp in list_team:
                                vamp.messages = Message(self.create_message('vampier_kill_target',[target, choesed_vampire]), vamp)

                    elif intrandom < 0.7 and self.conversion_power_vampire:
                        target.change_role_vampier()
                        choesed_vampire.messages = Message(self.create_message('VampireConvert',[target]),choesed_vampire)
                        target.messages = Message(self.create_message('VampireConvertUser'), target)
                        if len(list_team) > 0:
                            for vamp in list_team:
                                vamp.messages = Message(self.create_message('VampireConvertTeam',[target, Bloodthirsty]), vamp)

                    else:
                        choesed_vampire.messages = Message(self.create_message('VampireMessageNoKill',[target]),choesed_vampire)
                        target.messages = Message(self.create_message('VampireMessageNoKillPlayer'), target)
                        list_team = list_vampire.remove(choesed_vampire)
                        if len(list_team) > 0:
                            for vamp in list_team:
                                vamp.messages = Message(self.create_message('VampireMessageNoKillTeam',[choesed_vampire, target]), vamp)
            
            else:
                choesed_vampire = random.choice(list_vampire)
                if target.grouping == 'wolf':
                    choesed_vampire.you_were_killed(target)
                    choesed_vampire.messages = Message(self.create_message('VampireDeadWolf',[target]),choesed_vampire)
                    self.group.messages = Message(self.create_message('VampireDeadWolfGroupMessage',[choesed_vampire]), self.group)
                    list_team = list_vampire.remove(choesed_vampire)
                    if len(list_team) > 0:
                        for vamp in list_team:
                            vamp.messages = Message(self.create_message('VampireDeadWolfTeam',[choesed_vampire ,target]), vamp)
                
                elif target.role == 'shekar':
                    choesed_vampire.you_were_killed(target)
                    choesed_vampire.messages = Message(self.create_message('VampireDeadCH',[target]),choesed_vampire)
                    self.group.messages = Message(self.create_message('VampireDeadCHGroupMessage',[choesed_vampire]), self.group)
                    list_team = list_vampire.remove(choesed_vampire)
                    if len(list_team) > 0:
                        for vamp in list_team:
                            vamp.messages = Message(self.create_message('VampireDeadCHTeam',[choesed_vampire ,target]), vamp)

                elif target.role == 'Qatel':
                    choesed_vampire.you_were_killed(target)
                    choesed_vampire.messages = Message(self.create_message('VampireDeadByKiller',[target]),choesed_vampire)
                    target.messages = Message(self.create_message('VampireConKiller', [choesed_vampire]), target)
                    self.group.messages = Message(self.create_message('VampireDeadByKillerGroupMessage',[choesed_vampire]), self.group)
                    list_team = list_vampire.remove(choesed_vampire)
                    if len(list_team) > 0:
                        for vamp in list_team:
                            vamp.messages = Message(self.create_message('VampireDeadByKillerTeam',[target, choesed_vampire]), vamp)
                else:
                    if random.random() < 0.4:
                        target.change_role_vampier()
                        Bloodthirsty.messages = Message(self.create_message('VampireConvert',[target]),Bloodthirsty)
                        target.messages = Message(self.create_message('BittenTurnedVampire'), target)
                        # self.group.messages = Message(self.create_message('VampireKillPlayer').format(self.create_tag(target), self.roleannouncement(target)), self.group)
                        list_team = list_vampire.remove(choesed_vampire)
                        if len(list_team) > 0:
                            for vamp in list_team:
                                vamp.messages = Message(self.create_message('VampireConvertByBlood',[target, Bloodthirsty]), vamp)

                    else:
                        target.you_were_killed(choesed_vampire)
                        choesed_vampire.messages = Message(self.create_message('vampier_one_kill_target',[target]),choesed_vampire)
                        target.messages = Message(self.create_message('eat_Vampire'), target)
                        self.group.messages = Message(self.create_message('VampireKillPlayer').format(self.create_tag(target), self.roleannouncement(target)), self.group)
                        list_team = list_vampire.remove(choesed_vampire)
                        if len(list_team) > 0:
                            for vamp in list_team:
                                vamp.messages = Message(self.create_message('vampier_kill_target',[target, choesed_vampire]), vamp)

                    
                            
    def implementation_action_kentvampire(self, kentvampire):
        if kentvampire.target != None:
            # if self.is_there_vampire():
            if kentvampire.target.where == None:
                kentvampire.messages = Message(self.create_message('KentVampireNoFind',[kentvampire.target]), kentvampire)
            else:
                kentvampire.messages = Message(self.create_message('KentVampireFind').format(self.create_tag(kentvampire.target), self.roleannouncement(kentvampire.target)), kentvampire)

            # else:
            #     kentvampire.target.you_were_killed(kentvampire)
            #     self.group.messages = Message(self.create_message('VampireKillPlayer').format(self.create_tag(target), self.roleannouncement(target)), self.group)

                



    def implementation_action_Archer(self, Archer):
        if Archer.target != None:
            if Archer.target.alive == True:
                if Archer.target.save_Franc:
                    Archer.messages = Message(self.create_message('FrancGourdArcherMessage',[Archer.target]), Archer)
                    Archer.target.messages = Message(self.create_message('PlayerMessageFrancS'), Archer.target)
                    for ply in self.players:
                        if ply.role == 'Franc':
                            ply.messages = Message(self.create_message('ArcherCult', [Archer.target]), ply)
                    return


                if Archer.target.role == 'Sweetheart':
                    Archer.target.fallling_in_love_Sweetheart(Archer)
                    Archer.target.messages = Message(self.create_message('MsgLoveSweetHeart', [Archer]), Archer.target)
                    Archer.messages = Message(self.create_message('MsgPlayerACLoved', [Archer.target]), Archer)
                    return

                if Archer.target.save_WhiteWolf:
                    Archer.messages = Message(self.create_message('WhiteWolfGourdArcherMessage',[Archer.target]), Archer)
                    Archer.target.messages = Message(self.create_message('WolfMessageGourdWhiteWolf'), Archer.target)
                    for ply in self.players:
                        if ply.role == 'WhiteWolf':
                            ply.messages = Message(self.create_message('WhiteWolfGourdArcher', [Archer.target]), ply)
                else:
                    Archer.target.you_were_killed(Archer)
                    Archer.messages = Message(self.create_message('archerkilltarget',[Archer.target]), Archer)
                    Archer.target.messages = Message(self.create_message('ArcherDeadPlayer'), Archer.target)
                    self.group.messages = Message(self.dict_game_texts['ArcherDeadPlayerGroupMessage'].format(self.create_tag(Archer.target),self.roleannouncement(Archer.target)), self.group)

            else:
                Archer.messages = Message(self.create_message('ArcherDeadPlayerMessage',[Archer.target]), Archer)

    def implementation_action_shekar(self,shekar):
        if shekar.target != None:
            if shekar.target.alive == True:
                if shekar.target.role == 'Franc':
                    if random.random() <= 0.1:
                        shekar.target.messages = Message(self.create_message('CultHunterFrancMessage'), shekar.target)
                        # shekar.messages = Message(self.create_message('MsgPlayerKNLoved', [shekar.target]), shekar)
                        self.group.messages = Message(self.create_message('CultHunterKillByFrancGroup', [shekar]), self.group)
                        

                    else:
                        shekar.target.messages = Message(self.create_message('CultHunterKillFrancMessage', [shekar]), shekar.target)
                        # shekar.messages = Message(self.create_message('MsgPlayerKNLoved', [shekar.target]), shekar)
                        self.group.messages = Message(self.create_message('CultHunterKillFrancGroup', [shekar.target]), self.group)  
                    return


                if shekar.target.role == 'Sweetheart':
                    shekar.target.fallling_in_love_Sweetheart(shekar)
                    shekar.target.messages = Message(self.create_message('MsgLoveSweetHeart', [shekar]), shekar.target)
                    shekar.messages = Message(self.create_message('MsgPlayerKNLoved', [shekar.target]), shekar)
                    return

                if shekar.target.role == 'Qatel':
                    shekar.you_were_killed(shekar.target)
                    self.group.messages = Message(self.create_message('SerialKillerKilledCH',[shekar]), self.group)

                elif shekar.target.grouping == 'cult':
                    shekar.target.you_were_killed(shekar)
                    shekar.messages = Message(self.create_message('HunterFindCultist',[shekar.target]), shekar)
                    self.group.messages = Message(self.create_message('HunterKilledCultist',[shekar.target]), self.group)
                    shekar.target.messages = Message(self.create_message('HunterKilledCultistOn',[shekar.target]), shekar.target)

                else:
                    shekar.messages = Message(self.create_message('HunterFailedToFind',[shekar.target]), shekar)
            else:
                shekar.messages = Message(self.create_message('HunterVisitDead',[shekar.target]), shekar)


    def implementation_action_Firefighter(self, Firefighter):
        if Firefighter.target != None:
            Firefighter.target.oil_spraying = True
            Firefighter.messages = Message(self.create_message('FireFighterOk', [Firefighter.target]), Firefighter)

    def implementation_action_Knight(self, Knight):
        if Knight.target != None:
            if Knight.target.alive:
                if Knight.target.role == 'Sweetheart':
                    Knight.target.fallling_in_love_Sweetheart(Knight)
                    Knight.target.messages = Message(self.create_message('MsgLoveSweetHeart', [Knight]), Knight.target)
                    Knight.messages = Message(self.create_message('MsgPlayerKNLoved', [Knight.target]), Knight)
                    return

                if Knight.target.grouping == 'village':
                    Knight.messages = Message(self.create_message('KnightNoKillUser', [Knight.target]), Knight)

                elif Knight.target.grouping in ['wolf', 'cult', 'Qatel','vampire']:
                    Knight.target.you_were_killed(Knight)
                    Knight.messages = Message(self.create_message('KnightKillPlayer', [Knight.target]), Knight)
                    self.group.messages = Message(self.create_message('KnightKillPlayerGroupMessage').format(self.create_tag(Knight.target), self.roleannouncement(Knight.target)), self.group)
                    Knight.target.messages = Message(self.create_message('KnightKillPlayerMessage'), Knight.target)
            else:
                Knight.messages = Message(self.create_message('KnightPlayerIsDeadSee', [Knight.target]), Knight)

    
    def implementation_action_Spy(self, Spy):
        if Spy.target != None:
            list_harmless_roles = ['rosta', 'pishgo']

            if Spy.target in list_harmless_roles:
                Spy.messages = Message(self.create_message('SpySeeMessageNo', [Spy.target]), Spy)
            else:
                Spy.messages = Message(self.create_message('SpySeeMessage', [Spy.target]), Spy)


    def implementation_action_enchanter(self, enchanter):
        if enchanter.target != None:
            if enchanter.target.alive == True:
                if enchanter.target.bewitched == False:
                    if enchanter.target.grouping == 'wolf' :
                        enchanter.messages = Message(self.create_message('EnchanterWolfFinde', [enchanter.target]), enchanter)
                    elif enchanter.target.save_fereshte:
                        enchanter.target.you_were_killed(enchanter.target)
                        enchanter.messages = Message(self.create_message('EnchanterDeadAngelInUserHome', [enchanter.target]), enchanter)
                        self.group.messages = Message(self.create_message('EnchanterDeadAngelInUserHomeGroupMessage', [enchanter]), self.group)
                    else:
                        enchanter.target.bewitched = True
                        enchanter.target.messages = Message(self.create_message('EnchanterSuccessUser'), enchanter.target)
                        enchanter.messages = Message(self.create_message('EnchanterSuccess', [enchanter.target]), enchanter)
                else:
                    enchanter.messages = Message(self.create_message('EnchanterBefore',[enchanter.target]), enchanter)
            else:
                enchanter.messages = Message(self.create_message('EnchanterDeadPlayer', [enchanter.target]), enchanter)


    def implementation_action_WolfJadogar(self, WolfJadogar):
        if WolfJadogar.target != None:
            if WolfJadogar.target.alive == True:
                if WolfJadogar.target.grouping == 'wolf':
                    WolfJadogar.messages = Message(self.dict_game_texts['SeerSees'].format(self.create_tag(WolfJadogar.target), WolfJadogar.target.role_name), WolfJadogar)

                elif WolfJadogar.target.role == 'pishgo':
                    WolfJadogar.messages = Message(self.dict_game_texts['SeerSees'].format(self.create_tag(WolfJadogar.target), WolfJadogar.target.role_name), WolfJadogar)
                
                else:
                    WolfJadogar.messages = Message(self.create_message('SorcererOther', [WolfJadogar.target]), WolfJadogar)



    # def implementation_action_day_tofangdar(self, tofangdar):
    #     if tofangdar.target != None:
    #         if tofangdar.target.role == 'rishsefid':
    #             pass
    #         else:
    #             Message(self.create_message('DefaultShot').format(self.create_tag(tofangdar), self.create_tag(tofangdar.target), self.roleannouncement(tofangdar.target))).send_message()
    
    
    def burning_oiled_houses(self, Firefighter):
        players_who_burn = set()
        for player in self.players:
            if player.oil_spraying:
                players_who_burn.add(player)
                if len(player.home)>1:
                    for ply in player.home:
                        if ply.role != 'fereshte':
                            players_who_burn.add(ply)
        
        for dead_player in players_who_burn:
            if dead_player.save_fereshte:
                Firefighter.messages = Message(self.create_message('AngelInHomeForFireFighter', [dead_player]), Firefighter)
                dead_player.messages = Message(self.create_message('AngelInHomeForPlayer'), dead_player)



    def checking_shekarchi_in_game(self): # چک وجود شکارچی
        if self.send_message_for_expose_shekar == False:
            if self.settings.expose_shekar == 'active':
                for player in self.players:
                    if player.role == 'shekar':
                        self.group.messages = Message(self.dict_game_texts['Shekar_msg'].format(self.create_tag(player), self.settings.expose_shekar_day), self.group)
                        self.send_message_for_expose_shekar = True

    def send_notification_for_player(self):# پیامی که در هنگام شروع گیم ارسال میشود
        for player in self.players:
            player.notification_assign_role()

    def send_start_notification_in_group(self):
        self.group.messages = Message(self.create_message('GameStart',[]),self.group)


    def send_night_notification_in_group(self): # پیامی که در انتهای روز و برای اعلام شب ارسال میشود
        self.group.messages = Message(self.create_message('MassgeFortypeSummery_night',[]).format(self.settings.time_night), self.group) # وارد کردن تایم از دیتابیس
        self.group.send_message()

    def send_dey_notification_in_group(self):
        Message(self.create_message('MassgeFortypeSummery_day').format(self.settings.day_time) + '\n' + self.create_message('Day_nos').format(self.day), self.group).send_message() # وارد کردن تایم از دیتابیس

    def send_voting_notification_in_group(self):
        Message(self.create_message('MassgeFortypeSummery_vote',[]).format(self.settings.time_vote), self.group).send_message() 

    def send_list_players_in_group(self):
        text_players_list_dead = ''
        text_players_list_alive = ''
        text_players_list_fired = ''
        number_alive = 0
        for player in self.players:
            if player.alive == True:
                number_alive += 1
                text_players_list_alive+=f"{self.create_tag(player)} : {self.create_message('is_on',[])}\n"
            else:
                if player.status == 'smite':
                    text_players_list_fired+=f"{self.create_tag(player)} : {player.role_name} - {self.create_message('fired',[])}\n"
                else:
                    text_players_list_dead+=f"{self.create_tag(player)} : {player.role_name} - {self.create_message('is_dead',[])}\n"

        text_players_list = text_players_list_dead + text_players_list_alive + text_players_list_fired
        Message(self.create_message('playerlistOn',[]).format(f'{len(self.players)}/{number_alive}',text_players_list),self.group).send_message()
    
    def send_list_winner_in_group(self,group_win):
        text_players_list_dead = ''
        text_players_list_alive = ''
        text_players_list_fired = ''
        number_alive = 0
        for player in self.players:
            if player.grouping == group_win:
                if player.alive == True:
                    number_alive += 1
                    text_players_list_alive+=f"{self.create_tag(player)} : {player.role_name} -  {self.create_message('is_on',[])} - {self.create_message('winner',[])}\n"
                else:
                    if player.status == 'smite':
                        text_players_list_fired+=f"{self.create_tag(player)} : {player.role_name} - {self.create_message('fired',[])} - {self.create_message('winner',[])}\n"
                    else:
                        text_players_list_dead+=f"{self.create_tag(player)} : {player.role_name} - {self.create_message('is_dead',[])} - {self.create_message('winner',[])}\n"

            else:
                if player.alive == True:
                    text_players_list_alive+=f"{self.create_tag(player)} : {player.role_name} -  {self.create_message('is_on',[])} - {self.create_message('loset',[])}\n"
                else:
                    if player.status == 'smite':
                        text_players_list_fired+=f"{self.create_tag(player)} : {player.role_name} - {self.create_message('fired',[])} - {self.create_message('loset',[])}\n"
                    else:
                        text_players_list_dead+=f"{self.create_tag(player)} : {player.role_name} - {self.create_message('is_dead',[])} - {self.create_message('loset',[])}\n"

        text_players_list = text_players_list_dead + text_players_list_alive + text_players_list_fired
        Message(self.create_message('playerlistOn',[]).format(f'{len(self.players)}/{number_alive}',text_players_list),self.group).send_message()
           

    def list_target_for_player(self,player_target):
        # گروه روستا
        if player_target.role == 'shekar':
            text = self.dict_game_texts['howToHoHome']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'kalantar':
            pass

        elif player_target.role == 'pishgo':
            text = self.dict_game_texts['howSeeIs']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'tofangdar':
            pass

        elif player_target.role == 'fereshte':
            text = self.dict_game_texts['HowAngelIs']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'Knight':
            text = self.dict_game_texts['KnightAsk']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'faheshe':
            text = self.dict_game_texts['howFahesheIs']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'ahmaq':
            text = self.dict_game_texts['howSeeIs']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'karagah':
            text = self.dict_game_texts['howEstelamIs']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'ngativ':
            text = self.dict_game_texts['Negativ_l']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'Chemist':
            text = self.dict_game_texts['AskChemist']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)


         # گروه گرگ ها
        elif player_target.role in ['WolfGorgine', 'Wolfx' ,'WolfAlpha', 'WolfTolle']:
            if self.wolves_can_attack:
                text = self.dict_game_texts['HowWasEatUser']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    # if player != player_target:
                    if player.role in ['enchanter','WolfJadogar']:
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))    
                    elif player.grouping != player_target.grouping:
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target.setdefault(player_target ,target_message)

                text_grouping = self.text_get_teammates(player_target)
                if text_grouping:
                    text_team = self.dict_game_texts['eatUserTeem'].format(text_grouping)
                    Message(text_team,player_target).send_message()
            else:
                Message(self.create_message('message_cannt_attak'), player_target).send_message()

        elif player_target.role == 'WhiteWolf':
            text = self.dict_game_texts['AskWhiteWolf']
            markup = InlineKeyboardMarkup()
            check = False
            for player in self.players:
                if player != player_target:
                    if player.grouping == 'wolf' and player.role not in ['enchanter','WolfJadogar']:
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name, callback_data=f'target_night_{player.id}_{player.name}'))
                            check = True
            if check:
                target_message = Message(text, player_target, markup)
                target_message.send_message()
                self.dict_message_choice_target.setdefault(player_target ,target_message)


        elif player_target.role == 'enchanter':
            text = self.dict_game_texts['AskEnchanter']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'WolfJadogar':
            text = self.dict_game_texts['askJado']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                if player != player_target:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

        elif player_target.role == 'Honey':
            text = self.dict_game_texts['Ask_Honey']
            markup = InlineKeyboardMarkup()
            check = False
            for player in self.players:
                if player != player_target:
                    if player.grouping != 'wolf':
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name, callback_data=f'target_night_{player.id}_{player.name}'))
                            check = True
            if check:
                target_message = Message(text, player_target, markup)
                target_message.send_message()
                self.dict_message_choice_target.setdefault(player_target ,target_message)


        # گروه قاتل
        elif player_target.role == 'Qatel':
            text = self.dict_game_texts['HowTokillUser']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message) 
            
            text_grouping = self.text_get_teammates(player_target)
            if text_grouping:
                text_team = self.dict_game_texts['DiscussWith'].format(text_grouping)
                Message(text_team,player_target).send_message()

        elif player_target.role == 'Archer':
            if self.day % 2 != 0:
                text = self.dict_game_texts['AskArcher']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    # if player != player_target:
                    if player.grouping != player_target.grouping:
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target.setdefault(player_target ,target_message)
            else:
                Message(self.create_message('archernottarget'), player_target).send_message()

            text_grouping = self.text_get_teammates(player_target)
            if text_grouping:
                text_team = self.dict_game_texts['DiscussWith'].format(text_grouping)
                Message(text_team,player_target).send_message()



         # گروه فرقه ها
        elif player_target.role == 'ferqe':
            text = self.dict_game_texts['AskConvert']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name, callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

            text_grouping = self.text_get_teammates(player_target)
            if text_grouping:
                text_team = self.dict_game_texts['DiscussWith'].format(text_grouping)
                Message(text_team,player_target).send_message()

        elif player_target.role == 'Royce': 
            text = self.dict_game_texts['AskConvert']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

            text_grouping = self.text_get_teammates(player_target)
            if text_grouping:
                text_team = self.dict_game_texts['DiscussWith'].format(text_grouping)
                Message(text_team,player_target).send_message()

        elif player_target.role == 'Franc':
            if self.is_there_cult():
                text = self.dict_game_texts['AskFranc']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    if player != player_target:
                        if player.grouping == player_target.grouping:
                            if player.alive == True:
                                markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            else:
                text = self.dict_game_texts['FrancAskNight']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    # if player != player_target:
                    if player.grouping != player_target.grouping:
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))

            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)

            text_grouping = self.text_get_teammates(player_target)
            if text_grouping:
                text_team = self.dict_game_texts['DiscussWith'].format(text_grouping)
                Message(text_team,player_target).send_message()


        # گروه آتش
        elif player_target.role == 'Firefighter':
            text = self.dict_game_texts['AskFireFighter']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            markup.add(InlineKeyboardButton(self.create_message('ButtenFireFighter'), callback_data='fire'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)


        elif player_target.role == 'IceQueen':
            text = self.dict_game_texts['IceQeenAsk']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)


        # گروه ومپایر
        elif player_target.role == 'Vampire':
            if self.is_vampire_imprisoned:
                text = self.dict_game_texts['AskVampire']
            else:
                text = self.dict_game_texts['AskWhenBlood']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)
            
            text_grouping = self.text_get_teammates(player_target)
            if text_grouping:
                text_team = self.dict_game_texts['teemvampire'].format(text_grouping)
                Message(text_team,player_target).send_message()

        elif player_target.role == 'Bloodthirsty':
            if self.is_vampire_imprisoned == False:
                text = self.dict_game_texts['AskWhenBlood']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))
            target_message = Message(text,player_target,markup)
            target_message.send_message()
            self.dict_message_choice_target.setdefault(player_target ,target_message)
            
            text_grouping = self.text_get_teammates(player_target)
            if text_grouping:
                text_team = self.dict_game_texts['teemvampire'].format(text_grouping)
                Message(text_team,player_target).send_message()
            
        elif player_target.role == 'kentvampire':
            text = self.dict_game_texts['AskKentVampire']
            markup = InlineKeyboardMarkup()
            for player in self.players:
                # if player != player_target:
                if player.grouping != player_target.grouping:
                    if player.alive == True:
                        markup.add(InlineKeyboardButton(player.name,callback_data=f'target_night_{player.id}_{player.name}'))

            target_message = Message(text,player_target,markup)
            target_message.send_message()
            if text_grouping:
                text_team = self.dict_game_texts['teemvampire'].format(text_grouping)
                Message(text_team,player_target).send_message()



    def list_target_day_for_player(self, player_target):
        if player_target.role == 'tofangdar':
            if player_target.number_of_shot > 0:
                text = self.dict_game_texts['AskShoot'].format(player_target.number_of_shot)
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    if player != player_target:
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name, callback_data=f'target_day_{player.id}_{player.name}'))
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)            

        elif player_target.role == 'Solh':
            if player_target.can_there_solh:
                text = self.dict_game_texts['solh_L']
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(self.dict_game_texts['solh_btn'], callback_data=f'target_day_Solh')) 
                markup.add(InlineKeyboardButton(self.dict_game_texts['solh_no'], callback_data=f'target_day_no')) 
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)       

        elif player_target.role == 'Ahangar':
            if player_target.can_there_spreadsilver:
                text = self.dict_game_texts['ahangar_L']
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(self.dict_game_texts['ahangar_btnY'], callback_data=f'target_day_ahangar')) 
                markup.add(InlineKeyboardButton(self.dict_game_texts['ahangar_btn'], callback_data=f'target_day_no')) 
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)  

        elif player_target.role == 'trouble':
            if player_target.can_vote_agian:
                text = self.dict_game_texts['Asktrouble']
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(self.dict_game_texts['troubleBtnYes'], callback_data=f'target_day_voteagain')) 
                markup.add(InlineKeyboardButton(self.dict_game_texts['troubleBtnNo'], callback_data=f'target_day_no')) 
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)  

        elif player_target.role == 'Kadkhoda':
            if player_target.notify_kadkhoda :
                text = self.dict_game_texts['Kadkhoda_l']
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(self.dict_game_texts['Kadkhoda_btn'], callback_data=f'target_day_notify')) 
                markup.add(InlineKeyboardButton(self.dict_game_texts['troubleBtnNo'], callback_data=f'target_day_no')) 
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)  

        elif player_target.role == 'Ruler':
            if player_target.can_Ruler_vote :
                text = self.dict_game_texts['RulerAsk']
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(self.dict_game_texts['Kadkhoda_btn'], callback_data=f'target_day_voteruler')) 
                markup.add(InlineKeyboardButton(self.dict_game_texts['troubleBtnNo'], callback_data=f'target_day_no')) 
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)  

        elif player_target.role == 'KhabGozar':
            if player_target.can_KhabGozar :
                text = self.dict_game_texts['KHABGOZAR_l']
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(self.dict_game_texts['KHABGOZAR_BTN'], callback_data=f'target_day_KhabGozar')) 
                markup.add(InlineKeyboardButton(self.dict_game_texts['KHABGOZAR_BTN_N'], callback_data=f'target_day_no')) 
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)  



        elif player_target.role == 'kentvampire':
            if self.is_there_vampire() == False:
                text = self.dict_game_texts['AskDayKentVampire']
                markup = InlineKeyboardMarkup()
                for player in self.players:
                    if player.grouping != 'vampire':
                        if player.alive == True:
                            markup.add(InlineKeyboardButton(player.name, callback_data=f'target_day_{player.id}_{player.name}'))
                target_message = Message(text,player_target,markup)
                target_message.send_message()
                self.dict_message_choice_target_day.setdefault(player_target, target_message)   

    def shot_kentvampire(self, kentvampire, target):
        target.you_were_killed(kentvampire) 
        Message(self.create_message('KentVampireKillPlayer').format(self.create_tag(target), self.roleannouncement(target)),self.group).send_message()

        check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
        if check_win:
            return 'end game'


    def shot_tofangdar(self, tofangdar, id_target):
        tofangdar.number_of_shot -= 1
        for player in self.players:
            if player.id == id_target:
                if player.role == 'rishsefid':
                    pass
                else:
                    Message(self.create_message('DefaultShot').format(self.create_tag(tofangdar), self.create_tag(player), self.roleannouncement(player)),self.group).send_message()
                    player.you_were_killed(tofangdar) 
        check_win = self.analysis_of_events_and_review_of_winning() # چک کردن اینکه گروهی برنده بازی شده یا خیر
        if check_win:
            return 'end game'


    def is_there_vampire(self):
        for player in self.players:
            if player.grouping == 'vampire' and player.role != 'kentvampire':
                if player.alive:
                    return True
        else:
            return False

    def is_there_cult(self):
        for player in self.players:
            if player.grouping == 'cult' and player.role != 'Franc':
                if player.alive:
                    return True
        else:
            return False

    def text_get_teammates(self,player_target):
        text_grouping = '\n'
        for player in self.players:
            if player.grouping == player_target.grouping and player.role not in ['enchanter','WolfJadogar']:
                if player.alive == True:
                    if player.id != player_target.id:
                        text_grouping += self.create_tag(player) + '\n'
        if text_grouping == '\n':
            return False
        else:
            return text_grouping 

    def create_tag(self,user):
        return f'[{user.name}](tg://user?id={user.id})'
        
    def create_message(self,name_message,list_user_for_tag=[]):
        if len(list_user_for_tag) == 0:
            return self.dict_game_texts[name_message]
        
        elif len(list_user_for_tag) == 1:
            return self.dict_game_texts[name_message].format(self.create_tag(list_user_for_tag[0]))

        elif len(list_user_for_tag) == 2:
            return self.dict_game_texts[name_message].format(self.create_tag(list_user_for_tag[0]),self.create_tag(list_user_for_tag[1]))
    
    def roleannouncement(self,target):
        return self.dict_game_texts['user_role'].format(target.role_name)


    def chack_number_player(self):
        number_players=len(self.players)
        if number_players>=5:  # چک برای اجرای بازی با تعداد کافی
            # player.assign_role('role', self)
            return 'started'
        else:
            self.active=False
            return 'not enough'




class Message: # کلاس مسیج()
    def __init__(self, text, receiver, _Inline_KeyboardButton=[], mid_for_copy = None):
        self.text = text
        self.receiver = receiver
        self._Inline_KeyboardButton = _Inline_KeyboardButton
        self.mid_for_copy = mid_for_copy
        self.send = False
        self.message_id = None

    def send_message(self, replay_message_id=None):# متد ارسال پیام
        if self.mid_for_copy == None:
            message_info = send_message(self.receiver.id, self.text, reply_markup = self._Inline_KeyboardButton, parse_mode = 'Markdown', reply_to_message_id = replay_message_id)
            self.send = True
            self.message_id = message_info.message_id
        else:
            message_info = bot.copy_message(self.receiver.id, channel_id_description, self.mid_for_copy, self.text, parse_mode = 'Markdown', reply_markup = self._Inline_KeyboardButton, reply_to_message_id=replay_message_id)
            self.send = True
            self.message_id = message_info.message_id

    def reply_message(self,message): # متد ریپلای
        reply_message(message, self.text, reply_markup = self._Inline_KeyboardButton, parse_mode= 'Markdown')

    def edit_message_reply_markup(self, markup):
        edit_message_reply_markup(self.receiver.id ,self.message_id, reply_markup = markup)

    def edit_message_text(self, text): # متد ادیت
        if self.send == True:
            edit_message_text(text, self.receiver.id, self.message_id ,reply_markup = None, parse_mode = 'Markdown')
        else:
            logging.exception( f' Error in edit_message_text in class Message send != True')


def send_message(*args, **kwargs):# تابع ارسال پیام
    try:
        # return bot.send_message(*args, **kwargs)
        return antiflood(bot.send_message, *args, **kwargs)
    except ApiTelegramException as e:
        logging.exception( f' Error in send_message Exception: ' + str(e.result_json))
        if e.error_code != 403:     # 403: bot was blocked by the user or user is deactivated.
            bot.send_message(master_cid,f'Warning: Error in send_message ApiTelegramException: ' + str(e.result_json))
        return False
    except Exception as e:
        logging.exception( f' Error in send_message Exception: ' + str(e))
        bot.send_message(master_cid, f'Warning: Error in send_message Exception: ' + str(e))
        return False

def reply_message(*args, **kwargs):
    try:
        return antiflood(bot.reply_to, *args, **kwargs)
    except ApiTelegramException as e:
        logging.exception(f' Error in reply_message Exception: ' + str(e.result_json))
        if e.error_code != 403:   
            bot.send_message(master_cid,f'Warning: Error in reply_message ApiTelegramException: ' + str(e.result_json))
        return False
    except Exception as e:
        logging.exception(f' Error in reply_message Exception: ' + str(e))
        bot.send_message(master_cid, f'Warning: Error in reply_message Exception: ' + str(e))
        return False

def edit_message_reply_markup(*args, **kwargs):
    try:
        return antiflood(bot.edit_message_reply_markup, *args, **kwargs)
    except ApiTelegramException as e:
        logging.exception( f' Error in edit_message_reply_markup Exception: ' + str(e.result_json))
        if e.error_code != 403:    
            bot.send_message(master_cid,f'Warning: Error in edit_message_reply_markup ApiTelegramException: ' + str(e.result_json))
        return False
    except Exception as e:
        logging.exception(f' Error in edit_message_reply_markup Exception: ' + str(e))
        bot.send_message(master_cid, f'Warning: Error in edit_message_reply_markup Exception: ' + str(e))
        return False

def edit_message_text(*args, **kwargs):
    try:
        bot.edit_message_text(*args, **kwargs)
    except Exception as e:
        logging.exception( f' Error in edit_message_text Exception: ' + str(e))
        send_message(master_cid, f'Warning: Error in edit_message_text Exception: ' + str(e))







