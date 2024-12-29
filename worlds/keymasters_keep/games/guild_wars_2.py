from __future__ import annotations

from typing import List, Set

from dataclasses import dataclass

from Options import OptionSet

from ..game import Game
from ..game_objective_template import GameObjectiveTemplate

from ..enums import KeymastersKeepGamePlatforms


@dataclass
class GuildWars2ArchipelagoOptions:
    guild_wars_2_storylines_owned: GuildWars2StorylinesOwned
    guild_wars_2_game_modes: GuildWars2GameModes


class GuildWars2Game(Game):
    name = "Guild Wars 2"
    platform = KeymastersKeepGamePlatforms.PC

    platforms_other = [
    ]

    is_adult_only_or_unrated = False

    options_cls = GuildWars2ArchipelagoOptions

    def optional_game_constraint_templates(self) -> List[GameObjectiveTemplate]:
        return list()

    def game_objective_templates(self) -> List[GameObjectiveTemplate]:
        objective_list = [
            GameObjectiveTemplate(
                label="Craft a Legendary",
                data={},
                is_time_consuming=True,
                is_difficult=False,
                weight=1,
            ),
            GameObjectiveTemplate(
                label="Gain AP_AMOUNT AP",
                data={
                    "AP_AMOUNT": (self.ap_amounts, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=3,
            ),
            GameObjectiveTemplate(
                label="Do DAILY_CATEGORY Dailies",
                data={
                    "DAILY_CATEGORY": (self.daily_categories, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=len(self.daily_categories()),
            ),
            GameObjectiveTemplate(
                label="Do a WEEKLY_CATEGORY Weekly",
                data={
                    "WEEKLY_CATEGORY": (self.weekly_categories, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=len(self.weekly_categories()),
            ),
            GameObjectiveTemplate(
                label="Do a Wizard's Vault Special",
                data={},
                is_time_consuming=True,
                is_difficult=False,
                weight=2,
            ),
        ]

        if "Open World" in self.game_modes_played:
            objective_list.append(GameObjectiveTemplate(
                label="Participate in META_EVENT event",
                data={
                    "META_EVENT": (self.meta_events, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=5,
            ))

        if "Story" in self.game_modes_played:
            objective_list.append(GameObjectiveTemplate(
                label="Complete a story mission from STORYLINE",
                data={
                    "STORYLINE": (self.storylines, 1),
                },
                is_time_consuming=False,
                is_difficult=False,
                weight=3,
            ))

        if "WvW" in self.game_modes_played:
            objective_list += [
                GameObjectiveTemplate(
                    label="Capture WVW_OBJECTIVE in WvW",
                    data={
                        "WVW_OBJECTIVE": (self.wvw_objectives, 1),
                    },
                    is_time_consuming=False,
                    is_difficult=False,
                    weight=5,
                ),
                GameObjectiveTemplate(
                    label="Earn a large skirmish chest",
                    data={},
                    is_time_consuming=True,
                    is_difficult=False,
                    weight=2,
                ),
            ]

        if "PvP" in self.game_modes_played:
            objective_list.append(GameObjectiveTemplate(
                label="Play PVP_MATCH_COUNT PvP Matches",
                data={
                    "PVP_MATCH_COUNT": (self.pvp_match_counts, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=3,
            ))

        if "Fractals" in self.game_modes_played:
            objective_list.append(GameObjectiveTemplate(
                label="Run Tier TIER FRACTAL Fractal",
                data={
                    "TIER": (self.fractal_tiers, 1),
                    "FRACTAL": (self.fractals, 1),
                },
                is_time_consuming=False,
                is_difficult=True,
                weight=3,
            ))

        if "Dungeons" in self.game_modes_played:
            objective_list.append(GameObjectiveTemplate(
                label="Run DUNGEON",
                data={
                    "DUNGEON": (self.dungeons, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=3,
            ))

        if "Raids" in self.game_modes_played and len(self.raids()) > 0:
            objective_list.append(GameObjectiveTemplate(
                label="Run RAID",
                data={
                    "RAID": (self.raids, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=2,
            ))

        if "Strikes" in self.game_modes_played:
            objective_list.append(GameObjectiveTemplate(
                label="Run STRIKE",
                data={
                    "STRIKE": (self.strikes, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=3,
            ))

        if "Convergences" in self.game_modes_played:
            objective_list.append(GameObjectiveTemplate(
                label="Participate in CONVERGENCE",
                data={
                    "CONVERGENCE": (self.convergences, 1),
                },
                is_time_consuming=True,
                is_difficult=False,
                weight=3,
            ))

        return objective_list

    @property
    def storylines_owned(self) -> Set[str]:
        return self.archipelago_options.guild_wars_2_storylines_owned.value

    def storylines(self) -> List[str]:
        return sorted(self.storylines_owned)

    @property
    def game_modes_played(self) -> Set[str]:
        return self.archipelago_options.guild_wars_2_game_modes.value

    def daily_categories(self) -> List[str]:
        categories = ["Wizard's Vault"]
        if "Open World" in self.game_modes_played:
            categories += [
                "Blood in the Water",
                "Daily Portal Closer",
            ]
        if "PvP" in self.game_modes_played:
            categories += ["League Participator"]
        if "Strikes" in self.game_modes_played:
            categories += ["Strikes"]
        if "Fractals" in self.game_modes_played:
            categories += ["Fractals"]
        if "End of Dragons" in self.storylines_owned:
            categories += ["End of Dragons"]
        if "Icebrood Saga" in self.storylines_owned:
            categories += ["Icebrood Saga"]
        if "Season 4" in self.storylines_owned:
            categories += ["Living World Season 4"]
        if "Season 3" in self.storylines_owned:
            categories += ["Living World Season 3"]
        if "Janthir Wilds" in self.storylines_owned:
            categories += ["Buzzy Treetops"]

        return categories

    def weekly_categories(self) -> List[str]:
        categories = ["Wizard's Vault"]
        if "WvW" in self.game_modes_played:
            categories += ["WvW"]

        if "Secrets of the Obscure" in self.storylines_owned:
            categories += ["Krytpis Rift Hunting"]

        if "Janthir Wilds" in self.storylines_owned:
            categories += ["Janthir Rift Hunting"]

        return categories

    def meta_events(self) -> List[str]:
        events = [
            "Svanir Shaman Chief",
            "Fire Elemental",
            "Shadow Behemoth",
            "Great Jungle Wurm",
            "Modniir Ulgoth",
            "Admiral Taidha Covington",
            "The Shatterer",
            "Megadestroyer",
            "Inquest Golem Mark II",
            "Claw of Jormag",
            "Triple Trouble",
            "Tequatl the Sunless"
            "Karka Queen",
            "Ley-Line Anomaly",
            "Scarlet's Invastion",
            "Awakened Invasion",
        ]

        if "Season 2" in self.storylines_owned:
            events += ["RIBA"]

        if "Heart of Thorns" in self.storylines_owned:
            events += [
                "Verdant Brink Night Bosses",
                "Octovine",
                "Chak Gerent",
                "Dragon's Stand",
            ]

        if "Path of Fire" in self.storylines_owned:
            events += [
                "Choya Pinata",
                "Buried Treasure",
                "Doppelganger",
                "Junundu Rising",
                "Maws of Torment",
                "Forged with Fire",
                "Serpent's Ire",
            ]

        if "Season 4" in self.storylines_owned:
            events += [
                "Palawadan",
                "Death-Branded Shatterer",
                "Thunderhead Keep",
                "The Oil Floes"
            ]

        if "Icebrood Saga" in self.storylines_owned:
            events += [
                "Effigy",
                "Doomlore Shrine",
                "Ooze Pits",
                "Metal Concert",
                "Jora's Keep",
                "Drakkar",
                "Drizzlewood Coast",
            ]

        if "End of Dragons" in self.storylines_owned:
            events += [
                "Aetherblade Assault",
                "Kaineng Blackout",
                "Gang War",
                "Aspenwood",
                "Jade Maw",
                "The Battle for the Jade Sea",
            ]

        if "Secrets of the Obscure" in self.storylines_owned:
            events += [
                "Unlocking the Wizard's Tower",
                "Defense of Amnytas",
                "The Road to Heitor",
                "The Fangs That Gnash",
                "Into the Spider's Lair",
            ]

        if "Janthir Wilds" in self.storylines_owned:
            events += [
                "Bog Queen",
                "Of Mists and Monsters",
            ]
        return events

    def wvw_objectives(self) -> List[str]:
        return [
            "Ruin",
            "Sentry Point",
            "Shrine",
            "Supply Camp",
            "Tower",
            "Keep",
            "Stonemist Castle"
        ]

    def pvp_match_counts(self) -> List[int]:
        return list(range(1, 4))

    def fractal_tiers(self) -> List[int]:
        return [1, 2, 3, 4]

    def fractals(self) -> List[str]:
        return [
            "Aetherblade",
            "Aquatic Ruins",
            "Captain Mai Trin Boss",
            "Chaos",
            "Cliffside",
            "Deepstone",
            "Lonely Tower",
            "Molten Boss",
            "Molten Furnace",
            "Nightmare",
            "Shattered Observatory",
            "Silent Surf",
            "Siren's Reef",
            "Snowblind",
            "Sunqua Peak",
            "Solid Ocean",
            "Swampland",
            "Thaumanova Reactor"
            "Twilight Oasis"
            "Uncategorized",
            "Underground Facility",
            "Urban Battleground",
            "Volcanic",
        ]

    def dungeons(self) -> List[str]:
        dungeons = [
            "Ascalonian Catacombs",
            "Caudecus's Manor",
            "Twilight Arbor",
            "Sorrow's Embrace",
            "Citadel of Flame",
            "Honor of the Waves",
            "Crucible of Eternity",
        ]
        dungeon_paths = []
        for dungeon in dungeons:
            dungeon_paths += [f"{dungeon} - Story Mode"]

        dungeons += ["The Ruined City of Arah"]

        for dungeon in dungeons:
            for path in [1, 2, 3]:
                dungeon_paths += [f"{dungeon} - Explorable Path {path}"]

        dungeon_paths += ["The Ruined City of Arah - Explorable Path 4"]

        return dungeon_paths

    def raids(self) -> List[str]:
        raids = []
        if "Heart of Thorns" in self.storylines_owned:
            raids += [
                "Spirit Vale",
                "Salvation Pass",
                "Stronghold of the Faithful",
                "Bastion of the Penitent"
            ]

        if "Path of Fire" in self.storylines_owned:
            raids += [
                "Hall of Chains",
                "Mythwright Gambit",
                "The Key of Ahdashim"
            ]

        if "Janthir Wilds" in self.storylines_owned:
            raids += ["Mount Balrior"]

        return raids

    def strikes(self) -> List[str]:
        strikes = ["Old Lion's Court"]
        if "Icebrood Saga" in self.storylines_owned:
            strikes += [
                "Shiverpeaks Pass",
                "Voice of the Fallen and Claw of the Fallen",
                "Fraenir of Jormag",
                "Boneskinner",
                "Whisper of Jormag",
                "Forging Steel",
                "Cold War",
            ]

        if "End of Dragons" in self.storylines_owned:
            strikes += [
                "Aetherblade Hideout",
                "Xunlai Jade Junkyard",
                "Kaineng Overlook",
                "Harvest Temple",
            ]

        if "Secrets of the Obscure" in self.storylines_owned:
            strikes += [
                "Cosmic Observatory",
                "Temple of Febe",
            ]

        return strikes

    def convergences(self) -> List[str]:
        convergences = [
            "Tower of Nightmares",
            "Twisted Marionette",
            "Battle for Lion's Arch"
        ]

        if "Icebrood Saga" in self.storylines_owned:
            convergences.append("Dragonstorm")
        if "Secrets of the Obscure" in self.storylines_owned:
            convergences.append("Kryptis Convergence")
        if "Janthir Wilds" in self.storylines_owned:
            convergences.append("Titan Convergence")
        return convergences

    def ap_amounts(self) -> List[int]:
        return [1, 3, 5]


# Archipelago Options
class GuildWars2StorylinesOwned(OptionSet):
    """
    Indicates which Guild Wars 2 expansions and living world seasons the player owns.
    """

    display_name = "Guild Wars 2 Storylines Owned"
    valid_keys = [
        "Core",
        "Season 1",
        "Season 2",
        "Heart of Thorns",
        "Season 3",
        "Path of Fire",
        "Season 4",
        "Icebrood Saga",
        "End of Dragons",
        "Secrets of the Obscure",
        "Janthir Wilds",
    ]

    default = valid_keys


class GuildWars2GameModes(OptionSet):
    """
    Indicates which Guild Wars 2 game modes the player plays.
    """

    display_name = "Guild Wars 2 Game Modes"
    valid_keys = [
        "Open World",
        "Story",
        "PvP",
        "WvW",
        "Dungeons",
        "Fractals",
        "Raids",
        "Strikes",
        "Convergences",  #includes things like The Twisted Marrionette, Battle for Lion's Arch, and Dragonstorm
    ]

    default = valid_keys
