from ui.views.MainMenu import MainMenuView
from ui.views.WordExperimentFlet import WordExperimentView
import flet as ft
from GazeManager import GazeManager


async def main(page: ft.Page):
    page.title = "WordTest"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    gaze_manager = GazeManager()

    page.window.always_on_top = True

    page.views.append(MainMenuView(page, gaze_manager))

    async def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        match e.route:
            case "/":
                page.views.append(MainMenuView(page, gaze_manager))

            case "/WordExperiment":
                page.views.append(WordExperimentView(gaze_manager))

    page.on_route_change = route_change

    await page.push_route("/")
