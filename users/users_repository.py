from .models import Users, UsersGroups


class UsersRepository:
    def __init__(self):
        pass

    def find_by_id_or_fail(self, user_id):
        return Users.objects.get(id=user_id)


class UsersGroupRepository:

    @staticmethod
    def get_all_users_groups():
        return UsersGroups.objects.all()
