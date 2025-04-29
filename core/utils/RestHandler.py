import aiohttp
from aiogram import Bot

from core.settings import settings


class RestHandler:
    def __init__(self, bot: Bot = None):
        self.bot = bot
        self.basic_url = settings.bots.api_path
        self.basic_headers = {
            'Content-Type': 'application/json',
        }

    async def _refresh_token(self, state):
        data = await state.get_data()
        refresh = data.get("user", {}).get("refresh")
        if not refresh:
            raise Exception("🔒 Refresh токен не найден")

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.basic_url}v1/auth/token/refresh/", json={"refresh": refresh}) as resp:
                if resp.status != 200:
                    raise Exception("🔒 Не удалось обновить токен")
                new_token = await resp.json()
                access = new_token.get("access")
                if access:
                    await state.update_data(token=access)
                    return access
                raise Exception("🔒 Новый access токен не получен")

    async def _request(self, method, url, data=None, params=None, state=None):
        from aiogram.fsm.context import FSMContext  # импорт здесь, чтобы не циклилось

        data = data or {}
        headers = self.basic_headers.copy()
        if state:
            state_data = await state.get_data()
            token = state_data.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"

        async with aiohttp.ClientSession() as session:
            req = getattr(session, method)
            async with req(self.basic_url + url, json=data, params=params, headers=headers) as resp:
                if resp.status == 401 and state:
                    # пробуем обновить токен
                    new_token = await self._refresh_token(state)
                    headers["Authorization"] = f"Bearer {new_token}"
                    async with req(self.basic_url + url, json=data, params=params, headers=headers) as retry_resp:
                        return await retry_resp.json()
                return await resp.json()

    async def get(self, url: str, params: dict = None, state=None):
        return await self._request("get", url, params=params, state=state)

    async def post(self, url: str, data: dict = None, state=None):
        return await self._request("post", url, data=data, state=state)

    async def update(self, url: str, data: dict = None, state=None):
        return await self._request("put", url, data=data, state=state)

    async def delete(self, url: str, state=None):
        return await self._request("delete", url, state=state)
