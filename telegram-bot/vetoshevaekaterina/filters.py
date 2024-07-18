from telebot import types
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

class CoursesCallbackFilter(AdvancedCustomFilter):
    key='course'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter) :
        return config.check(query=call)

course_factory = CallbackData('course_id', prefix='course')

class GroupsCallbackFilter(AdvancedCustomFilter):
    key='group'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter) :
        return config.check(query=call)

groups_factory = CallbackData("course_id", "group_id", prefix='group')

class LabsCallbackFilter(AdvancedCustomFilter):
    key='lab'

    async def check(self, call: types.CallbackQuery, config: CallbackDataFilter) :
        return config.check(query=call)

labs_factory = CallbackData("course_id", "group_id", "lab_id", prefix='lab')