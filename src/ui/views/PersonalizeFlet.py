from dataclasses import field

import flet as ft
from ui.AppState import AppState


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, group, word, index, on_swap):
        content = ft.Draggable(
            group=group,
            content=ft.Container(content=ft.Text(word, weight=ft.FontWeight.W_400), width=100, height=100),
        )
        super().__init__(content)
        self.group = group
        self.word = word
        self.on_accept = on_swap
        self.data = index
        self.expand = True


@ft.control
class WordPicker(ft.Row):
    """A widget to arrange 4 words in a grid"""
    words = list[str]

    def init(self, words=["A", "B", "C", "D"]):
        self.build_grid()
        self.expand = True

    def build_grid(self):
        self.controls = [
            ft.Column(
                controls=[
                    DragTile("1", "A", 1, self.handle_swap),
                    DragTile("1", "B", 2, self.handle_swap),
                ], expand=True
            ),
            ft.Column(
                controls=[
                    DragTile("1", "C", 3, self.handle_swap),
                    DragTile("1", "D", 4, self.handle_swap),
                ], expand=True
            )
        ]

    def handle_swap(self, e: ft.DragTargetEvent):
        print(str(e.src.parent.word))
        # src_index = int(e.src.data)  # D'où ça vient
        # dst_index = int(e.control.data)  # Où ça arrive
        #
        # self.words[src_index], self.words[dst_index] = self.words[dst_index], self.words[src_index]
        #
        # # On reconstruit la grille proprement
        # self.build_grid()
        # self.update()


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
            # ft.Column(
            #     controls=[
            #         ft.Text(self.words[0], weight=ft.FontWeight.W_600),
            #         ft.Text(self.words[1], weight=ft.FontWeight.W_600),
            #
            #     ]
            # ),
            # ft.Column(
            #     controls=[
            #         ft.Text(self.words[2], weight=ft.FontWeight.W_600),
            #         ft.Text(self.words[3], weight=ft.FontWeight.W_600),
            #     ]
            # ),

            WordPicker(self.words)
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

    widgets.append(
        ft.ReorderableListView(
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
                      on_click=lambda _: page.run_task(page.push_route, "/WordExperiment")
                      )
        ],
        expand=1
    ))

    return ft.View(
        controls=ft.Row(controls=widgets, expand=True),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
