import flet as ft
from GazeManager import GazeManager
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppSettings import WordExperimentSettings
from ui.AppState import AppState
from ui.views.MainMenuFlet import MainMenuView
from ui.views.ResultsScreenFlet import ResultScreenView
from ui.views.WordExperimentFlet import WordExperimentView


async def main(page: ft.Page):
    page.title = "WordTest"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    state = AppState(
        gaze_manager=GazeManager(),
        settings=WordExperimentSettings(),
        word_groups=[
            WordGroup(
                ["trait", "rond", "poule", "boule"],
                "rond",
                "pronunciation_fr_poule.mp3"),
            WordGroup(
                ["bas", "pas", "tarte", "permis"],
                "bas",
                "pronunciation_fr_bas.mp3"),
        ],
    )

    page.window.always_on_top = True

    async def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        match e.route:
            case "/":
                page.views.append(MainMenuView(page, state))

            case "/WordExperiment":
                page.views.append(WordExperimentView(page, state))
            case "/Results":
                page.views.append(ResultScreenView(page, state))

        page.update()

    page.on_route_change = route_change

    page.views.append(MainMenuView(page, state))

    await page.push_route("/")
