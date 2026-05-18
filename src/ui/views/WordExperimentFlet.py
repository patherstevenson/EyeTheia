import asyncio

import flet as ft
from experiments.wordExperiment.WordExperiment import WordExperiment
from ui.AppState import AppState
from ui.FletUtils import playSound


def WordExperimentView(page: ft.Page, state: AppState):
    exp = WordExperiment(state)

    quarter_width = max((page.window.width or 1920) / 2, 200) * state.settings.buttons_size
    quarter_height = max((page.window.height or 1080) / 2, 140) * state.settings.buttons_size

    container = ft.Column(
        controls=[],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    words = [
        ft.Container(
            content=ft.Button(
                content=ft.Text(word),
                width=quarter_width,
                height=quarter_height,
                on_click=lambda _, i=index: page.run_task(exp.next_words, i)
            ),
            expand=1,
            alignment=ft.Alignment.CENTER,
        )
        for index, word in enumerate(exp.word_groups[0].words)
    ]
    words_grid = ft.Column(
        controls=[
            ft.Row(
                controls=words[:2],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
            ft.Row(
                controls=words[2:4],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        expand=True,
    )

    def show_plus():
        """Show a big "+" in the middle of the screen for a time set in AppSettings"""
        container.controls = [
            ft.Icon(
                icon=ft.Icons.ADD,
                size=100,
                color="black",
            )
        ]
        page.update()

    async def show_word_group():
        """Show the 4 words of the current word_group in 4 buttons, each ones in a quater of the screen, with a size set in AppSettings"""
        current_words = exp.get_current_words()

        for word_index, button in enumerate(words):
            content = button.content.content
            if content:
                content.value = current_words[word_index]

        container.controls = [words_grid]
        page.update()
        await playSound(exp.get_current_sound())

    exp.listeners["show_plus"] = show_plus
    exp.listeners["show_word_group"] = show_word_group

    queue = asyncio.Queue()
    ui_loop = asyncio.get_running_loop()
    process_state = {"process_started": False}

    def on_new_coords(cx, cy):
        """Called when the tracker finished to guess the Gaze coordinates"""
        ui_loop.call_soon_threadsafe(queue.put_nowait, (cx, cy))

    exp.add_listener(on_new_coords)

    async def start_experiment(_):
        """Start an experiment"""
        if not process_state["process_started"]:
            process_state["process_started"] = True
        await exp.start()

    def stop_experiment():
        """Stop the running experiment"""
        exp.stop()
        ui_loop.call_soon_threadsafe(queue.put_nowait, None)
        process_state["process_started"] = False
        page.update()

        # for res in state.results:
        #     print(str(res))

        page.run_task(page.push_route, "/Results")

    exp.add_finish_listener(stop_experiment)

    async def back_to_main_menu(page: ft.Page):
        """Go back to main menu"""
        await page.push_route("/")

    container.controls = [
        ft.Column(
            controls=[
                ft.Text("Before Starting : ", weight=ft.FontWeight.W_900, size=12),
                ft.Row(
                    controls=[
                        ft.Button(
                            content="Calibration", on_click=state.gaze_manager.calibrate
                        ),
                        ft.Button(
                            content="Personalize Experiment",
                            on_click=lambda _: page.run_task(page.push_route, "/Personalize")
                        ),
                        # ft.Button(
                        #     content="LoadCSV",
                        #     on_click=lambda _: page.run_task(loadCSV, page)
                        # ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Button(
                    content="Démarrer l'expérience",
                    on_click=start_experiment,
                ),
                ft.Button(
                    content="MainMenu",
                    on_click=lambda _: page.run_task(back_to_main_menu, page)
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    ]

    return ft.View(
        controls=[container],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
