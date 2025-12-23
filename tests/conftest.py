import pytest
from unittest.mock import AsyncMock


class DummyState:
    def __init__(self, initial_state=None, data=None):
        self._state = initial_state
        self._data = data or {}
        self.set_state = AsyncMock()
        self.clear = AsyncMock()
        self.update_data = AsyncMock(side_effect=self._update)

    async def get_state(self):
        return self._state

    async def get_data(self):
        return dict(self._data)

    def _update(self, **kwargs):
        self._data.update(kwargs)


class DummyMessage:
    def __init__(self, text=None):
        self.text = text
        self.answer = AsyncMock()
        self.answer_media_group = AsyncMock()
        self.edit_reply_markup = AsyncMock()


class DummyUser:
    def __init__(self, user_id=1):
        self.id = user_id


class DummyCallbackQuery:
    def __init__(self, data, user_id=1, message=None):
        self.data = data
        self.from_user = DummyUser(user_id)
        self.message = message or DummyMessage()
        self.answer = AsyncMock()


@pytest.fixture
def msg():
    return DummyMessage()


@pytest.fixture
def state():
    return DummyState()


@pytest.fixture
def cb():
    return DummyCallbackQuery("noop")
