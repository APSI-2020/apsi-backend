from django.http import JsonResponse
from users.users_service import UsersService


def get_events(request):
    jwt = request.headers['Authorization']
    users_service = UsersService()
    user_id = users_service.findUserBasedOnJwt(jwt)
    # 2. Find events available for given user with respect to given filters

    # 3. Find for which events user is signed up
    # 4. Find requirements for each events
    # 5. Filter events based on requirements
    # 6. Transform events to DTOs
    # 7. Return DTOs
    return JsonResponse(dict(response="hello"))
