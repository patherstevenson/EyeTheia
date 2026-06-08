from dataclasses import dataclass
from enum import Enum


@dataclass
class WordExperimentSettings:
    """Class representing settings for word experiment"""
    max_time_to_choose: int = 15
    time_to_wait_between: float = 0.5
    buttons_size: float = 0.5
    gaze_per_second: int = 5
    sound_interval: int = 5
    sound_repeat: int = 2


class AppSettingsEnum(Enum):
    MAX_TIME_TO_CHOOSE = "max_time_to_choose"
    TIME_TO_WAIT_BETWEEN = "time_to_wait_between"
    BUTTONS_SIZE = "buttons_size"
    GAZE_PER_SECOND = "gaze_per_second"
    SOUND_INTERVAL = "sound_interval"
    SOUND_REPEAT = "sound_repeat"