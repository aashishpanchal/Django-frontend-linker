import os
from django.core.management.base import BaseCommand
from frontlink.management.exceptions import DirDoesNotExist
from frontlink.management.text_styles import style_info, style_error, style_warning
from frontlink.management.base import frontbuild


class Command(BaseCommand):
    help = "This command will django link frontend"
    template_suffix = (".html", ".htm", ".xhtml")
    static_outer_file = ('media',)

    def add_arguments(self, parser):
        parser.add_argument('--dir', '-d', type=str,
                            required=True, help='location of build directory')
        parser.add_argument('--build-name', '--b-n', type=str,
                            default='build', help='The build directory name')
        parser.add_argument('--clear', '--c', action='store_true', default=False, help='clear the build directory')

    def handle(self, *args, **options):
        target = options.get('dir')
        build_name = options.get('build_name')

        if os.path.isdir(target):
            root = os.path.abspath(path=target)
            self.stdout.write("%s: %s" % (style_info("Root Directory"), root))
            build_dir = os.path.join(root, build_name)
            if not os.path.isdir(build_dir):
                raise DirDoesNotExist("%s directory does not exist in %s" % (
                    style_warning(build_name), style_warning(root)))
        else:
            raise DirDoesNotExist("Target directory does not exist")
        self.stdout.write("Build Status:")
        kwargs = {**options, 'stdout': self.stdout}
        frontbuild(build_dir, self.template_suffix, **
                   kwargs).run(build_name=build_name)
