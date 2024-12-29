from random import Random
from typing import Any, List, Tuple, Type

from .game import Game
from .games import AutoGameRegister


GameObjectiveGeneratorData = List[Tuple[Type[Game], List[str], List[str]]]


class GameObjectiveGeneratorException(Exception):
    pass


class GameObjectiveGenerator:
    games: List[Type[Game]]
    archipelago_options: Any

    def __init__(
        self,
        allowable_games: List[str] = None,
        include_adult_only_or_unrated_games: bool = False,
        include_difficult_objectives: bool = False,
        include_time_consuming_objectives: bool = False,
        archipelago_options: Any = None,
    ) -> None:
        self.archipelago_options = archipelago_options

        self.games = self._filter_games(
            allowable_games,
            include_adult_only_or_unrated_games,
            include_difficult_objectives,
            include_time_consuming_objectives,
        )

        if not len(self.games):
            raise GameObjectiveGeneratorException("No games are left after game / objective filtering")

    def generate_from_plan(
        self,
        plan: List[int] = None,
        random: Random = None,
        include_difficult: bool = False,
        excluded_games_difficult: List[str] = None,
        include_time_consuming: bool = False,
        excluded_games_time_consuming: List[str] = None,
    ) -> GameObjectiveGeneratorData:
        if plan is None or not len(plan):
            return list()

        plan_length: int = len(plan)
        random = random or Random()

        game_selection: List[Type[Game]] = list()

        if plan_length <= len(self.games):
            game_selection = random.sample(self.games, plan_length)
        else:
            for _ in range(plan_length):
                game_selection.append(random.choice(self.games))

        data: GameObjectiveGeneratorData = list()

        i: int
        count: int
        for i, count in enumerate(plan):
            game: Game = game_selection[i](random=random, archipelago_options=self.archipelago_options)

            is_in_difficult_exclusions: bool = game.game_name_with_platforms() in excluded_games_difficult
            include_difficult = include_difficult and not is_in_difficult_exclusions

            # This appears to completely ignore the passed 'include_difficult' value, but in reality, a game that only
            # implements difficult objectives would already be filtered out in the constructor when 'include_difficult'
            # is False, so we are only forcing it on when it's in the excluded list.
            if game.only_has_difficult_objectives and not include_difficult:
                include_difficult = True

            is_in_time_consuming_exclusions: bool = game.game_name_with_platforms() in excluded_games_time_consuming
            include_time_consuming = include_time_consuming and not is_in_time_consuming_exclusions

            # Same as above
            if game.only_has_time_consuming_objectives and not include_time_consuming:
                include_time_consuming = True

            optional_constraints: List[str]
            objectives: List[str]
            optional_constraints, objectives = game.generate_objectives(
                count=count,
                include_difficult=include_difficult,
                include_time_consuming=include_time_consuming,
            )

            data.append((game, optional_constraints, objectives))

        return data

    def _filter_games(
        self,
        allowable_games: List[str],
        include_adult_only_or_unrated_games: bool,
        include_difficult_objectives: bool,
        include_time_consuming_objectives: bool
    ) -> List[Type[Game]]:
        filtered_games: List[Type[Game]] = list()

        game_name: str
        for game_name in allowable_games:
            if game_name not in AutoGameRegister.games and game_name not in AutoGameRegister.metagames:
                continue

            game: Type[Game] = AutoGameRegister.games.get(game_name, AutoGameRegister.metagames.get(game_name))
            game_instance: Game = game(archipelago_options=self.archipelago_options)

            if not include_adult_only_or_unrated_games and game.is_adult_only_or_unrated:
                continue

            if not include_difficult_objectives and game_instance.only_has_difficult_objectives:
                continue

            if not include_time_consuming_objectives and game_instance.only_has_time_consuming_objectives:
                continue

            filtered_games.append(game)

        return filtered_games