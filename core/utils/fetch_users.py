from core.utils.RestHandler import RestHandler

rest = RestHandler()


async def fetch_users(role: str = "support") -> list[str]:
    users_dict: list[dict] = await rest.post(f"v1/auth/find/", {
        "role": role
    })
    return [user.get("telegram_id") for user in users_dict]
