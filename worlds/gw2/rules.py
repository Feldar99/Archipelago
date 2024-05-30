from typing import Callable, Optional

from BaseClasses import CollectionState
from .options import CharacterProfession
from .items import item_groups, elite_specs


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

    print("Missing " + group + " Skill")
    return False


def has_heal_skill(state: CollectionState, player: int, profession: Optional[CharacterProfession] = None, elite_spec: Optional[str] = None) -> bool:
    return has_skill(state, player, "Healing", 1, elite_spec) or has_skill(state, player, "Legend", 1, elite_spec)


def has_utility_skills(state: CollectionState, player: int, elite_spec: Optional[str] = None) -> bool:
    return has_skill(state, player, "Utility", 3, elite_spec) or has_skill(state, player, "Legend", 2, elite_spec)


def has_elite_skills(state: CollectionState, player: int, elite_spec: Optional[str] = None) -> bool:
    return has_skill(state, player, "Elite", 1, elite_spec) or has_skill(state, player, "Legend", 2, elite_spec)


def has_full_spec(state: CollectionState, player: int, elite_spec: Optional[str] = None) -> bool:
    specs_unlocked = 0
    if elite_spec is not None:
        if not state.has("Progressive " + elite_spec + " Trait", player, 3):
            print("Missing 3 " + elite_spec + " Traits")
            return False
        specs_unlocked = 1

    for trait in item_groups["Core Traits"]:
        if state.has(trait.name, player, 3):
            specs_unlocked += 1
        if specs_unlocked >= 3:
            return True

    print("Missing Spec, specs_unlocked: ", specs_unlocked)
    return False


def has_all_gear(state: CollectionState, player: int) -> bool:
    if state.has_all([item.name for item in item_groups["Gear"]], player):
        return True
    else:
        print("Missing Gear")
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
            print("No elite spec for ", item.name)
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

    print("Missing Weapon")
    return False


def has_full_build_helper(state: CollectionState, player: int, profession: CharacterProfession, elite_spec: Optional[str] = None) -> bool:
    return (has_full_spec(state, player, elite_spec) and has_heal_skill(state, player, elite_spec=elite_spec)
            and has_utility_skills(state, player, elite_spec) and has_elite_skills(state, player, elite_spec)
            and has_all_gear(state, player) and has_all_weapon_slots(state, player, profession, elite_spec))


def has_full_build(state: CollectionState, player: int, profession: CharacterProfession) -> bool:
    if has_full_build_helper(state, player, profession):
        print("Full Core Build")
        return True
    for elite_spec in elite_specs:
        if (state.has("Progressive " + elite_spec + " Trait", player, 1)
                and has_full_build_helper(state, player, profession, elite_spec)):
            print("Full " + elite_spec + " Build")
            return True
    return False
