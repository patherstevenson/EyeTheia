import asyncio

import GazeManager
import flet as ft
from experiments.WordExperiment import WordExperiment


def WordExperimentView(page: ft.Page, gaze_manager: GazeManager):
    exp = WordExperiment(gaze_manager)
    cx_text = ft.Text("cx: -")
    cy_text = ft.Text("cy: -")
    status_text = ft.Text("Statut: idle")

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
        page.update()
        exp.start()

    def stop_experiment(_):
        exp.stop()
        status_text.value = "Statut: stopped"
        ui_loop.call_soon_threadsafe(queue.put_nowait, None)
        state["process_started"] = False
        page.update()


    async def back_to_main_menu(page: ft.Page):
        await page.push_route("/")

    return ft.View(
        controls=[
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
    )
