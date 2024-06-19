from dataclasses import dataclass

from Options import Range, NamedRange, Toggle, Choice, OptionSet, PerGameCommonOptions, DeathLink
from .items import Profession as ProfessionEum, Race as RaceEnum


class CharacterProfession(Choice):
    """Profession of the character you will play"""

    internal_name = "profession"
    display_name = "Profession"
    option_warrior = ProfessionEum.WARRIOR.value
    option_guardian = ProfessionEum.GUARDIAN.value
    option_revenant = ProfessionEum.REVENANT.value
    option_thief = ProfessionEum.THIEF.value
    option_engineer = ProfessionEum.ENGINEER.value
    option_ranger = ProfessionEum.RANGER.value
    option_mesmer = ProfessionEum.MESMER.value
    option_elementalist = ProfessionEum.ELEMENTALIST.value
    option_necromancer = ProfessionEum.NECROMANCER.value

    default = option_engineer


class CharacterRace(Choice):
    """Race of the character you will play"""

    internal_name = "race"
    display_name = "Race"
    option_asura = RaceEnum.ASURA.value
    option_charr = RaceEnum.CHARR.value
    option_human = RaceEnum.HUMAN.value
    option_norn = RaceEnum.NORN.value
    option_sylvari = RaceEnum.SYLVARI.value

    default = option_charr


class Storyline(Choice):
    """Storyline to focus on for PvE content"""

    option_core = 0
    option_season_1 = 1
    option_season_2 = 2
    option_heart_of_thorns = 3
    option_season_3 = 4
    option_path_of_fire = 5
    option_season_4 = 6
    option_icebrood_saga = 7
    option_end_of_dragons = 8
    option_secrets_of_the_obscure = 9


class StartingMainhandWeapon(Choice):
    """Sets your starting mainhand weapon.

    none: Do not start with a mainhand weapon. Only valid if you select an offhand.  Some offhand weapons are difficult
        to do damage with, so be careful with this option.
    random/random_proficient: Selects a mainhand or two-handed weapon your character is proficient with.
    random_proficient_one_handed: Selects a one-handed weapon that your profession is proficient with.
    random_proficient_two_handed: Selects a two-handed weapon that your profession is proficient with.

    """

    option_none = 0
    option_axe = 1
    option_dagger = 2
    option_mace = 3
    option_pistol = 4
    option_sword = 5
    option_scepter = 6
    option_greatsword = 11
    option_hammer = 12
    option_longbow = 13
    option_rifle = 14
    option_short_bow = 15
    option_staff = 16
    option_random_proficient = 17
    option_random_proficient_one_handed = 18
    option_random_proficient_two_handed = 19

    default = option_random_proficient

    @classmethod
    def from_text(cls, text: str):
        if text == "random":
            return cls.option_random_proficient
        else:
            return super().from_text(text)


class StartingOffhandWeapon(Choice):
    """Sets your starting offhand weapon.
    This will be ignored if a two-handed weapon was selected for starting_mainhand_weapon

    none: Do not start with an offhand weapon. Only valid if you select a mainhand.
    random/random_proficient: Selects an offhand weapon your character is proficient with.

    """

    option_none = 0
    option_scepter = 6
    option_focus = 7
    option_shield = 8
    option_torch = 9
    option_warhorn = 10
    option_random_proficient = 17

    default = option_random_proficient

    @classmethod
    def from_text(cls, text: str):
        if text == "random":
            return cls.option_random_proficient
        else:
            return super().from_text(text)


class GroupContent(Choice):
    """Sets what kind of group content you are interested in. Please be respectful of other players and do not join
    pugs doing difficult content if you do not have the unlocks to contribute (Don't try to fight Dhuum naked)

    none: Limits game to open world, story, and WvW (if competitive is selected)
    five_man: Also allows fractals, dungeons, and PvP (if competitive is selected)
    ten_man: Also allows raids and strikes
    """

    option_none = 0
    option_five_man = 1
    option_ten_man = 2

    default = option_none


class IncludeCompetitive(Toggle):
    """Allows PvP and WvW achievements to be included"""


class AchievementWeight(Range):
    """The probability weight of any location being an achievement"""

    range_start = 0
    range_end = 1000
    default = 500


class QuestWeight(Range):
    """The probability weight of any location being a quest"""

    range_start = 0
    range_end = 1000
    default = 100


class MaxQuests(Range):
    """ The maximum number of quest locations to generate"""

    range_start = 0
    range_end = 100
    default = 0


class TrainingWeight(Range):
    """The probability weight of any location being a skill/trait unlock"""

    range_start = 0
    range_end = 1000
    default = 0


class WorldBossWeight(Range):
    """The probability weight of any location being a world boss"""

    range_start = 0
    range_end = 1000
    default = 250


@dataclass
class GuildWars2Options(PerGameCommonOptions):
    character_profession: CharacterProfession
    character_race: CharacterRace
    starting_mainhand_weapon: StartingMainhandWeapon
    starting_offhand_weapon: StartingOffhandWeapon
    group_content: GroupContent
    include_competitive: IncludeCompetitive
    achievement_weight: AchievementWeight
    quest_weight: QuestWeight
    max_quests: MaxQuests
    training_weight: TrainingWeight
    world_boss_weight: WorldBossWeight
    storyline: Storyline
