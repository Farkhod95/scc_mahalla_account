from django.http import HttpResponse, JsonResponse

def custom_404(request, exception=None):
    """
    DEBUG=True bo‘lsa ham, Django default debug 404 sahifasini ko‘rsatmaydi.
    API so‘rovlar uchun JSON qaytaradi, brauzer uchun oddiy matn.
    """
    accepts_json = (
        request.path.startswith("/api/") or
        request.headers.get("Accept", "").lower().find("application/json") != -1
    )

    if accepts_json:
        return JsonResponse({"detail": "Not Found"}, status=404)

    return HttpResponse("Not Found", status=404, content_type="text/plain; charset=utf-8")
