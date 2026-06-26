from django.http import HttpResponse, JsonResponse


class SimpleNotFoundMiddleware:
    """
    DEBUG=True bo‘lsa ham 404 sahifada URL patterns ro'yxatini chiqarishni to'xtatadi.
    Har qanday 404 response'ni oddiy 'Not Found' (yoki JSON) ga almashtiradi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # ✅ 404 bo'lsa — qanday holat bo'lishidan qat'i nazar soddalashtiramiz
        if getattr(response, "status_code", None) == 404:
            wants_json = (
                request.path.startswith("/api/") or
                "application/json" in (request.headers.get("Accept", "").lower())
            )

            if wants_json:
                return JsonResponse({"detail": "Not Found"}, status=404)

            return HttpResponse("Not Found", status=404, content_type="text/plain; charset=utf-8")

        return response
