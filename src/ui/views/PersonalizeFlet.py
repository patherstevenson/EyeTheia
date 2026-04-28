from dataclasses import field

import flet as ft
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppState import AppState
from ui.FletUtils import playSound


def PersonalizeView(page: ft.Page, state: AppState):
    """A screen to personalize an experiment"""
    widgets = []

    page.data = state

    word_groups = state.word_groups

    group_list = [
        GroupCustomization(
            group_index=i,
            word_group=group,
            page=page
        )
        for i, group in enumerate(state.word_groups)
    ]
    widgets.append(
        ft.Column(
            controls=group_list,
            expand=1,
            scroll=ft.ScrollMode.AUTO,  # Remplace auto_scroll
            spacing=20  # Espacement entre tes groupes
        )
    )

    widgets.append(ft.VerticalDivider())

    widgets.append(
        ft.Column(
            controls=[
                ft.Button(
                    content="Go Back to Main Menu",
                    on_click=lambda _: page.run_task(page.push_route, "/WordExperiment")
                )
            ],
            expand=1
        )
    )

    return ft.View(
        controls=ft.Row(
            controls=widgets,
            expand=True
        ),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )


@ft.control
class GroupCustomization(ft.DragTarget):
    def __init__(self, group_index, word_group, page):
        content = self.build_content(page, group_index, word_group)

        super().__init__(content)
        self.content = content
        self.group = "GROUP_SWAP"
        self.group_index = group_index
        self.word_group = word_group
        self.on_accept = self.handle_group_swap

    def build_content(self, page=None, group_index=None, word_group=None):
        if page == None:
            page = self.page
        if group_index == None:
            group_index = self.group_index
        if word_group == None:
            word_group = self.word_group

        draggable_content = ft.Container(
            border=ft.Border.all(5, ft.Colors.BLACK_26),
            padding=5,
            margin=ft.Margin.symmetric(vertical=5),
            bgcolor=ft.Colors.SURFACE,
            content=ft.Row(
                controls=[
                    WordPicker(group_index=group_index, words=page.data.word_groups[group_index].words),
                    ft.Column(
                        controls=[
                            SoundPicker(group_index=group_index, word_groups = page.data.word_groups),
                            CorrectAnwserWidget(group_index=group_index, word_groups = page.data.word_groups)
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
        )

        return ft.Draggable(
            group="GROUP_SWAP",
            data=self,
            axis=ft.Axis.VERTICAL,
            content=draggable_content,
            # Feedback visuel pendant le déplacement (optionnel mais recommandé)
            content_feedback=draggable_content
        )

    def handle_group_swap(self, event: ft.DragTargetEvent):
        src_idx = event.src.data.group_index
        dst_idx = event.control.group_index

        if src_idx == dst_idx:
            return

        word_groups = event.page.data.word_groups
        word_groups[src_idx], word_groups[dst_idx] = word_groups[dst_idx], word_groups[src_idx]

        event.src.parent.content = event.src.parent.build_content()
        # event.src.parent.update()
        event.control.content = event.control.build_content()
        # event.control.update()


@ft.control
class SoundPicker(ft.Container):
    """A widget to show, play and modify the picked sound of a word_group"""

    word_group: WordGroup = None
    group_index: int = -1
    word_groups: list[WordGroup] = field(default_factory=list)

    def init(self):
        self.content = ft.Row(
            controls=[
                ft.Text(self.word_groups[self.group_index].sound),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    icon_color=ft.Colors.BLUE,
                    icon_size=40,
                    on_click=self.playsound
                )
            ]
        )

    async def playsound(self):
        await playSound(self.word_groups[self.group_index].sound)


@ft.control
class CorrectAnwserWidget(ft.Container):
    word_group: WordGroup = None
    group_index: int = -1
    word_groups: list[WordGroup] = field(default_factory=list)

    def init(self):
        options = []
        self.content = ft.Row(
            controls=[
                ft.Text("Correct Answer : "),
                ft.Dropdown(
                    options=options,
                    value=self.word_groups[self.group_index].correct,
                    on_select=self.handle_select,
                )
            ],
        )
        self.padding = 2
        self.margin = 5

        for word in self.word_groups[self.group_index].words:
            options.append(ft.DropdownOption(key=word, text=word))

            self.border = ft.Border.all(2, ft.Colors.GREY)

    def handle_select(self, e):
        self.word_groups[self.group_index].correct = e.control.value
        print(self.word_groups[self.group_index].correct)


@ft.control
class WordPicker(ft.Column):
    """A widget to arrange 4 words in a grid"""
    words: list[str] = field(default_factory=list)
    group_index: int = -1

    def init(self):
        self.expand = True
        self.build_grid()

    def build_grid(self):
        self.controls = [
            ft.Row(controls=[DragTile(self.words[0], self.group_index, 0, self.handle_swap, self.handle_change_word), DragTile(self.words[1], self.group_index, 1, self.handle_swap, self.handle_change_word), ], expand=True),
            ft.Row(controls=[DragTile(self.words[2], self.group_index, 2, self.handle_swap, self.handle_change_word), DragTile(self.words[3], self.group_index, 3, self.handle_swap, self.handle_change_word), ], expand=True)]

    def handle_swap(self, e: ft.DragTargetEvent):
        print(str(e.src.parent.word))

        print(self.words)

        src_index = self.words.index(e.src.parent.word)
        new_index = self.words.index(e.control.word)

        self.words[src_index], self.words[new_index] = self.words[new_index], self.words[src_index]

        # On reconstruit la grille proprement
        self.build_grid()
        self.update()
        self.expand = True

    def handle_change_word(self, e):
        word_index = e.control.parent.parent.parent.word_index

        self.page.data.word_groups[self.group_index].words[word_index] = e.control.value



@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, word, group_index, word_index, on_swap, on_change):
        content = ft.Draggable(
            expand=True,
            group=str(group_index),
            content=ft.Container(
                expand=True,
                content=ft.TextField(value=word, on_change=on_change, expand=True),
                width=100,
                height=100,
                # border=ft.Border.all(2, ft.Colors.BLUE),
                alignment=ft.Alignment.CENTER
            ),
        )
        super().__init__(content)
        self.word_index = word_index
        self.group_index = group_index
        self.on_accept = on_swap
        self.data = word_index
        self.expand = True

    def handleChange(self, e):
        new_word = e.control.word
