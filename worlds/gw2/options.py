from dataclasses import dataclass

from Options import Range, NamedRange, Toggle, Choice, OptionSet, PerGameCommonOptions, DeathLink, FreeText
from .storylines import StorylineEnum
from .types import Profession as ProfessionEnum, Race as RaceEnum


class CharacterProfession(Choice):
    """Profession of the character you will play"""

    internal_name = "profession"
    display_name = "Profession"
    option_warrior = ProfessionEnum.WARRIOR.value
    option_guardian = ProfessionEnum.GUARDIAN.value
    option_revenant = ProfessionEnum.REVENANT.value
    option_thief = ProfessionEnum.THIEF.value
    option_engineer = ProfessionEnum.ENGINEER.value
    option_ranger = ProfessionEnum.RANGER.value
    option_mesmer = ProfessionEnum.MESMER.value
    option_elementalist = ProfessionEnum.ELEMENTALIST.value
    option_necromancer = ProfessionEnum.NECROMANCER.value

    default = "random"


class CharacterRace(Choice):
    """Race of the character you will play"""

    internal_name = "race"
    display_name = "Race"
    option_asura = RaceEnum.ASURA.value
    option_charr = RaceEnum.CHARR.value
    option_human = RaceEnum.HUMAN.value
    option_norn = RaceEnum.NORN.value
    option_sylvari = RaceEnum.SYLVARI.value

    default = "random"


class Storyline(Choice):
    """Storyline to focus on for PvE content"""

    option_core = StorylineEnum.CORE.value
    option_season_1 = StorylineEnum.SEASON_1.value
    option_season_2 = StorylineEnum.SEASON_2.value
    option_heart_of_thorns = StorylineEnum.HEART_OF_THORNS.value
    option_season_3 = StorylineEnum.SEASON_3.value
    option_path_of_fire = StorylineEnum.PATH_OF_FIRE.value
    option_season_4 = StorylineEnum.SEASON_4.value
    option_icebrood_saga = StorylineEnum.ICEBROOD_SAGA.value
    option_end_of_dragons = StorylineEnum.END_OF_DRAGONS.value
    option_secrets_of_the_obscure = StorylineEnum.SECRETS_OF_THE_OBSCURE.value
    option_janthir_wilds = StorylineEnum.JANTHIR_WILDS.value
    option_visions_of_eternity = StorylineEnum.VISIONS_OF_ETERNITY.value

    default = option_core


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
    option_spear = 17
    option_random_proficient = 18
    option_random_proficient_one_handed = 19
    option_random_proficient_two_handed = 20

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
    """ The maximum number of quest locations to generate. The number of quests in each storyline are as follows:

        Core => 49,
        Season1 => 30,
        Season2 => 32,
        HeartOfThorns => 16,
        Season3 => 36,
        PathOfFire => 16,
        Season4 => 30,
        IcebroodSaga => 41,
        EndOfDragons => 27,
        SecretsOfTheObscure => 20,
    """

    range_start = 0
    range_end = 100
    default = 49


class TrainingWeight(Range):
    """The probability weight of any location being a skill/trait unlock"""

    range_start = 0
    range_end = 1000
    default = 0


class MaxTraining(Range):
    """ The maximum number of training locations to generate. The number of training in each storyline are as follows:

        Core => 49,
        Season1 => 0,
        Season2 => 0,
        HeartOfThorns => 16,
        Season3 => 0,
        PathOfFire => 16,
        Season4 => 0,
        IcebroodSaga => 0,
        EndOfDragons => 27,
        SecretsOfTheObscure => 0,
    """

    range_start = 0
    range_end = 100
    default = 49


class WorldBossWeight(Range):
    """The probability weight of any location being a world boss"""

    range_start = 0
    range_end = 1000
    default = 250

class UniqueItemWeight(Range):
    """The probability weight of any location being a purchase from a heart vendor (or similar for maps without hearts)"""

    range_start = 0
    range_end = 1000
    default = 100

class PoiWeight(Range):
    """The probability weight of any location being a point of interest (includes waypoints, vistas, and hero points)"""

    range_start = 0
    range_end = 1000
    default = 400


class MistFragmentsRequired(Range):
    """The number of "Mist Fragment" items required to complete this world"""

    range_start = 1
    range_end = 100
    default = 20


class ExtraMistFragmentPercent(Range):
    """Multiplier to determine how many extra Mist Fragments to create. For example if mist_fragments_required is 20
    and this is value is 50, there will be 30 Mist Fragments in the multi-world,
    but only 20 will be required to finish. """

    range_start = 0
    range_end = 1000
    default = 50


class Character(FreeText):
    """ The name of the character that you will play or "New Character" if you will be making a new
     character for it"""

    default = "New Character"


class HealSkill(Choice):
    """A random core heal skill could be placed early or given to the player as a starting skill"""

    option_randomize = 0
    option_early = 1
    option_starting = 2

    default = option_starting


class GearSlots(Choice):
    """Gear slots could be placed early or given to the player at the start"""

    option_randomize = 0
    option_early = 1
    option_starting = 2

    default = option_early


class StorylineItems(Choice):
    """
    Which skills, traits, and weapons do you want shuffled into the item pool
    all: all skills, traits, and weapons
    core: only core skills, traits, and weapons
    storyline: limit to core items plus those from the selected storyline. Living World storylines include the items
        from their associated expansion
    storyline_plus: all items from the selected storyline and all preceding storylines.
    """

    option_all = 0
    option_core = 1
    option_storyline = 2
    option_storyline_plus = 3

    default = option_storyline_plus


@dataclass
class GuildWars2Options(PerGameCommonOptions):
    character: Character
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
    max_training: MaxTraining
    world_boss_weight: WorldBossWeight
    unique_item_weight: UniqueItemWeight
    poi_weight: PoiWeight
    storyline: Storyline
    mist_fragments_required: MistFragmentsRequired
    extra_mist_fragment_percent: ExtraMistFragmentPercent
    heal_skill: HealSkill
    gear_slots: GearSlots
    storyline_items: StorylineItems
