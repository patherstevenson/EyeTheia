import flet as ft
from PIL.ImageOps import expand
from experiments.wordExperiment.GroupResults import GroupResults
from experiments.wordExperiment.WordGroup import WordGroup
from flet import controls
from flet.controls import alignment, border
from flet.controls.core import icon
from scipy.cluster.hierarchy import weighted
from torch.nn.modules import container

from ui.AppState import AppState


def tabWidget(data, size, font: ft.FontWeight, spacing, border_width, border_color):
    words = []
    for o in data:
        words.append(str(o))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Text(words[0], size=size, weight=font),
                              ft.Text(words[1], size=size, weight=font)],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,

                ),
                ft.Row(
                    controls=[ft.Text(words[2], size=size, weight=font),
                              ft.Text(words[3], size=size, weight=font)],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=spacing,
        ),
        border=ft.Border.all(border_width, border_color),
        expand=1,
        aspect_ratio=1
    )


def data_widget(res):
    score_tab_widget = tabWidget(res.gaze_score, 12, ft.FontWeight.W_600, 8, 4, ft.Colors.GREY)
    score_tab_widget.expand = False

    # Data
    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Sound.mp3", size=20, weight=ft.FontWeight.W_600),
                        ft.Icon(
                            icon=ft.Icons.PLAY_ARROW,
                            color=ft.Colors.BLUE,
                            size=40
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                border=ft.Border.all(4, ft.Colors.GREY),
                expand=1
            )
            ,
            ft.Row(
                controls=[
                    score_tab_widget,
                    ft.Column(
                        controls=[
                            ft.Text("102 Gaze Out", size=14, weight=ft.FontWeight.W_600, overflow=ft.TextOverflow.FADE),
                            ft.Divider(height=9, thickness=3),
                            ft.Text("Je sais pas quelle info mettre ici", size=14, weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.FADE),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    )

                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=3
            )
        ],
        expand=1,
        aspect_ratio=1
    )


def res_widget(res):
    word_tab_widget = tabWidget(res.words.words, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.GREY)

    word_tab_widget.aspect_ratio = 1

    res_data_widget = data_widget(res)

    # Group Result
    return ft.Container(
        content=ft.Row(
            controls=[
                # TabWidget : Words
                word_tab_widget,
                res_data_widget
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True
        ),
        border=ft.Border.all(10, ft.Colors.AMBER_100),
        expand=1,
    )


def ResultScreenView(page: ft.Page, state: AppState):
    if state.results == []:
        state.results = [
            GroupResults(0, WordGroup(["orange", "blouse", "pas", "bas"], "pas", "pronunciation_fr_pas.mp3"), 1),
            GroupResults(1, WordGroup(["permis", "feutre", "peine", "beine"], "peine", "pronunciation_fr_peine.mp3"),
                         2),
            GroupResults(2, WordGroup(["trait", "rond", "poule", "boule"], "poule", "pronunciation_fr_poule.mp3"), 0),
            GroupResults(3, WordGroup(["bas", "blouse", "pas", "orange"], "bas", "pronunciation_fr_bas.mp3"), 3),
            GroupResults(4, WordGroup(["beine", "feutre", "peine", "permis"], "beine", "pronunciation_fr_beine.mp3"),
                         1),
            GroupResults(5, WordGroup(["boule", "rond", "poule", "trait"], "boule", "pronunciation_fr_boule.mp3"), 2),
            GroupResults(5, WordGroup(["boule", "rond", "poule", "trait"], "boule", "pronunciation_fr_boule.mp3"), 2),

        ]
        state.results[0].gaze_score = [1, 5, 2, 7]
        state.results[1].gaze_score = [1, 0, 4, 19]
        state.results[2].gaze_score = [7, 2, 18, 7]
        state.results[3].gaze_score = [1, 9, 4, 7]
        state.results[4].gaze_score = [6, 2, 24, 6]
        state.results[5].gaze_score = [14, 2, 4, 0]

    widget_list = [
        res_widget(res)
        for res in state.results
    ]

    page.update()

    return ft.View(
        controls=[
            ft.ListView(controls=ft.Column(
                controls=widget_list,
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
                auto_scroll=True,
                height=page.height - 50, ),
            ft.Button(
                content="Go Back To Main Menu",
                on_click=lambda _: page.run_task(page.push_route, ("/"))
            )],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        # scroll=ft.ScrollMode.AUTO
    )
