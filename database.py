import mysql.connector
from config import *
import logging
import os

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(filename=LogFile,level=logging.DEBUG,format=LOG_FORMAT,filemode='w')

dict_messages_general = {}
file_path_general = r'Game_Mode\general_fa.ini'
file_path_general = os.path.join('Game_Mode', 'general_fa.ini')



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

read_ini_file(file_path_general, dict_messages_general)

def ErrorReport(message, FunctionName, Type='General'):
    if Local:
        print(f' Error in {Type} in function ({FunctionName}): ' + str(message))
    else:
        logging.error(f' Error in {Type} in function ({FunctionName}): ' + str(message))

def CreateDatabase():
    import mysql.connector
    # config = {'user': 'root', 'password': 'ma8h2dii', 'host': 'localhost'}
    config = {'user': 'root', 'password': 'ka25wWJnMY4ilhXrDoLl', 'host': 'localhost'}
    conn = mysql.connector.connect(**config)
    mycursor = conn.cursor()
    mycursor.execute("DROP DATABASE IF EXISTS detabase_mafia")
    mycursor.execute("CREATE DATABASE IF NOT EXISTS detabase_mafia")
    conn.commit()
    conn.close()
    print("Database Created")



class SQL:
    def __init__(self, FuncName='General'):
        self.conn = mysql.connector.connect(**config)
        self.conn.autocommit = False
        self.name = FuncName

    def __enter__(self):
        return self.conn.cursor(dictionary=True)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            ErrorReport(exc_value, FunctionName=self.name, Type='SQL Queries')
            self.conn.rollback()
            return exc_traceback
        else:
            self.conn.commit()
        if self.conn.is_connected():
            self.conn.close()
        
    def cursor(self):
        return self.conn.cursor(dictionary=True)
    
def CreateTable():
    with SQL('Create_group_information_Table') as c:
        try:
            SQL_QUERY = ('''
CREATE TABLE IF NOT EXISTS GroupsTable (   
    group_id                BIGINT PRIMARY KEY,
    title                   VARCHAR(500),
    username                VARCHAR(500),
    subscription_type       ENUM('free', 'paid') DEFAULT 'free',
    cid_admin_added_bot     BIGINT,
    number_of_game          INT DEFAULT 0,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP        
);
''')
            c.execute(SQL_QUERY)

            SQL_QUERY_SETTINGS="""
CREATE TABLE IF NOT EXISTS group_settings (
    group_id                   BIGINT,

    nitht_time                 int DEFAULT 60,
    day_time                   int DEFAULT 60,
    voting_time                int DEFAULT 60,
    time_to_join               int DEFAULT 60,
    extra_time_to_vote         int DEFAULT 60,
   
    role_fool                  ENUM('active', 'inactive') DEFAULT 'active',
    role_monafeq               ENUM('active', 'inactive') DEFAULT 'active',
    role_cult                  ENUM('active', 'inactive') DEFAULT 'active',
    role_lucifer               ENUM('active', 'inactive') DEFAULT 'active',
   
    expose_shekar              ENUM('active', 'inactive') DEFAULT 'inactive',
    expose_shekar_day          int DEFAULT 1,
    voting_secret              ENUM('active', 'inactive') DEFAULT 'inactive',
    number_vote_voting_secret  ENUM('active', 'inactive') DEFAULT 'inactive',
    name_vote_voting_secret    ENUM('active', 'inactive') DEFAULT 'inactive',
    silence_after_deeth        ENUM('active', 'inactive') DEFAULT 'inactive',

    type_game                  ENUM('normal', 'selective') DEFAULT 'selective',
    show_role_end_game         ENUM('live', 'all', 'nothing') DEFAULT 'all',
    show_role_after_deeth      ENUM('active', 'inactive') DEFAULT 'active',
    escape_player              ENUM('active', 'inactive') DEFAULT 'inactive',
    adding_time_by_player      ENUM('active', 'inactive') DEFAULT 'inactive',
    manege_roles               VARCHAR(500),

    created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update                TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (group_id) REFERENCES GroupsTable (group_id)
);
"""
            c.execute(SQL_QUERY_SETTINGS)

            SQL_QUERY_SCORES="""
CREATE TABLE IF NOT EXISTS scores (
    cid                     BIGINT PRIMARY KEY,
    group_id                BIGINT,
    score                   INT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES GroupsTable (group_id)
);
"""
            c.execute(SQL_QUERY_SCORES)

            SQL_QUERY_PLAYERS="""
CREATE TABLE IF NOT EXISTS players (
    cid                     BIGINT PRIMARY KEY,
    score                   INT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP    
);
"""
            c.execute(SQL_QUERY_PLAYERS)


            SQL_QUERY_USERS="""
CREATE TABLE IF NOT EXISTS users (
    cid                     BIGINT PRIMARY KEY,
    username                VARCHAR(500),
    name                    VARCHAR(500),
    inventory               bigint DEFAULT 0,
    emoji                   VARCHAR(500),
    nickname                VARCHAR(500),
    XP                      bigint DEFAULT 0,
    
    power_soul              int DEFAULT 0,
    power_chinesenews       int DEFAULT 0,
    power_silence           int DEFAULT 0,
    power_espionage         int DEFAULT 0,
    power_bodyguard         int DEFAULT 0,

    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP    
);
"""
            c.execute(SQL_QUERY_USERS)


            SQL_QUERY_ROLES="""
CREATE TABLE IF NOT EXISTS roles (
    code_role               TINYINT PRIMARY KEY AUTO_INCREMENT COMMENT 'کد نقش',
    role                    VARCHAR(500) NOT NULL COMMENT 'نقش',
    role_name               VARCHAR(500) NOT NULL COMMENT 'اسم نقش',
    role_grouping           VARCHAR(500) NOT NULL COMMENT 'گروه',
    becoming_cult           DECIMAL(5,2) NOT NULL COMMENT 'فرقه شدن',
    role_type               ENUM('free', 'paid') DEFAULT 'free',
    role_status             ENUM('on', 'off') DEFAULT 'on',

    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP    
);
"""
            c.execute(SQL_QUERY_ROLES)


            SQL_QUERY_ROLES_GROUPS="""
CREATE TABLE IF NOT EXISTS closed_roles_for_groups (
    group_id                BIGINT,
    code_role               TINYINT COMMENT 'کد نقش',

    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES GroupsTable (group_id),
    FOREIGN KEY (code_role) REFERENCES roles (code_role)   
);
"""

            c.execute(SQL_QUERY_ROLES_GROUPS)

            SQL_QUERY_BLOCKED_GROUPS="""
CREATE TABLE IF NOT EXISTS blocked_groups (
    group_id                BIGINT COMMENT 'آیدی گروه',

    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES GroupsTable (group_id)
);
"""
            c.execute(SQL_QUERY_BLOCKED_GROUPS)


            SQL_QUERY_BLOCKED_USERS="""
CREATE TABLE IF NOT EXISTS blocked_users (
    cid                     BIGINT COMMENT 'آیدی کاربر',

    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cid) REFERENCES users (cid)
);
"""
            c.execute(SQL_QUERY_BLOCKED_USERS)




            SQL_QUERY_BLOCKED_USERS="""
CREATE TABLE IF NOT EXISTS blocked_users_from_group (
    cid                     BIGINT COMMENT 'آیدی کاربر',
    group_id                BIGINT,

    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    last_update             TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cid) REFERENCES users (cid),
    FOREIGN KEY (group_id) REFERENCES GroupsTable (group_id)

);
"""
            c.execute(SQL_QUERY_BLOCKED_USERS)


        except mysql.connector.errors.IntegrityError:
            ErrorReport('CREATE TABLE','CreateTable',Type='SQL Queries')



# ----------------------------------------------------------------------insert-----------------------------------------------------

def insert_groups(group_id, title, username, cid_admin_added_bot):
    with SQL('insert_GroupsTable') as c:
        try:
            c.execute(f'INSERT IGNORE INTO GroupsTable (group_id, title, username, cid_admin_added_bot) VALUES (%s, %s, %s, %s)', (group_id, title, username, cid_admin_added_bot))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','GroupsTable',Type='SQL Queries')

def insert_scores(cid, score):
    with SQL('insert_scores') as c:
        try:
            c.execute(f'INSERT IGNORE INTO scores (cid, scores) VALUES (%s, %s)', (cid, score))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','scores',Type='SQL Queries')

def insert_group_settings(group_id):
    with SQL('insert_group_settings') as c:
        try:
            c.execute(f'INSERT IGNORE INTO group_settings (group_id) VALUES (%s)', (group_id,))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','group_settings',Type='SQL Queries')

def insert_roles(role, grouping, role_name,  becoming_cult):
    # print(role, grouping, role_name,  becoming_cult)
    with SQL('insert_roles') as c:
        try:
            c.execute(f'INSERT INTO roles (role, role_name, role_grouping, becoming_cult) VALUES (%s, %s, %s, %s)', (role, role_name, grouping, becoming_cult))
            # c.execute(f"INSERT INTO roles (role, role_name, grouping, becoming_cult) VALUES ('{role}', '{role_name}', '{grouping}', {becoming_cult})")
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','roles',Type='SQL Queries')


def insert_closed_roles_for_groups(group_id, code_role):
    with SQL('insert_closed_roles_for_groups') as c:
        try:
            c.execute(f'INSERT IGNORE INTO closed_roles_for_groups (group_id, code_role) VALUES (%s, %s)', (group_id, code_role))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','insert_closed_roles_for_groups',Type='SQL Queries')

def insert_users(cid, username, name):
    with SQL('insert_users') as c:
        try:
            c.execute(f'INSERT IGNORE INTO users (cid, username, name) VALUES (%s, %s, %s)', (cid, username, name))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','users',Type='SQL Queries')

def insert_blocked_groups(group_id):
    with SQL('insert_blocked_groups') as c:
        try:
            c.execute(f'INSERT IGNORE INTO blocked_groups (group_id) VALUES (%s)', (group_id,))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','blocked_groups',Type='SQL Queries')

def insert_blocked_users(cid):
    with SQL('insert_blocked_users') as c:
        try:
            c.execute(f'INSERT IGNORE INTO blocked_users (cid) VALUES (%s)', (cid,))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','blocked_users',Type='SQL Queries')


def insert_blocked_users_from_group(group_id, cid):
    with SQL('insert_blocked_users_from_group') as c:
        try:
            c.execute(f'INSERT IGNORE INTO blocked_users_from_group (group_id, cid) VALUES (%s, %s)', (group_id, cid))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('insert TABLE','blocked_users_from_group',Type='SQL Queries')
# ----------------------------------------------------------------------update-----------------------------------------------------

def update_group_settings(key, value, group_id):
    with SQL('update_group_settings') as c:
        try:
            c.execute(f"update group_settings set {key}='{value}' where group_id=%s", (group_id,))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('update TABLE','group_settings',Type='SQL Queries')


def update_roles(key, value, role):
    with SQL('update_roles') as c:
        try:
            c.execute(f"update roles set {key}='{value}' where role=%s", (role,))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('update TABLE','roles',Type='SQL Queries')

def update_GroupsTable(key, value, group_id):
    with SQL('update_GroupsTable') as c:
        try:
            c.execute(f"update GroupsTable set {key}='{value}' where group_id=%s", (group_id,))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('update TABLE','GroupsTable',Type='SQL Queries')
# def update_roles_of_groups(key, value, group_id, code_role):
#     with SQL('update_roles_of_groups') as c:
#         try:
#             c.execute(f"update roles_of_groups set {key}='{value}' where group_id=%s AND code_role=%s", (group_id,code_role))
#         except mysql.connector.errors.IntegrityError:
#             ErrorReport('update TABLE','roles_of_groups',Type='SQL Queries')

# ----------------------------------------------------------------------select-----------------------------------------------------

def select_group_settings_by_group_id(group_id):
    with SQL('select_group_settings_by_group_id') as c:
        try:
            c.execute('SELECT * FROM group_settings WHERE group_id = %s',(group_id,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_group_settings_by_group_id',Type='SQL Queries')

def select_geoup_by_group_id(group_id):
    with SQL('select_GroupsTable_by_group_id') as c:
        try:
            c.execute('SELECT * FROM GroupsTable WHERE group_id = %s',(group_id,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_GroupsTable_by_group_id',Type='SQL Queries')

def select_all_GroupsTable():
    with SQL('select_all_GroupsTable') as c:
        try:
            c.execute('SELECT * FROM GroupsTable')
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_all_GroupsTable',Type='SQL Queries')

# def select_url_detaile():
#     with SQL('select_url_detaile') as c:
#         try:
#             c.execute('SELECT url FROM property_information')
#             res = c.fetchall()
#             return [i['url'] for i in res]
#         except mysql.connector.errors.IntegrityError:
#             ErrorReport('select TABLE','select_url_detaile',Type='SQL Queries')

def select_all_roles():
    with SQL('select_all_roles') as c:
        try:
            c.execute('SELECT * FROM roles')
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_all_roles',Type='SQL Queries')

def select_role_by_role(role):
    with SQL('select_role_by_role') as c:
        try:
            c.execute('SELECT * FROM roles WHERE role = %s', (role,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_role_by_role',Type='SQL Queries')

def select_roles_by_grouping(role_grouping):
    with SQL('select_roles_by_grouping') as c:
        try:
            c.execute('SELECT * FROM roles WHERE role_grouping = %s', (role_grouping,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_roles_by_grouping',Type='SQL Queries')

def select_closed_roles_for_groups_by_group_id(group_id, code_role):
    with SQL('select_closed_roles_for_groups_by_group_id') as c:
        try:
            c.execute('SELECT * FROM closed_roles_for_groups WHERE group_id = %s and code_role = %s',(group_id, code_role))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_closed_roles_for_groups_by_group_id',Type='SQL Queries')

def select_blocked_groups_by_group_id(group_id):
    with SQL('select_blocked_groups_by_group_id') as c:
        try:
            c.execute('SELECT * FROM blocked_groups WHERE group_id = %s',(group_id,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_blocked_groups_by_group_id',Type='SQL Queries')

def select_users_by_cid(cid):
    with SQL('select_users_by_cid') as c:
        try:
            c.execute('SELECT * FROM users WHERE cid = %s',(cid,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_users_by_cid',Type='SQL Queries')


def select_users_by_username(username):
    with SQL('select_users_by_username') as c:
        try:
            c.execute('SELECT * FROM users WHERE username = %s',(username,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_users_by_username',Type='SQL Queries')

def select_users_by_cid(cid):
    with SQL('select_users_by_cid') as c:
        try:
            c.execute('SELECT * FROM users WHERE cid = %s',(cid,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_users_by_cid',Type='SQL Queries')


def select_blocked_users_by_cid(cid):
    with SQL('select_blocked_users_by_cid') as c:
        try:
            c.execute('SELECT * FROM blocked_users WHERE cid = %s',(cid,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_blocked_users_by_cid',Type='SQL Queries')


def select_blocked_users_from_group(cid, group_id):
    with SQL('select_blocked_users_from_group_by_id') as c:
        try:
            c.execute('SELECT * FROM blocked_users_from_group WHERE cid = %s and group_id = %s ',(cid, group_id))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_blocked_users_from_group',Type='SQL Queries')


def select_blocked_users_from_group_by_groupid(group_id):
    with SQL('select_blocked_users_from_group_by_groupid') as c:
        try:
            c.execute('SELECT * FROM blocked_users_from_group WHERE group_id = %s',(group_id,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('select TABLE','select_blocked_users_from_group_by_groupid',Type='SQL Queries')
# ----------------------------------------------------------------------delete-----------------------------------------------------

def delete_row_group(group_id):
    with SQL('delete_row_group') as c:
        try:
            c.execute('DELETE FROM GROUPS WHERE group_id = %s',(group_id,))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('DELETE TABLE','delete_row_group',Type='SQL Queries')


def delete_row_blocked_groups(group_id):
    with SQL('delete_row_blocked_groups') as c:
        try:
            c.execute('DELETE FROM blocked_groups WHERE group_id = %s',(group_id,))
        except mysql.connector.errors.IntegrityError:
            ErrorReport('DELETE TABLE','delete_row_blocked_groups',Type='SQL Queries')


def delete_closed_roles_for_groups_by_group_id(group_id, code_role):
    with SQL('delete_closed_roles_for_groups_by_group_id') as c:
        try:
            c.execute('DELETE FROM closed_roles_for_groups WHERE group_id = %s and code_role = %s',(group_id, code_role))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('DELETE TABLE','delete_closed_roles_for_groups_by_group_id',Type='SQL Queries')


def delete_blocked_users_from_group(group_id, cid):
    with SQL('delete_blocked_users_from_group') as c:
        try:
            c.execute('DELETE FROM blocked_users_from_group WHERE group_id = %s and cid = %s',(group_id, cid))
            res = c.fetchall()
            return res
        except mysql.connector.errors.IntegrityError:
            ErrorReport('DELETE TABLE','delete_blocked_users_from_group',Type='SQL Queries')







# if __name__ == "__main__":
def create_data():
    CreateDatabase()
    CreateTable()

    insert_roles( 'rosta',           'village', dict_messages_general['role_rosta_n'], 1)
    insert_roles( 'shekar',          'village', dict_messages_general['role_shekar_n'], 0)
    insert_roles( 'pishgo',          'village', dict_messages_general['role_pishgo_n'], 0.4)
    insert_roles( 'kalantar',        'village', dict_messages_general['role_kalantar_n'], 0.5)
    insert_roles( 'tofangdar',       'village', dict_messages_general['role_tofangdar_n'], 1)
    insert_roles( 'fereshte',        'village', dict_messages_general['role_Fereshte_n'], 0.6)
    insert_roles( 'rishSefid',       'village', dict_messages_general['role_rishSefid_n'], 0.3)
    insert_roles( 'Knight',          'village', dict_messages_general['role_Knight_n'], 0.3)
    insert_roles( 'PishRezerv',      'village', dict_messages_general['role_PishRezerv_n'], 1)
    insert_roles( 'Solh',            'village', dict_messages_general['role_Solh_n'], 0.8)
    insert_roles( 'Ahangar',         'village', dict_messages_general['role_Ahangar_n'], 0.75)
    insert_roles( 'karagah',         'village', dict_messages_general['role_karagah_n'], 0.7)
    insert_roles( 'faheshe',         'village', dict_messages_general['role_faheshe_n'], 0.7)
    insert_roles( 'trouble',         'village', dict_messages_general['role_trouble_n'], 0.6)
    insert_roles( 'ahmaq',           'village', dict_messages_general['role_ahmaq_n'], 1)
    insert_roles( 'Kadkhoda',        'village', dict_messages_general['role_Kadkhoda_n'], 1)
    insert_roles( 'Ruler',           'village', dict_messages_general['role_Ruler_n'], 1) 
    insert_roles( 'Mast',            'village', dict_messages_general['role_Mast_n'], 1) 
    insert_roles( 'NefrinShode',     'village', dict_messages_general['role_NefrinShode_n'], 0.6) 
    insert_roles( 'Khaen',           'village', dict_messages_general['role_Khaen_n'], 1) 
    insert_roles( 'KhabGozar',       'village', dict_messages_general['role_KhabGozar_n'], 0.6) 
    insert_roles( 'Gorgname',        'village', dict_messages_general['role_Gorgname_n'], 1) 
    insert_roles( 'PesarGij',        'village', dict_messages_general['role_PesarGij_n'], 1) 
    insert_roles( 'Vahshi',          'village', dict_messages_general['role_Vahshi_n'], 1) 
    insert_roles( 'Augur',           'village', dict_messages_general['role_Augur_n'], 0.4) 
    insert_roles( 'elahe',           'village', dict_messages_general['role_elahe_n'], 1) 
    insert_roles( 'ngativ',          'village', dict_messages_general['role_ngativ_n'], 0.5) 
    insert_roles( 'Chemist',         'village', dict_messages_general['role_Chemist_n'], 0.5) 
    insert_roles( 'Shahzade',        'village', dict_messages_general['role_Shahzade_n'], 1) 
    insert_roles( 'Sweetheart',      'village', dict_messages_general['role_Sweetheart_n'], 1) 

    insert_roles( 'Qatel'             ,"Qatel", dict_messages_general['role_Qatel_n'], 0)
    insert_roles( 'Archer'            ,"Qatel", dict_messages_general['role_Archer_n'], 0)

    # insert_roles( 'forestQueen'       ,"wolf", dict_messages_general['role_forestQueen_n'], 0) 
    insert_roles( 'WolfAlpha'         ,"wolf", dict_messages_general['role_WolfAlpha_n'], 0) 
    insert_roles( 'WolfGorgine'       ,"wolf", dict_messages_general['role_WolfGorgine_n'], 0)
    insert_roles( 'WolfTolle'         ,'wolf', dict_messages_general['role_WolfTolle_n'], 0)
    insert_roles( 'Wolfx'             ,'wolf', dict_messages_general['role_Wolfx_n'], 0)
    insert_roles( 'WhiteWolf'         ,'wolf', dict_messages_general['role_WhiteWolf_n'], 0)
    # insert_roles( 'Honey'             ,'wolf', dict_messages_general['role_Honey_n'], 0.6)
    # insert_roles( 'enchanter'         ,'wolf', dict_messages_general['role_enchanter_n'], 0.6)
    # insert_roles( 'WolfJadogar'       ,'wolf', dict_messages_general['role_WolfJadogar_n'], 0.4)


    insert_roles('ferqe'               ,'cult',dict_messages_general['role_ferqe_n'], 1)
    insert_roles('Royce'               ,'cult',dict_messages_general['role_Royce_n'], 1) 
    insert_roles('Franc'               ,'cult',dict_messages_general['role_franc_n'], 1) 



    insert_roles( 'Vampire'             ,"vampire", dict_messages_general['role_Vampire_n'], 0) 
    insert_roles( 'Bloodthirsty'        ,"vampire", dict_messages_general['role_Bloodthirsty_n'], 0) 
    insert_roles( 'kentvampire'         ,"vampire", dict_messages_general['role_kentvampire_n'], 0) 
    # insert_roles( 'Chiang'         ,"vampire", dict_messages_general['role_Chiang_n'], 0) 


    # insert_roles( 'Firefighter'             ,"fire", dict_messages_general['role_Firefighter_n'], 0) 
    # insert_roles( 'IceQueen'                ,"fire", dict_messages_general['role_IceQueen_n'], 0) 




