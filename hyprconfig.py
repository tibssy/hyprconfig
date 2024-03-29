import flet as ft
from flet_color_selector import ColorSelector, RoundedElevatedButton
import json
import time


class OptionControl(ft.UserControl):
    def __init__(self, name=None, description=None):
        super().__init__()
        self.name = ft.Text(name)
        self.description = ft.Text(description)
        self.title = ft.Text(self.get_title())

    def get_title(self):
        return self.name.value.replace('_', ' ').replace('.', ' ').title()

    def on_value_change(self, current_value, default_value):
        if current_value != default_value:
            self.page.session.set(self.name.value, current_value)

        elif self.page.session.get(self.name.value) is not None:
            self.page.session.remove(self.name.value)


class OptionSwitch(OptionControl):
    def __init__(self, name=None, description=None, value=True):
        super().__init__(name, description)
        self.value = value

    def build(self):
        control = ft.Switch(value=self.value, on_change=self.on_switch)
        return ft.CupertinoListTile(title=self.title, subtitle=self.description, trailing=control, notched=True)

    def on_switch(self, e):
        self.on_value_change(e.control.value, self.value)


class OptionSlider(OptionControl):
    def __init__(self, name=None, description=None, value=0.0, min_value=0.0, max_value=10.0):
        super().__init__(name, description)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = ft.Text(f'{self.value:.2f}')

    def build(self):
        control = ft.Slider(value=self.value, min=self.min_value, max=self.max_value, on_change=self.on_slide)
        return ft.CupertinoListTile(title=self.title, subtitle=self.description, additional_info=self.current_value, trailing=control, notched=True)

    def on_slide(self, e):
        self.current_value.value = f'{e.control.value:.2f}'
        self.update()
        self.on_value_change(e.control.value, self.value)


class OptionCounter(OptionControl):
    def __init__(self, name=None, description=None, value=0):
        super().__init__(name, description)
        self.value = value
        self.txt_number = ft.TextField(value=f'{value}', text_align=ft.TextAlign.CENTER, width=100, scale=0.9, content_padding=ft.padding.symmetric(horizontal=5, vertical=0))

    def build(self):
        control = ft.Row(
            controls=[
                ft.IconButton(ft.icons.REMOVE, on_click=lambda e: self.change_value(-1)),
                self.txt_number,
                ft.IconButton(ft.icons.ADD, on_click=lambda e: self.change_value(1))
            ]
        )
        return ft.CupertinoListTile(title=self.title, subtitle=self.description, trailing=control, notched=True)

    def change_value(self, value):
        self.txt_number.value = f'{int(self.txt_number.value) + value}'
        self.update()
        self.on_value_change(int(self.txt_number.value), self.value)


class OptionColorPicker(OptionControl):
    def __init__(self, name=None, description=None, value=None):
        super().__init__(name, description)
        self.value = value
        self.color_button = None

    def build(self):
        color_selector = ColorSelector(on_color=self.on_color_change)
        color = f'#{self.value[-6:]}' if self.value != 'unset' else '#000000'
        self.color_button = RoundedElevatedButton(bgcolor=color, radius=6, scale=0.9, on_click=color_selector.open_dialog)
        return ft.CupertinoListTile(title=self.title, subtitle=self.description, trailing=self.color_button, notched=True)

    def on_color_change(self, color):
        self.on_value_change(color, f'#{self.value[-6:]}')


def get_options():
    with open('options_v0.37.0.json', encoding='utf-8') as options_file:
        return json.load(options_file)


def switch_theme(page):
    page.splash.visible = True
    themes = {'light': ('dark', 'light_mode'), 'dark': ('light', 'dark_mode')}
    page.theme_mode, page.appbar.actions[0].icon = themes[page.theme_mode]
    page.update()
    time.sleep(0.5)
    page.splash.visible = False
    page.update()


def get_range(text):
    left = text.rfind('[')
    if left != -1:
        range_text = text[left + 1:text.rfind(']')]
        if range_text:
            min_value, max_value = range_text.split('-')
            return float(min_value.strip()), float(max_value.strip())
    return 0.0, 1.0


def generate_row(option):
    title = option['name']
    description = option['description']
    value_type = option['type']
    if value_type == 'bool':
        default_value = option['default'].lower() in ['true', 'yes', '1']
        return OptionSwitch(name=title, description=description, value=default_value)
    elif value_type == 'float':
        default_value = float(option['default'])
        minimum_value, maximum_value = get_range(description)
        return OptionSlider(name=title, description=description, value=default_value, min_value=minimum_value, max_value=maximum_value)
    elif value_type == 'int':
        default_value = int(option['default'])
        return OptionCounter(name=title, description=description, value=default_value)
    elif value_type == 'color':
        default_value = option['default'] if option['default'] != 'unset' else 'FFFFFF'
        return OptionColorPicker(name=title, description=description, value=default_value)
    elif value_type == 'gradient':
        default_value = option['default'] if option['default'] != 'unset' else 'FFFFFF'
        return OptionColorPicker(name=title, description=description, value=default_value)
    else:
        return ft.CupertinoListTile(title=ft.Text(title), subtitle=ft.Text(description), notched=True)


def generate_tab(args):
    tab_name, tab_page = args
    icon_name = tab_page.get('icon')
    sub_categories = tab_page.get('sub_categories')
    options = tab_page.get('options')
    list_view_content = list(map(generate_row, options))
    if sub_categories:
        for sub_category in sub_categories.items():
            sub_category_name, sub_category_content = sub_category
            container = [ft.Text(f'{sub_category_name.capitalize()}:', size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.JUSTIFY)]
            container.extend(map(generate_row, sub_category_content))
            card = ft.Card(elevation=5, margin=10, content=ft.Container(content=ft.Column(container), padding=10))
            list_view_content.append(card)

    list_view = ft.ListView(divider_thickness=1, expand=1, spacing=10, padding=20, horizontal=False, auto_scroll=False, controls=list_view_content)
    return ft.Tab(icon=icon_name, text=f'{tab_name.capitalize()}', content=list_view)


def get_session_storage(page):
    print(page.session.get_keys())
    for key in page.session.get_keys():
        print(f'{key}: {page.session.get(key)}')


def main(page: ft.Page):
    categories = get_options()
    page.theme_mode = 'dark'
    # page.window_opacity = 0.8
    page.theme = ft.theme.Theme(color_scheme_seed='#6CC6F8')
    page.window_frameless = True
    page.splash = ft.ProgressBar(visible=False)
    page.appbar = ft.AppBar(title=ft.Text(f'Hyprland Control Center'), toolbar_height=45)
    page.appbar.actions = [
        ft.IconButton(icon='light_mode', on_click=lambda e: switch_theme(page)),
        ft.CupertinoButton(content=ft.Text('Save'), bgcolor=page.theme.color_scheme_seed, scale=0.8, border_radius=ft.border_radius.all(10),  on_click=lambda e: get_session_storage(page))
    ]
    tabs = map(generate_tab, categories.items())
    page.add(ft.Tabs(animation_duration=300, tabs=list(tabs), expand=1, indicator_tab_size=True))


ft.app(target=main)
