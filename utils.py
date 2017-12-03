from kivy.core.text import LabelBase

from config import KIVY_FONTS

for font in KIVY_FONTS:
    LabelBase.register(**font)
