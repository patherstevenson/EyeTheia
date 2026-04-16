import flet as ft
from PIL.ImageOps import expand
from experiments.wordExperiment.GroupResults import GroupResults
from experiments.wordExperiment.WordGroup import WordGroup
from flet import controls
from flet.controls import alignment, border
from torch.nn.modules import container

from ui.AppState import AppState


def ResultScreenView(page: ft.Page, state: AppState):
    if state.results == []:
        state.results = [
            GroupResults(0, WordGroup(["orange", "blouse", "pas", "bas"], "pas", "pronunciation_fr_pas.mp3"), 1),
            GroupResults(1, WordGroup(["permis", "feutre", "peine", "beine"], "peine", "pronunciation_fr_peine.mp3"),2),
            GroupResults(2, WordGroup(["trait", "rond", "poule", "boule"], "poule", "pronunciation_fr_poule.mp3"), 0),
            GroupResults(3, WordGroup(["bas", "blouse", "pas", "orange"], "bas", "pronunciation_fr_bas.mp3"), 3),
            GroupResults(4, WordGroup(["beine", "feutre", "peine", "permis"], "beine", "pronunciation_fr_beine.mp3"),1),
            GroupResults(5, WordGroup(["boule", "rond", "poule", "trait"], "boule", "pronunciation_fr_boule.mp3"), 2),
            GroupResults(5, WordGroup(["boule", "rond", "poule", "trait"], "boule", "pronunciation_fr_boule.mp3"), 2),

        ]
        state.results[0].gaze_score = [1, 2, 4, 7]
        state.results[1].gaze_score = [1, 2, 4, 7]
        state.results[2].gaze_score = [1, 2, 4, 7]
        state.results[3].gaze_score = [1, 2, 4, 7]
        state.results[4].gaze_score = [1, 2, 4, 7]
        state.results[5].gaze_score = [1, 2, 4, 7]



    page_content = [
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[ft.Text(res.words.words[0], size=24, weight=ft.FontWeight.W_600),
                                  ft.Text(res.words.words[1], size=24, weight=ft.FontWeight.W_600)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[ft.Text(res.words.words[2], size=24, weight=ft.FontWeight.W_600),
                                  ft.Text(res.words.words[3], size=24, weight=ft.FontWeight.W_600)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            border=ft.Border.all(10, ft.Colors.AMBER_100)
        )
        for res in state.results
    ]

    sf = ft.Column(
        controls=page_content,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.update()

    return ft.View(
        controls=[
            ft.ListView(controls=sf,
                        auto_scroll=True,
                        height=page.height - 50,),
            ft.Button(
                content="Go Back To Main Menu",
                on_click=lambda _: page.run_task(page.push_route, ("/"))
            )],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        # scroll=ft.ScrollMode.AUTO
    )
