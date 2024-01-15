import re
import os
import sys
import yaml
from craft_util import *

ENCHANT     = 99

script_dir = os.path.dirname(os.path.abspath(__file__))

def loadCapabilityDict():
    """key = str 能力名, value = int 能力ID"""
    with open(f'{script_dir}/発動能力コード.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return {capability.get('name'): capability.get('code') for capability in config['capabilities']}


def loadEquipmentTypeDict():
    """key = str 部位名, value = int 部位コード"""
    with open(f'{script_dir}/装備部位コード.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return {capability.get('name'): capability.get('code') for capability in config['equipment']}


def loadEquipableCodeDict():
    """key = str 装備可能職, value = int 職ID"""
    with open(f'{script_dir}/装備可能コード.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return {capability.get('name'): capability.get('code') for capability in config['equipable_list']}


def loadSkillDict() -> dict:
    """key = str スキル名, value = int スキルID"""
    pattern = r'\[(\d+),\d+,"(\(.+\))*(.+)"(\(.+\))*\],'
    with open(f'{script_dir}/../roro/m/js/skill.dat.js', 'r', encoding='utf-8') as file:
        js_code = file.read()
    return { m[2]: int(m[0]) for m in re.findall(pattern, js_code) }


def loadUsableSkillDict() -> dict:
    """key = (int スキルID, int スキルLv), value = int 使用可能スキルID"""
    pattern = r'\[(\d+),\d,(\d+),(\d+)\],'
    with open(f'{script_dir}/../roro/m/js/usableskill.dat.js', 'r', encoding='utf-8') as file:
        js_code = file.read()
    return { (int(m[1]), int(m[2])): int(m[0]) for m in re.findall(pattern, js_code) }


def loadItemList():
    pattern = r'\[(\d+),(\d+),\d+,\d+,\d+,\d+,\d+,\d+,([^,]*),[^,]*,[^,]*,[^]]*0\]'
    with open(f'{script_dir}/../roro/m/js/item.dat.js', 'r', encoding='utf-8') as file:
        js_code = file.read()
    matches = re.findall(pattern, js_code)
    return [[int(id), name.replace('"',''), int(type)] for id, type, name in matches]


def loadSlotInfoList():
    pattern = r'\[(\d+),-1,0,0,\[\["([^"]+)","([^"]+)"]],\[],\[\[\[174,\[50,\[(\d+)]]],.+\[]]'
    with open(f'{script_dir}/../roro/m/js/data/mig.enchlist.dat.js', 'r', encoding='utf-8') as file:
        js_code = file.read()
    matches = re.findall(pattern, js_code)
    return [[int(id), name, code] for id, name, code, item_id in matches]


def getLatestIdFromItemSet():
    pattern = r'w_SE\[(\d+)] = \[[^;]+;'
    with open(f'{script_dir}/../roro/m/js/itemset.dat.js', 'r', encoding='utf-8') as file:
        js_code = file.read()
    matches = re.findall(pattern, js_code)
    return int(max([id for id in matches]))


def loadItemDict():
    pattern = r'\[(\d+),(\d+),\d+,\d+,\d+,\d+,\d+,\d+,([^,]*),[^,]*,[^,]*,[^]]*0\]'
    with open(f'{script_dir}/../roro/m/js/item.dat.js', 'r', encoding='utf-8') as file:
        js_code = file.read()
    matches = re.findall(pattern, js_code)
    return  {name.replace('"',''): int(id) for id, type, name in matches if type != "100"}    


def getEnchantDict(enchant_list):
    return {item[1]: item[0] for item in enchant_list}


def getId(name, list):
    lookup_dict_reverse = {item[1]: item[0] for item in list}
    return lookup_dict_reverse.get(name)


def getLatestId(list):
    return max([entity[0] for entity in list])


def getEnchantTypeCode(name, slotinfo_list):
    lookup_dict_reverse = {item[1]: item[2] for item in slotinfo_list}
    return lookup_dict_reverse.get(name)


def loadAutoSpellDict() -> dict:
    """key = (int スキルID, int スキルLv), value = int 使用可能スキルID"""
    pattern = r'\[(\d+),\d,(\d+),(\d+),\d+,\d+\],'
    with open(f'{script_dir}/../roro/m/js/autospell.dat.js', 'r', encoding='utf-8') as file:
        js_code = file.read()
    return { (int(m[1]), int(m[2])): int(m[0]) for m in re.findall(pattern, js_code) }


PER_STATUS_10_CODE = {
    'Str': 1,
    'Agi': 2,
    'Vit': 3,
    'Int': 4,
    'Dex': 5,
    'Luk': 6,
}
AT_STATUS_110_CODE = {
    'Str': 25,
    'Agi': 26,
    'Vit': 27,
    'Int': 28,
    'Dex': 29,
    'Luk': 30,
}
AT_STATUS_130_CODE = {
    'Str': 37,
    'Agi': 38,
    'Vit': 39,
    'Int': 40,
    'Dex': 41,
    'Luk': 42,
}
AT_SP_STATUS_100_CODE = {
    'Pow': 43,
    'Sta': 44,
    'Wis': 45,
    'Spl': 46,
    'Con': 47,
    'Crt': 48,
}
AT_BASE_LV_CODE = {
    170: 1,
    100: 2,
     99: 3,
    175: 4,
}

SKILL_CODE = loadSkillDict()
USABLE_SKILL_CODE = loadUsableSkillDict()
CARD_OR_ENCH_CODE = loadCardDict()
ITEM_CODE = loadItemDict()
AUTO_SPELL_CODE = loadAutoSpellDict()

def getCapabilityRecord(capability):

    # 能力コード取得
    capability_code = int(capability_dict.get(capability['name']))

    # 条件コード取得
    per_refine = int(capability['per_refine']) if 'per_refine' in capability else 0
    at_refine = int(capability['at_refine']) if 'at_refine' in capability else 0
    per_baselv = int(capability['per_lv']) if 'per_lv' in capability else 0
    per_status_10 = PER_STATUS_10_CODE[capability['per_status_10']] if 'per_status_10' in capability else 0
    at_status = 0
    if 'at_status_110' in capability:
        at_status = AT_STATUS_110_CODE[capability['at_status_110']]
    elif 'at_status_130' in capability:
        at_status = AT_STATUS_130_CODE[capability['at_status_130']]
    elif 'at_sp_status_100' in capability:
        at_status = AT_SP_STATUS_100_CODE[capability['at_sp_status_100']]
    at_baselv = 0
    if 'at_lv' in capability:
        at_baselv = AT_BASE_LV_CODE[capability['at_lv']]

    # 能力値取得
    value = int(capability['value']) if 'value' in capability else None
    if 'skill' in capability:
        skill_code = SKILL_CODE.get(capability['skill'])
        # スキル習得時に発動する効果の場合
        if capability_code in [199]:
            value = skill_code
        elif 'skill_lv' in capability:
            # スキル使用可能になる能力の場合
            if capability_code in [220, 222, 224]:
                value = USABLE_SKILL_CODE.get((skill_code, int(capability['skill_lv'])))
            # オートスペルの場合
            if capability_code in [221, 223, 225]:
                value = AUTO_SPELL_CODE.get((skill_code, int(capability['skill_lv'])))
        else:
            # スキル性能が変化する能力の場合
            capability_code += SKILL_CODE.get(capability['skill'])

    code  = f"{at_baselv}"                      # ベースLvが n 以上のときに（Lv99は "以下" で判定）
    code += f"{per_baselv:02d}"                 # ベースLvが n 上がる度に発動する
    code += f"00"                               # 不明コード
    code += f"{at_status:02d}"                  # 純粋なステータス x が n 以上の時に発動する
    code += f"{per_status_10:01d}"              # 純粋なステータス x が10増加する度に発動する {x : 1=Str, 2=Agi, 3=Vit, 4=Int, 5=Dex, 6=Luk}
    code += f"{at_refine:02d}"                  # 精錬値が n 以上の時に発動する
    code += f"{per_refine:01d}"                 # 精錬値が n 上がる度に発動する
    code += f"{capability_code:05d}"            # 発動する効果ID
    return f"{int(code)},{value},"
 
# -----------------------------------
# 初期化
# -----------------------------------
item_list = loadItemList()
enchant_list = loadEnchantList()
slotinfo_list = loadSlotInfoList()
equipment_type_list = loadEquipmentTypeDict()
enchant_dict = getEnchantDict(enchant_list)
capability_dict = loadCapabilityDict()
equipable_dict = loadEquipableCodeDict()

if __name__ == "__main__":
    
    item_dat_js = []
    itemset_dat_js = []
    mig_enchlist_dat_js = []

    item_id = getLatestId(item_list)
    itemset_id = getLatestIdFromItemSet()
    enchant_id = getLatestId(slotinfo_list)
    
    with open(f'{script_dir}/item.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    for item_info in config['item_list']:

    # ------------------------------------------------------
    #  item.dat.js
    # ------------------------------------------------------

        # アイテム基本性能の出力
        item_id += 1
        base_id = item_id
        equipment_type = equipment_type_list.get(item_info["type"])
        equipable_code = equipable_dict.get(item_info["required_job"])
        description = ""
        if 'desc' in item_info:
            description = item_info['desc']
        record  = f'ItemObjNew[{item_id}] = [{item_id},{equipment_type},{equipable_code},{item_info["atk_or_def"]},{item_info["weapon_lv"]},'
        record += f'{item_info["slot"]},{item_info["weight"]},{item_info["required_lv"]},'
        record += f'"{item_info["name"]}","{item_info["yomi"]}","{description}",'
        for capability in item_info['capabilities']:
            record += getCapabilityRecord(capability)
        record += "0];"
        item_dat_js.append(record)

        # item.dat.js に記述すべきセット効果の出力
        if 'set_list' in item_info:
            item_to_set_record = f"ItemIdToSetIdMap[{base_id}] = ["
            for set_info in item_info['set_list']:
                item_id += 1
                record  = f'ItemObjNew[{item_id}] = [{item_id},100,0,0,0,0,0,0,0,0,"",'
                for capability in set_info['capabilities']:
                    record += getCapabilityRecord(capability)
                record += "0];"
                item_dat_js.append(record)

        # ------------------------------------------------------
        #  itemset.dat.js
        # ------------------------------------------------------
                
                # セット条件の出力
                itemset_id += 1
                record = f"w_SE[{itemset_id}] = [{item_id},{base_id},"
                for entity in set_info['entity_list']:
                    set_entity_id = ITEM_CODE.get(entity['item_name']) if 'item_name' in entity else CARD_OR_ENCH_CODE.get(entity['card_name']) * -1
                    record += f"{set_entity_id},"
                # EOF
                record += "];"
                itemset_dat_js.append(record)
                item_to_set_record += f"{itemset_id},"
            # EOF                
            item_to_set_record += f"];"
            itemset_dat_js.append(item_to_set_record)

    # ------------------------------------------------------
    #  mig.enchlist.dat.js
    # ------------------------------------------------------
            
        if 'enchant' in item_info:
            enchant_type = item_info['enchant']['name']
            enchant_hash = getEnchantTypeCode(enchant_type, slotinfo_list)
            enchant_id += 1
            record  = f'g_constDataManager.enchListDataManager.sourceArray[{enchant_id}] = '
            record += f'[{enchant_id},-1,0,0,[["{enchant_type}","{enchant_hash}"]],[],[[[174,[50,[{base_id}]]],,['
            for slot_info in item_info['enchant']['slot_list']:
                record += f'[[178,[27,[{slot_info["slot"]}]]],,[[[187,[59,{slot_info["refine"]}],[60,4]],,[[[186,[51,['
                for enchant in slot_info['enchant_list']:
                    record += f'{CARD_OR_ENCH_CODE.get(enchant["name"])},'
                record += f']]],,[]]]]]],'
            record += f']]],[]];'
            mig_enchlist_dat_js.append(record)
            record = f'g_constDataManager.enchListDataManager.reverseResolveArrayItemId[{base_id}] = [{enchant_id}];'
            mig_enchlist_dat_js.append(record)


    OUTPUT_FILE = [
        ('item.dat.js', item_dat_js),
        ('itemset.dat.js', itemset_dat_js),
        ('mig.enchlist.dat.js', mig_enchlist_dat_js),
    ]
    for file_name, data_array in OUTPUT_FILE:
        print(f"--- {file_name} ---")
        for record in data_array:
            if 'None' in record:
                print('エラー: 空のデータが挿入されています')
                print(record)
                sys.exit(0)
        with open(f"{script_dir}/output_{file_name}", "w", encoding="utf-8") as f:
            f.write("\n".join(data_array))
