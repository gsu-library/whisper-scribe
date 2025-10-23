from django.apps import AppConfig
from django.core.cache import cache
from django.db.models.signals import post_migrate


class WebuiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webui'

    def ready(self):
        post_migrate.connect(self.clear_cache, sender=self)

    def clear_cache(self, sender, **kwargs):
        """
        Clears the cache on app start.
        """
        try:
            cache.clear()
        except:
            print('Error clearing cache.')
