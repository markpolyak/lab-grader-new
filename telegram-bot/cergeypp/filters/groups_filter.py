from telebot import types
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

class GroupsCallbackFilter(AdvancedCustomFilter):
    key='group'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter) :
        return config.check(query=call)

groups_factory = CallbackData("course_id", "group_id", prefix='group')