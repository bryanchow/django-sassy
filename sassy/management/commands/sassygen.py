import os, commands, optparse
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):

    help = "Generate CSS from Sass"
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            '--style',
            '-t',
            dest = 'css_style',
            default = getattr(settings, 'SASSY_CSS_STYLE', 'nested'),
            help = "Output style. Can be nested (default), compact, compressed, or expanded."
        ),
    )
    requires_model_validation = False

    def handle(self, *args, **kwargs):

        css_style = kwargs.get('css_style')
        if css_style not in ('nested', 'compact', 'compressed', 'expanded'):
            raise CommandError("Invalid output style: %s" % css_style)

        resources = getattr(settings, 'SASSY_RESOURCES')
        if not resources:
            raise CommandError("Missing SASSY_RESOURCES setting.")

        for key in resources:
            source_path = os.path.join(settings.MEDIA_ROOT, resources[key]['source'])
            output_path = os.path.join(settings.MEDIA_ROOT, resources[key]['output'])
            self.generate_css(source_path, output_path, css_style)
            print "%s -> %s" % (source_path, output_path)

    def generate_css(self, source_path, output_path, css_style):

        cmd = '%(sass_bin)s -t %(css_style)s --no-cache %(source_path)s %(output_path)s' % {
            'sass_bin': getattr(settings, 'SASSY_SASS_BIN', 'sass'),
            'css_style': css_style,
            'source_path': source_path,
            'output_path': output_path,
        }
        (status, output) = commands.getstatusoutput(cmd)
        if not status == 0:
            raise CommandError(output)
