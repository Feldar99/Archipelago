from typing import Dict, Any, Optional, List
from copy import deepcopy

from .types import Race, StorylineEnum
from .storylines import storyline_from_str, get_owned_storylines
from .rules import get_map_rule, get_region_rule
from BaseClasses import Region, Tutorial, ItemClassification
from .Util import random_round
from .options import GuildWars2Options, GroupContent, StartingMainhandWeapon, CharacterProfession, CharacterRace, \
    StartingOffhandWeapon, Storyline, HealSkill, GearSlots, StorylineItems
from worlds.AutoWorld import World, WebWorld
from .items import item_table, Gw2ItemData, Gw2Item, weapons_by_slot, item_groups, item_data, elite_specs
from .regions import MapType, group_content, ten_man_content, competitive_content, map_data
from .locations import location_table, LocationType, location_groups, Gw2Location, LocationData, storyline_items, \
    storyline_pois


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

    region_table: dict[str, Region]
    player_items: List[Gw2ItemData]

    web = Gw2Web()

    """
    Guild Wars 2 is an online role-playing game with fast-paced action combat, a rich and detailed universe of
    stories, awe-inspiring landscapes to explore, two challenging player vs. player modes—and no subscription fees!
    """
    game = "Guild Wars 2"

    starting_mainhand: Optional[Gw2ItemData]
    starting_offhand: Optional[Gw2ItemData]
    starting_map: Gw2ItemData

    def includes_storyline(self, storyline: StorylineEnum):
        if storyline is StorylineEnum.CORE:
            return True
        if self.options.storyline_items.value == StorylineItems.option_all:
            return True
        elif self.options.storyline_items.value == StorylineItems.option_storyline_plus:
            return storyline.value <= self.options.storyline.value
        elif self.options.storyline_items.value == StorylineItems.option_storyline:
            if self.options.storyline.value == Storyline.option_season_3:
                return storyline == StorylineEnum.HEART_OF_THORNS
            elif self.options.storyline.value == Storyline.option_season_4:
                return storyline == StorylineEnum.PATH_OF_FIRE
            elif self.options.storyline.value == Storyline.option_icebrood_saga:
                return storyline == StorylineEnum.PATH_OF_FIRE
            else:
                return storyline.value == self.options.storyline.value
        else:
            return False

    def includes_map_type(self, map_type: MapType):
        if map_type in group_content and self.options.group_content == GroupContent.option_none:
            return False
        if map_type in ten_man_content and self.options.group_content != GroupContent.option_ten_man:
            return False
        if map_type in competitive_content and not self.options.include_competitive:
            return False

        return True

    def item_is_usable(self, item: Gw2ItemData, allow_elite_spec: bool) -> bool:
        #Map Items
        if item.name in map_data:
            gw2_map = map_data[item.name]

            if not self.includes_map_type(gw2_map.type):
                # print(item.name + " not usable: Map Type")
                return False

            storyline = StorylineEnum(self.options.storyline.value)
            for owned_storyline in get_owned_storylines(storyline):
                if owned_storyline in gw2_map.storylines:
                    # print(item.name)
                    return True


            # print(item.name + " not usable: Storyline")
            return False


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
            skill = self.get_random_heal_skill()
            self.multiworld.early_items[self.player][skill.name] = 1

        if self.options.gear_slots.value == GearSlots.option_early:
            for item in item_groups["Gear"]:
                self.multiworld.early_items[self.player][item.name] = 1

        self.select_starting_weapons()

    def get_random_heal_skill(self):
        skill = None
        item_group = "Healing"
        if self.options.character_profession.value == CharacterProfession.option_revenant:
            item_group = "Legend"
        self.random.shuffle(item_groups[item_group])
        for heal_skill in item_groups[item_group]:
            if self.item_is_usable(heal_skill, False):
                skill = heal_skill
        return skill

    def create_regions(self) -> None:

        self.region_table = {}

        #Create Menu region
        menu = Region(name="Menu", player=self.player, multiworld=self.multiworld)
        self.multiworld.regions.append(menu)
        open_world = None

        # Create map regions
        map_connections = []
        start_map = None
        for gw2_map in map_data.values():
            region = Region(name=gw2_map.name, player=self.player, multiworld=self.multiworld)
            self.region_table[gw2_map.name] = region
            for entrance_map_name in gw2_map.entrances:
                map_connections.append((entrance_map_name, region, get_map_rule(gw2_map, self.player, self.options.character_profession)))
            storyline = StorylineEnum(self.options.storyline.value)
            # if len(gw2_map.start) > 0:
            #     print(storyline, gw2_map.start)
            if storyline in gw2_map.start:
                race = gw2_map.start[storyline]
                # print(race, Race(self.options.character_race.value))
                if race == "ANY" or Race[race] == Race(self.options.character_race.value):
                    # print(region)
                    start_map = region

        # print(menu.name, start_map.name)
        menu.connect(start_map)

        for map_connection in map_connections:
            self.region_table[map_connection[0]].connect(map_connection[1], rule=map_connection[2])

        # Generic Regions for achievements and quests until I can get those fully cataloged
        for region_enum in MapType:
            if not self.includes_map_type(region_enum):
                continue

            region = Region(name=region_enum.name, player=self.player, multiworld=self.multiworld)
            start_map.connect(region,
                              rule=get_region_rule(region_enum,
                                                   self.player,
                                                   StorylineEnum(self.options.storyline.value),
                                                   self.options.character_profession))

            self.region_table[region_enum.name] = region

        #determine which items will be generated by logic
        self.player_items = []
        item_count = 0
        for item_name, item in item_table.items():
            if not self.item_is_usable(item,
                                       True):
                continue

            # print(item_name)
            self.player_items.append(item)
            item_count += item.quantity

        # need a location for every map except the starting map
        item_count -= 1
        # self.player_items.extend(item_groups["Maps"])
        self.starting_map = map_data[start_map.name].item


        if self.options.gear_slots.value == GearSlots.option_starting:
            item_count -= len(item_groups["Gear"])

        if self.options.heal_skill.value == GearSlots.option_starting:
            item_count -= 1

        if self.starting_offhand is not None:
            item_count -= 1

        if self.starting_mainhand is not None:
            item_count -= 1

        #create a number of locations equal to the number of items that will be generated

        location_count = 0
        unused_locations = deepcopy(location_groups)
        unused_items = deepcopy(storyline_items[self.options.storyline.value]) if self.options.storyline in storyline_items else []
        unused_pois = deepcopy(storyline_pois[self.options.storyline.value]) if self.options.storyline in storyline_pois else []
        max_counts = (item_count,
                      self.options.max_quests.value,
                      0,
                      0,
                      len(unused_items),
                      len(unused_pois),
                      )
        weights = [self.options.achievement_weight.value,
                   self.options.quest_weight.value if max_counts[1] > 0 else 0,
                   self.options.training_weight.value if max_counts[2] > 0 else 0,
                   self.options.world_boss_weight.value if max_counts[3] > 0 else 0,
                   self.options.unique_item_weight.value if max_counts[4] > 0 else 0,
                   self.options.poi_weight.value if max_counts[5] > 0 else 0,
                   ]
        counts = [0, 0, 0, 0, 0, 0]
        while location_count < item_count:
            location_type = self.random.choices([location for location in LocationType], weights=weights, k=1)[0]

            location_region_data = unused_locations[location_type]
            region = None
            while region is None:
                region_enum = self.random.choice(location_type.get_valid_regions())

                # Core story has no achievements
                if (self.options.storyline == Storyline.option_core
                        and region_enum == MapType.STORY
                        and location_type == LocationType.ACHIEVEMENT):
                    continue

                if region_enum.name in self.region_table.keys():
                    region = self.region_table[region_enum.name]

            if location_type == LocationType.UNIQUE_ITEM:
                location_index = self.random.randint(0, len(unused_items) - 1)
                # print(location_index, " / ", len(unused_items))
                location_data = unused_items.pop(location_index)
            elif location_type == LocationType.POINT_OF_INTEREST:
                location_index = self.random.randint(0, len(unused_pois) - 1)
                location_data = unused_pois.pop(location_index)
            else:
                location_data_objects = location_region_data[region_enum]
                location_data = location_data_objects.pop(0)

            if location_data.map is not None:
                region = self.region_table[location_data.map.name]

            location = Gw2Location(self.player, location_data.name, location_data.code, region)
            region.locations.append(location)

            counts[location_type.value] += 1
            location_count += 1
            if counts[location_type.value] >= max_counts[location_type.value]:
                # print("No more ", location_type)
                weights[location_type.value] = 0

        self.multiworld.regions.extend(self.region_table.values())
        # for name in self.region_table:
        #     region = self.region_table[name]
        #     print("Region: ", name)
        #     print("Locations: ")
        #     for location in region.locations:
        #         print("  ", location)
        #     print("Exits: ")
        #     for exit in region.exits:
        #         print("  ", exit.name)

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
        self.multiworld.push_precollected(self.create_item_from_data(self.starting_map))
        if self.starting_mainhand is not None:
            self.multiworld.push_precollected(self.create_item_from_data(self.starting_mainhand))
        if self.starting_offhand is not None:
            self.multiworld.push_precollected(self.create_item_from_data(self.starting_offhand))

        if self.options.heal_skill.value == HealSkill.option_starting:
            skill = self.get_random_heal_skill()

            self.multiworld.push_precollected(self.create_item_from_data(skill))

        if self.options.gear_slots.value == GearSlots.option_starting:
            for item in item_groups["Gear"]:
                self.multiworld.push_precollected(self.create_item_from_data(item))

    def select_starting_weapons(self) -> None:
        two_handed_weapons = list(filter(lambda weapon: self.item_is_usable(weapon, False),
                                         weapons_by_slot["TwoHanded"]))
        self.starting_mainhand = self.select_starting_mainhand(two_handed_weapons)
        if self.starting_mainhand in two_handed_weapons:
            self.starting_offhand = None
        else:
            self.starting_offhand = self.select_starting_offhand()

    def select_starting_offhand(self) -> Optional[Gw2ItemData]:
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

    def select_starting_mainhand(self, two_handed_weapons: list[Gw2ItemData]) -> Optional[Gw2ItemData]:
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
        elif self.options.starting_mainhand_weapon == StartingMainhandWeapon.option_spear:
            return item_table["TwoHanded Spear"]
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
