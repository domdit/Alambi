from flask import current_app
from alambi.models import Theme
from PIL import Image
import os

def img_uploader(data):

    _, f_ext = os.path.splitext(data.filename)

    if f_ext != ".png":
        f_ext = ".png"
    else:
        pass

    picture_fn = 'sidebar' + f_ext


    folder = os.path.join(current_app.root_path, 'static/sidebar/')

    picture_path = os.path.join(folder, picture_fn)

    if os.path.isfile(picture_path):
        os.remove(picture_path)

    i = Image.open(data)

    return i.save(picture_path)


class ThemeName:

    def __init__(self):
        self.one = Theme.query.get_or_404(1)
        self.two = Theme.query.get_or_404(2)
        self.three = Theme.query.get_or_404(3)
        self.four = Theme.query.get_or_404(4)
        self.five = Theme.query.get_or_404(5)
        self.six = Theme.query.get_or_404(6)
        self.seven = Theme.query.get_or_404(7)
        self.eight = Theme.query.get_or_404(8)

