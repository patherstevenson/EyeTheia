from ui.views.MainMenu import MainMenuView
import flet as ft


async def main(page: ft.Page):
    page.title = "WordTest"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    page.window.always_on_top = True

    tf = ft.TextField(label="a")

    page.views.append(MainMenuView())



