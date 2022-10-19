from vkbottle.bot import Bot, Message, rules
from vkbottle.dispatch.rules.base import CommandRule
from typing import Tuple
from vkbottle import Keyboard, KeyboardButtonColor, Callback
from vkbottle import GroupTypes, VKAPIError , BaseStateGroup , CtxStorage , GroupEventType , PhotoMessageUploader, EMPTY_KEYBOARD
import json
import asyncio
import time
from keyboard import create_keyboard
from file_for_text import QUESTIONS

#const с ID
group_id = -215533989                   #ID группы
chats_id = [388438756, ]                #ID чатов для рассылки
value_id = []
elite_id = [388438756]                           #ID юзеров с повышенным доступом

#const для рулзов
prefix = ["!", "/"]                     #возможные перфиксы для команд
sep = '``#$!%!%~%~@%~!~%(^*(~^@*$'      #Разделитель текста (Просто надо так, не менять)

#const для сообщений
hello_msg = "Привет! \nЯ бот группы \"Факультет информационных технологий БГТУ\". Теперь вы будете получчать уведомления с новостями от нашего сообщества!\nЧтобы узнать мои комнады напиши !помощь или /помощь."   
command = ['!рассылка <включить/отключить>',
           '!помощь <команда>',
           '!задать вопрос',
           ]

command_text = {
    "помощь": "Команда имеет следущий синтаксис:\n!помощь <командка>\nАтрибуты:\n<команда> - необязательный. Здесь пишется название той команды, о которой хотите узнать. При отсутствии атрибута покажется полный список команд.\nПример использования: !помощь рассылка",
    "рассылка": "Команда имеет следущий синтаксис:\n!рассылка <включить/отключить>\nАтрибуты:\n<включить/выключить> - обязательный. Здесь вы переключаете режимы оповещения о новых записях на стене сообщества, сообщениях от администрации и иной информации. По умолчанию оповещения включены.\nПример использования: !рассылка включить",
    "задать вопрос": "Команда имеет следущий синтаксис:\n!задать вопрос\nАтрибуты:\nНет атрибутов.\nВы можете задать вопрос администрации, выбирая нужные категории.\nПример использования: !задать вопрос",
}

#токен сообщества
token="753b6d2af4be2474f230397314391c9b56282ee801dd1bcf8419b0952fd43ef4fe4da5f2eb05966ecd41e"
bot = Bot(token=token)

#функции удобства
def read_file ( path: str ):
	with open ( path , 'r' ) as f:
		data: dict = json.load ( f )
	return data


def write_file ( path: str , data: dict ):
	with open ( path , 'w' ) as f:
		json.dump ( data , f , ensure_ascii=False , indent=4 )




#ОБРАБОТЧИКИ СОБЫТИЙ

#Показывет список команд. Синтаксис: !помощь
@bot.on.message(CommandRule(command_text='помощь', prefixes=prefix, args_count=0, sep=sep))
async def help(message: Message):
    global command
    text = "Доступные команды: \n"
    for i in command:
        text += i + "\n"
    await bot.api.messages.send(peer_id=message.peer_id, 
                                message=text, 
                                random_id=0)

#Помощь по командам. Синтаксис: !помощь <команда>
@bot.on.message(CommandRule(command_text='помощь', prefixes=prefix, args_count=1, sep=sep))
async def help_for_command(message: Message, args: Tuple[str]):
    global command_text
    try:
        message_text = command_text[args[0]]
        await bot.api.messages.send(peer_id=message.peer_id, 
                                    message=message_text, 
                                    random_id=0)
    except:
        await bot.api.messages.send(peer_id=message.peer_id, 
                                    message="Такая команда не найдена", 
                                    random_id=0)
    
#Срабатывает на вход бота в беседу
@bot.on.message(rules.ChatActionRule('chat_invite_user'))
async def invite(message: Message):
    global chats_id
    if message.peer_id in chats_id:
        await bot.api.messages.send(peer_id=message.peer_id, 
                                    message="Ваша беседа уже активирована!", 
                                    random_id=0)    
    else:
        chats_id.append(message.peer_id)
        await bot.api.messages.send(peer_id=message.peer_id, 
                                    message="Беседа успешно активирована!", 
                                    random_id=0)

#!рассылка <включить/отключить>. Включает/выключает рассылку
@bot.on.message(CommandRule(command_text="рассылка", prefixes=prefix, args_count=1, sep=sep))
async def mail(message: Message, args: Tuple[str]):
    global chats_id
    if args[0] in ['отключить', 'выключить']:
        if message.peer_id in chats_id:
            chats_id.remove(message.peer_id)
            await bot.api.messages.send(peer_id=message.peer_id, 
                                        message="Рассылка отключена! Теперь вы НЕ будете получать важные сообщения.",
                                        random_id=0)
        else:
            await bot.api.messages.send(peer_id=message.peer_id, 
                                        message="Вы уже отключены от рассылки!",
                                        random_id=0)
    elif args[0] == 'включить':
        if message.peer_id in chats_id:
            await bot.api.messages.send(peer_id=message.peer_id, 
                                        message="Вы уже подключены к рассылке!",
                                        random_id=0)             
        else:
            chats_id.append(message.peer_id)
            await bot.api.messages.send(peer_id=message.peer_id, 
                                        message="Рассылка подключена! Теперь вы будете получать важные сообщения.",
                                        random_id=0)   

#!объявление <текст>. Рассылает сообщение пользователям
@bot.on.message(CommandRule(command_text="объявление", prefixes=prefix, args_count=1, sep=sep))
async def warning(message: Message, args: Tuple[str]):
    if message.peer_id in elite_id:
        global chats_id
        users_info = await bot.api.users.get(message.from_id)
        text = f"{users_info[0].first_name} {users_info[0].last_name}: {args[0]}"
        if chats_id != []:
            await bot.api.messages.send(peer_ids=chats_id, 
            							message=text,
                                        random_id=0)
    else:
     	await bot.api.messages.send(peer_id=message.peer_id,
                           			message='У вас нет прав на использование этой команды!',
                             		random_id=0)

#Срабатывает на новые посты в группе
@bot.on.raw_event(GroupEventType.WALL_POST_NEW, dataclass=GroupTypes.WallPostNew)
async def new_post(event: GroupTypes.WallPostNew):
    global chats_id
    if chats_id != []:
        await bot.api.messages.send(peer_ids=chats_id, 
                                    message="На странице появилась новая запись! ", 
                                    random_id=0, 
                                    attachment=f'wall-{event.group_id}_{event.object.id}'
                                    )
        
#ивент начала личного диалога с юзером
@bot.on.raw_event(GroupEventType.MESSAGE_ALLOW, dataclass=GroupTypes.MessageAllow)
async def new_user(event: GroupTypes.MessageAllow):
    global hello_msg
    global chats_id
    if not (event.object.user_id in chats_id):
        chats_id.append(event.object.user_id)
    await bot.api.messages.send(user_id=event.object.user_id, 
                                message=hello_msg, 
                                random_id=0)


#добавление вопроса в жсон
@bot.on.private_message ( CommandRule ( "вопрос добавить" , prefix , 1 , sep=sep) )
async def add_quiz ( message: Message , args: Tuple [ str ] ):
	try:
		if message.from_id in elite_id:
			item = args [ 0 ]
			data = read_file ( 'data.json' )
			# Проверка на совпадение
			for index , each in enumerate ( list ( data.values ( ) ) ):
				if item in each [ 'question' ]:
					await message.answer ( f"Данный вопрос уже есть базе данных под id {index + 1}" )
					return
			# Проверяем целосность ID, что бы если удалили один, то он заменился добавленным
			arr = list ( data.keys ( ) )
			last_key = 0
			for i in arr:
				if int ( i ) > last_key: last_key = int ( i )
			ID = False
			for key in range ( 1 , last_key + 1 ):
				if str ( key ) not in arr:
					ID = key
					break
			if not ID:
				ID = len ( data ) + 1
			# Добавляем в БД новый вопрос
			data.update ( { ID: { "question": item , "answer": None } } )
			write_file ( 'data.json' , data )
			await message.answer ( f"Вопрос добавлен в базу данных под id {ID}" )
		else:
			await bot.api.messages.send(peer_id=message.peer_id,
                               			message='Вы не можете использовать эту комманду!',
                                 	 	random_id=0)
	except VKAPIError as e:
		print ( "Возникла ошибка [1]" , e.code )

#Удаление вопроса из жсон
@bot.on.private_message ( CommandRule ( "вопрос удалить" , prefix , 1 , sep=sep) )
async def remove_quiz ( message: Message , args: Tuple [ str ] ):
	try:
		if message.peer_id in elite_id:
			id = args [ 0 ]
			data = read_file ( 'data.json' )
			# Проверка на id
			if id not in data:
				await message.answer ( f"Вопроса с данным id в базе данных не найдено" )
				return
			del data [ id ]
			write_file ( 'data.json' , data )
			await message.answer ( f"Вопрос с данным id был успешно удален" )
		else:
			await bot.api.messages.send(peer_id=message.peer_id,
                               			message='У вас нет прав на использование этой команды!',
                                 		random_id=0)
	except VKAPIError as e:
		print ( "Возникла ошибка [2]" , e.code )

#Покаазать вопрос из жсона
@bot.on.private_message ( CommandRule ( "вопрос показать" , prefix , 1 , sep=str ( time.time ( ) ) ) )
async def show_quiz ( message: Message , args: Tuple [ str ] ):
	try:
		id = args [ 0 ]
		data = read_file ( 'data.json' )
		# Проверка на id
		if id not in data:
			await message.answer ( f"Вопроса с данным id в базе данных не найдено" )
			return
		info = data [ id ]
		await message.answer ( f"Вопрос: {info [ 'question' ]}\n"
		                       f"Ответ: {info [ 'answer' ]}" )
	except VKAPIError as e:
		print ( "Возникла ошибка [3]" , e.code )

#Добавляет ответ к вопросу с указанным id
@bot.on.private_message ( CommandRule ( "ответ" , prefix , 1 , sep=sep))
async def show_quiz ( message: Message , args: Tuple [ str ] ):
	try:
		if message.peer_id in elite_id:
			args = args [ 0 ]
			args = args.split ( maxsplit=1 )
			id , answer = args [ 0 ] , args [ 1 ]
			data = read_file ( 'data.json' )
			# Проверка на id
			if id not in data:
				await message.answer ( f"Вопроса с данным id в базе данных не найдено" )
				return
			# Добавляем в БД новый вопрос
			data.update ( { id: { "question": data [ id ] [ 'question' ] , "answer": answer } } )
			write_file ( 'data.json' , data )
			await message.answer ( f"Ответ добавлен в базу данных под id {id}" )
		else:
			await bot.api.messages.send(peer_id=message.peer_id,
                               			message='У вас нет прав на использование этой команды!',
                                 		random_id=0)
	except VKAPIError as e:
		print ( "Возникла ошибка [4]" , e.code )


class QT ( BaseStateGroup ):
	FirstStep = "2"
	SecondStep = "3"
	ThirdStep = "4"
	FourthStep = "5"
	FifthStep = "6"
	NotIncluded = None  # Это что бы не ломалось ничего


class Question ( BaseStateGroup ):
	CreateQuestion = "CreateQuestion"


QT_Arr = [ QT.FirstStep , QT.SecondStep , QT.ThirdStep , QT.FourthStep , QT.FifthStep , QT.NotIncluded ]
# ctx будет нужен для сохранения ответов.
ctx = CtxStorage ( )


@bot.on.private_message ( CommandRule ( "задать вопрос" , prefix , 0 ) )
async def ask_question ( message: Message ):
	try:
		global keyboard_text
		global step
		global Info
		step = 0
		keyboard_text = [ ]
		text = f"На какую тему вы хотите задать вопрос?\n"
		for ind , question in enumerate ( QUESTIONS ):
			text += f"{ind + 1}) {question [ 'name' ]}\n"
			keyboard_text.append ( question [ 'name' ] )
		await bot.state_dispenser.set ( message.peer_id , QT_Arr [ step ] )
		Info = await message.answer ( text , keyboard=create_keyboard ( keyboard_text ) )
	except VKAPIError as e:
		print ( "Возникла ошибка [6]" , e.code )


# Обработчик диалога
@bot.on.raw_event ( GroupEventType.MESSAGE_EVENT )
async def MessageTree ( message: Message ):
	try:
		await bot.api.messages.send_message_event_answer (
			event_id=message [ 'object' ] [ 'event_id' ] ,
			peer_id=message [ 'object' ] [ 'peer_id' ] ,
			user_id=message [ 'object' ] [ 'user_id' ]
		)
		messageText = message [ 'object' ] [ 'payload' ] [ 'cmd' ]
		# ----------------------------------------
		global Info
		global keyboard_text
		print ( keyboard_text )
		answer = [ [ i , x ] for i , x in enumerate ( keyboard_text ) if x == messageText ]
		if answer [ 0 ] [ 1 ] == 'Здесь нет моего варианта':
			await bot.state_dispenser.set ( message [ 'object' ] [ 'peer_id' ] , Question.CreateQuestion )
			await bot.api.messages.send ( peer_id=message [ 'object' ] [ 'peer_id' ] ,
			                              message="Опишите свою проблему или задайте вопрос" , random_id=0 )
			return
		answer = answer [ 0 ]

		if answer == [ ]:
			await bot.api.messages.send ( message="Я вас не понял!" , peer_id=Info.peer_id , random_id=0 )
			return
		# Смотрим есть ли продолжение для диалога
		global step
		if step == 0:
			TestArr = QUESTIONS [ answer [ 0 ] ]
		else:
			TestArr = QUESTIONS [ ctx.get ( 0 ) ]
		for i in range ( step ):
			if i == step - 1:
				TestArr = TestArr [ QT_Arr [ i ].value ] [ "choices" ] [ answer [ 0 ] ]
			else:
				TestArr = TestArr [ QT_Arr [ i ].value ] [ "choices" ] [ ctx.get ( i + 1 ) ]
		ctx.set ( step , answer [ 0 ] )

		if QT_Arr [ step ].value in list ( TestArr.keys ( ) ):
			keyboard_text = []
			await bot.state_dispenser.set ( Info.peer_id , QT_Arr [ step ] )
			text = f"{TestArr [ QT_Arr [ step ].value ] [ 'text' ]}\n"
			for ind , question in enumerate ( TestArr [ QT_Arr [ step ].value ] [ "choices" ] ):
				text += f"{ind + 1}) {question [ 'name' ]}\n"
				keyboard_text.append ( question [ 'name' ] )
			await bot.api.messages.edit ( peer_id=Info.peer_id , message=text , message_id=Info.message_id ,
			                              keyboard=create_keyboard ( keyboard_text ) )
		elif "attachment" in list ( TestArr.keys ( ) ):
			photo_uploader = PhotoMessageUploader ( bot.api )
			attachment = await photo_uploader.upload ( TestArr['attachment'] )
			if "answer" in list ( TestArr.keys ( ) ):
				await bot.api.messages.edit ( peer_id=Info.peer_id , message=TestArr [ "answer" ] ,
				                              message_id=Info.message_id , attachment=attachment, keyboard=EMPTY_KEYBOARD )
			else:
				await bot.api.messages.edit ( peer_id=Info.peer_id , message="Смотри фото" ,
				                              message_id=Info.message_id , attachment=attachment, keyboard=EMPTY_KEYBOARD )
		else:
			await bot.api.messages.edit ( peer_id=Info.peer_id , message=TestArr [ "answer" ] ,
			                              message_id=Info.message_id,keyboard=EMPTY_KEYBOARD)
		step += 1
	except VKAPIError as e:
		print ( "Возникла ошибка [7]" , e.code )


# Создает и отправляет вопрос пользователя
@bot.on.private_message ( state=Question.CreateQuestion )
async def MessageTree ( message: Message ):
	try:
		print ( "I'm here" )
		_ID = 255117463  # 388438756
		forward = { "peer_id": message.peer_id , "conversation_message_ids": [ message.conversation_message_id ] }
		forward = json.dumps ( forward )
		users_info = await bot.api.users.get ( message.from_id )
		await bot.api.messages.send ( user_id=_ID , forward=forward , random_id=0 ,
		                              message=f"Был задан вопрос от {users_info [ 0 ].first_name} {users_info [ 0 ].last_name}" )
		send_user = await bot.api.users.get ( _ID )
		await message.answer (
			f"Ваш вопрос был отправлен админу {send_user [ 0 ].first_name} {send_user [ 0 ].last_name}" )
	except VKAPIError as e:
		print ( "Возникла ошибка [8]" , e.code )

if __name__ == "__main__":
    bot.run_forever()