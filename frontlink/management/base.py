import os
import sys
import shutil
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.validators import URLValidator
from django.core.management.base import OutputWrapper
from frontlink.management.text_styles import *
from frontlink.conf import WarningMessage, STATIC_NAME


class Base:
    helptext = HelpTextMixin()

    def __init__(self, build_dir, template_suffix=(".html", ".htm", ".xhtml"), **kwargs):
        self.build_dir = build_dir
        self.template_suffix = template_suffix
        self.BASE_DIR = kwargs.get('BASE_DIR', settings.BASE_DIR)
        self.stdout = kwargs.get('stdout', OutputWrapper(sys.stdout))
        self._kwargs = kwargs

    def get_kwargs_value(self, key, default=None):
        return self._kwargs.get(key, default)

    def get_kwargs(self):
        return self._kwargs.copy()

    def checker(self, filename):
        return filename.endswith(self.template_suffix)

    def path_rest(self, build_dir, root_path, new_build_dir):
        """This method will return the rest of the path"""
        rest_path = root_path[len(build_dir)+1:]
        if rest_path:
            os.makedirs(os.path.join(new_build_dir, rest_path), exist_ok=True)
        return rest_path

    def run(self, **kwargs):
        """This method will be called when the command is executed"""
        pass


class StaticMixin:
    def isUrl(self, text):
        validator = URLValidator()
        try:
            validator(text)
            return True
        except:
            return False


class StaticLinkerMixin:
    def inspect_parser(self, tag, attrs):
        for x in self.soup.find_all(tag):
            if x.get(attrs) and not self.isUrl(x.get(attrs)):
                self.stdout.write("Link Apply: %s .... %s" % (
                    style_warning(x.get(attrs)), style_info("OK")))
                x[attrs] = "{% static \"" + x[attrs] + "\" %}"
            else:
                self.stdout.write("Link not Apply: %s .... %s" % (
                    style_warning(x.get(attrs)), style_error("FAILED")))


class FrontBuilder(Base, StaticMixin, StaticLinkerMixin):
    def run(self, **kwargs):
        self.helptext.add_helptext("Information:", color=style_info)
        build_name = kwargs.get('build_name', 'build')
        template_dir, static_dir = self.create_dirs(self.BASE_DIR, build_name)
        for root, dirs, files in os.walk(self.build_dir):

            rest_path = self.path_rest(self.build_dir, root, static_dir)

            for filename in files:
                if self.checker(filename):
                    self.stdout.write("%s: %s" % (style_info(
                        "Template File"), style_bwarn(filename)))
                    old_template_file_path = os.path.join(root, filename)
                    new_template_file_path = os.path.join(
                        template_dir, filename)
                    self.soup = BeautifulSoup(
                        open(old_template_file_path), "html.parser")
                    self.soup.insert(0, '{% load static %}')
                    self.inspect_parser('link', 'href')
                    self.inspect_parser('script', 'src')
                    with open(new_template_file_path, 'wb') as f:
                        text = self.soup.prettify()
                        f.write(self.add_indent(text, 2).encode('utf-8'))
                else:
                    old_static_file_path = os.path.join(root, filename)
                    new_static_file_path = os.path.join(
                        static_dir, rest_path, filename)
                    shutil.copyfile(old_static_file_path, new_static_file_path)
                    try:
                        # copy permission bits (mode)
                        shutil.copymode(old_static_file_path,
                                        new_static_file_path)
                    except OSError:
                        self.stderr.write(
                            "Notice: Couldn't set permission bits on %s. You're "
                            "probably using an uncommon filesystem setup. No "
                            "problem." % new_static_file_path, style_info)
        self.stdout.write("successfully linked", style_info)
        # add some warnings
        if STATIC_NAME != static_dir.replace(str(self.BASE_DIR) + "\\", ""):
            self.inner_warn(static_dir=static_dir)
        self.stdout.write(self.helptext.get_helptext())

    def add_indent(self, text, n):
        """
        This method will add indent to the Template(html, XHTML, XML)
        """
        sp = " "*n
        lsep = chr(10) if text.find(chr(13)) == -1 else chr(13)+chr(10)
        lines = text.split(lsep)
        for i in range(len(lines)):
            spacediff = len(lines[i]) - len(lines[i].lstrip())
            if spacediff:
                lines[i] = sp*spacediff + lines[i]
        return lsep.join(lines)

    def create_dirs(self, path, build_name):
        template_dir = os.path.join(path, '%s_templates' % build_name)
        static_dir = os.path.join(path, '%s_staticfiles' % build_name)
        if self.get_kwargs_value('clear'):
            self.clear_dir(template_dir)
            self.clear_dir(static_dir)
        self.helptext.add_helptext("Template Directory: %s" % style_bwarn(
            template_dir), indent=4, linegap=1)
        self.helptext.add_helptext(
            "Static Directory:   %s" % style_bwarn(static_dir), indent=4, linegap=1)

        dirs = (template_dir, static_dir)

        for dirname in dirs:
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
        return dirs

    def clear_dir(self, path):
        if os.path.isdir(path):
            self.stdout.write("WARNING: you can lost previous data", style_warning)
            self.stdout.write("(y/n) default(y): ", ending="")
            try:
                x=input() or "y"
            except KeyboardInterrupt:
                sys.exit()
            if x.lower() == 'y':
                shutil.rmtree(path)
            else:
                sys.exit()

    def inner_warn(self, **kwargs):
        """other warnings"""
        self.helptext.add_helptext("Warning:", color=style_warning, linegap=1)
        if kwargs.get('static_dir'):
            self.helptext.add_helptext(
                WarningMessage % kwargs['static_dir'].replace(
                    str(self.BASE_DIR) + "\\", ""),
                newline=False,
                color=style_bwarn
            )


def frontbuild(build_dir, template_suffix, **kwargs):
    """
    This function is return the FrontBuilder object
    """
    return FrontBuilder(build_dir, template_suffix, **kwargs)
