import enum

from BaseClasses import Item
from typing import Dict, Optional
from Utils import parse_yaml
from . import data
from importlib.resources import files

from .types import Profession, Race, Gw2ItemData, StorylineEnum, Spec
from .regions import map_data

from .storylines import storyline_from_str


class Gw2Item(Item):
    game: str = "Guild Wars 2"


def create_item_data(name: str, quantity=1, storyline=None):
    item = Gw2ItemData()
    item.name = name
    item.code = Gw2ItemData.next_id_val
    item.quantity = quantity
    item.specs = set()
    item.race = None
    item.storyline = storyline
    Gw2ItemData.next_id_val += 1

    item_data[item.code] = item
    return item


def create_trait_data(name: str, tier: int, spec_name: str, quantity=1, storyline=None):
    trait_data = create_item_data(name, quantity, storyline)
    trait_data.tier = tier
    trait_data.spec_name = spec_name

    return trait_data


class TraitData(Gw2ItemData):
    tier: int
    spec_name: str


item_data: dict[int, Gw2ItemData] = {}
weapons_by_slot: dict[str, [Gw2ItemData]] = {}
item_groups: dict[str, [Gw2ItemData]] = {}
elite_specs: dict[str, StorylineEnum] = {}
core_specs: set[str] = set()


def load_weapons():
    weapons_items = []
    item_groups["Weapons"] = []

    with files(data).joinpath("Weapons.yaml").open() as f:
        weapons = parse_yaml(f.read())
        for weapon_name in weapons:
            weapon_slots = weapons[weapon_name]
            for weapon_slot in weapon_slots:
                professions = weapon_slots[weapon_slot]
                specs = set()
                for profession_data in professions:
                    elite_spec = None
                    profession = profession_data
                    if isinstance(profession_data, dict):
                        for profession_name in profession:
                            elite_spec = (profession_data[profession_name])
                            profession = profession_name
                    spec = Spec(profession=Profession[profession.upper()], elite_spec=elite_spec)
                    specs.add(spec)
                item_name = weapon_slot + " " + weapon_name
                weapon = create_item_data(item_name)
                weapon.specs = specs
                weapons_items.append(weapon)
                item_groups["Weapons"].append(weapon)
                if weapon_slot in weapons_by_slot.keys():
                    weapons_by_slot[weapon_slot].append(weapon)
                else:
                    weapons_by_slot[weapon_slot] = [weapon]

    return weapons_items


def load_skill_group(skills_data, spec: Optional[Spec] = None,
                     race: Optional[Race] = None,
                     storyline: Optional[StorylineEnum] = None):
    skills = []
    skill_types = ["Healing", "Utility", "Elite", "Legend"]
    for skill_type in skill_types:
        if skill_type not in skills_data.keys():
            continue
        if skill_type not in item_groups.keys():
            item_groups[skill_type] = []
        for skill_name in skills_data[skill_type]:
            skill = create_item_data(name=skill_name + " " + skill_type + " Skill", quantity=1, storyline=storyline)
            if spec is not None:
                skill.specs.add(spec)
            skill.race = race
            skills.append(skill)
            item_groups[skill_type].append(skill)
    return skills


def load_skills():
    skills = []

    with files(data).joinpath("Skills.yaml").open() as f:
        skill_data = parse_yaml(f.read())
        for profession in Profession:
            spec = Spec(profession)
            skills.extend(load_skill_group(skill_data[profession.name]["Core"], spec=spec))

            for group in skill_data[profession.name].keys():
                if group in elite_specs:
                    spec = Spec(profession=profession, elite_spec=group)
                    skills.extend(
                        load_skill_group(skill_data[profession.name][group], spec=spec, storyline=elite_specs[group]))

        for race in Race:
            skills.extend(load_skill_group(skill_data[race.name], race=race))

    return skills


def load_traits():
    traits_items = []
    item_groups["Traits"] = []
    item_groups["Core Traits"] = []
    item_groups["Elite Spec Traits"] = []
    elite_specs.clear()
    with files(data).joinpath("Traits.yaml").open() as f:
        trait_data = parse_yaml(f.read())
        for profession_name in trait_data:
            profession_data = trait_data[profession_name]
            for spec_name in profession_data:
                spec_data = profession_data[spec_name]
                storyline = None
                if "storyline" in spec_data:
                    storyline = storyline_from_str(spec_data["storyline"])
                    elite_specs[spec_name] = storyline
                else:
                    core_specs.add(spec_name)
                traits = spec_data["traits"]
                for index, trait in enumerate(traits):
                    item = create_trait_data(name=trait + " " + spec_name + " Trait",
                                             tier=index // 3,
                                             spec_name=spec_name,
                                             storyline=storyline)
                    spec = Spec(Profession[profession_name.upper()])
                    item.specs.add(spec)
                    traits_items.append(item)
                    if storyline is None:
                        item_groups["Core Traits"].append(item)
                    else:
                        item_groups["Elite Spec Traits"].append(item)

            # traits = profession_traits["Core"]
            # traits.extend(profession_traits["Elite"])
            # for trait in traits:
            #     storyline = storyline_from_str(trait)
            #     if storyline is not None:
            #         trait = profession_traits["Elite"][trait]
            #         elite_specs[trait] = storyline
            #     item = Gw2ItemData(name="Progressive " + trait + " Trait", quantity=9, storyline=storyline)
            #     spec = Spec(Profession[profession_name.upper()])
            #     item.specs.add(spec)
            #     traits_items.append(item)
            #     if trait in elite_specs:
            #         item_groups["Elite Spec Traits"].append(item)
            #     else:
            #         item_groups["Core Traits"].append(item)

    item_groups["Traits"].extend(traits_items)
    return traits_items


def load_gear():
    armor_items = []
    armor_slots = ["Head", "Shoulders", "Chest", "Gloves", "Legs", "Boots", "Back", "Ring 1", "Ring 2", "Amulet",
                   "Accessory 1", "Accessory 2", "Relic", "Aqua Breather"]
    for slot in armor_slots:
        item = create_item_data(slot)
        armor_items.append(item)

    item_groups["Gear"] = armor_items
    return armor_items


def create_map_item_data():
    map_items = []
    for gw2_map in map_data.values():
        item = create_item_data(gw2_map.name)
        map_items.append(item)
        gw2_map.item = item

    item_groups["Maps"] = map_items
    return map_items


item_table: Dict[str, Gw2ItemData] = {}


def load_items():
    items = []
    items.extend(load_weapons())
    items.extend(load_traits())
    items.extend(load_skills())
    items.extend(load_gear())
    items.extend(create_map_item_data())
    items.append(create_item_data("Mist Fragment"))  # Quantity will get set after options have been loaded

    for item in items:
        item_table[item.name] = item


load_items()
