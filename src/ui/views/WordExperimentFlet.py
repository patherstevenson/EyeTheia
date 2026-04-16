import asyncio

from playsound3 import playsound
import flet as ft
from experiments.wordExperiment.WordExperiment import WordExperiment
from ui.AppState import AppState


def WordExperimentView(page: ft.Page, state: AppState):
    exp = WordExperiment(state)



    cx_text = ft.Text("cx: -")
    cy_text = ft.Text("cy: -")
    quarter_width = max((page.window.width or 1200) / 2 - 24, 200) * state.settings.buttons_size
    quarter_height = max((page.window.height or 800) / 2 - 24, 140) * state.settings.buttons_size

    container = ft.Column(
        controls=[],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    words = [
        ft.Button(
            content=ft.Text(word),
            width=quarter_width,
            height=quarter_height,
            on_click=lambda _, i=index: page.run_task(exp.choose, i)
        )
        for index, word in enumerate(exp.get_current_words())
    ]

    words_grid = ft.Column(
        controls=[
            ft.Row(
                controls=words[:2],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=words[2:4],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
    )

    def show_plus():
        container.controls = [
            ft.Icon(
                icon=ft.Icons.ADD,
                size=100,
                color="black",
            )
        ]
        page.update()

    async def show_word_group():

        current_words = exp.get_current_words()

        for word_index, button in enumerate(words):
            button.content.value = current_words[word_index]

        container.controls = [words_grid]
        page.update()
        playsound("src/experiments/wordExperiment/res/sounds/" + exp.get_current_sound())

    exp._listeners["show_plus"] = show_plus
    exp._listeners["show_word_group"] = show_word_group

    queue = asyncio.Queue()
    ui_loop = asyncio.get_running_loop()
    process_state = {"process_started": False}

    def on_new_coords(cx, cy):
        ui_loop.call_soon_threadsafe(queue.put_nowait, (cx, cy))

    exp.add_listener(on_new_coords)

    async def start_experiment(_):
        if not process_state["process_started"]:
            process_state["process_started"] = True
        await exp.start()
        await show_word_group()

    def stop_experiment():
        exp.stop()
        ui_loop.call_soon_threadsafe(queue.put_nowait, None)
        process_state["process_started"] = False
        page.update()

        for res in exp.results.values():
            print(str(res))

        page.run_task(back_to_main_menu, page)

    exp.add_finish_listener(stop_experiment)

    async def back_to_main_menu(page: ft.Page):
        await page.push_route("/")

    container.controls = [
        ft.Row(
            controls=[
                ft.Button(
                    content="Démarrer l'expérience",
                    on_click=start_experiment,
                ),
                ft.Button(
                    content="MainMenu",
                    on_click=lambda _: page.run_task(back_to_main_menu, page)
                ),
            ]
        ),
    ]

    return ft.View(
        controls=[container],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
