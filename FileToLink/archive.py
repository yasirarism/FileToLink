from pyrogram import filters
from pyrogram.types import (Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, User)
from pyrogram.errors.exceptions import ButtonDataInvalid

from FileToLink import bot, Config, Strings


async def archive_msg(msg: Message):
    buttons = [[InlineKeyboardButton("🚫", callback_data='delete-file')]]

    if forward := msg.forward_from or msg.forward_from_chat:
        if forward.username:
            buttons[0].append(InlineKeyboardButton("↪", url=f'https://t.me/{forward.username}'))
        else:
            if hasattr(forward, 'title') and forward.title is not None:
                name = forward.title
            else:
                name = (
                    f'{forward.first_name} {forward.last_name}'
                    if forward.last_name
                    else forward.first_name
                )
            if len(name) >= (64 - len('from|')):
                name = name[:(64 - len('from|'))]
            buttons[0].append(InlineKeyboardButton("↪", callback_data=f'from|{name}'))

    if msg.chat.username:
        buttons[0].append(InlineKeyboardButton("👤", url=f'https://t.me/{msg.chat.username}'))
    else:
        buttons[0].append(InlineKeyboardButton("👤", callback_data=f'user|{msg.chat.id}'))

    try:
        reply_markup = InlineKeyboardMarkup(buttons)
        archived_msg: Message = await bot.copy_message(Config.Archive_Channel_ID, msg.chat.id, msg.message_id,
                                                       reply_markup=reply_markup)
    except ButtonDataInvalid:
        archived_msg: Message = await bot.copy_message(Config.Archive_Channel_ID, msg.chat.id, msg.message_id)
    return archived_msg


@bot.on_callback_query(filters.create(lambda _, __, cb: cb.data.split('|')[0] == 'user'))
async def user_info(_, cb: CallbackQuery):
    user: User = await bot.get_users(int(cb.data.split('|')[1]))
    name = (
        f'{user.first_name} {user.last_name}'
        if user.last_name
        else user.first_name
    )
    await cb.answer(f'Name: {name}\nID: {user.id}', show_alert=True)


@bot.on_callback_query(filters.create(lambda _, __, cb: cb.data.split('|')[0] == 'from'))
async def from_info(_, cb: CallbackQuery):
    await cb.answer(f'Forwarded From: {cb.data.split("|")[1]}', show_alert=True)


@bot.on_callback_query(filters.create(lambda _, __, cb: cb.data == 'time-out'))
async def time_out(_, cb: CallbackQuery):
    await cb.answer(Strings.delete_forbidden, show_alert=True)
