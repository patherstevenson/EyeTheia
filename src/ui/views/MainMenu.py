import flet as ft

def onCalibration():
    print("Calibration")

async def onWordExperiment(page: ft.Page):
    await page.push_route("/WordExperiment")
    print("j'ai push")


def onLoadCSV():
    print("Load CSV")


def onSettings():
    print("Settings")

def MainMenuView(page: ft.Page):
    buttons = [
        ft.Button(
            content="Calibration",
            on_click=onCalibration
        ),
        ft.Button(
            content="WordTest",
            on_click=lambda _: page.run_task(onWordExperiment, page)
        ),
        ft.Button(
            content="LoadCSV",
            on_click=onLoadCSV
        ),
        ft.Button(
            content="Settings",
            on_click=onSettings
        ),
    ]
    column = ft.Column(
        controls=buttons,
        alignment=ft.Alignment.CENTER,
        spacing=20
    )

    return ft.View(
        controls=column,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
