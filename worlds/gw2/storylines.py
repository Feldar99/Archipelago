import enum
from typing import Optional

from .types import StorylineEnum


def storyline_from_str(text) -> Optional[StorylineEnum]:
    text = text.lower()
    if text in ("core", "core tyria"):
        return StorylineEnum.CORE
    if text in ("season 1", "season1", "s1", "living world season 1"):
        return StorylineEnum.SEASON_1
    if text in ("season 2", "season2", "s2", "living world season 2"):
        return StorylineEnum.SEASON_2
    if text in ("heart of thorns", "heartofthorns", "hot"):
        return StorylineEnum.HEART_OF_THORNS
    if text in ("season 3", "season3", "s3", "living world season 3"):
        return StorylineEnum.SEASON_3
    if text in ("path of fire", "pathoffire", "pof"):
        return StorylineEnum.PATH_OF_FIRE
    if text in ("season 4", "season4", "s4", "living world season 4"):
        return StorylineEnum.SEASON_4
    if text in ("icebrood saga", "icebroodsaga", "ibs", "the icebrood saga"):
        return StorylineEnum.ICEBROOD_SAGA
    if text in ("end of dragons", "endofdragons", "eod"):
        return StorylineEnum.END_OF_DRAGONS
    if text in ("secrets of the obscure", "secretsoftheobscure", "soto"):
        return StorylineEnum.SECRETS_OF_THE_OBSCURE
    if text in ("janthir wilds", "janthirwilds", "janthir", "jw"):
        return StorylineEnum.JANTHIR_WILDS
    if text in ("visions of eternity", "visionsofeternity", "voe"):
        return StorylineEnum.VISIONS_OF_ETERNITY
    return None


def get_owned_storylines(storyline) -> list[StorylineEnum]:
    storylines = [storyline]

    if storyline is not StorylineEnum.CORE:
        storylines.append(StorylineEnum.CORE)
    if storyline.value > StorylineEnum.SEASON_1.value:
        storylines.append(StorylineEnum.SEASON_1)
    if storyline.value > StorylineEnum.SEASON_2.value:
        storylines.append(StorylineEnum.SEASON_2)
    if storyline is StorylineEnum.SEASON_3:
        storylines.append(StorylineEnum.HEART_OF_THORNS)
    if storyline is StorylineEnum.SEASON_4 or storyline is StorylineEnum.ICEBROOD_SAGA:
        storylines.append(StorylineEnum.PATH_OF_FIRE)

    return storylines
