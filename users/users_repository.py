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

    @staticmethod
    def find_guest_user_group_or_fail():
        return UsersGroups.objects.get(name='Guest')


class LecturerRepository:

    @staticmethod
    def get_all_lecturers():
        return Users.objects.filter(groups__name='Lecturer')
