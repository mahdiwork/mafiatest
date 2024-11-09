import database
import json
import os


file_path_general = r'Game_Mode\general_fa.ini'
dict_messages_general = {}


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

list_role = database.select_all_roles()

print(list_role[0])

list_json = [{'Name': 'روستا', 'Products': []},{'Name': "قاتل", 'Products': []},{'Name': "گرگ", 'Products': []},{'Name': "فرقه", 'Products': []},{'Name': "ومپایر", 'Products': []}]

for role in list_role:
    if role['role_grouping'] == 'village':
        if role['role'] == 'fereshte':
            j = {'Img':'specials-1.png', 'Name':role['role_name'], 'Description':dict_messages_general['role_Fereshte']}
            list_json[0]['Products'].append(j)
        else:
            j = {'Img':'specials-1.png', 'Name':role['role_name'], 'Description':dict_messages_general["role_" + role['role']]}
            list_json[0]['Products'].append(j)
    
    elif role['role_grouping'] == 'Qatel':
        j = {'Img':'specials-1.png', 'Name':role['role_name'], 'Description':dict_messages_general["role_" + role['role']]}
        list_json[1]['Products'].append(j)

    elif role['role_grouping'] == 'wolf':
        j = {'Img':'specials-1.png', 'Name':role['role_name'], 'Description':dict_messages_general["role_" + role['role']]}
        list_json[2]['Products'].append(j)

    elif role['role_grouping'] == 'cult':
        if role['role'] == 'Franc':
            j = {'Img':'specials-1.png', 'Name':role['role_name'], 'Description':dict_messages_general['role_franc']}
            list_json[3]['Products'].append(j)
        else:
            j = {'Img':'specials-1.png', 'Name':role['role_name'], 'Description':dict_messages_general["role_" + role['role']]}
            list_json[3]['Products'].append(j)

    elif role['role_grouping'] == 'vampire':
        j = {'Img':'specials-1.png', 'Name':role['role_name'], 'Description':dict_messages_general["role_" + role['role']]}
        list_json[4]['Products'].append(j)


print(list_json)



def create_json_file(name, data):
    # hed = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64)'
    # }
    # res = requests.get(f'https://snappfood.ir/mobile/v2/restaurant/details/dynamic?optionalClient=WEBSITE&appVersion=8.1.1&vendorCode={vendorCode}&show_party=1&fetch-static-data=1', headers=hed)
    # data_json = res.json()
    # os.makedirs(f'data', exist_ok=True)
    # delete_file(os.path.join('..','irwebsite','data',name+'.json'))
    with open(os.path.join(name+'.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f)


create_json_file('mafia_roles', {'Products':list_json})