from experiments.WordGroup import WordGroup
from ui.views.MainMenu import MainMenuView
from ui.views.WordExperimentFlet import WordExperimentView
import flet as ft
from GazeManager import GazeManager


async def main(page: ft.Page):
    page.title = "WordTest"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    gaze_manager = GazeManager()

    word_groups = [
        WordGroup(
            ["trait", "rond", "poule", "boule"],
            "rond",
            "pronunciation_fr_poule.mp3"),
        WordGroup(
            ["bas", "pas", "tarte", "permis"],
            "bas",
            "pronunciation_fr_bas.mp3"),
    ]

    page.window.always_on_top = True

    async def change_word_groups(new_word_groups):
        word_groups.clear()
        word_groups.extend(new_word_groups)
        print("ça a été changé")

    page.views.append(MainMenuView(page, gaze_manager, change_word_groups))


    async def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        match e.route:
            case "/":
                page.views.append(MainMenuView(page, gaze_manager, change_word_groups))

            case "/WordExperiment":
                page.views.append(WordExperimentView(page, gaze_manager, word_groups))
                print(len(word_groups))


    page.on_route_change = route_change

    await page.push_route("/")
