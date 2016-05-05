class LoginRequired(Exception):
    """
    Exception class for views to use to tell LoginRequiredMiddleware to require login
    """
    pass

