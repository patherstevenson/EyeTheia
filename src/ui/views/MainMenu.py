import GazeManager
import flet as ft
import csv

from experiments.WordGroup import WordGroup


def onCalibration():
    print("Calibration")

async def onWordExperiment(page: ft.Page):
    await page.push_route("/WordExperiment")


async def onLoadCSV(change_word_groups):
    print("Load CSV")
    file_path = await ft.FilePicker().pick_files(allow_multiple=False)

    with open(file_path[0].path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        wordData = []

        for row in reader:
            print(row)
            wordData.append(WordGroup(row[:4], row[4], row[5]))

        await change_word_groups(wordData)
        print(str(len(wordData)))






def onSettings():
    print("Settings")

def MainMenuView(page: ft.Page, gaze_manager: GazeManager, change_word_groups):
    buttons = [
        ft.Button(
            content="Calibration",
            on_click=gaze_manager.calibrate
        ),
        ft.Button(
            content="WordTest",
            on_click=lambda _: page.run_task(onWordExperiment, page)
        ),
        ft.Button(
            content="LoadCSV",
            on_click=lambda _: page.run_task(onLoadCSV, change_word_groups)
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
