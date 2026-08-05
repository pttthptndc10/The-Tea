def auth_session_context_processor(request):
    """
    Context processor to pass `just_logged_in` flag to templates.
    Ensures `just_logged_in` is evaluated as True ONLY on the first request after login,
    and explicitly marks request.session as modified so the flag is immediately cleared.
    """
    just_logged_in = False
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.session.get('just_logged_in'):
            just_logged_in = True
            request.session['just_logged_in'] = False
            request.session.modified = True
    return {
        'just_logged_in': just_logged_in
    }
