from playsound3 import playsound


async def playSound(path: str):
    if(path.startswith("/")):
        playsound(path)
    else:
        playsound("src/experiments/wordExperiment/res/sounds/" + path)