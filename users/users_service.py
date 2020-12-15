from .users_repository import UsersRepository
from django.conf import settings
import jwt


class UsersService:
    def __init__(self):
        self.user_repository = UsersRepository()

    def fetch_by_jwt(self, token):
        token_begins_at = len(settings.SIMPLE_JWT['AUTH_HEADER_TYPES'][0]) + 1
        extracted_token = token[token_begins_at:]
        decoded = jwt.decode(extracted_token, settings.SECRET_KEY)
        user_id = decoded['user_id']

        return self.user_repository.find_by_id_or_fail(user_id)

