import logging

from typing import Any, Dict, List, Optional, Set, Tuple, Union, TextIO

from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from Utils import visualize_regions

from worlds.AutoWorld import WebWorld, World

from .data_funcs import (
    item_names_to_id,
    location_names_to_id,
    item_groups,
    location_groups,
    id_to_goals,
    access_rule_for,
)

from .data.item_data import KeymastersKeepItemData, item_data
from .data.location_data import KeymastersKeepLocationData, location_data
from .data.mapping_data import region_to_trial_locations, region_to_unlock_location_and_item

from .enums import (
    KeymastersKeepItems,
    KeymastersKeepGoals,
    KeymastersKeepLocations,
    KeymastersKeepRegions,
    KeymastersKeepTags,
)

from .options import KeymastersKeepOptions, option_groups


class KeymastersKeepItem(Item):
    game = "Keymaster's Keep"


class KeymastersKeepLocation(Location):
    game = "Keymaster's Keep"


class KeymastersKeepWebWorld(WebWorld):
    theme: str = "stone"

    tutorials: List[Tutorial] = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up the Keymaster's Keep randomizer connected to an Archipelago Multiworld",
            "English",
            "setup_en.md",
            "setup/en",
            ["Serpent.AI"],
        )
    ]

    # Option presets here...
    option_groups = option_groups


class KeymastersKeepWorld(World):
    """
    Embark on a quest through the Keymaster's Keep, a mysterious castle where every door and passage hides a series of
    video game chalenges, and only the right keys can unlock the path forward. Complete challenges, find keys, uncover
    artifacts of resolve, and face the ultimate trial to claim victory.
    """

    options_dataclass = KeymastersKeepOptions
    options: KeymastersKeepOptions

    game = "Keymaster's Keep"

    item_name_to_id = item_names_to_id()
    location_name_to_id = location_names_to_id()

    item_name_groups = item_groups()
    location_name_groups = location_groups()

    required_client_version: Tuple[int, int, int] = (0, 5, 1)

    web = KeymastersKeepWebWorld()

    area_trials: Dict[KeymastersKeepRegions, List[KeymastersKeepLocationData]]
    area_trials_maximum: int
    area_trials_minimum: int
    artifacts_of_resolve_required: int
    artifacts_of_resolve_total: int
    filler_item_names: List[str] = item_groups()["Filler"]
    goal: KeymastersKeepGoals
    keep_areas: int
    keep_data: Any
    lock_combinations: Dict[KeymastersKeepRegions, Optional[List[KeymastersKeepItems]]]
    lock_magic_keys_maximum: int
    lock_magic_keys_minimum: int
    magic_keys_required: int
    magic_keys_total: int
    selected_areas: List[KeymastersKeepRegions]
    selected_magic_keys: List[KeymastersKeepItems]
    unlocked_areas: int
    unused_magic_keys: Set[KeymastersKeepItems]

    def generate_early(self) -> None:
        self.goal = id_to_goals()[self.options.goal.value]

        self.artifacts_of_resolve_required = self.options.artifacts_of_resolve_required.value
        self.artifacts_of_resolve_total = self.options.artifacts_of_resolve_total.value

        if self.artifacts_of_resolve_required > self.artifacts_of_resolve_total:
            self.artifacts_of_resolve_total = self.artifacts_of_resolve_required

            if self.goal == KeymastersKeepGoals.KEYMASTERS_CHALLENGE:
                logging.warning(
                    f"Keymaster's Keep: {self.player_name} has more required artifacts than total artifacts. Using "
                    "required amount for total."
                )

        self.magic_keys_required = self.options.magic_keys_required.value
        self.magic_keys_total = self.options.magic_keys_total.value

        if self.magic_keys_required > self.magic_keys_total:
            self.magic_keys_total = self.magic_keys_required

            if self.goal == KeymastersKeepGoals.MAGIC_KEY_HEIST:
                logging.warning(
                    f"Keymaster's Keep: {self.player_name} has more required magic keys than total magic keys. Using "
                    "required amount for total."
                )

        self.keep_areas = self.options.keep_areas.value

        self.unlocked_areas = self.options.unlocked_areas.value

        self.lock_magic_keys_minimum = self.options.lock_magic_keys_minimum.value
        self.lock_magic_keys_maximum = self.options.lock_magic_keys_maximum.value

        if self.lock_magic_keys_minimum > self.lock_magic_keys_maximum:
            self.lock_magic_keys_maximum = self.lock_magic_keys_minimum

            logging.warning(
                f"Keymaster's Keep: {self.player_name} has a minimum lock magic keys value greater than the maximum. "
                "Using minimum value for maximum."
            )

        self.area_trials_minimum = self.options.area_trials_minimum.value
        self.area_trials_maximum = self.options.area_trials_maximum.value

        if self.area_trials_minimum > self.area_trials_maximum:
            self.area_trials_maximum = self.area_trials_minimum

            logging.warning(
                f"Keymaster's Keep: {self.player_name} has a minimum area trials value greater than the maximum. "
                "Using minimum value for maximum."
            )

        smallest_possible_trial_count: int = self.area_trials_minimum * self.keep_areas

        locations_needed: int = self.magic_keys_total

        if self.goal == KeymastersKeepGoals.KEYMASTERS_CHALLENGE:
            locations_needed += self.artifacts_of_resolve_total

        area_trials_range_modified: bool = False

        if locations_needed > smallest_possible_trial_count:
            area_trials_range_modified = True

            while True:
                self.area_trials_minimum += 1

                if self.area_trials_maximum < self.area_trials_minimum:
                    self.area_trials_maximum = self.area_trials_minimum

                smallest_possible_trial_count = self.area_trials_minimum * self.keep_areas

                if smallest_possible_trial_count >= locations_needed:
                    break

        if area_trials_range_modified:
            logging.warning(
                f"Keymaster's Keep: {self.player_name} has had their area trials range modified to ensure enough "
                "trials are available to generate successfully."
            )

        self._generate_keep()

        # Debugging
        print("Selected Areas:")
        for area in self.selected_areas:
            print(f"  {area.value}")

        print()

        print("Selected Magic Keys:")
        for key in self.selected_magic_keys:
            print(f"  {key.value}")

        print()

        print("Lock Combinations:")
        for area, keys in self.lock_combinations.items():
            if keys is None:
                print(f"  {area.value}: Unlocked")
                continue

            print(f"  {area.value}:")

            for key in keys:
                print(f"    {key.value}")

        print()

        print("Area Trials:")
        for area, trials in self.area_trials.items():
            print(f"  {area.value}:")

            for trial in trials:
                print(f"    {trial.name}")

        print()

        print("Unused Magic Keys:")
        for key in self.unused_magic_keys:
            print(f"  {key.value}")

        print()

    def create_regions(self) -> None:
        #### Menu -> Keymaster's Keep
        region_menu: Region = Region(KeymastersKeepRegions.MENU.value, self.player, self.multiworld)

        region_keymasters_keep: Region = Region(
            KeymastersKeepRegions.KEYMASTERS_KEEP.value, self.player, self.multiworld
        )

        region_menu.connect(region_keymasters_keep)

        self.multiworld.regions.append(region_menu)

        #### Keymaster's Keep
        region_keymasters_keep.connect(region_menu)

        ### Keymaster's Keep -> Keymaster's Keep Areas
        area: KeymastersKeepRegions
        for area in self.selected_areas:
            ## Unlock Location
            location_enum_item: KeymastersKeepLocations
            item_enum_item: KeymastersKeepItems

            location_enum_item, item_enum_item = region_to_unlock_location_and_item[area]
            data: KeymastersKeepLocationData = location_data[location_enum_item]

            unlock_location: KeymastersKeepLocation = KeymastersKeepLocation(
                self.player,
                location_enum_item.value,
                data.archipelago_id,
                region_keymasters_keep,
            )

            access_rule: Optional[str] = access_rule_for(self.lock_combinations[area], self.player)

            if access_rule is not None:
                unlock_location.access_rule = eval(access_rule)

            unlock_location.place_locked_item(self.create_item(item_enum_item.value))

            region_keymasters_keep.locations.append(unlock_location)

            ## Entrance
            region_area: Region = Region(area.value, self.player, self.multiworld)
            region_keymasters_keep.connect(region_area, rule=eval(access_rule_for([item_enum_item], self.player)))

            ## Keymaster's Keep Area
            region_area.connect(region_keymasters_keep)

            # Assign Trial Locations
            trial: KeymastersKeepLocationData
            for trial in self.area_trials[area]:
                trial_location: KeymastersKeepLocation = KeymastersKeepLocation(
                    self.player,
                    trial.name,
                    trial.archipelago_id,
                    region_area,
                )

                region_area.locations.append(trial_location)

            self.multiworld.regions.append(region_area)

        ### Goal
        region_endgame: Region = Region(KeymastersKeepRegions.ENDGAME.value, self.player, self.multiworld)

        location_victory: KeymastersKeepLocation = KeymastersKeepLocation(
            self.player,
            "Victory",
            None,
            region_endgame,
        )

        location_victory.place_locked_item(
            KeymastersKeepItem(
                "Victory",
                ItemClassification.progression,
                None,
                self.player,
            )
        )

        region_endgame.locations.append(location_victory)

        if self.goal == KeymastersKeepGoals.KEYMASTERS_CHALLENGE:
            # Unlock Location
            unlock_location: KeymastersKeepLocation = KeymastersKeepLocation(
                self.player,
                KeymastersKeepLocations.THE_KEYMASTERS_CHALLENGE_CHAMBER_UNLOCK.value,
                location_data[KeymastersKeepLocations.THE_KEYMASTERS_CHALLENGE_CHAMBER_UNLOCK].archipelago_id,
                region_keymasters_keep,
            )

            unlock_location.place_locked_item(
                self.create_item(KeymastersKeepItems.UNLOCK_THE_KEYMASTERS_CHALLENGE_CHAMBER.value)
            )

            unlock_location.access_rule = lambda state: state.has(
                KeymastersKeepItems.ARTIFACT_OF_RESOLVE.value,
                self.player,
                count=self.artifacts_of_resolve_required
            )

            region_keymasters_keep.locations.append(unlock_location)

            # Challenge Chamber
            region_challenge_chamber: Region = Region(
                KeymastersKeepRegions.THE_KEYMASTERS_CHALLENGE_CHAMBER.value, self.player, self.multiworld
            )

            region_keymasters_keep.connect(
                region_challenge_chamber,
                rule=eval(access_rule_for([KeymastersKeepItems.UNLOCK_THE_KEYMASTERS_CHALLENGE_CHAMBER], self.player))
            )

            region_challenge_chamber.connect(region_keymasters_keep)

            location_challenge: KeymastersKeepLocation = KeymastersKeepLocation(
                self.player,
                KeymastersKeepLocations.THE_KEYMASTERS_CHALLENGE_CHAMBER_VICTORY.value,
                location_data[KeymastersKeepLocations.THE_KEYMASTERS_CHALLENGE_CHAMBER_VICTORY].archipelago_id,
                region_challenge_chamber,
            )

            location_challenge.place_locked_item(
                self.create_item(KeymastersKeepItems.KEYMASTERS_KEEP_CHALLENGE_COMPLETE.value)
            )

            region_challenge_chamber.locations.append(location_challenge)

            # Endgame
            region_challenge_chamber.connect(
                region_endgame,
                rule=eval(access_rule_for([KeymastersKeepItems.KEYMASTERS_KEEP_CHALLENGE_COMPLETE], self.player))
            )

            region_endgame.connect(region_challenge_chamber)

            self.multiworld.regions.append(region_challenge_chamber)
        elif self.goal == KeymastersKeepGoals.MAGIC_KEY_HEIST:
            # Endgame
            region_keymasters_keep.connect(
                region_endgame,
                rule=eval(access_rule_for(self.selected_magic_keys, self.player)),
            )

            region_endgame.connect(region_keymasters_keep)

        self.multiworld.regions.append(region_keymasters_keep)
        self.multiworld.regions.append(region_endgame)

        visualize_regions(self.multiworld.get_region("Menu", self.player), "kmk.puml")

    def create_items(self) -> None:
        item_pool: List[KeymastersKeepItem] = list()

        # Magic Keys
        for magic_key in self.selected_magic_keys:
            item: KeymastersKeepItem = self.create_item(magic_key.value)

            if magic_key in self.unused_magic_keys and self.goal == KeymastersKeepGoals.KEYMASTERS_CHALLENGE:
                item.classification = ItemClassification.filler

            item_pool.append(item)

        # Artifacts of Resolve
        if self.goal == KeymastersKeepGoals.KEYMASTERS_CHALLENGE:
            i: int
            for i in range(self.artifacts_of_resolve_total):
                item: KeymastersKeepItem = self.create_item(KeymastersKeepItems.ARTIFACT_OF_RESOLVE.value)

                if i >= self.artifacts_of_resolve_required:
                    item.classification = ItemClassification.filler

                item_pool.append(item)

        # Filler
        total_location_count: int = len(self.multiworld.get_unfilled_locations(self.player))
        to_fill_location_count: int = total_location_count - len(item_pool)

        item_pool += [self.create_filler() for _ in range(to_fill_location_count)]

        self.multiworld.itempool += item_pool

    def create_item(self, name: str) -> KeymastersKeepItem:
        data: KeymastersKeepItemData = item_data[KeymastersKeepItems(name)]

        return KeymastersKeepItem(
            name,
            data.classification,
            data.archipelago_id,
            self.player,
        )

    def generate_basic(self) -> None:
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def write_spoiler_header(self, spoiler_handle: TextIO) -> None:
        # Lock Combinations
        spoiler_handle.write("\nRequired Keys:")

        area: KeymastersKeepRegions
        keys: Optional[List[KeymastersKeepItems]]
        for area, keys in self.lock_combinations.items():
            if keys is None:
                spoiler_handle.write(f"\n    {area.value}: Unlocked")
                continue

            spoiler_handle.write(f"\n    {area.value}: {', '.join(key.value for key in keys)}")

        # Write Game Challenges to Spoiler Log
        # ...

    def get_filler_item_name(self) -> str:
        return self.random.choice(self.filler_item_names)

    # Extend Hint Data With Game Challenges
    # Write Slot Data

    def _generate_keep(self) -> None:
        # Select Areas
        potential_areas: List[KeymastersKeepRegions] = list()

        excluded_areas: Tuple[KeymastersKeepRegions, ...] = (
            KeymastersKeepRegions.ENDGAME,
            KeymastersKeepRegions.THE_KEYMASTERS_CHALLENGE_CHAMBER,
            KeymastersKeepRegions.KEYMASTERS_KEEP,
            KeymastersKeepRegions.MENU,
        )

        area: KeymastersKeepRegions
        for area in KeymastersKeepRegions:
            if area not in excluded_areas:
                potential_areas.append(area)

        self.selected_areas = self.random.sample(potential_areas, self.keep_areas)

        # Select Magic Keys
        potential_magic_keys: List[KeymastersKeepItemData] = list()

        item: KeymastersKeepItems
        data: KeymastersKeepItemData
        for item, data in item_data.items():
            if KeymastersKeepTags.KEYS in data.tags:
                potential_magic_keys.append(item)

        self.selected_magic_keys = self.random.sample(potential_magic_keys, self.magic_keys_total)

        # Generate Lock Combinations
        self.lock_combinations = dict()
        used_keys: Set[KeymastersKeepItems] = set()

        i: int
        area: KeymastersKeepRegions
        for i, area in enumerate(self.selected_areas):
            if i < self.unlocked_areas:
                self.lock_combinations[area] = None
                continue

            key_count: int = self.random.randint(self.lock_magic_keys_minimum, self.lock_magic_keys_maximum)

            # Conditionally force single key locks to prevent overly restrictive starts and generation failures
            if i < self.unlocked_areas + (5 - self.unlocked_areas):
                key_count = 1

            keys_to_lock: List[KeymastersKeepItems] = self.random.sample(self.selected_magic_keys, key_count)

            key: KeymastersKeepItems
            for key in keys_to_lock:
                used_keys.add(key)

            self.lock_combinations[area] = keys_to_lock

        self.unused_magic_keys = set(self.selected_magic_keys) - used_keys

        # Assign Trials to Areas
        self.area_trials = dict()

        area: KeymastersKeepRegions
        for area in self.selected_areas:
            possible_trials: List[KeymastersKeepLocationData] = location_data[region_to_trial_locations[area]]
            trial_count: int = self.random.randint(self.area_trials_minimum, self.area_trials_maximum)

            self.area_trials[area] = self.random.sample(possible_trials, trial_count)
