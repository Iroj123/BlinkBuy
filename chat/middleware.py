import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract token from query string: ?token=abc.def.ghi
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")

        if token:
            try:
                payload = jwt.decode(token[0], settings.SECRET_KEY, algorithms=["HS256"])
                user = await get_user(payload["user_id"])
                scope["user"] = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
                scope["user"] = None
        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)
