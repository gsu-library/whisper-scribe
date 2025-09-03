from .utils import get_version


def webui(request):
   """
   Create a context processor for the project. Provides the current version of the
   application.
   """
   version = get_version()
   return { 'version': version }
