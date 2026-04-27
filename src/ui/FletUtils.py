from playsound3 import playsound


async def playSound(path: str):
    if(path.startswith("/")):
        playSound(path)
    else:
        playsound("src/experiments/wordExperiment/res/sounds/" + path)