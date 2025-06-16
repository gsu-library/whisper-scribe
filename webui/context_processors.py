from .utils import get_version


# Function webui
def webui(request):
   version = get_version()
   return { 'version': version }
