from telebot import types
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

class CoursesCallbackFilter(AdvancedCustomFilter):
    key='course'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter) :
        return config.check(query=call)

course_factory = CallbackData('course_id', prefix='course')