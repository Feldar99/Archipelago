from typing import Callable, Optional

from BaseClasses import CollectionState
from .storylines import get_owned_storylines
from .types import MapType, StorylineEnum
from .options import CharacterProfession
from .items import item_groups, elite_specs, core_specs
from .regions import Map, group_content, map_data


class Rule:
    player: int
    func: Callable[[CollectionState, int, Optional[CharacterProfession]], bool]
    profession: Optional[CharacterProfession]

    def __init__(self,
                 player: int,
                 func: Callable[[CollectionState, int, Optional[CharacterProfession]], bool],
                 profession: Optional[CharacterProfession] = None):
        self.player = player
        self.func = func
        self.profession = profession

    def __call__(self, state: CollectionState) -> bool:
        return self.func(state, self.player, self.profession)


class MapRule(Rule):

    def __init__(self, map_name: str, map_type: MapType, player: int, profession: Optional[CharacterProfession] = None):
        Rule.__init__(self, player,
                      lambda state, player, profession: has_map(state, player, map_name) and
                                                        can_access_region(state, player, map_type, profession),
                      profession)


def has_map(state: CollectionState, player: int, map_name: str):
    gw2_map = map_data[map_name]
    has_item = state.has(gw2_map.name, player)
    # print("item.name: ", item.name, ", has_item: ", has_item)
    return has_item


def has_skill(state: CollectionState, player: int, group: str, count: int, elite_spec: Optional[str] = None):
    skill_count = 0
    for item in item_groups[group]:
        if not state.has(item.name, player):
            continue

        is_elite_skill = False
        for spec in item.specs:
            if spec.elite_spec is not None:
                is_elite_skill = True

                # skills can only be used by the equipped elite spec
                if elite_spec is None or spec.elite_spec != elite_spec:
                    break
                # elite spec skills require the elite spec to be unlocked
                if not state.has("Progressive " + spec.elite_spec + " Trait", player):
                    break

                skill_count += 1
                break
        if not is_elite_skill:
            skill_count += 1
        if skill_count >= count:
            return True

    return False


def has_heal_skill(state: CollectionState, player: int, profession: Optional[CharacterProfession] = None,
                   elite_spec: Optional[str] = None) -> bool:
    return has_skill(state, player, "Healing", 1, elite_spec) or has_skill(state, player, "Legend", 1, elite_spec)


def has_utility_skills(state: CollectionState, player: int, elite_spec: Optional[str] = None) -> bool:
    return has_skill(state, player, "Utility", 3, elite_spec) or has_skill(state, player, "Legend", 2, elite_spec)


def has_elite_skills(state: CollectionState, player: int, elite_spec: Optional[str] = None) -> bool:
    return has_skill(state, player, "Elite", 1, elite_spec) or has_skill(state, player, "Legend", 2, elite_spec)


def has_spec(state: CollectionState, player: int, spec_name: str, elite_spec: Optional[str] = None) -> bool:
    tiers = [False, False, False]
    trait_count = 0
    group = item_groups["Core Traits"]
    if elite_spec is not None:
        group = item_groups["Elite Spec Traits"]
    for trait in group:
        if spec_name == trait.spec_name and not tiers[trait.tier]:
            if state.has(trait.name, player, 1):
                trait_count += 1
                tiers[trait.tier] = True
                if trait_count >= 3:
                    return True
    return False


def has_full_spec(state: CollectionState, player: int, elite_spec: Optional[str] = None) -> bool:
    specs_unlocked = 0
    if elite_spec is not None:
        if not has_spec(state, player, elite_spec, elite_spec):
            return False
        specs_unlocked = 1

    for spec_name in core_specs:
        if has_spec(state, player, spec_name, elite_spec):
            specs_unlocked += 1
        if specs_unlocked >= 3:
            return True

    return False


def has_all_gear(state: CollectionState, player: int) -> bool:
    if state.has_all([item.name for item in item_groups["Gear"]], player):
        return True
    else:
        return False


def has_all_weapon_slots(state: CollectionState, player: int, profession: CharacterProfession,
                         elite_spec: Optional[str] = None):
    mainhand_count = 0
    offhand_count = 0
    two_handed_count = 0
    for item in item_groups["Weapons"]:
        if not state.has(item.name, player):
            continue

        elite_spec_weapon = False
        weapon_matches_elite_spec = False
        for spec in item.specs:
            if spec.elite_spec is not None and spec.profession.value == profession.value:
                elite_spec_weapon = True

                if spec.elite_spec == elite_spec:
                    weapon_matches_elite_spec = True
                    break
        if elite_spec_weapon and not weapon_matches_elite_spec:
            continue

        if item.name.startswith("Mainhand"):
            mainhand_count += 1
        elif item.name.startswith("Offhand"):
            offhand_count += 1
        elif item.name.startswith("TwoHanded"):
            two_handed_count += 1
        # TODO: Update for elementalists and engineers
        if mainhand_count + two_handed_count >= 2 and offhand_count + two_handed_count >= 2:
            return True

    return False


def has_full_build_helper(state: CollectionState, player: int, profession: CharacterProfession,
                          elite_spec: Optional[str] = None) -> bool:
    return (has_full_spec(state, player, elite_spec) and has_heal_skill(state, player, elite_spec=elite_spec)
            and has_utility_skills(state, player, elite_spec) and has_elite_skills(state, player, elite_spec)
            and has_all_gear(state, player) and has_all_weapon_slots(state, player, profession, elite_spec))


def has_full_build(state: CollectionState, player: int, profession: CharacterProfession) -> bool:
    if has_full_build_helper(state, player, profession):
        return True
    for elite_spec in elite_specs:
        if (state.has("Progressive " + elite_spec + " Trait", player, 1)
                and has_full_build_helper(state, player, profession, elite_spec)):
            return True
    return False


def can_access_all_maps_in_region(state: CollectionState, player: int, region: MapType, storyline: StorylineEnum,
                                  profession: Optional[CharacterProfession]) -> bool:
    # print("can_access_all_maps_in_region: ", region)
    if not can_access_region(state, player, region, profession):
        # print("Cannot access Region")
        return False

    if region is MapType.STORY:
        region = MapType.OPEN_WORLD

    for item in item_groups["Maps"]:
        gw2_map = map_data[item.name]
        # print(gw2_map.type, region)
        if gw2_map.type == region:
            if not state.has(item.name, player):
                for owned_storyline in get_owned_storylines(storyline):
                    if owned_storyline in gw2_map.storylines:
                        return False

    return True


def can_access_region(state: CollectionState, player: int, region: MapType,
                      profession: Optional[CharacterProfession]) -> bool:
    # print(region)
    if region == MapType.OPEN_WORLD or region == MapType.PVP:
        return True
    elif region == MapType.STORY:
        return has_heal_skill(state, player, profession)
    elif region in group_content or region == MapType.WVW:
        return has_full_build(state, player, profession)


def get_map_rule(gw2_map: Map, player: int, profession: Optional[CharacterProfession]) -> Optional[Rule]:
    return MapRule(gw2_map.name, gw2_map.type, player, profession)


def get_region_rule(map_type: MapType, player: int, storyline: StorylineEnum, profession: Optional[CharacterProfession]) -> Rule:
    return Rule(player,
                lambda state, player, profession: can_access_all_maps_in_region(state, player, map_type, storyline, profession),
                profession)
