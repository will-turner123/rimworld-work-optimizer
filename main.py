import xml.etree.ElementTree as ET
from lxml import etree
import os
import time
import json

# TODO: colonist must be capable of intellectual work to use drug lab
# Maybe include grow zones and hydroponics basins to calculate plant growth and drug production?


class Pawn:
    skills = {}

    def __init__(self, name):
        self.name = name

    def set_skill(self, data):
        self.skills[data['skill']] = {
            'level': data['level'],
            'passion': data['passion'],
            'priority': data['priority'],
        }

    def print_skills(self):
        print(json.dumps(self.skills, indent=2))


def read_save():
    # get first save file in saves dir
    for file in os.listdir('./saves'):
        print(f'Opening {file}')
        f = open(f'./saves/{file}', 'r', encoding='utf-8').read()
        break
    parsed_file = ET.fromstring(f)
    return parsed_file


def get_faction(save):
    game = save[1]
    for child in game.findall('world'):
        factions = child.findall('factionManager')[0]
        player_faction = False
        for faction in factions.find('allFactions').iter():
            if faction.tag == 'def':
                if faction.text == 'PlayerColony':
                    player_faction = True
            elif faction.tag == 'loadID':
                load_id = faction.text
                if player_faction:
                    return f"Faction_{load_id}"
            # li > <def>PlayerColony</def>. load id is what we need from it

def handle_pawn_data(pawn):
    name = pawn.find('name').find('nick').text
    pawnObj = Pawn(name)
    index = 0
    for skill in pawn.find('skills').find('skills').findall('li'):
        skill_name = skill.find('def').text
        skill_level = skill.find('level')
        if skill_level is not None:
            skill_level = skill_level.text
        else:
            skill_level = 0
        skill_passion = skill.find('passion')
        if skill_passion is not None:
            if skill_passion == 'Minor':
                skill_passion = 1
            else:
                skill_passion = 2
        else:
            skill_passion = 0
        # find priority
        work_priority = pawn.find('workSettings').find('priorities').find('vals').findall('li')[index].text
        skill_data = {
            'skill': skill_name,
            'passion': skill_passion,
            'priority': int(work_priority),
            'level': int(skill_level)
        }
        pawnObj.set_skill(skill_data)
        index += 1
    pawnObj.print_skills()

    return pawnObj


def read_workbench():
    f = open('./workbench_skills.json', 'r')
    return json.load(f)
        
def get_workbenches():
    game = save[1]
    bill_list = []
    for child in game.find('maps').iter():
        try:
            # in not equal bc stoves are Building_WorkTable_HeatPush
            if "Building_WorkTable" in child.attrib["Class"]:
                name = child.find('def')
                related_skills = read_workbench()
                if name in related_skills:
                    related_skill = related_skills[name]
                else:
                    # if we dont know what skill a workbench uses, we assume crafting
                    related_skill = "Crafting"
                bills = child.find('billStack').find('bills').findall("li")
                for bill in bills:
                    print(bill)
        except KeyError:
            pass

def get_pawns():
    game = save[1]
    pawns = []
    for child in game.find('maps').iter():
        # TODO: make this better
        try:
            if child.attrib["Class"] == "Pawn":
                for data in child.iter():
                    faction_id = data.find('faction')
                    
                    if faction_id is not None:
                        if faction_id.text == player_faction:
                            pawn_data = handle_pawn_data(data)
                            pawns.append(pawn_data)
        except KeyError: 
            pass

save = read_save()

player_faction = get_faction(save)

# get_pawns()
get_workbenches()