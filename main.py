

import logging

from telegram import chat
from inf import env
from telegram import *
from telegram.ext import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def login(update: Update, context: CallbackContext) -> None:
    # print('activated')
    user_id = update.message.from_user.id
    if update.message.chat.type == 'private':
        if not user_id in env.admins:
            echo = update.message.text
            inpu = echo.lstrip('/login').lstrip(' ')
            if inpu == env.password:
                env.admins.append(update.message.from_user.id)

                # Save to the datanase admins.pickle
                

                update.message.reply_text(f'You are successfully looged in.Now you can add new questions /new_qn [ your question ]')
            else:
                update.message.reply_text('⚠️⚠️ Warning\n\nwrong password Please try again !!\n\n⚠️⚠️')

        else:
            update.message.reply_text(f'You are already looged in...Now you can add new questions /new_qn [ your question ]')

    
    return

def add_qn(update: Update, context: CallbackContext) -> None:
    if update.message.chat.type == 'private':
        chat_id = update.message.chat_id
        text = update.message.text
        if update.message.from_user.id in env.admins:
            env.user_data[chat_id]['step']='add_ans'
            env.user_data[chat_id]['qn_no']=len(env.questions)+1
            inpu =  text.lstrip('/new_qn').replace(' ','').lower()
            print(inpu)
            env.questions.append({'qn':inpu,'id':(len(env.questions)+1),'answers':[],'photos':[],'main_qn':text.lstrip('/new_qn')})
            print(env.questions)
            update.message.reply_text('Please send the answers for the question you can set multiple answer for one question ')
            return
        else:
            update.message.reply_text('Please login First /login { password }')
            return

def dissmiss_ans(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    env.user_data[chat_id]['step']='question'
    update.message.reply_text('succesfully added qn and answers ')
    return

def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    user = update.message.from_user
    env.user_data[user.id]={'step':'question' , 'data' : {}}
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='yes_start')],
        [ InlineKeyboardButton("Trial", callback_data='trial_start')],
        [InlineKeyboardButton("question", callback_data='question_start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('"Hi, welcome to Cryptomatic!  \nIf you chose a plan to subscribe, click "subscribe",\nIf  you want to benefit from the 7 days trial for free, click "trial",\nIf you have a question, click "question", thank you !"',parse_mode='HTML',reply_markup=reply_markup)
    
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')

def photo(update: Update, context: CallbackContext) -> None:
    # print(update.message.photo[-1].file_unique_id)
    # print(update.message.photo[-1].file_id)
    file_id = update.message.photo[-1].file_id
    chat_id = update.message.chat_id
    # image = context.bot.get_file(file_id)
    # context.bot.send_photo(chat_id = chat_id , photo = str(file_id))

    if env.user_data[chat_id]['step'] == 'FTX_PHOTO':
        env.user_data[chat_id]['step'] = 'FTX_API_KEY'
        env.user_data[chat_id]['data']['transaction_photo_id'] = str(file_id)
        update.message.reply_text('Thank you, your transaction has been confirmed. You are almost ready ! We need to collect your API keys (see tuto API on the channel if needed) It is important that you keep your public and private API keys written somewhere. Please start by answering with your public API key:')
        return
    elif env.user_data[chat_id]['step'] == 'add_ans':
        print(env.user_data[chat_id]['qn_no']-1)
        env.questions[env.user_data[chat_id]['qn_no']-1]['photos'].append(str(file_id))
        update.message.reply_text('To add another answer just simply type in the text to save the ans write /save')
        # env.user_data[chat_id]['step'] = 'month_data'
        return
    return



def echo(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    chat_id = update.message.chat_id
    user = update.message.from_user
    if env.user_data[chat_id]['step'] == 'yes_start':
        env.user_data[chat_id]['data']['amount'] = text
        update.message.reply_text('Please enter the plan duration you want (1 month, 3 months or 6 months)')
        env.user_data[chat_id]['step'] = 'month_data'
        return
    
    elif env.user_data[chat_id]['step'] == 'month_data':
        env.user_data[chat_id]['data']['month'] = text
        keyboard = [
            [InlineKeyboardButton("Binance", callback_data='Binance')],
            [ InlineKeyboardButton("FTX", callback_data='FTX')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_photo(photo=open('static/ftx.jpg','rb'),caption='Have you a Binance or FTX account ? Please answer "binance" or "FTX" (if not, you need to create an account on one of these exchanges):',parse_mode='HTML',reply_markup=reply_markup)
        
        env.user_data[chat_id]['step'] = 'question'
        return

    
    elif env.user_data[chat_id]['step'] == 'month_data_trial':
        env.user_data[chat_id]['data']['amount'] = text
        keyboard = [
            [InlineKeyboardButton("Binance", callback_data='Binance_trial')],
            [ InlineKeyboardButton("FTX", callback_data='FTX_trial')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_photo(photo=open('static/ftx.jpg','rb'),caption = 'Have you a Binance or FTX account ? Please answer "binance" or "FTX" (if not, you need to create an account on one of these exchanges):',parse_mode='HTML',reply_markup=reply_markup)
        
        env.user_data[chat_id]['step'] = 'question'
        return
    
    elif env.user_data[chat_id]['step'] == 'FTX_API_KEY':
        env.user_data[chat_id]['data']['Public_API_KEY'] = text
        env.user_data[chat_id]['step'] = 'FTX_API_KEY_PRIVATE'
        update.message.reply_text('Thank you, now answer with your private API key:')
        return
    elif env.user_data[chat_id]['step'] == 'FTX_API_KEY_PRIVATE':
        env.user_data[chat_id]['data']['Private_API_KEY'] = text
        update.message.reply_text('Thank you, you are ready ! The bot will start trading, it is important that you do not interact with the trades taken by the bot.')
        env.user_data[chat_id]['step'] = 'question'
        for i in env.admins:
            private_key = env.user_data[chat_id]['data']['Private_API_KEY']
            public_key = env.user_data[chat_id]['data']['Public_API_KEY']
            t = f'A new user has paid \n\nUser Name : {update.message.from_user.first_name}   @{update.message.from_user.username} \nPublic API_KEY : {public_key} \nPrivate API_KEY : {private_key}  '
            
            context.bot.send_photo(chat_id = i , photo = str(env.user_data[chat_id]['data']['transaction_photo_id']) , caption = t)
            
        return

    elif env.user_data[chat_id]['step'] == 'add_ans':
        print(env.user_data[chat_id]['qn_no']-1)
        env.questions[env.user_data[chat_id]['qn_no']-1]['answers'].append(text)
        update.message.reply_text('To add another answer just simply type in the text to save the ans write /save')
        # env.user_data[chat_id]['step'] = 'month_data'
        return
    
    elif env.user_data[chat_id]['step'] == 'question':
        print(env.questions)
        all_questions = list()
        for i in env.questions:
            qn = i['qn']
            sent_once = False
            print(qn)
            print(text.replace(" ",'').lower())
            if  text.replace(" ",'').lower() in qn :
                sent_once = True
                for j in i['answers']:
                    update.message.reply_text(j)
                for p in i['photos']:
                    update.message.reply_photo(photo=str(p))
                
            elif   qn in text.replace(" ",'').lower() :
                if  sent_once==False:
                    for j in i['answers']:
                        update.message.reply_text(j)
                    for p in i['photos']:
                        update.message.reply_photo(photo=str(p))
            sent_once = False
                
        return
    
def getClickButtonData(update:Update,context:CallbackContext)->None:
    logic = update.callback_query.to_dict()
    chat_id = logic['from']['id']
    # print(logic)
    # print(logic['data'])
    data = logic['data']



    if env.user_data[chat_id]['step'] == 'yes_start':
        env.user_data[chat_id]['data']['amount'] = data
        keyboard = [
            [InlineKeyboardButton("1 Month", callback_data='1 to 3k USD')],
            [ InlineKeyboardButton("3 Month", callback_data='3 to 5k USD')],
            [ InlineKeyboardButton("6 Month", callback_data='5 to 10k USD')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id = logic['from']['id'],reply_markup=reply_markup,text  = 'Please enter the plan duration you want (1 month, 3 months or 6 months)')
        env.user_data[chat_id]['step'] = 'month_data'
        return
    elif env.user_data[chat_id]['step'] == 'month_data':
        env.user_data[chat_id]['data']['month'] = data
        keyboard = [
            [InlineKeyboardButton("Binance", callback_data='Binance')],
            [ InlineKeyboardButton("FTX", callback_data='FTX')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_photo(chat_id = logic['from']['id'],photo=open('static/ftx.jpg','rb'),caption='Have you a Binance or FTX account ? Please answer "binance" or "FTX" (if not, you need to create an account on one of these exchanges):',parse_mode='HTML',reply_markup=reply_markup)
        
        env.user_data[chat_id]['step'] = 'question'
        return
    elif env.user_data[chat_id]['step'] == 'month_data_trial':
        env.user_data[chat_id]['data']['amount'] = data
        keyboard = [
            [InlineKeyboardButton("Binance", callback_data='Binance_trial')],
            [ InlineKeyboardButton("FTX", callback_data='FTX_trial')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_photo(chat_id = logic['from']['id'],photo=open('static/ftx.jpg','rb'),caption = 'Have you a Binance or FTX account ? Please answer "binance" or "FTX" (if not, you need to create an account on one of these exchanges):',parse_mode='HTML',reply_markup=reply_markup)
        
        env.user_data[chat_id]['step'] = 'question'
        return


    elif env.user_data[chat_id]['step'] == 'question':
        print(env.questions)
        all_questions = list()
        for i in env.questions:
            qn = i['qn']
            sent_once = False
            print(qn)
            print(data.replace(" ",'').lower())
            if  data.replace(" ",'').lower() in qn :
                sent_once = True
                for j in i['answers']:
                    context.bot.send_message(chat_id = logic['from']['id'],text =j)
                for p in i['photos']:
                    context.bot.send_photo(chat_id = logic['from']['id'],photo=str(p))
                
            elif   qn in data.replace(" ",'').lower() :
                if  sent_once==False:
                    for j in i['answers']:
                        context.bot.send_message(chat_id = logic['from']['id'],text =j)
                    for p in i['photos']:
                        context.bot.send_photo(chat_id = logic['from']['id'],photo=str(p))
            sent_once = False
                
        







    if data == 'yes_start':
        keyboard = [
            [InlineKeyboardButton("1 to 3k USD", callback_data='1 to 3k USD')],
            [ InlineKeyboardButton("3 to 5k USD", callback_data='3 to 5k USD')],
            [ InlineKeyboardButton("5 to 10k USD", callback_data='5 to 10k USD')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_photo(chat_id = logic['from']['id'],reply_markup = reply_markup , photo = open('static/yes_photo.jpg','rb') , caption = 'Please enter the amount of capital you want to \nuse (this amount must be minimum 1k$)')
        env.user_data[chat_id]['step'] = 'yes_start'

    


    elif data == 'question_start':
        env.user_data[chat_id]['step'] = 'question'
        keyboard = [
            [InlineKeyboardButton("all question", callback_data='question_start')],
            
        ]
        for i in env.questions :
            for q,ans in i.items():    
                if q == 'qn':
                    print(i['main_qn'])
                    keyboard.append([InlineKeyboardButton(f"{i['main_qn']}", callback_data=ans)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(reply_markup=reply_markup,chat_id = logic['from']['id'],text='Now you can ask question to us!!!!!Please ask what you want to know ?')
    
    
    elif data == 'trial_start':
        # context.bot.send_message(chat_id = logic['from']['id'],text  = "Please enter the amount of capital you want to use (this amount must be minimum 1k$)")     
        keyboard = [
            [InlineKeyboardButton("1 to 3k USD", callback_data='1 to 3k USD')],
            [ InlineKeyboardButton("3 to 5k USD", callback_data='3 to 5k USD')],
            [ InlineKeyboardButton("5 to 10k USD", callback_data='5 to 10k USD')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_photo(chat_id = logic['from']['id'],reply_markup = reply_markup , photo = open('static/yes_photo.jpg','rb') , caption = 'Please enter the amount of capital you want to \nuse (this amount must be minimum 1k$)')
        env.user_data[chat_id]['step'] = 'month_data_trial'
    elif (data == 'FTX') or (data == 'Binance'):
        context.bot.send_message(chat_id=chat_id,text = "Thank you, you are a few steps from using our service ! Please send the subscription fee (X$) in USDT, USDC or BUSD at the following adress:\n'- USDT adress XXXXX\n'- USDC adress XXXXX\n'- BUSD adress XXXXX\nOnce the transfer is made, please send a screenshot here with the transaction ID:")
        env.user_data[chat_id]['step'] = 'FTX_PHOTO'
    elif (data == 'FTX_trial') or (data == 'Binance_trial'):
        context.bot.send_message(chat_id=chat_id,text = "You are almost ready ! We need to collect your API keys (see tuto API on the channel if needed) It is important that you keep your public and private API keys written somewhere. Please start by answering with your public API key:")
        env.user_data[chat_id]['step'] = 'FTX_API_KEY'
    

    


    return

def main() -> None:
    updater = Updater(env.API_KEY)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("save", dissmiss_ans))
    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(CommandHandler("new_qn", add_qn))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(getClickButtonData))
    dispatcher.add_handler(MessageHandler(Filters.photo, photo))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
