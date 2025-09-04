from .utils import get_version


def webui(request):
   """
   Context processor for the web UI. This function provides context data to templates
   rendered in the web UI.

   Returns:
      dict: A dictionary containing the application version under the key 'version'.
   """
   version = get_version()
   return { 'version': version }
