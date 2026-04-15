import csv

import flet as ft
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppState import AppState


def onCalibration():
    print("Calibration")


async def onWordExperiment(page: ft.Page):
    await page.push_route("/WordExperiment")


async def onLoadCSV(state: AppState):
    print("Load CSV")
    file_path = await ft.FilePicker().pick_files(allow_multiple=False)

    if not file_path:
        file_path = "src/experiments/wordExperiment/res/WordData.csv"
    else:
        file_path = file_path[0].path

    await loadCSV(file_path, state)

async def loadCSV(file_path, state):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        wordData = []

        for row in reader:
            print(row)
            wordData.append(WordGroup(row[:4], row[4], row[5]))

        state.set_word_groups(wordData)
        print(str(len(wordData)))



def onSettings():
    print("Settings")


def MainMenuView(page: ft.Page, state: AppState):
    buttons = [
        ft.Button(
            content="Calibration",
            on_click=state.gaze_manager.calibrate
        ),
        ft.Button(
            content="WordTest",
            on_click=lambda _: page.run_task(onWordExperiment, page)
        ),
        ft.Button(
            content="LoadCSV",
            on_click=lambda _: page.run_task(onLoadCSV, state)
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
