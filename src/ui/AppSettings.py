from dataclasses import dataclass


@dataclass
class WordExperimentSettings:
    max_time_to_choose: int = 5
    time_to_wait_between: float = 2.5
    buttons_size: float = 1.0
