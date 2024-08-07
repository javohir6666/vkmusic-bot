from asgiref.sync import sync_to_async
from users.models import CustomUser
@sync_to_async
def get_user(user_id):
    return CustomUser.objects.get(telegram_id=user_id)