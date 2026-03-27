from django.apps import AppConfig


class ProjectbranchConfig(AppConfig):
    name = 'projectbranch'

    def ready(self):
        import projectbranch.signals
