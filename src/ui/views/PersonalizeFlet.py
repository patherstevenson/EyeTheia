from typing import Callable

import flet as ft
from experiments.wordExperiment.WordGroup import WordGroup
from ui.AppSettings import AppSettingsEnum
from ui.AppState import AppState
from ui.FletUtils import playSound, loadCSV, saveExperienceToCSV

WORDS_PER_GROUP = 4


def PersonalizeView(page: ft.Page, state: AppState):
    """Build the screen used to customize word groups."""

    reorderable_list = ft.ReorderableListView(
        show_default_drag_handles=False,
        controls=[],
        expand=1,
        auto_scroll=True,
        height=page.height,
        on_reorder=lambda e: handle_reorder(e, state),
        on_size_change=lambda e: handle_size_change(e)
    )

    def update_list_controls():
        reorderable_list.controls = [
            GroupCustomization(group_index=index, word_group=group, update_callback = update_list_controls)
            for index, group in enumerate(state.word_groups)
        ]

    update_list_controls()

    button_preview = ButtonSizePreview()

    max_time_to_choose = AppSettingsWidget(
        setting=AppSettingsEnum.MAX_TIME_TO_CHOOSE,
        value_picker=NumberPicker(minimum=0),
        description="Maximum time to chose a word",
        data=page.data.settings)
    time_between = AppSettingsWidget(
        setting=AppSettingsEnum.TIME_TO_WAIT_BETWEEN,
        value_picker=NumberPicker(step=0.5, minimum=0),
        description="Time to wait between 2 word groups",
        data=page.data.settings)
    gaze_per_second = AppSettingsWidget(
        setting=AppSettingsEnum.GAZE_PER_SECOND,
        value_picker=NumberPicker(step=1, minimum=0),
        description="Number of gaze the app will try to make every second",
        data=page.data.settings)
    button_size = AppSettingsWidget(
        setting=AppSettingsEnum.BUTTONS_SIZE,
        value_picker=SliderPicker(),
        description="Size of the buttons",
        data=page.data.settings,
        to_update=[button_preview]
    )

    return ft.View(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            AddGroupWidget(update_callback=update_list_controls),
                            reorderable_list,
                        ],
                        expand=True
                    ),
                    ft.VerticalDivider(),
                    ft.Column(
                        controls=[
                            max_time_to_choose,
                            time_between,
                            gaze_per_second,
                            button_size,
                            button_preview,
                            ft.Row(
                                controls=[
                                    ft.Button(content="Load CSV", on_click=lambda _: page.run_task(loadCSV, page)),
                                    ft.Button(content="Save To CSV", on_click=lambda _: page.run_task(saveExperienceToCSV, state)),
                                    ft.Button(content="Go Back", on_click=lambda _: page.run_task(page.push_route, "/WordExperiment"),
                                              ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY
                            )
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


def handle_size_change(e):
    e.control.height = e.page.window.height
    e.control.update()


@ft.control
class AddGroupWidget(ft.IconButton):
    def __init__(self, update_callback, **kwargs):
        self.update_callback = update_callback
        super().__init__(**kwargs)
        self.on_click = self.handle_click
        self.icon = ft.Icons.ADD_BOX
        self.icon_color = ft.Colors.BLUE

    def handle_click(self, e):
        self.page.data.word_groups.append(WordGroup())
        self.update_callback()


@ft.control
class RemoveGroupWidget(ft.IconButton):
    def __init__(self, group_index, update_callback, **kwargs):
        self.update_callback = update_callback
        self.group_index = group_index
        super().__init__(**kwargs)
        self.on_click = self.handle_click
        self.icon = ft.Icons.DELETE
        self.icon_color = ft.Colors.RED

    def handle_click(self, e):
        self.page.data.word_groups.pop(self.group_index)
        self.update_callback()


@ft.control
class CorrectAnswerDropdown(ft.Dropdown):

    def __init__(self, word_group: WordGroup, **kwargs):
        self.word_group = word_group
        super().__init__(**kwargs)

        self.options = [
            ft.DropdownOption(key=word, text=word)
            for word in self.word_group.words
        ]
        self.value: str = self.word_group.correct

        val = self.word_group.words.index(self.value)

        if val is not None:
            self.index = val
        else:
            self.index = -1

        self.on_select = self.handle_select

    def handle_select(self, e):
        self.word_group.correct = e.control.value
        self.index = self.word_group.words.index(e.control.value)

    def update_list(self):
        self.options = [
            ft.DropdownOption(key=word, text=word)
            for word in self.word_group.words
        ]
        self.value = self.word_group.words[self.index]
        self.word_group.correct = self.value


@ft.control
class SoundPicker(ft.Container):
    """Display the selected sound and allow replaying it."""

    def __init__(self, word_group: WordGroup, **kwargs):
        super().__init__(content=None, **kwargs)

        self.word_group = word_group
        self.buttons = [
            ft.Button(content=word_group.sound),
            ft.IconButton(
                icon=ft.Icons.PLAY_ARROW,
                icon_color=ft.Colors.BLUE,
                icon_size=40,
            ), ]
        self.content = ft.Row(
            controls=self.buttons
        )
        self.border = ft.Border.all(1, ft.Colors.GREY)
        self.border_radius = ft.BorderRadius.all(15)

        self.padding = ft.Padding.all(5)

    def build(self):
        self.buttons[0].on_click = lambda _: self.page.run_task(self.choose_sound)
        self.buttons[1].on_click = lambda _: self.page.run_task(self.play_sound)

    async def play_sound(self):
        await playSound(self.word_group.sound)

    def update_text(self):
        self.buttons[0].content = self.word_group.sound.split("/")[-1]
        self.update()

    async def choose_sound(self):
        file_path = await ft.FilePicker().pick_files(allow_multiple=False)

        if file_path:
            self.word_group.sound = file_path[0].path
        self.update_text()


@ft.control
class GroupCustomization(ft.Container):
    """Widget used to edit one WordGroup."""

    def __init__(self, group_index: int, word_group: WordGroup, update_callback, **kwargs):
        self.group_index: int = group_index
        self.word_group: WordGroup = word_group
        self.update_callback = update_callback

        super().__init__(**kwargs)

        self.expand = True
        self.padding = 10
        self.margin = ft.Margin.symmetric(vertical=2.5)
        self.border = ft.Border.all(3, ft.Colors.BLUE_ACCENT)
        self.border_radius = ft.BorderRadius.all(5)

        self.word_picker = WordPicker(on_word_change=self.update_correct_dropdown, word_group=self.word_group)
        self.sound_picker = SoundPicker(word_group=self.word_group)
        self.correct_answer_dropdown = CorrectAnswerDropdown(word_group=self.word_group)

        self.content = ft.Row(
            controls=[
                self.word_picker,
                ft.Column(
                    controls=[
                        self.sound_picker,
                        ft.Row(
                            controls=[
                                ft.Text("Correct Answer : "),
                                self.correct_answer_dropdown,

                            ]
                        )
                    ]
                ),
                ft.Column(controls=[
                    RemoveGroupWidget(group_index=group_index, update_callback=self.update_callback),
                    ft.ReorderableDragHandle(
                        content=ft.Icon(ft.Icons.DRAG_INDICATOR, color=ft.Colors.BLUE),
                        mouse_cursor=ft.MouseCursor.GRAB,
                    ),
                ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                )
            ],
            expand=1,
        )

    def update_correct_dropdown(self):
        self.correct_answer_dropdown.update_list()

    def remove_word_group(self):
        self.page.data.word_groups.remove(self.word_group)


@ft.control
class WordPicker(ft.Column):
    """Display a 2x2 editable grid for one WordGroup."""

    def __init__(self, on_word_change, word_group: WordGroup, **kwargs):
        super().__init__(controls=None, **kwargs)

        self.word_group = word_group

        self.expand = True
        self.validate_words()
        self.build_grid()
        self.on_word_change = on_word_change

    def validate_words(self):
        if len(self.word_group.words) != WORDS_PER_GROUP:
            raise ValueError(
                f"Each WordGroup must contain exactly {WORDS_PER_GROUP} words. "
                f"Received {len(self.word_group.words)}."
            )

    def build_grid(self):
        tiles = [
            DragTile(self.word_group.words[index], index, self.handle_swap, self.handle_change_word)
            for index, word in enumerate(self.word_group.words)
        ]

        self.controls = [
            ft.Row(controls=tiles[:2], expand=True),
            ft.Row(controls=tiles[2:4], expand=True),
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
        self.on_word_change()


@ft.control
class DragTile(ft.DragTarget):
    def __init__(self, word: str, index: int, on_swap, on_change, **kwargs):
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

        super().__init__(content=content, **kwargs)
        self.content = content
        self.on_accept = on_swap
        self.data = index
        self.expand = True


@ft.control
class AppSettingsWidget(ft.Container):
    """The widget used to modify any parameter in AppSettings. Store the reference of the AppSettings in his Data attribute."""

    def __init__(self, setting: AppSettingsEnum, value_picker: ft.Control, description: str, to_update: list[ft.Control] = [], **kwargs):
        self.setting = setting
        self.value_picker = value_picker
        self.description = description
        self.to_update = to_update

        super().__init__(**kwargs)

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
        if new_value == None:
            if new_value == "":
                new_value = 0.0
            else:
                new_value = float(e.control.value)
        self.value_picker.set_value(new_value)
        setattr(self.page.data.settings, self.setting.value, new_value)
        self.value_picker.update_shown()
        self.update()

        for ctrl in self.to_update:
            ctrl.update()


@ft.control
class NumberPicker(ft.Row):

    def __init__(self, step: float = 1.0, minimum: float = None, **kwargs):
        super().__init__(**kwargs)

        self.step = step
        self.minimum = minimum
        self.value = "0"

        self.text_field = ft.TextField(value=self.value,
                                       keyboard_type=ft.KeyboardType.NUMBER,
                                       input_filter=ft.InputFilter(allow=True, regex_string=r"^(\d+\.)?\d*$", replacement_string=""),
                                       expand_loose=True,
                                       text_align=ft.TextAlign.CENTER,
                                       )

        self.controls = [
            ft.IconButton(icon=ft.Icons.REMOVE, on_click=self.button_down),
            self.text_field,
            ft.IconButton(icon=ft.Icons.ADD, on_click=self.button_up),
        ]

        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def set_value_updater(self, method: Callable):
        self.text_field.on_change = method

    def button_up(self, e):
        new_val = float(self.value) + self.step
        if self.minimum is not None:
            if new_val < self.minimum:
                return
        self.text_field.on_change(e, new_val)

    def button_down(self, e):
        new_val = float(self.value) - self.step
        if self.minimum is not None:
            if new_val < self.minimum:
                return
        self.text_field.on_change(e, new_val)

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

    def set_value_updater(self, method: Callable):
        self.slider.on_change = method
        self.text_field.on_change = method

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = 0.0

        self.built = False
        self.slider = ft.Slider(value=self.value)
        self.text_field = ft.TextField(value=str(self.value),
                                       keyboard_type=ft.KeyboardType.NUMBER,
                                       input_filter=ft.InputFilter(allow=True, regex_string=r"^(\d+\.)?\d*$", replacement_string=""),
                                       expand_loose=True,
                                       width=100,
                                       text_align=ft.TextAlign.CENTER,
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
            self.parent.update()


@ft.control
class ButtonSizePreview(ft.Container):

    def __init__(self, size: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.size = size

        self.aspect_ratio = 16 / 9
        self.buttons = [
            ft.Container(
                content=ft.Button(content=content),
                expand=1,
                alignment=ft.Alignment.CENTER,
            )
            for content in ["A", "B", "C", "D"]
        ]

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=self.buttons[:2],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
                ft.Row(
                    controls=self.buttons[2:4],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.expand = True
        self.on_size_change = self.handle_resize
        self.border = ft.Border.all(2, ft.Colors.GREY)

    def before_update(self) -> None:
        self.resize_buttons()

    def resize_buttons(self):
        self.size = self.page.data.settings.buttons_size

        for button in self.buttons:
            button.content.width = max((self.width or 1920) / 2, 200) * self.size * 0.95
            button.content.height = max((self.height or 1080) / 2, 140) * self.size * 0.95

    def handle_resize(self, e):
        self.width = e.width
        self.height = e.height
