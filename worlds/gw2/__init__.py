import json
import os
from typing import Dict, Any, Iterable, Optional, Union, List, TextIO
from copy import deepcopy

from BaseClasses import Region, Entrance, Location, Item, Tutorial, ItemClassification, MultiWorld
from .Util import random_round
from .locations import location_table, LocationType, location_groups, Gw2Location, LocationData
from .options import GuildWars2Options, GroupContent, StartingMainhandWeapon, CharacterProfession, CharacterRace, \
    StartingOffhandWeapon, Storyline, HealSkill, GearSlots, StorylineItems
from worlds.AutoWorld import World, WebWorld
from .items import item_table, Gw2ItemData, Gw2Item, weapons_by_slot, item_groups, item_data, elite_specs
from .regions import RegionEnum, group_content, ten_man_content, competitive_content, get_region_rule
from .storylines import StorylineEnum, storyline_from_str


class Gw2Web(WebWorld):
    tutorials = [Tutorial(
        "Mod Setup and Use Guide",
        "A guide to playing Guild Wars 2 with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Feldar"]
    )]


class Gw2World(World):
    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = {name: data.code for name, data in location_table.items()}

    options_dataclass = GuildWars2Options
    options: GuildWars2Options

    region_table: dict[RegionEnum, Region]
    player_items: List[Gw2ItemData]

    web = Gw2Web()

    """
    Guild Wars 2 is an online role-playing game with fast-paced action combat, a rich and detailed universe of
    stories, awe-inspiring landscapes to explore, two challenging player vs. player modes—and no subscription fees!
    """
    game = "Guild Wars 2"

    def includes_storyline(self, storyline: StorylineEnum):
        if storyline is StorylineEnum.CORE:
            return True
        match self.options.storyline_items.value:
            case StorylineItems.option_all:
                return True
            case StorylineItems.option_storyline_plus:
                return storyline.value <= self.options.storyline.value
            case StorylineItems.option_storyline:
                match self.options.storyline.value:
                    case Storyline.option_season_3:
                        return storyline == StorylineEnum.HEART_OF_THORNS
                    case Storyline.option_season_4:
                        return storyline == StorylineEnum.PATH_OF_FIRE
                    case Storyline.option_icebrood_saga:
                        return storyline == StorylineEnum.PATH_OF_FIRE
                    case _:
                        return storyline == self.options.storyline
            case _:
                return False

    def item_is_usable(self, item: Gw2ItemData, allow_elite_spec: bool) -> bool:
        if item.storyline is not None and not self.includes_storyline(item.storyline):
            return False

        if len(item.specs) > 0:
            match = False
            for spec in item.specs:
                if not allow_elite_spec and spec.elite_spec is not None:
                    continue
                if spec.profession.value == self.options.character_profession.value:
                    if spec.elite_spec is not None:
                        storyline = storyline_from_str(spec.elite_spec) or elite_specs[spec.elite_spec]
                        if storyline is not None and not self.includes_storyline(storyline):
                            continue
                    match = True
                    break
            if not match:
                return False

        # Revenants can't use racial skills
        if item.race is not None and self.options.character_profession == CharacterProfession.option_revenant:
            return False

        if item.race is not None and item.race.value != self.options.character_race.value:
            return False

        return True

    def generate_early(self) -> None:
        #Update Mist Fragment count
        mist_fragments_required = self.options.mist_fragments_required.value
        bonus_mist_fragments = random_round(self.random, mist_fragments_required * (
                    self.options.extra_mist_fragment_percent / 100.0))
        mist_fragment_count = mist_fragments_required + bonus_mist_fragments
        item_table["Mist Fragment"].quantity = mist_fragment_count

        self.options.local_items.value.add("Mist Fragment")

        if self.options.heal_skill.value == HealSkill.option_early:
            skill = None
            item_group = "Healing"
            if self.options.character_profession.value == CharacterProfession.option_revenant:
                item_group = "Legend"
            self.random.shuffle(item_groups[item_group])
            for heal_skill in item_groups[item_group]:
                if self.item_is_usable(heal_skill, False):
                    skill = heal_skill

            self.multiworld.early_items[self.player][skill.name] = 1

        if self.options.gear_slots.value == GearSlots.option_early:
            for item in item_groups["Gear"]:
                self.multiworld.early_items[self.player][item.name] = 1

    def create_regions(self) -> None:

        self.region_table = {}

        #Create Menu region
        menu = Region(name="Menu", player=self.player, multiworld=self.multiworld)
        self.multiworld.regions.append(menu)
        open_world = None
        for region_enum in RegionEnum:
            if region_enum in group_content and self.options.group_content == GroupContent.option_none:
                continue
            if region_enum in ten_man_content and self.options.group_content != GroupContent.option_ten_man:
                continue
            if region_enum in competitive_content and not self.options.include_competitive:
                continue

            region = Region(name=region_enum.name, player=self.player, multiworld=self.multiworld)
            if region_enum == RegionEnum.OPEN_WORLD:
                open_world = region
                menu.connect(open_world)
            else:
                open_world.connect(region,
                                   rule=get_region_rule(region_enum, self.player, self.options.character_profession))
                region.connect(open_world)

            self.region_table[region_enum] = region

        #determine which items will be generated by logic
        self.player_items = []
        item_count = 0
        for item_name, item in item_table.items():
            if not self.item_is_usable(item,
                                  True):
                continue

            self.player_items.append(item)
            item_count += item.quantity

        #create a number of locations equal to the number of items that will be generated

        location_count = 0
        max_counts = (item_count, self.options.max_quests.value, 0, 0)
        weights = [self.options.achievement_weight.value,
                   self.options.quest_weight.value if max_counts[1] > 0 else 0,
                   self.options.training_weight.value if max_counts[2] > 0 else 0,
                   self.options.world_boss_weight.value if max_counts[3] > 0 else 0]
        counts = [0, 0, 0, 0]
        unused_locations = deepcopy(location_groups)
        while location_count < item_count:
            location_type = self.random.choices([location for location in LocationType], weights=weights, k=1)[0]

            location_region_data = unused_locations[location_type]
            region = None
            while region is None:
                region_enum = self.random.choice(location_type.get_valid_regions())

                # Core story has no achievements
                if (self.options.storyline == Storyline.option_core
                        and region_enum == RegionEnum.STORY
                        and location_type == LocationType.ACHIEVEMENT):
                    continue

                if region_enum in self.region_table.keys():
                    region = self.region_table[region_enum]

            location_data_objects = location_region_data[region_enum]
            location_data = location_data_objects.pop(0)

            location = Gw2Location(self.player, location_data.name, location_data.code, region)
            region.locations.append(location)

            counts[location_type.value] += 1
            location_count += 1
            if counts[location_type.value] >= max_counts[location_type.value]:
                weights[location_type.value] = 0

        self.multiworld.regions.extend(self.region_table.values())

    def create_item(self, item_name: str) -> Gw2Item:
        return Gw2Item(item_name, ItemClassification.progression, self.item_name_to_id[item_name], self.player)

    def create_item_from_data(self, data: Gw2ItemData) -> Gw2Item:
        return Gw2Item(data.name, ItemClassification.progression, data.code, self.player)

    def create_items(self) -> None:
        self.precollect_starting_items()

        for item_name, item_data in item_table.items():
            if item_name in {item.name for item in self.multiworld.precollected_items[self.player]}:
                continue

            if not self.item_is_usable(item_data, True):
                continue

            quantity = item_data.quantity
            for i in range(quantity):
                self.multiworld.itempool.append(self.create_item_from_data(item_data))

    def precollect_starting_items(self) -> None:
        self.precollect_starting_weapons()

        if self.options.heal_skill.value == HealSkill.option_starting:
            skill = None
            item_group = "Healing"
            if self.options.character_profession.value == CharacterProfession.option_revenant:
                item_group = "Legend"
            self.random.shuffle(item_groups[item_group])
            for heal_skill in item_groups[item_group]:
                if self.item_is_usable(heal_skill, False):
                    skill = heal_skill

            self.multiworld.push_precollected(self.create_item_from_data(skill))

        if self.options.gear_slots.value == GearSlots.option_early:
            for item in item_groups["Gear"]:
                self.multiworld.push_precollected(self.create_item_from_data(item))

    def precollect_starting_weapons(self) -> None:
        two_handed_weapons = list(filter(lambda weapon: self.item_is_usable(weapon, False),
                                         weapons_by_slot["TwoHanded"]))
        mainhand = self.select_starting_mainhand(two_handed_weapons)
        if mainhand not in two_handed_weapons:
            offhand = self.select_starting_offhand()
            self.multiworld.push_precollected(self.create_item_from_data(offhand))
        self.multiworld.push_precollected(self.create_item_from_data(mainhand))

    def select_starting_offhand(self) -> None:
        offhand_weapons = list(filter(lambda weapon: self.item_is_usable(weapon, False),
                                      weapons_by_slot["Offhand"]))
        if self.options.starting_offhand_weapon == StartingOffhandWeapon.option_random_proficient:
            return self.random.choice(offhand_weapons)
        elif self.options.starting_offhand_weapon == StartingOffhandWeapon.option_scepter:
            return item_table["Offhand Scepter"]
        elif self.options.starting_offhand_weapon == StartingOffhandWeapon.option_focus:
            return item_table["Offhand Focus"]
        elif self.options.starting_offhand_weapon == StartingOffhandWeapon.option_shield:
            return item_table["Offhand Shield"]
        elif self.options.starting_offhand_weapon == StartingOffhandWeapon.option_torch:
            return item_table["Offhand Torch"]
        elif self.options.starting_offhand_weapon == StartingOffhandWeapon.option_warhorn:
            return item_table["Offhand Warhorn"]
        return None

    def select_starting_mainhand(self, two_handed_weapons: list[Gw2ItemData]) -> None:
        mainhand_weapons = list(filter(lambda weapon: self.item_is_usable(weapon, False),
                                       weapons_by_slot["Mainhand"]))
        if self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_random_proficient:
            return self.random.choice(mainhand_weapons + two_handed_weapons)
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_random_proficient_one_handed:
            return self.random.choice(mainhand_weapons)
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_random_proficient_two_handed:
            return self.random.choice(two_handed_weapons)
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_axe:
            return item_table["Mainhand Axe"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_dagger:
            return item_table["Mainhand Dagger"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_mace:
            return item_table["Mainhand Mace"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_pistol:
            return item_table["Mainhand Pistol"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_sword:
            return item_table["Mainhand Sword"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_scepter:
            return item_table["Mainhand Scepter"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_greatsword:
            return item_table["TwoHanded Greatsword"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_hammer:
            return item_table["TwoHanded Hammer"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_longbow:
            return item_table["TwoHanded Longbow"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_rifle:
            return item_table["TwoHanded Rifle"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_short_bow:
            return item_table["TwoHanded ShortBow"]
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_staff:
            return item_table["TwoHanded Staff"]
        return None

    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict("storyline", "mist_fragments_required", "character", "character_race",
                                    "character_profession", casing="pascal")

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = \
            lambda state: state.has("Mist Fragment", self.player, self.options.mist_fragments_required.value)

    # def generate_output(self, output_directory: str) -> None:
    #     data = {}
    #     for region in self.multiworld.regions:
    #         if region.player != self.player:
    #             continue
    #         data[region.name] = []
    #         for location in region.locations:
    #             data[region.name].append(location.name)
    #
    #     filename = f"{self.multiworld.get_out_file_name_base(self.player)}.apgw2"
    #     with open(os.path.join(output_directory, filename), 'w') as f:
    #         json.dump(data, f)
