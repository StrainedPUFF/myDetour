from django.http import HttpResponseRedirect

class RootRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/":  # Root URL
            return HttpResponseRedirect('/home_view/')  # Redirect to Django's primary view
        return self.get_response(request)
