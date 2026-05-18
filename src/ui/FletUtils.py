import csv

import flet as ft
from experiments.wordExperiment.GazePoint import GazePoint
from experiments.wordExperiment.GroupResults import GroupResults
from experiments.wordExperiment.WordGroup import WordGroup
from playsound3 import playsound
from ui.AppState import AppState


async def playSound(path: str):
    """Play a sound. Take a full path, or just the file name (in that case, look at src/experiments/wordExperiment/res/sounds)"""
    if path.startswith("/"):
        playsound(path)
    else:
        playsound("src/experiments/wordExperiment/res/sounds/" + path)


async def loadCSV(page: ft.Page):
    """Load a CSV in the memory"""
    file_path = await ft.FilePicker().pick_files(allow_multiple=False)

    if not file_path:
        file_path = "src/experiments/wordExperiment/res/WordData.csv"
    else:
        file_path = file_path[0].path

    await load_this_csv(page, file_path)

    await page.push_route("/WordExperiment")


async def load_this_csv(page: ft.Page, file_path: str):
    """Load the specified CSV based on his first word
    If first word is "experience", will load the data in appState.word_groups
    If first word is "results", will load data in appState.results
    """
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        first_row = True
        file_type = "experience"

        for row in reader:
            if first_row:
                if row[0] == "experience":
                    file_type = "experience"
                    page.data.settings.max_time_to_choose = float(row[1])
                    page.data.settings.time_to_wait_between = float(row[2])
                    page.data.settings.buttons_size = float(row[3])
                    page.data.settings.gaze_per_second = float(row[4])

                    page.data.word_groups = []
                elif row[0] == "result_index":
                    file_type = "results"
                    page.data.results = []

                first_row = False
            else:
                if file_type == "experience":
                    page.data.word_groups.append(WordGroup(row[:4], row[4], row[5]))
                elif file_type == "results":
                    print("results")
                    print(row)
                    index = int(row[0])
                    word_group = WordGroup(row[1:5], row[5], row[6])
                    selected = int(row[7])
                    total_time = float(row[8])
                    gaze_score = [int(row[9]), int(row[10]), int(row[11]), int(row[12]), int(row[13])]
                    gaze_points_str = row[14].split(";")

                    gaze_points = []

                    cpt_gaze = 0

                    for str_pt in gaze_points_str:
                        print(str_pt)
                        x = str_pt.split(":")[0].strip("(")
                        y = str_pt.split(":")[1].strip(")")
                        gaze_points.append(GazePoint(cpt_gaze, x, y))

                    page.data.results.append(GroupResults(index, word_group, selected, total_time, gaze_score, gaze_points))

            if file_type == "results":
                page.push_route("/")


async def saveExperienceToCSV(state: AppState):
    """Save the experience in memory to a CSV file"""
    fp = ft.FilePicker()
    file_path = await fp.save_file(dialog_title="Save File", file_name="word_experience.csv", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=[".csv"])

    with(open(file_path, 'w', newline='')) as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        writer.writerow(["experience", state.settings.max_time_to_choose, state.settings.time_to_wait_between, state.settings.buttons_size, state.settings.gaze_per_second])

        for word_group in state.word_groups:
            writer.writerow(word_group.words + [word_group.correct, word_group.sound])


async def saveResultsToCSV(state: AppState):
    """Save the results in memory to a CSV file"""
    fp = ft.FilePicker()
    file_path = await fp.save_file(dialog_title="Save File", file_name="word_experience_results.csv", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=[".csv"])

    with(open(file_path, 'w', newline='')) as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        writer.writerow(["result_index", "word_top_left", "word_top_right", "word_down_left", "word_down_right", "correct_word", "sound", "selected", "total_time", "gaze_score_top_left", "gaze_score_top_right", "gaze_score_down_left",
                         "gaze_score_down_right", "gaze_where_not_detected", "points", ])

        for res in state.results:
            points = ""

            for pt in res.gaze_points:
                points += str(pt) + ";"
            points = points.removesuffix(";")

            writer.writerow([res.index] + res.words.words + [res.words.correct, res.words.sound, res.selected, res.total_time] + res.gaze_score + [points])
