import flet as ft
from flet import controls
from pandas.core.interchange import column


def onCalibration():
    print("Calibration")


def onWordTest():
    print("WordTest")


def onLoadCSV():
    print("Load CSV")


def onSettings():
    print("Settings")


buttons = [
    ft.Button(
        content="Calibration",
        on_click=onCalibration
    ),
    ft.Button(
        content="WordTest",
        on_click=onWordTest
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


def MainMenuView():
    return ft.View(
        controls=column,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
