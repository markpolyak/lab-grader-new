import filters
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def generate_subject_keyboard(subjects):
    keyboard = InlineKeyboardMarkup(
        keyboard=[
            [
                InlineKeyboardButton(
                    text=subject['name'] + " " + subject['semester'],
                    callback_data=filters.subject_factory.new(subject=subject['id'])
                )
                for subject in subjects
            ]
        ]
    )
    return keyboard

def generate_group_keyboard(subject, groups):
    keyboard = InlineKeyboardMarkup(
        keyboard=[
            [
                InlineKeyboardButton(
                    text=group,
                    callback_data=filters.group_factory.new(subject=subject, group=group)
                )
                for group in groups
            ]
        ]
    )
    return keyboard

def generate_labs_keyboard(subject, group, labs):
    keyboard = InlineKeyboardMarkup(
        keyboard=[
            [
                InlineKeyboardButton(
                    text=lab,
                    callback_data=filters.lab_factory.new(subject=subject, group=group, lab=lab)
                )
                for lab in labs
            ]
        ]
    )
    return keyboard
