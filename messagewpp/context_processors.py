def admins_context(request):
    return {'admins': request.user} if request.user.is_authenticated else {}
