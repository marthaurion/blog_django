from django.conf import settings

def show_toolbar(request):
    if request.is_ajax():
        return False

    return bool(settings.DEBUG)