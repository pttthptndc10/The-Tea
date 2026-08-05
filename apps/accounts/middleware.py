class NoCacheAuthenticatedMiddleware:
    """
    Middleware to ensure authenticated pages are never cached by the browser.
    This guarantees that closing a tab or navigating back will force the browser
    to re-verify session state with the server rather than loading a cached page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
