from dataclasses import field
from typing import Callable

import flet as ft
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppSettings import AppSettingsEnum
from ui.AppState import AppState
from ui.FletUtils import playSound

WORDS_PER_GROUP = 4


def PersonalizeView(page: ft.Page, state: AppState):
    """Build the screen used to customize word groups."""
    group_list = [
        GroupCustomization(group_index=index, word_group=group)
        for index, group in enumerate(state.word_groups)
    ]

    reorderable_list = ft.ReorderableListView(
        show_default_drag_handles=False,
        controls=group_list,
        expand=1,
        auto_scroll=True,
        height=page.height - 100,
        on_reorder=lambda e: handle_reorder(e, state),
        spacing=120,
    )

    button_preview = ButtonSizePreview()

    return ft.View(
        controls=[
            ft.Row(
                controls=[
                    reorderable_list,
                    ft.VerticalDivider(),
                    ft.Column(
                        controls=[
                            ft.Button(
                                content="Go Back to Main Menu",
                                on_click=lambda _: page.run_task(page.push_route, "/WordExperiment"),
                            ),
                            AppSettingsWidget(setting=AppSettingsEnum.MAX_TIME_TO_CHOOSE,
                                              value_picker=NumberPicker(),
                                              description="Maximum time to chose a word",
                                              data=page.data.settings),
                            AppSettingsWidget(setting=AppSettingsEnum.TIME_TO_WAIT_BETWEEN,
                                              value_picker=NumberPicker(step=0.5),
                                              description="Time to wait between 2 word groups",
                                              data=page.data.settings),
                            AppSettingsWidget(setting=AppSettingsEnum.GAZE_PER_SECOND,
                                              value_picker=NumberPicker(step=1),
                                              description="Number of gaze the app will try to make avery second",
                                              data=page.data.settings),
                            AppSettingsWidget(setting=AppSettingsEnum.BUTTONS_SIZE,
                                              value_picker=SliderPicker(),
                                              description="Size of the buttons",
                                              data=page.data.settings),
                            button_preview,
                            ft.IconButton(icon=ft.Icons.BOY, on_click=lambda _: button_preview.resize_buttons())
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        expand=True
    )


def handle_reorder(e: ft.OnReorderEvent, state: AppState):
    word_groups = list(state.word_groups)
    moved_group = word_groups.pop(e.old_index)
    word_groups.insert(e.new_index, moved_group)
    state.set_word_groups(word_groups)

    reordered_controls = list(e.control.controls)
    moved_control = reordered_controls.pop(e.old_index)
    reordered_controls.insert(e.new_index, moved_control)

    for index, control in enumerate(reordered_controls):
        control.group_index = index

    e.control.controls = reordered_controls
    e.control.update()


@ft.control
class CorrectAnswerDropdown(ft.Dropdown):
    word_group: WordGroup = None

    def init(self):
        self.options = [
            ft.DropdownOption(key=word, text=word)
            for word in self.word_group.words
        ]
        self.value = self.word_group.correct
        self.on_select = self.handle_select

    def handle_select(self, e):
        self.word_group.correct = e.control.value


@ft.control
class SoundPicker(ft.Container):
    """Display the selected sound and allow replaying it."""

    word_group: WordGroup = None

    def init(self):
        self.content = ft.Row(
            controls=[
                ft.Text(self.word_group.sound),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    icon_color=ft.Colors.BLUE,
                    icon_size=40,
                    on_click=self.play_sound,
                ),
            ]
        )
        self.border = ft.Border.all(2, ft.Colors.GREY)

    async def play_sound(self, _):
        await playSound(self.word_group.sound)


@ft.control
class GroupCustomization(ft.Container):
    """Widget used to edit one WordGroup."""

    group_index: int = -1
    word_group: WordGroup = None

    def init(self):
        self.expand = True
        self.padding = 10
        self.border = ft.Border.all(5, ft.Colors.BLACK_26)
        self.content = ft.Row(
            controls=[
                WordPicker(word_group=self.word_group),
                ft.Column(
                    controls=[
                        SoundPicker(word_group=self.word_group),
                        CorrectAnswerDropdown(word_group=self.word_group),
                    ]
                ),
                ft.ReorderableDragHandle(
                    content=ft.Icon(ft.Icons.DRAG_INDICATOR, color=ft.Colors.BLUE),
                    expand=1,
                ),
            ],
            expand=1,
        )


@ft.control
class WordPicker(ft.Column):
    """Display a 2x2 editable grid for one WordGroup."""

    word_group: WordGroup = None

    def init(self):
        self.expand = True
        self.validate_words()
        self.build_grid()

    def validate_words(self):
        if len(self.word_group.words) != WORDS_PER_GROUP:
            raise ValueError(
                f"Each WordGroup must contain exactly {WORDS_PER_GROUP} words. "
                f"Received {len(self.word_group.words)}."
            )

    def build_grid(self):
        words = self.word_group.words
        self.controls = [
            ft.Row(
                controls=[
                    DragTile(words[0], 0, self.handle_swap, self.handle_change_word),
                    DragTile(words[1], 1, self.handle_swap, self.handle_change_word),
                ],
                expand=True,
            ),
            ft.Row(
                controls=[
                    DragTile(words[2], 2, self.handle_swap, self.handle_change_word),
                    DragTile(words[3], 3, self.handle_swap, self.handle_change_word),
                ],
                expand=True,
            ),
        ]

    def handle_swap(self, e: ft.DragTargetEvent):
        source_index = e.src.data
        target_index = e.control.data
        words = self.word_group.words

        words[source_index], words[target_index] = words[target_index], words[source_index]
        self.build_grid()
        self.update()

    def handle_change_word(self, word_index: int, new_word: str):
        self.word_group.words[word_index] = new_word


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, word: str, index: int, on_swap, on_change):
        text_field = ft.TextField(
            value=word,
            on_change=lambda e, tile_index=index: on_change(tile_index, e.control.value),
            expand=True,
        )

        content = ft.Draggable(
            expand=True,
            content=ft.Container(
                expand=True,
                content=text_field,
                width=100,
                height=100,
                alignment=ft.Alignment.CENTER,
            ),
            data=index,
        )

        super().__init__(content=content, on_accept=on_swap, data=index, expand=True)


@ft.control
class AppSettingsWidget(ft.Container):
    """The widget used to modify any parameter in AppSettings. Store the reference of the AppSettings in his Data attribute."""
    setting: AppSettingsEnum = None
    value_picker: ft.Control = None
    description: str = ""
    bound: list[ft.Control] = field(default_factory=list)

    def init(self):
        value = getattr(self.data, self.setting.value)
        self.value_picker.value = value
        self.value_picker.set_value(value)
        self.value_picker.set_value_updater(self.update_intern_value)

        self.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.BLUE, expand=1),
                self.value_picker,
                ft.Text(value=self.description, weight=ft.FontWeight.W_600, expand=8),
            ],
            tight=True
        )

    def update_intern_value(self, e, new_value=None):
        """Updates the value in the App setting and in the Picker Object"""
        if (new_value == None):
            if new_value == "":
                new_value = 0.0
            else:
                new_value = float(e.control.value)
        self.value_picker.set_value(new_value)
        setattr(self.page.data.settings, self.setting.value, new_value)
        self.value_picker.update_shown()
        self.update()


@ft.control
class NumberPicker(ft.Row):
    setting: AppSettingsEnum = None
    value: str = "0"
    step: float = 1.0

    def set_value_updater(self, method: Callable):
        self.text_field.on_change = method

    def init(self):
        self.text_field = ft.TextField(value=self.value,
                                       keyboard_type=ft.KeyboardType.NUMBER,
                                       input_filter=ft.InputFilter(allow=True, regex_string=r"^(\d+\.)?\d*$", replacement_string=""),
                                       expand_loose=True,
                                       )

        self.controls = [
            ft.IconButton(icon=ft.Icons.REMOVE, on_click=self.button_down),
            self.text_field,
            ft.IconButton(icon=ft.Icons.ADD, on_click=self.button_up),
        ]

        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def button_up(self, e):
        self.text_field.on_change(e, self.value + self.step)

    def button_down(self, e):
        self.text_field.on_change(e, self.value - self.step)

    def set_value(self, value):
        self.value = value
        self.text_field.value = str(value)

    def update_shown(self):
        """Updates the value shown based on widget value"""
        self.text_field.value = str(self.value)
        if (self.page):
            self.update()


@ft.control
class SliderPicker(ft.Row):
    setting: AppSettingsEnum = None
    value: float = 0.0

    def set_value_updater(self, method: Callable):
        self.slider.on_change = method
        self.text_field.on_change = method

    def init(self):
        self.built = False
        self.slider = ft.Slider(value=self.value)
        self.text_field = ft.TextField(value=str(self.value),
                                       keyboard_type=ft.KeyboardType.NUMBER,
                                       input_filter=ft.InputFilter(allow=True, regex_string=r"^(\d+\.)?\d*$", replacement_string=""),
                                       expand_loose=True,
                                       width=100
                                       )

        self.controls = [
            self.slider,
            self.text_field
        ]

    def build(self):
        self.built = True

    def set_value(self, value):
        if (value > 1):
            value = 1.0
        self.value = value
        self.update_shown()

    def update_shown(self):
        """Updates the value shown based on widget value"""
        self.slider.value = self.value
        self.text_field.value = str(self.value)
        if (self.built):
            self.update()
            self.parent.parent.update()


@ft.control
class ButtonSizePreview(ft.Container):
    size: float = 0.5

    def init(self):
        self.aspect_ratio = 16 / 9

        self.buttons = [
            ft.Button(content="A", width=480, height=270),
            ft.Button(content="B", width=480, height=270),
            ft.Button(content="C", width=480, height=270),
            ft.Button(content="D", width=480, height=270),
        ]

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.buttons[0],
                        self.buttons[1]
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        self.buttons[2],
                        self.buttons[3]
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.expand = True
        self.on_size_change = self.handle_resize
        self.border = ft.Border.all(2, ft.Colors.GREY)

    def before_update(self) -> None:
        self.resize_buttons()

    def resize_buttons(self):
        self.size = self.page.data.settings.buttons_size

        for button in self.buttons:
            button.width = max((self.width or 1920) / 2, 200) * self.size * 0.95
            button.height = max((self.height or 1080) / 2, 140) * self.size * 0.95

    def handle_resize(self, e):
        self.width = e.width
        self.height = e.height
