from django.utils.termcolors import make_style

style_info = make_style(fg='green', opts=('bold',))
style_warning = make_style(fg='yellow', opts=('bold',))
style_error = make_style(fg='red', opts=('bold',))
style_bwarn = make_style(fg='blue', opts=('bold',))


class HelpTextMixin:
    def __init__(self, helptext=""):
        self._helptext = helptext

    def get_helptext(self):
        return self._helptext

    def add_helptext(self, helptext, newline=True, indent=0, color=lambda x: x, linegap=0):
        if newline:
            self._helptext += "\n"
        self._helptext += (linegap * "\n")
        self._helptext += indent * " " + color(helptext)
