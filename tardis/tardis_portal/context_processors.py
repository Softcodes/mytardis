from django.conf import settings
from tardis.tardis_portal.staging import get_full_staging_path

def single_search_processor(request):

    context = {}
    single_search_on = False
    try:
        if settings.SINGLE_SEARCH_ENABLED:
            single_search_on = True
    except AttributeError:
        pass

    context =  {
	    'search_form': single_search_on,
    }

    return context

def tokenuser_processor(request):
    is_token_user = request.user.username == settings.TOKEN_USERNAME
    return {'is_token_user': is_token_user}

def registration_processor(request):
    def is_registration_enabled():
        try:
            if 'registration' in settings.INSTALLED_APPS:
                return getattr(settings, 'REGISTRATION_OPEN', True)
        except AttributeError:
            pass
        return False
    return {'registration_enabled': is_registration_enabled()}

def user_details_processor(request):
    is_authenticated = request.user.is_authenticated()
    if is_authenticated:
        is_superuser = request.user.is_superuser
        username = request.user.username
    else:
        is_superuser = False
        username = None
    staging = True if get_full_staging_path(username) else False
    return {'username': username,
            'is_authenticated': is_authenticated,
            'is_superuser': is_superuser, 
            'has_staging_access': staging}
