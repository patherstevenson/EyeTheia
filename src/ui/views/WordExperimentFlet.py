import asyncio

import GazeManager
import flet as ft
from experiments import WordGroup
from experiments.WordExperiment import WordExperiment


def WordExperimentView(page: ft.Page, gaze_manager: GazeManager, data: [WordGroup]):
    exp = WordExperiment(gaze_manager)
    cx_text = ft.Text("cx: -")
    cy_text = ft.Text("cy: -")
    status_text = ft.Text("Statut: idle")

    container = ft.Column(controls=[])

    words = [
        ft.Button(
            content=data[0].words[0],
            on_click=lambda _: choose(0)
        ),
        ft.Button(
            content=data[0].words[1],
            on_click=lambda _: choose(1)
        ),
        ft.Button(
            content=data[0].words[2],
            on_click=lambda _: choose(2)
        ),
        ft.Button(
            content=data[0].words[3],
            on_click=lambda _: print("a")
        )]

    def choose(index):
        exp.choose(index)
        print(str(index))
        # todo reset user's gaze and go to the next word group

    queue = asyncio.Queue()
    ui_loop = asyncio.get_running_loop()
    state = {"process_started": False}

    def on_new_coords(cx, cy):
        ui_loop.call_soon_threadsafe(queue.put_nowait, (cx, cy))

    exp.add_listener(on_new_coords)

    async def process_results():
        while True:
            coords = await queue.get()
            if coords is None:
                break
            cx, cy = coords
            cx_text.value = f"cx: {cx}"
            cy_text.value = f"cy: {cy}"
            page.update()

    async def start_experiment(_):
        if not state["process_started"]:
            state["process_started"] = True
            page.run_task(process_results)
        status_text.value = "Statut: running"
        exp.start()
        container.controls = words
        page.update()

    def stop_experiment(_):
        exp.stop()
        status_text.value = "Statut: stopped"
        ui_loop.call_soon_threadsafe(queue.put_nowait, None)
        state["process_started"] = False
        page.update()

    async def back_to_main_menu(page: ft.Page):
        await page.push_route("/")

    container.controls = [
        status_text,
        cx_text,
        cy_text,
        ft.Row(
            controls=[
                ft.Button(
                    content="Démarrer l'expérience",
                    on_click=start_experiment,
                ),
                ft.Button(
                    content="Stop",
                    on_click=stop_experiment,
                ),
            ]
        ),
        ft.Row(
            controls=[
                ft.Button(
                    content="MainMenu",
                    on_click=lambda _: page.run_task(back_to_main_menu, page)
                )
            ]
        ),
    ]

    return ft.View(
        controls=container
    )
