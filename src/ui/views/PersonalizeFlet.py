from dataclasses import field

import flet as ft
from ui.AppState import AppState



@ft.control
class WordPicker(ft.Row):
    """A widget to arrange 4 words in a grid"""
    words= list[str] = field(default_factory=list)

    def init(self):
        self.controls=[

        ]

@ft.control
class GroupCustomization(ft.Row):
    """A widget to configure a single WordGroup"""
    words: list[str] = field(default_factory=list)
    correct_answer: str = ""
    sound: str = ""

    def init(self):
        self.words = ["A", "B", "C", "D"]
        self.controls = [
            ft.Checkbox(),
            ft.Column(
                controls=[
                    ft.Text(self.words[0], weight=ft.FontWeight.W_600),
                    ft.Text(self.words[1], weight=ft.FontWeight.W_600),

                ]
            ),
            ft.Column(
                controls=[
                    ft.Text(self.words[2], weight=ft.FontWeight.W_600),
                    ft.Text(self.words[3], weight=ft.FontWeight.W_600),
                ]
            )
        ]


def handle_reorder(e: ft.OnReorderEvent):
    rlv = e.control
    moved_item = rlv.controls.pop(e.old_index)  # Remove the reordered item from its old position
    rlv.controls.insert(e.new_index, moved_item)  # Insert the reordered item into its new position
    rlv.update()


def PersonalizeView(page: ft.Page, state: AppState):
    widgets = []

    group_list = [
        ft.Draggable(content=GroupCustomization(), group="group")
        for i in range(20)
    ]

    widgets.append(ft.ReorderableListView(
        controls=group_list,
        expand=1,
        auto_scroll=True,
        height=page.height - 100,
        on_reorder=handle_reorder
    )
    )

    widgets.append(ft.VerticalDivider())

    widgets.append(ft.Column(
        controls=[
            ft.Button(content="Go Back to Main Menu",
                      on_click=lambda _: page.run_task(page.push_route, "/WordExperiment"))
        ],
        expand=1
    ))

    print("test")

    return ft.View(
        controls=ft.Row(controls=widgets, expand=True),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
