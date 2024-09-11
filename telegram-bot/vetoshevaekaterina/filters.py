import telebot
from telebot import AdvancedCustomFilter
from telebot.callback_data import CallbackData

subject_factory = CallbackData("subject", prefix="subject")
group_factory = CallbackData("subject", "group", prefix="group")
lab_factory = CallbackData("subject", "group", "lab", prefix="lab")

class SubjectDataFilter(AdvancedCustomFilter):
    key = 'subject_config'

    def check(self, call, config):
        return config.check(query=call)

class GroupDataFilter(AdvancedCustomFilter):
    key = 'group_config'

    def check(self, call, config):
        return config.check(query=call)

class LabDataFilter(AdvancedCustomFilter):
    key = 'lab_config'

    def check(self, call, config):
        return config.check(query=call)
    

def add_filters(bot):
    bot.add_custom_filter(SubjectDataFilter())
    bot.add_custom_filter(GroupDataFilter())
    bot.add_custom_filter(LabDataFilter())