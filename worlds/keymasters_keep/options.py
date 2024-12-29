import typing

from dataclasses import dataclass

from Options import Choice, OptionGroup, OptionSet, PerGameCommonOptions, Range, StartInventoryPool, Toggle

from .game import AutoGameRegister
from .games import GameArchipelagoOptions


class Goal(Choice):
    """
    Determines the victory condition.

    Keymasters Challenge: Retrieve X artifacts of resolve to unlock the Keymaster's challenge chamber and beat the ultimate challenge
    Magic Key Heist: Acquire X magic keys and escape the Keymaster's Keep
    """

    display_name: str = "Goal"

    option_keymasters_challenge: int = 0
    option_magic_key_heist: int = 1

    default = 0


class ArtifactsOfResolveTotal(Range):
    """
    Determines how many Artifacts of Resolve are in the item pool.

    Only relevant if the selected goal is Keymaster's Challenge.
    """

    display_name: str = "Artifacts of Resolve Total"

    range_start: int = 3
    range_end: int = 25

    default = 5


class ArtifactsOfResolveRequired(Range):
    """
    Determines how many Artifacts of Resolve are required to unlock the Keymaster's challenge room.

    Only relevant if the selected goal is Keymaster's Challenge.
    """

    display_name: str = "Artifacts of Resolve Required"

    range_start: int = 1
    range_end: int = 25

    default = 3


class MagicKeysRequired(Range):
    """
    Determines how many Magic Keys are required before escaping the Keymaster's Keep.

    Only relevant if the selected goal is Magic Key Heist.
    """

    display_name: str = "Magic Keys Required"

    range_start: int = 10
    range_end: int = 50

    default = 18


class KeepAreas(Range):
    """
    Determines how many areas are in the Keymaster's Keep.

    Each area will contain a new set of trials and most will be locked by one or more keys.
    """

    display_name: str = "Keep Areas"

    range_start: int = 10
    range_end: int = 100

    default = 20


class MagicKeysTotal(Range):
    """
    Determines how many Magic Keys are in the item pool.

    The keys in that pool will be used to generate the lock combinations for areas in the Keymaster's Keep. They will
    also act as the amount of available keys to the player in the Magic Key Heist goal.
    """

    display_name: str = "Magic Keys Total"

    range_start: int = 10
    range_end: int = 50

    default = 30


class UnlockedAreas(Range):
    """
    Determines how many areas are unlocked at the start of the game.

    The remaining areas will be locked by one or more keys.
    """

    display_name: str = "Unlocked Areas"

    range_start: int = 1
    range_end: int = 5

    default = 1


class LockMagicKeysMinimum(Range):
    """
    Determines the minimum amount of Magic Keys that could be required to unlock an area.

    The amount of keys required to unlock an area will be a random number between this value and the maximum. Note that
    this option will be ignored for the first few areas to ensure the game is completable.
    """

    display_name: str = "Lock Keys Minimum"

    range_start: int = 1
    range_end: int = 5

    default = 1


class LockMagicKeysMaximum(Range):
    """
    Determines the maximum amount of Magic Keys that could be required to unlock an area.

    The amount of keys required to unlock an area will be a random number between the minimum and this value. Note that
    this option will be ignored for the first few areas to ensure the game is completable.
    """

    display_name: str = "Lock Keys Maximum"

    range_start: int = 1
    range_end: int = 5

    default = 3


class AreaTrialsMinimum(Range):
    """
    Determines the minimum amount of trials that could be in an area.

    The amount of trials in an area will be a random number between this value and the maximum, but might get adjusted
    upwards to hold the item pool size.
    """

    display_name: str = "Area Trials Minimum"

    range_start: int = 1
    range_end: int = 25

    default = 3


class AreaTrialsMaximum(Range):
    """
    Determines the maximum amount of trials that could be in an area.

    The amount of trials in an area will be a random number between the minimum and this value, but might get adjusted
    upwards to hold the item pool size.
    """

    display_name: str = "Area Trials Maximum"

    range_start: int = 1
    range_end: int = 25

    default = 7


class GameSelection(OptionSet):
    """
    Defines the game pool to select from.

    All supported games are listed. Remove the ones you don't own or want to play.
    """

    display_name: str = "Game Selection"
    valid_keys = AutoGameRegister.games.keys()

    default = AutoGameRegister.games.keys()


class MetagameSelection(OptionSet):
    """
    Defines the metagame pool to select from.

    All supported metagames are listed. Remove the ones you don't own or want to play.
    """

    display_name: str = "Metagame Selection"
    valid_keys = AutoGameRegister.metagames.keys()

    default = AutoGameRegister.metagames.keys()


class IncludeAdultOnlyOrUnratedGames(Toggle):
    """
    Determines if adult only or unrated games should be considered for the game pool.
    """

    display_name: str = "Include Adult Only or Unrated Games"


class IncludeDifficultObjectives(Toggle):
    """
    Determines if difficult objectives should be considered.

    Enabling this option might yield objectives that some players will struggle or not be able to complete.

    If enabled, you can still exclude specific games with the 'excluded_games_difficult_objectives' option.
    """

    display_name: str = "Include Difficult Objectives"


class ExcludedGamesDifficultObjectives(OptionSet):
    """
    When 'include_difficult_objectives' is enabled, this option allows you to still exclude specific games.

    Only game names from 'game_selection' and 'metagame_selection' are accepted.

    If a game specified here only offers difficult objectives, this option will have no effect for it.
    """

    display_name: str = "Excluded Games Difficult Objectives"
    valid_keys = sorted(AutoGameRegister.games.keys()) + sorted(AutoGameRegister.metagames.keys())

    default = list()


class IncludeTimeConsumingObjectives(Toggle):
    """
    Determines if time-consuming objectives should be considered.

    Enabling this option might yield objectives that take much longer to complete (i.e. more than 1 hour).

    If enabled, you can still exclude specific games with the 'excluded_games_time_consuming_objectives' option.
    """

    display_name: str = "Include Time-Consuming Objectives"


class ExcludedGamesTimeConsumingObjectives(OptionSet):
    """
    When 'include_time_consuming_objectives' is enabled, this option allows you to still exclude specific games.

    Only game names from 'game_selection' and 'metagame_selection' are accepted.

    If a game specified here only offers time-consuming objectives, this option will have no effect for it.
    """

    display_name: str = "Excluded Games Time-Consuming Objectives"
    valid_keys = sorted(AutoGameRegister.games.keys()) + sorted(AutoGameRegister.metagames.keys())

    default = list()


class HintsRevealObjectives(Toggle):
    """
    Determines if Archipelago hints will provide information about a location's objective.

    Enabling this option will potentially spoil the game for an area and the objective that needs to be completed.
    """

    display_name: str = "Hints Reveal Objectives"


@dataclass
class KeymastersKeepOptions(PerGameCommonOptions, GameArchipelagoOptions):
    start_inventory_from_pool: StartInventoryPool
    goal: Goal
    artifacts_of_resolve_total: ArtifactsOfResolveTotal
    artifacts_of_resolve_required: ArtifactsOfResolveRequired
    magic_keys_required: MagicKeysRequired
    keep_areas: KeepAreas
    magic_keys_total: MagicKeysTotal
    unlocked_areas: UnlockedAreas
    lock_magic_keys_minimum: LockMagicKeysMinimum
    lock_magic_keys_maximum: LockMagicKeysMaximum
    area_trials_minimum: AreaTrialsMinimum
    area_trials_maximum: AreaTrialsMaximum
    game_selection: GameSelection
    metagame_selection: MetagameSelection
    include_adult_only_or_unrated_games: IncludeAdultOnlyOrUnratedGames
    include_difficult_objectives: IncludeDifficultObjectives
    excluded_games_difficult_objectives: ExcludedGamesDifficultObjectives
    include_time_consuming_objectives: IncludeTimeConsumingObjectives
    excluded_games_time_consuming_objectives: ExcludedGamesTimeConsumingObjectives
    hints_reveal_objectives: HintsRevealObjectives


# Option presets here...


option_groups: typing.List[OptionGroup] = [
    OptionGroup(
        "Goal Options",
        [
            Goal,
            ArtifactsOfResolveTotal,
            ArtifactsOfResolveRequired,
            MagicKeysRequired,
        ],
    ),
    OptionGroup(
        "Keep Generation Options",
        [
            KeepAreas,
            MagicKeysTotal,
            UnlockedAreas,
            LockMagicKeysMinimum,
            LockMagicKeysMaximum,
            AreaTrialsMinimum,
            AreaTrialsMaximum,
        ],
    ),
    OptionGroup(
        "Game / Objective Selection Options",
        [
            IncludeAdultOnlyOrUnratedGames,
            IncludeDifficultObjectives,
            ExcludedGamesDifficultObjectives,
            IncludeTimeConsumingObjectives,
            ExcludedGamesTimeConsumingObjectives,
            HintsRevealObjectives,
            MetagameSelection,
            GameSelection,
        ],
    ),
    OptionGroup(
        "Individual Game Options",
        typing.get_type_hints(GameArchipelagoOptions).values(),
    )
]