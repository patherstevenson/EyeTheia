import flet as ft
from GazeManager import GazeManager
from experiments.wordExperiment.WordGroup import WordGroup
from flet import controls
from ui.AppSettings import WordExperimentSettings
from ui.AppState import AppState
from ui.views.MainMenuFlet import MainMenuView
from ui.views.ResultsScreenFlet import ResultScreenView
from ui.views.WordExperimentFlet import WordExperimentView
from ui.views.CanvaTestFlet import CanvaTestView


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
            case "/CanvaTest":
                page.views.append(CanvaTestView(page, state))
            case "/Personalize":
                page.views.append(ft.View(controls=ft.Column(controls=[
                    ft.Text("WIP"), ft.Button(content="Go Back",
                                              on_click=lambda _: page.run_task(page.push_route, "/"))], ),
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER))

        page.update()

    page.on_route_change = route_change

    page.views.append(MainMenuView(page, state))

    await page.push_route("/")
