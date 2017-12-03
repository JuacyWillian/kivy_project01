import os

basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.path.join(basedir, 'database.db')

FONTS = [
    # {
    #     "name": "",
    #     "fn_regular": "data/fonts/.ttf",
    #     "fn_bold": "data/fonts/.ttf",
    #     "fn_italic": "data/fonts/.ttf",
    #     "fn_bolditalic": "data/fonts/.ttf"
    # },
]

ICON_FONTS = [
    {
        'name': "fontawesome",
        'ttf_fname': "data/fonts/FontAwesome-webfont.ttf",
        'css_fname': "data/fonts/font-awesome.css",
        'fontd_fname': "data/fonts/FontAwesome-webfont.fontd",
        'output_fname': "data/fonts/FontAwesome-webfont.fontd"
    },
]

DEFAULT_FONT_NAME = ''
DEFAULT_ICON_FONT_NAME = ICON_FONTS[0]['name']
