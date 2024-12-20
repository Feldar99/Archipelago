from typing import List

from dataclasses import dataclass

from Options import OptionSet, Toggle

from ..game import Game
from ..game_objective_template import GameObjectiveTemplate

from ..enums import KeymastersKeepGamePlatforms


class ArchipelagoMultiworldRandomizerGame(Game):
    name = "Archipelago Multiworld Randomizer"
    platform = KeymastersKeepGamePlatforms.PC

    platforms_other = None

    is_adult_only_or_unrated = False

    def optional_game_constraint_templates(self) -> List[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(
                label="Hint Cost: HINT_COST%",
                data={"HINT_COST": (self.hint_costs, 1)}
            ),
            GameObjectiveTemplate(
                label="Release: RELEASE",
                data={"RELEASE": (self.release, 1)}
            ),
        ]

    def game_objective_templates(self) -> List[GameObjectiveTemplate]:
        game_objective_templates: List[GameObjectiveTemplate] = [
            GameObjectiveTemplate(
                label="Complete a solo randomizer with GAME",
                data={"GAME": (self.games, 1)},
                is_time_consuming=True,
                is_difficult=False,
                weight=2,
            ),
            GameObjectiveTemplate(
                label="Complete a multiworld randomizer with GAMES",
                data={"GAMES": (self.games, 2)},
                is_time_consuming=True,
                is_difficult=False,
                weight=3,
            ),
            GameObjectiveTemplate(
                label="Complete a multiworld randomizer with GAMES",
                data={"GAMES": (self.games, 3)},
                is_time_consuming=True,
                is_difficult=False,
                weight=4,
            ),
            GameObjectiveTemplate(
                label="Complete a multiworld randomizer with GAMES",
                data={"GAMES": (self.games, 5)},
                is_time_consuming=True,
                is_difficult=False,
                weight=4,
            ),
        ]

        if bool(self.archipelago_options.archipelago_multiworld_randomizer_allow_apbingo_objectives):
            game_objective_templates += [
                GameObjectiveTemplate(
                    label="Blackout a SIZExSIZE APBingo board in a multiworld randomizer with GAMES",
                    data={"GAMES": (self.games, 2), "SIZE": (self.bingo_board_sizes, 1)},
                    is_time_consuming=True,
                    is_difficult=False,
                    weight=1,
                ),
                GameObjectiveTemplate(
                    label="Blackout a SIZExSIZE APBingo board in a multiworld randomizer with GAMES",
                    data={"GAMES": (self.games, 3), "SIZE": (self.bingo_board_sizes, 1)},
                    is_time_consuming=True,
                    is_difficult=False,
                    weight=1,
                ),
                GameObjectiveTemplate(
                    label="Blackout a SIZExSIZE APBingo board in a multiworld randomizer with GAMES",
                    data={"GAMES": (self.games, 5), "SIZE": (self.bingo_board_sizes, 1)},
                    is_time_consuming=True,
                    is_difficult=False,
                    weight=1,
                ),
                GameObjectiveTemplate(
                    label=(
                        "Complete a multiworld randomizer with GAMES and get COUNT bingo(s) on a "
                        "SIZExSIZE APBingo board"
                    ),
                    data={
                        "GAMES": (self.games, 2),
                        "COUNT": (self.bingo_counts, 1),
                        "SIZE": (self.bingo_board_sizes, 1)
                    },
                    is_time_consuming=True,
                    is_difficult=False,
                    weight=2,
                ),
                GameObjectiveTemplate(
                    label=(
                        "Complete a multiworld randomizer with GAMES and get COUNT bingo(s) on a "
                        "SIZExSIZE APBingo board"
                    ),
                    data={
                        "GAMES": (self.games, 3),
                        "COUNT": (self.bingo_counts, 1),
                        "SIZE": (self.bingo_board_sizes, 1)
                    },
                    is_time_consuming=True,
                    is_difficult=False,
                    weight=3,
                ),
                GameObjectiveTemplate(
                    label=(
                        "Complete a multiworld randomizer with GAMES and get COUNT bingo(s) on a "
                        "SIZExSIZE APBingo board"
                    ),
                    data={
                        "GAMES": (self.games, 5),
                        "COUNT": (self.bingo_counts, 1),
                        "SIZE": (self.bingo_board_sizes, 1)
                    },
                    is_time_consuming=True,
                    is_difficult=False,
                    weight=3,
                ),
            ]

        return game_objective_templates

    @staticmethod
    def hint_costs() -> List[int]:
        return list(range(0, 26)) + [100]

    @staticmethod
    def release() -> List[str]:
        return ["Off", "On", "On", "On", "On"]

    def games(self) -> List[str]:
        games: List[str] = list(
            self.archipelago_options.archipelago_multiworld_randomizer_supported_game_selection.value
        )

        games += list(
            self.archipelago_options.archipelago_multiworld_randomizer_unsupported_game_selection.value
        )

        if bool(self.archipelago_options.include_adult_only_or_unrated_games):
            games += list(
                self.archipelago_options.archipelago_multiworld_randomizer_adult_only_or_unrated_game_selection.value
            )

        games += list(
            self.archipelago_options.archipelago_multiworld_randomizer_custom_game_selection.value
        )

        return sorted(games)

    @staticmethod
    def bingo_board_sizes() -> List[int]:
        return list(range(3, 11))

    @staticmethod
    def bingo_counts() -> List[int]:
        return list(range(1, 9))


# Archipelago Options
class ArchipelagoMultiworldRandomizerSupportedGameSelection(OptionSet):
    """
    Defines which supported APWorlds to select from.

    All games are listed. Remove the ones you don't own or want to play.
    """

    display_name = "Archipelago Multiworld Randomizer Supported Game Selection"

    valid_keys = [
        "A Hat in Time",
        "A Short Hike",
        "Adventure",
        "Aquaria",
        "Blasphemous",
        "Bomb Rush Cyberfunk",
        "Bumper Stickers",
        "Castlevania",
        "Celeste 64",
        "ChecksFinder",
        "Clique",
        "Dark Souls III",
        "DLC Quest",
        "Donkey Kong Country 3: Dixie Kong's Double Trouble!",
        "DOOM 1993",
        "DOOM II",
        "Factorio",
        "Final Fantasy",
        "Final Fantasy: Mystic Quest",
        "Heretic",
        "Hollow Knight",
        "Hylics 2",
        "KINGDOM HEARTS FINAL MIX",
        "KINGDOM HEARTS II FINAL MIX",
        "Kirby's Dream Land 3",
        "Landstalker - The Treasures of King Nole",
        "Lingo",
        "Lufia II: Rise of the Sinistrals",
        "Mario & Luigi: Superstar Saga",
        "Mega Man 2",
        "Mega Man Battle Network 3 Blue",
        "Meritous",
        "Minecraft",
        "Muse Dash",
        "Noita",
        "Old School Runescape",
        "Overcooked! 2",
        "Pokémon Emerald",
        "Pokémon Red and Blue",
        "Raft",
        "Risk of Rain 2",
        "Rogue Legacy",
        "Secret of Evermore",
        "Shivers",
        "Slay the Spire",
        "SMZ3",
        "Sonic Adventure 2: Battle",
        "StarCraft II",
        "Stardew Valley",
        "Subnautica",
        "Super Mario 64",
        "Super Mario World",
        "Super Mario World 2: Yoshi's Island",
        "Super Metroid",
        "Terraria",
        "The Legend of Zelda",
        "The Legend of Zelda: A Link to the Past",
        "The Legend of Zelda: Link's Awakening DX",
        "The Legend of Zelda: Ocarina of Time",
        "The Messenger",
        "The Witness",
        "Timespinner",
        "TUNIC",
        "Undertale",
        "VVVVVV",
        "Wargroove",
        "Yacht Dice",
        "Yu-Gi-Oh! Ultimate Masters: WCT 2006",
        "Zillion",
        "Zork: Grand Inquisitor",
    ]

    default = valid_keys


class ArchipelagoMultiworldRandomizerUnsupportedGameSelection(OptionSet):
    """
    Defines which unsupported APWorlds to select from.

    All games are listed. Remove the ones you don't own or want to play.
    """

    display_name = "Archipelago Multiworld Randomizer Unsupported Game Selection"

    valid_keys = [
        "A Robot Named Fight!",
        "ActRaiser",
        "Against the Storm",
        "Air Delivery",
        "An Untitled Story",
        "ANIMAL WELL",
        "Anodyne",
        "Another Crab's Treasure",
        "Ape Escape",
        "Archipela-Go!",
        "Astalon: Tears of the Earth",
        "Banjo-Tooie",
        "Bloons TD 6",
        "Brotato",
        "Castlevania: Symphony of the Night",
        "Castlevania: Legacy of Darkness",
        "Castlevania: Circle of the Moon",
        "Cavern of Dreams",
        "Cave Story",
        "Celeste",
        "Chained Echoes",
        "ChecksMate",
        "Chrono Trigger",
        "CrossCode",
        "Crystalis",
        "Cuphead",
        "Dark Souls: Remastered",
        "Digimon World",
        "Dome Keeper",
        "Don't Starve Together",
        "Donkey Kong Country 2: Diddy's Kong Quest",
        "Diddy Kong Racing",
        "Duke Nukem 3D: Atomic Edition",
        "EarthBound",
        "Ender Lilies: Quietus of the Knights",
        "Enter the Gungeon",
        "Faxanadu",
        "Final Fantasy IV",
        "Final Fantasy V",
        "Final Fantasy VI",
        "Final Fantasy XII: Open World",
        "Final Fantasy XII: Trial Mode",
        "Final Fantasy Tactics Advance",
        "Final Fantasy Tactics A2: Grimoire of the Rift",
        "Fire Emblem: The Sacred Stones",
        "FNaF World",
        "Freddy Fazbear's Pizzeria Simulator",
        "Gauntlet Legends",
        "Golden Sun: The Lost Age",
        "Grim Dawn",
        "Guild Wars 2",
        "Hades",
        "Hammerwatch",
        "Hatsune Miku: Project Diva Mega Mix+",
        "Here Comes Niko!",
        "Inscryption",
        "Into the Breach",
        "Ittle Dew 2+",
        "Jak and Daxter: The Precursor Legacy",
        "Keep Talking and Nobody Explodes",
        "KINGDOM HEARTS Birth by Sleep FINAL MIX",
        "KINGDOM HEARTS 358/2 Days",
        "KINGDOM HEARTS Chain of Memories",
        "KINGDOM HEARTS Re:Chain of Memories",
        "Kirby 64: The Crystal Shards",
        "League of Legends",
        "Lethal Company",
        "Lil Gator Game",
        "Little Witch Nobeta",
        "Loonyland: Halloween Hill",
        "Lunacid",
        "Mario is Missing!",
        "Mario Kart 64",
        "Mega Man 3",
        "Mega Man X",
        "Mega Man X2",
        "Mega Man X3",
        "MetroCUBEvania",
        "Metroid Prime",
        "Metroid: Zero Mission",
        "Mindustry",
        "Minecraft Dig",
        "Minishoot' Adventures",
        "Minit",
        "Monster Sanctuary",
        "OpenRCT2",
        "Ori and the Blind Forest",
        "Osu!",
        "Outer Wilds",
        "Paper Mario",
        "Pokémon Crystal",
        "Pokémon FireRed and LeafGreen",
        "Prodigal",
        "Pseudoregalia",
        "Psychonauts",
        "Rabi-Ribi",
        "Reventure",
        "Rift Wizard",
        "Risk of Rain",
        "Rusted Moss",
        "Satisfactory",
        "Saving Princess",
        "Scooby-Doo! Night of 100 Frights",
        "Sea of Thieves",
        "Sentinels of the Multiverse",
        "Shadow the Hedgehog",
        "Shapez",
        "Sid Meier's Civilization VI",
        "Simon Tatham's Portable Puzzle Collection",
        "Sly Cooper and the Thievius Raccoonus",
        "Sonic Adventure DX",
        "Soul Blazer",
        "Spelunker",
        "Spelunky 2",
        "SpongeBob SquarePants: Battle For Bikini Bottom",
        "Stacklands",
        "Star Wars: Episode I - Racer",
        "Subversion",
        "Super Junkoid",
        "Super Mario Land 2: 6 Golden Coins",
        "Super Metroid Map Rando",
        "TEVI",
        "The Binding of Isaac: Repentance",
        "The Legend of Zelda: A Link Between Worlds",
        "The Legend of Zelda: Majora's Mask",
        "The Legend of Zelda: Oracle of Ages",
        "The Legend of Zelda: Oracle of Seasons",
        "The Legend of Zelda: The Wind Waker",
        "Toejam & Earl",
        "Turnip Boy Commits Tax Evasion",
        "Tyrian",
        "Vacation Simulator",
        "Void Stranger",
        "Wargroove 2",
        "Wario Land: Super Mario Land 3",
        "Wario Land 4",
        "Watery Words",
        "Yooka-Laylee",
        "Yu-Gi-Oh! Dungeon Dice Monsters",
        "Yu-Gi-Oh! Forbidden Memories",
        "XCOM 2: War of the Chosen",
    ]

    default = valid_keys


class ArchipelagoMultiworldRandomizerAdultOnlyOrUnratedGameSelection(OptionSet):
    """
    Defines which adult-only or unrated APWorlds to select from (if adult-only and unrated games are allowed).

    All games are listed. Remove the ones you don't own or want to play.
    """

    display_name = "Archipelago Multiworld Randomizer Adult-Only or Unrated Game Selection"

    valid_keys = [
        "Balatro",
        "FlipWitch - Forbidden Sex Hex",
        "HuniePop",
        "HuniePop 2: Double Date",
        "Kindergarten 2",
        "Resident Evil 2 (Remake)",
        "Resident Evil 3 (Remake)",
        "The Guardian Legend",
        "Touhou Koumakyou: The Embodiment of Scarlet Devil",
        "ULTRAKILL",
    ]

    default = valid_keys


class ArchipelagoMultiworldRandomizerCustomGameSelection(OptionSet):
    """
    Defines which custom APWorlds to select from.

    Use this to add APWorlds that are not in the supported or unsupported lists.
    """

    display_name = "Archipelago Multiworld Randomizer Custom Game Selection"

    default = list()


class ArchipelagoMultiworldRandomizerAllowAPBingoObjectives(Toggle):
    """
    Determines if APBingo objectives should be considered.
    """

    display_name = "Allow APBingo Objectives"


@dataclass
class ArchipelagoMultiworldRandomizerArchipelagoOptions:
    archipelago_multiworld_randomizer_supported_game_selection: ArchipelagoMultiworldRandomizerSupportedGameSelection

    archipelago_multiworld_randomizer_unsupported_game_selection: (
        ArchipelagoMultiworldRandomizerUnsupportedGameSelection
    )

    archipelago_multiworld_randomizer_adult_only_or_unrated_game_selection: (
        ArchipelagoMultiworldRandomizerAdultOnlyOrUnratedGameSelection
    )

    archipelago_multiworld_randomizer_custom_game_selection: ArchipelagoMultiworldRandomizerCustomGameSelection
    archipelago_multiworld_randomizer_allow_apbingo_objectives: ArchipelagoMultiworldRandomizerAllowAPBingoObjectives
