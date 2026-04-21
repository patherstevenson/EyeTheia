import flet as ft
from PIL.ImageOps import expand
from experiments.wordExperiment.GroupResults import GroupResults
from experiments.wordExperiment.WordGroup import WordGroup
from flet import controls
from flet.controls import alignment, border
from flet.controls.core import icon
from playsound3 import playsound
from scipy.cluster.hierarchy import weighted
from torch.nn.modules import container

from ui.AppState import AppState


def tabWidget(data, size, font: ft.FontWeight, spacing, border_width, border_color, is_score: bool = False):
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
            data=is_score
        ),
        border=ft.Border.all(border_width, border_color),
        expand=1,
        aspect_ratio=1,
    )


def data_widget(res):
    # Data
    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(res.words.sound, size=20, weight=ft.FontWeight.W_600),
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_color=ft.Colors.BLUE,
                            icon_size=40,
                            on_click=lambda _: playsound("src/experiments/wordExperiment/res/sounds/" + res.words.sound)
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
                    tabWidget(res.gaze_score, 18, ft.FontWeight.W_600, 8, 4, ft.Colors.GREY),
                    ft.Column(
                        controls=[
                            ft.Text(str(res.gaze_score[4]) + " gazes failed", size=14, weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.FADE),
                            ft.Divider(height=9, thickness=3),
                            ft.Text("Je sais pas quelle info mettre ici", size=14, weight=ft.FontWeight.W_600,
                                    overflow=ft.TextOverflow.FADE),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    )

                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=1
            )
        ],
        expand=1,
        aspect_ratio=1
    )


def switch_infos(word_tab_widget, res: GroupResults, page):
    if (word_tab_widget.content.data):
        word_tab_widget.content = tabWidget(res.words.words, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.GREY,
                                            False).content
        page.update()
    else:
        word_tab_widget.content = tabWidget(res.gaze_score, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.GREY,
                                            True).content
        page.update()

    word_tab_widget.on_click = lambda _: switch_infos(word_tab_widget, res, page)


def res_widget(page, res):
    word_tab_widget = tabWidget(res.words.words, 24, ft.FontWeight.W_600, 16, 6, ft.Colors.GREY)

    word_tab_widget.aspect_ratio = 1
    word_tab_widget.ink = True

    word_tab_widget.on_click = lambda _: switch_infos(word_tab_widget, res, page)

    res_data_widget = data_widget(res)

    # Group Result
    return ft.Container(
        content=ft.Row(
            controls=[
                # TabWidget : Words
                word_tab_widget,
                ft.VerticalDivider(width=9, thickness=3),
                res_data_widget
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True,
            spacing=50,
        ),
        border=ft.Border.all(10, ft.Colors.AMBER_100),
        expand=1,
        margin=ft.Margin.symmetric(horizontal=20)
    )


def ResultScreenView(page: ft.Page, state: AppState):
    # if state.results == []:
    #     state.results = [
    #         GroupResults(0, WordGroup(["orange", "blouse", "pas", "bas"], "pas", "pronunciation_fr_pas.mp3"), 1),
    #         GroupResults(1, WordGroup(["permis", "feutre", "peine", "beine"], "peine", "pronunciation_fr_peine.mp3"),
    #                      2),
    #         GroupResults(2, WordGroup(["trait", "rond", "poule", "boule"], "poule", "pronunciation_fr_poule.mp3"), 0),
    #         GroupResults(3, WordGroup(["bas", "blouse", "pas", "orange"], "bas", "pronunciation_fr_bas.mp3"), 3),
    #         GroupResults(4, WordGroup(["beine", "feutre", "peine", "permis"], "beine", "pronunciation_fr_beine.mp3"),
    #                      1),
    #         GroupResults(5, WordGroup(["boule", "rond", "poule", "trait"], "boule", "pronunciation_fr_boule.mp3"), 2),
    #
    #     ]
    #     state.results[0].gaze_score = [1, 5, 2, 7, 3]
    #     state.results[1].gaze_score = [1, 0, 4, 19, 20]
    #     state.results[2].gaze_score = [7, 2, 18, 7, 0]
    #     state.results[3].gaze_score = [1, 9, 4, 7, 0]
    #     state.results[4].gaze_score = [6, 2, 24, 6, 14]
    #     state.results[5].gaze_score = [14, 2, 4, 0, 7]

    widget_list = [
        res_widget(page, res)
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
                height=page.height - 100, ),
            ft.Button(
                content="Go Back To Main Menu",
                on_click=lambda _: page.run_task(page.push_route, ("/"))
            )],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        # scroll=ft.ScrollMode.AUTO
    )
