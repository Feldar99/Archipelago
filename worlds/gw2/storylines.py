import enum
from typing import Optional


class StorylineEnum(enum.Enum):
    CORE = enum.auto(value=0)
    SEASON_1 = enum.auto()
    SEASON_2 = enum.auto()
    HEART_OF_THORNS = enum.auto()
    SEASON_3 = enum.auto()
    PATH_OF_FIRE = enum.auto()
    SEASON_4 = enum.auto()
    ICEBROOD_SAGA = enum.auto()
    END_OF_DRAGONS = enum.auto()
    SECRETS_OF_THE_OBSCURE = enum.auto()


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
    return None
