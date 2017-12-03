from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

from config import FONTS, ICON_FONTS, DEFAULT_FONT_NAME, DEFAULT_ICON_FONT_NAME
from iconfonts import create_fontdict_file, register_iconfont, icon
from models import Job

kv_string = '''
#:import icon iconfonts.icon

<ActionItem>:
    markup: True

<MenuBar@RelativeLayout>:
    size_hint_x: None
    width: dp(240)
    pos: 0 - self.width if self.hide else 0, 0
    hide: False

    canvas.before:
        Color: 
            rgba: .1, .1, .1, 1
        Rectangle:
            size: self.size
            pos: self.pos


<MenuButton@Button>:
    size_hint_y: None
    height: dp(50)
    halign: 'left'
    text_size: (200, None)
    markup: True
    background_color: [.3, .3, .3, .8]


<MenuLabel@Label>:
    markup: True
    color: [.6, .6, .6, 1]
    # text_size: (None, dp(24))
    size_hint: 1, None
    height: dp(50)
    
<HomeScreen>:
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1,1,1,1
                
            Rectangle:
                pos: self.pos
                size: self.size
        RecycleView:
            id: rv
            viewclass: 'Label'
            scroll_type: ['bars', 'content']
            scroll_wheel_distance: dp(114)
            bar_width: dp(10)
            data: root.data
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(2)

BoxLayout:
    orientation: 'vertical'

    ActionBar:
        pos_hint: {'top':1}
        background_image: ''
        background_color: [.1, .1, .1, 1]

        ActionView:
            use_separator: False
            ActionPrevious:
                app_icon: ''
                title: 'Working At Home'
                with_previous: False

            ActionOverflow:
            ActionButton:
                text: '%s'%icon('fa-bars')
                on_release: app.toggle_menubar()


    PageLayout:
        id: sidebar
        border: dp(2)
        
        FloatLayout:
            MenuBar:
                BoxLayout:
                    orientation: 'vertical'
                    pos: 0,0
                    MenuButton:
                        text: '%s Home'%icon('fa-home')
                        on_release: app.goto_screen('home')
    
                    MenuButton:
                        text: '%s Jobs'%icon('fa-tasks')
                        on_release: app.goto_screen('list')
    
                    MenuButton:
                        text: '%s Settings'%icon('fa-cogs')
                        on_release: app.goto_screen('settings')
    
                    MenuButton:
                        text: '%s Quit'%icon('fa-power-off')
                        on_release: app.stop()
    
                    FloatLayout:
                    MenuLabel:
                        text: '%s juacywillian@yahoo.com'%icon('fa-envelope-o')
                        font_size: sp(12)
                FloatLayout:
                    
        ScreenManager:
            id: scrmngr
            pos: 0, 0
            HomeScreen:
                name: 'home'
                
            Screen:
                name: 'list'
                Button:
                    text: 'list'
                    on_release: print('list')
            Screen:
                name: 'settings'
                Button:
                    text: 'settings'
                    on_release: print('settings')
'''

class RVLabel(Label):
    def __init__(self, **kwargs):
        super(RVLabel, self).__init__(**kwargs)
        self.color = [0, 0, 0, 1]
        self.halign = 'left'



class HomeScreen(Screen):
    data = None

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.data = [
            {'text': '%s %s' % (icon('fa-sticky-note-o'), job.name), 'classview': 'RVLabel'}
            for job in Job.select().order_by(Job.name)]


class WorkingAtHome2(App):
    """
    todo
    """
    default_font = StringProperty(DEFAULT_FONT_NAME)
    default_iconfont = StringProperty(DEFAULT_ICON_FONT_NAME)

    def __init__(self, **kwargs):
        super(WorkingAtHome2, self).__init__(**kwargs)
        self.register_fonts()

    def register_fonts(self):
        for font in FONTS:
            LabelBase.register(**font)

        for iconfont in ICON_FONTS:
            create_fontdict_file(**iconfont)
            register_iconfont(**iconfont)

    def toggle_menubar(self):
        pl = self.root.ids.sidebar
        pl.page = 1 if pl.page == 0 else 0

    def goto_screen(self, name):
        app = App.get_running_app()
        app.root.ids.scrmngr.current = name
        self.toggle_menubar()

    def build(self):
        return Builder.load_string(kv_string)


if __name__ == '__main__':
    WorkingAtHome2().run()
