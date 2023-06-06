# coding=utf-8
from django.core.management.base import AppCommand

from core.utils import camel_case_to_dash


class Command(AppCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--tmp", action="store_true", help="Add tmp prefix")

    def handle_app_config(self, app_config, **options):
        postfix = ".tmp" if options["tmp"] else ""

        print(f"Creating views.py, urls.py, wagtail_hooks.py and serializers.py in app {app_config.label}.")

        hook_import_code = f"""from wagtail.contrib.modeladmin.options import ModelAdminGroup, ModelAdmin, modeladmin_register
from wagtail.core import hooks
from .models import {', '.join([model.__name__ for model in app_config.get_models()])}"""
        hooks_code = """
@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/ice-cream.svg',
    ]


"""

        serializer_import_code = "from rest_framework import serializers\n"
        serializer_code = ""

        views_import_code = "from rest_framework.viewsets import ModelViewSet\n"
        views_code = ""

        urls_import_code = "from rest_framework.routers import SimpleRouter\n"
        urls_code = "router = SimpleRouter(trailing_slash=True)\n"

        for model in app_config.get_models():
            fields = [f"'{f.name}'" for f in model._meta.fields]

            serializer_import_code += f"from .models import {model.__name__}\n"
            serializer_code += f"""class {model.__name__}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model.__name__}
        fields = ({', '.join(fields)})


"""

            views_import_code += f"from .serializers import {model.__name__}Serializer\n"
            views_import_code += f"from .models import {model.__name__}\n"

            views_code += f"""class {model.__name__}ViewSet(ModelViewSet):
    serializer_class = {model.__name__}Serializer

    def get_queryset(self):
        return {model.__name__}.objects.all()


"""
            hooks_code += f"""class {model.__name__}Admin(ModelAdmin):
    model = {model.__name__}
    menu_label = '{model.__name__}s'
    menu_icon = 'ice-cream'
    list_display = ('id',)
    search_fields = ('id',)


"""

            urls_import_code += f"from .views import {model.__name__}ViewSet\n"
            path = camel_case_to_dash(model.__name__)
            url_name = f'{app_config.name.replace("_", "-")}-{path}'
            urls_code += f"router.register(r'{path}s', {model.__name__}ViewSet, '{url_name}')\n"
        urls_code += "\nurlpatterns = router.urls\n"

        hooks_code += f"""class {app_config.name.capitalize()}Group(ModelAdminGroup):
    menu_label = '{app_config.name.capitalize()}'
    menu_icon = 'ice-cream'
    menu_order = 200
    items = ({', '.join([model.__name__ + 'Admin' for model in app_config.get_models()])})


modeladmin_register({app_config.name.capitalize()}Group)
"""

        with open(f"{app_config.path}/serializers{postfix}.py", "w") as f:
            f.write(serializer_import_code + "\n\n" + serializer_code)

        with open(f"{app_config.path}/views{postfix}.py", "w") as f:
            f.write(views_import_code + "\n\n" + views_code)

        with open(f"{app_config.path}/urls{postfix}.py", "w") as f:
            f.write(urls_import_code + "\n\n" + urls_code)

        with open(f"{app_config.path}/wagtail_hooks{postfix}.py", "w") as f:
            f.write(hook_import_code + "\n\n" + hooks_code)