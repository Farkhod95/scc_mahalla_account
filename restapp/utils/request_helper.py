from restapp.middlewares.middlewares import RequestMiddleware


def get_user():
    try:
        request = RequestMiddleware(get_response=None)
        request = request.thread_local.current_request
        return request.user
    finally:
        return None


def get_request():
    request = RequestMiddleware(get_response=None)
    request = request.thread_local.current_request
    return request
