from telegram import InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, Handler )
import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import time

TELEGRAM_HTTP_API_TOKEN = '420852520:AAHwTY-YRwTog5Hzc3o8p36pzwSyCi16FP4'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



from db_helper_v2 import is_new_member,create_connection, fetch_state, get_ad_id,list_null_fields,update_state,update_field,insert_ad
from db_helper_v2 import add_new_member,search_year,search_price,search_mileage

PROCESS_OPTION, READ_AD_TITLE, PROCESS_NULLS,ENTER_PRICE, ENTER_BRAND, ENTER_MILEAGE, ENTER_MODEL, ENTER_RELEASE_YEAR,\
    READ_TRANS,DONE, SEARCH, READ_START_YEAR, READ_END_YEAR,READ_START_PRICE,READ_END_PRICE,READ_END_MILEAGE, \
    READ_START_MILEAGE= range(17)

def start(bot,update):
    global conn
    conn=create_connection()
    try:
        member_id=update.message.chat_id
    except AttributeError:
        member_id=update.callback_query.message.chat_id
    if is_new_member(conn,member_id):
        add_new_member(conn, member_id)
        keyboard = [
            [InlineKeyboardButton(u"افزودن آگهی", callback_data='1')],
            [InlineKeyboardButton(u"انصراف", callback_data='2')],
            [InlineKeyboardButton(u"جستوجوی آگهی", callback_data='3')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            u"گزینه مورد نظر را انتخاب کنید",
            reply_markup=reply_markup
        )
        return PROCESS_OPTION
    else:
        member_state=fetch_state(member_id, conn)
        if member_state==0:
            keyboard = [
                [InlineKeyboardButton(u"افزودن آگهی", callback_data='1')],
                [InlineKeyboardButton(u"انصراف", callback_data='2')],
                [InlineKeyboardButton(u"جستوجوی آگهی", callback_data='3')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                u"گزینه مورد نظر را انتخاب کنید",
                reply_markup=reply_markup
            )
            return PROCESS_OPTION
        elif member_state==1:
            update.message.reply_text(u'عنوان آگهی خود را وارد کنید')
            return READ_AD_TITLE
        else:
            ad_id=get_ad_id(member_id,conn)
            null_values=list_null_fields(ad_id, conn)
            if len(null_values)==0:
                return cancel_state(bot,update)
            button_list = [KeyboardButton(s) for s in null_values]
            reply_markup = ReplyKeyboardMarkup(build_menu(button_list, n_cols=2))
            bot.send_message(chat_id=member_id, text=u"کدام اطلاعات را وارد میکنید؟", reply_markup=reply_markup)
            return PROCESS_NULLS


def process_option(bot,update):
    print('in process option method')
    option=update.callback_query.data
    print(option)
    option=int(option)
    member_id=update.callback_query.message.chat_id
    if option==1:
        print('option 1')
        update_state(member_id, 1, conn)
        bot.send_message(chat_id=member_id, text=u"عنوان آگهی خود را وارد کنید")
        return READ_AD_TITLE
    if option==2:
        update_state(member_id, 2, conn)
        return cancel_state(bot,update)
    if option==3:
        print(update)
        keyboard = [
            [InlineKeyboardButton(u"قیمت", callback_data='1')],
            [InlineKeyboardButton(u"کارکرد", callback_data='2')],
            [InlineKeyboardButton(u"سال تولید", callback_data='3')],
            [InlineKeyboardButton(u"برند", callback_data='4')],

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text(
            u"بر چه اساسی جست و جو میکنید؟",
            reply_markup=reply_markup
        )
        return SEARCH

def read_ad_title(bot,update):
    chat_id=update.message.chat_id
    title=update.message.text
    member_id=update.message.chat_id
    insert_ad(member_id, title, conn)
    ad_id=get_ad_id(chat_id,conn)
    update_state(member_id, ad_id, conn)
    return start(bot,update)

def process_nulls(bot,update):
    member_id=update.message.chat_id
    null_field=update.message.text
    print(null_field)
    if 'price' in null_field:
        reply_markup = ReplyKeyboardRemove()
        bot.send_message(chat_id=member_id, text=u"قیمت را وارد کنید",reply_markup=reply_markup)
        return ENTER_PRICE
    if 'brand' in null_field:
        reply_markup = ReplyKeyboardRemove()
        bot.send_message(chat_id=member_id, text=u"شرکت سازنده حودروی خود را وارد کنید",reply_markup=reply_markup)
        return ENTER_BRAND
    if 'mileage' in null_field:
        reply_markup = ReplyKeyboardRemove()
        bot.send_message(chat_id=member_id, text=u"کارکرد خودروی خود را وارد کنید",reply_markup=reply_markup)
        return ENTER_MILEAGE
    if 'model' in null_field:
        reply_markup = ReplyKeyboardRemove()
        bot.send_message(chat_id=member_id, text=u"مدل خودروی خود را وارد کنید",reply_markup=reply_markup)
        return ENTER_MODEL
    if 'release_year' in null_field:
        reply_markup = ReplyKeyboardRemove()
        bot.send_message(chat_id=member_id, text=u"سال تولید خودروی خود را وارد کنید",reply_markup=reply_markup)
        return ENTER_RELEASE_YEAR
    if 'transmission' in null_field:
        keyboard = [
            [InlineKeyboardButton(u"دنده ای", callback_data='1')],
            [InlineKeyboardButton(u"اتومات", callback_data='2')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            u"نوع دنده خودروی خود را وارد کنید",
            reply_markup=reply_markup
        )
        return READ_TRANS
    if null_field is None:
        return DONE




def enter_price(bot,update):
    price=update.message.text
    chat_id=update.message.chat_id
    ad_id=get_ad_id(chat_id,conn)
    price=int(price)
    print(price)
    update_field(ad_id, 'price', price, conn)
    return start(bot,update)

def enter_brand(bot,update):
    brand=update.message.text
    chat_id=update.message.chat_id
    ad_id=get_ad_id(chat_id,conn)
    brand=str(brand)
    print(brand)
    update_field(ad_id,'brand',brand,conn)
    return start(bot,update)

def enter_mileage(bot,update):
    mileage=update.message.text
    chat_id=update.message.chat_id
    ad_id=get_ad_id(chat_id,conn)
    mileage=int(mileage)
    print(mileage)
    update_field(ad_id,'mileage',mileage,conn)
    return start(bot,update)

def enter_model(bot,update):
    model=update.message.text
    chat_id=update.message.chat_id
    ad_id=get_ad_id(chat_id,conn)
    model=str(model)
    print(model)
    update_field(ad_id, 'model', model, conn)
    return start(bot,update)

def enter_release_year(bot,update):
    release_year=update.message.text
    chat_id = update.message.chat_id
    ad_id = get_ad_id(chat_id, conn)
    release_year = int(release_year)
    update_field(ad_id, 'release_year', release_year, conn)
    return start(bot, update)

def read_trans(bot,update):
    trans=update.callback_query.data
    chat_id=update.callback_query.message.chat_id
    ad_id=get_ad_id(chat_id,conn)
    trans=int(trans)
    update_field(ad_id,'transmission',trans,conn)
    return start(bot,update)

def done(bot,update):
    print(update)
    try:
        update.message.reply_text(u'آگهی شما با موفقیت افزوده شد')
    except AttributeError:
        update.callback_query.message.reply_text(u'آگهی شما با موفقیت افزوده شد')
    return ConversationHandler.END

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def search_ad(bot,update):
    query=int(update.callback_query.data)
    if query==1:
        update.callback_query.message.reply_text('از چه قیمتی جست وجو را شروع میکنید؟')
        return READ_START_PRICE
    if query==3:
        update.callback_query.message.reply_text('از چه سالی جست وجو را شروع میکنید؟')
        return READ_START_YEAR
    if query==2:
        update.callback_query.message.reply_text('از چه کارکردی جست وجو را شروع میکنید؟')
        return READ_START_MILEAGE


def read_start_year(bot,update):
    global start_date
    start_date=int(update.message.text)
    update.message.reply_text('تا چه سالی جست وجو میکنید؟')
    return READ_END_YEAR

def read_end_year(bot,update):
    print('read end year')
    member_id=update.message.chat_id
    end_date=int(update.message.text)
    ads=search_year(start_date, end_date, conn)
    for ad in ads:
        print(ad[0])
        info=u' مدل: '+str(ad[0])
        #print(model)
        info=info+u' برند: '+str(ad[1])
        info=info+u' کارکرد: '+str(ad[2])
        info=info+u' سال تولید: '+str(ad[3])
        info=info+u'قیمت: '+str(ad[4])
        keyboard = [
            #[InlineKeyboardButton(text=brand, url='www.google.com'),
            #InlineKeyboardButton(text=model,url='www.google.com'),
            [InlineKeyboardButton(text=info,url='www.google.com')],
            #[InlineKeyboardButton(text=year,url='www.google.com')],
            #[InlineKeyboardButton(text=price,url='www.google.com')],

        ]
        reply_markup = InlineKeyboardMarkup(keyboard,resize_keyboard=True,one_time_keyboard=True)
        bot.send_message(chat_id=member_id, text=u"خودروی منطبق", reply_markup=reply_markup)
        return start(bot,update)



def read_start_price(bot,update):
    global start_price
    start_price=int(update.message.text)
    update.message.reply_text('تا چه قیمتی جست وجو میکنید؟')
    return READ_END_PRICE

def read_end_price(bot,update):
    print('read end year')
    member_id=update.message.chat_id
    end_price=int(update.message.text)
    ads=search_price(start_price, end_price, conn)
    for ad in ads:
        print(ad[0])
        info=u' مدل: '+str(ad[0])
        #print(model)
        info=info+u' برند: '+str(ad[1])
        info=info+u' کارکرد: '+str(ad[2])
        info=info+u' سال تولید: '+str(ad[3])
        info=info+u'قیمت: '+str(ad[4])
        keyboard = [
            [InlineKeyboardButton(text=info,url='www.google.com')],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard,resize_keyboard=True,one_time_keyboard=True)
        bot.send_message(chat_id=member_id, text=u"خودروی منطبق", reply_markup=reply_markup)
        return start(bot,update)


def read_start_mileage(bot,update):
    global start_mileage
    start_mileage=int(update.message.text)
    update.message.reply_text('تا چه کارکردی جست وجو میکنید؟')
    return READ_END_MILEAGE

def read_end_mileage(bot,update):
    print('read end mileage')
    member_id=update.message.chat_id
    end_mileage=int(update.message.text)
    ads=search_mileage(start_mileage, end_mileage, conn)
    for ad in ads:
        print(ad[0])
        info=u' مدل: '+str(ad[0])
        #print(model)
        info=info+u' برند: '+str(ad[1])
        info=info+u' کارکرد: '+str(ad[2])
        info=info+u' سال تولید: '+str(ad[3])
        info=info+u'قیمت: '+str(ad[4])
        keyboard = [
            [InlineKeyboardButton(text=info,url='www.google.com')],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard,resize_keyboard=True,one_time_keyboard=True)
        bot.send_message(chat_id=member_id, text=u"خودروی منطبق", reply_markup=reply_markup)
        return start(bot,update)





def cancel_state(bot,update):
    if update.callback_query:
        query=update.callback_query
    else:
        query=update
    chat_id = query.message.chat_id

    #He must start from the scratch
    ad_id=get_ad_id(chat_id,conn)
    if ad_id is None:
        update_state(chat_id, 0,conn)
    else:
        nulls=list_null_fields(ad_id,conn)
        if len(nulls)==0:
            update_state(chat_id,0,conn)
            update.message.reply_text(u'آگهی شما با موفقیت افزوده شد')
        else:
            update_state(chat_id, ad_id,conn)
    user = query.message.from_user
    logger.info(u"User %s canceled the conversation.", user.first_name)
    query.message.reply_text(u'باز هم به ما سر بزن!',
                                  reply_markup=ReplyKeyboardRemove())
    conn.close()
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_HTTP_API_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            PROCESS_OPTION: [CallbackQueryHandler(process_option)
                       ],

            READ_AD_TITLE: [MessageHandler(Filters.text,
                                           read_ad_title
                                           ),
                            ],

            PROCESS_NULLS: [MessageHandler(Filters.text,
                                          process_nulls
                                          ),
                           ],
            ENTER_PRICE: [MessageHandler(Filters.text,
                                         enter_price)],
            ENTER_BRAND: [MessageHandler(Filters.text,
                                         enter_brand)],
            ENTER_MILEAGE: [MessageHandler(Filters.text,
                                         enter_mileage)],
            ENTER_MODEL: [MessageHandler(Filters.text,
                                         enter_model)],
            ENTER_RELEASE_YEAR: [MessageHandler(Filters.text,
                                         enter_release_year)],
            READ_TRANS: [CallbackQueryHandler(read_trans)],
            SEARCH: [CallbackQueryHandler(search_ad)],
            READ_START_YEAR: [MessageHandler(Filters.text,
                                              read_start_year)],
            READ_END_YEAR: [MessageHandler(Filters.text,
                                           read_end_year)],
            READ_START_PRICE: [MessageHandler(Filters.text,
                                              read_start_price)],
            READ_END_PRICE: [MessageHandler(Filters.text,
                                           read_end_price)],
            READ_START_MILEAGE: [MessageHandler(Filters.text,
                                              read_start_mileage)],
            READ_END_MILEAGE: [MessageHandler(Filters.text,
                                            read_end_mileage)],

        },

        fallbacks=[CommandHandler('cancel', cancel_state),
                   CallbackQueryHandler(cancel_state)],
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()