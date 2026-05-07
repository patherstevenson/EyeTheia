from ui.AppState import AppState
from experiments.wordExperiment.WordGroup import WordGroup
from playsound3 import playsound
import csv
import flet as ft


async def playSound(path: str):
    if(path.startswith("/")):
        playsound(path)
    else:
        playsound("src/experiments/wordExperiment/res/sounds/" + path)



async def loadCSV(page: ft.Page):
    file_path = await ft.FilePicker().pick_files(allow_multiple=False)

    if not file_path:
        file_path = "src/experiments/wordExperiment/res/WordData.csv"
    else:
        file_path = file_path[0].path

    """Load the specified CSV in state.word_groups"""
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        first_row = True

        for row in reader:
            if first_row:
                page.data.settings.max_time_to_choose = float(row[0])
                page.data.settings.time_to_wait_between = float(row[1])
                page.data.settings.buttons_size = float(row[2])
                page.data.settings.gaze_per_second = float(row[3])
                first_row = False
            else:
                page.data.word_groups.append(WordGroup(row[:4], row[4], row[5]))

    await page.push_route("/WordExperiment")


async def saveToCSV(state: AppState):
    fp = ft.FilePicker()
    file_path = await fp.save_file(dialog_title="Save File", file_name="word_experience.csv", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=[".csv"])

    with(open(file_path, 'w', newline='')) as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        writer.writerow([state.settings.max_time_to_choose, state.settings.time_to_wait_between, state.settings.buttons_size, state.settings.gaze_per_second])

        for word_group in state.word_groups:
            writer.writerow(word_group.words + [word_group.correct, word_group.sound])
