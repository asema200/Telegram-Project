import telebot
from telebot import types
import os
from dotenv import load_dotenv
import stats_advanced
import quiz

# Загрузка переменных окружения
load_dotenv()

# Токен бота - ВАЖНО: Создай файл .env в корне проекта и добавь:
# BOT_TOKEN=твой_токен_от_BotFather
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    print("📝 Создай файл .env в корне проекта и добавь строку:")
    print("   BOT_TOKEN=твой_токен_от_BotFather")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Инициализация викторины
quiz_manager = quiz.QuizSession()

# Словарь для хранения состояний и настроек пользователей (в памяти)
user_states = {}
user_settings = {}


def get_main_keyboard():
    '''Главная клавиатура с кнопками'''
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('🔍 Поиск вакансий'),
        types.KeyboardButton('⚖️ Сравнить профессии'),
        types.KeyboardButton('🎯 Тест на профориентацию'),
        types.KeyboardButton('⚙️ Настройки'),
        types.KeyboardButton('ℹ️ Помощь')
    )
    return keyboard


def get_cities_keyboard():
    '''Клавиатура выбора города'''
    markup = types.InlineKeyboardMarkup(row_width=2)
    cities = [
        ('Москва', 1),
        ('Санкт-Петербург', 2),
        ('Екатеринбург', 3),
        ('Новосибирск', 4),
        ('Казань', 88),
        ('Нижний Новгород', 66),
        ('Вся Россия', 113)
    ]
    buttons = [types.InlineKeyboardButton(name, callback_data=f'city_{id}')
               for name, id in cities]
    markup.add(*buttons)
    return markup


def get_experience_keyboard():
    '''Клавиатура выбора опыта'''
    markup = types.InlineKeyboardMarkup(row_width=2)
    experiences = [
        ('Не важно', 'all'),
        ('Без опыта', 'noExperience'),
        ('1-3 года', 'between1And3'),
        ('3-6 лет', 'between3And6'),
        ('Более 6 лет', 'moreThan6')
    ]
    buttons = [types.InlineKeyboardButton(name, callback_data=f'exp_{code}')
               for name, code in experiences]
    markup.add(*buttons)
    return markup


def get_user_settings(user_id):
    '''Получение настроек пользователя (из памяти)'''
    if user_id not in user_settings:
        user_settings[user_id] = {
            'city_id': 1,
            'experience': 'all',
            'remote_only': 0
        }
    return user_settings[user_id]


def update_user_settings(user_id, **kwargs):
    '''Обновление настроек пользователя'''
    if user_id not in user_settings:
        user_settings[user_id] = {
            'city_id': 1,
            'experience': 'all',
            'remote_only': 0
        }
    user_settings[user_id].update(kwargs)


@bot.message_handler(commands=['start'])
def start(message):
    '''Команда /start'''
    user_name = message.from_user.first_name
    msg = f"👋 Привет, <b>{user_name}</b>!\n\n"
    msg += "Я помогу тебе с выбором профессии! Могу показать:\n\n"
    msg += "🔍 Статистику по зарплатам с графиками\n"
    msg += "⚖️ Сравнение разных профессий\n"
    msg += "🎯 Тест на профориентацию\n\n"
    msg += "Используй кнопки ниже или просто напиши название профессии! 👇"

    bot.send_message(message.chat.id, msg, parse_mode='html',
                    reply_markup=get_main_keyboard())


@bot.message_handler(commands=['help'])
def help_command(message):
    '''Команда /help'''
    msg = "📖 <b>Как пользоваться ботом:</b>\n\n"
    msg += "1️⃣ <b>Поиск вакансий:</b>\n"
    msg += "   Просто напиши профессию, например: 'программист'\n\n"
    msg += "2️⃣ <b>Настройки:</b>\n"
    msg += "   Выбери город, опыт работы, удаленка/офис\n\n"
    msg += "3️⃣ <b>Сравнение:</b>\n"
    msg += "   Используй /compare программист, дизайнер\n\n"
    msg += "4️⃣ <b>Тест:</b>\n"
    msg += "   Пройди тест на профориентацию /quiz\n\n"
    msg += "<b>Команды:</b>\n"
    msg += "/start - Начать работу\n"
    msg += "/help - Помощь\n"
    msg += "/settings - Настройки\n"
    msg += "/compare - Сравнение профессий\n"
    msg += "/quiz - Тест на профориентацию\n"

    bot.send_message(message.chat.id, msg, parse_mode='html')


@bot.message_handler(commands=['settings'])
def settings(message):
    '''Настройки пользователя'''
    user_set = get_user_settings(message.from_user.id)

    msg = "⚙️ <b>Настройки поиска:</b>\n\n"
    city_name = stats_advanced.VacancyStats.CITIES.get(user_set['city_id'], 'Москва')
    msg += f"📍 Город: {city_name}\n"
    msg += f"💼 Опыт: {user_set['experience']}\n"
    msg += f"🏠 Только удаленка: {'Да' if user_set['remote_only'] else 'Нет'}\n\n"
    msg += "Выбери что хочешь изменить:"

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('📍 Изменить город', callback_data='settings_city'),
        types.InlineKeyboardButton('💼 Изменить опыт', callback_data='settings_exp'),
        types.InlineKeyboardButton('🏠 Переключить удаленку', callback_data='settings_remote')
    )

    bot.send_message(message.chat.id, msg, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['compare'])
def compare_command(message):
    '''Команда сравнения профессий'''
    msg = "⚖️ <b>Сравнение профессий</b>\n\n"
    msg += "Введи 2-4 профессии через запятую, например:\n"
    msg += "<code>программист, дизайнер, аналитик</code>\n\n"
    msg += "Я покажу сравнение зарплат!"

    bot.send_message(message.chat.id, msg, parse_mode='html')
    user_states[message.from_user.id] = {'state': 'waiting_compare'}


@bot.message_handler(commands=['quiz'])
def quiz_command(message):
    '''Запуск викторины'''
    quiz_manager.start_quiz(message.from_user.id)
    send_quiz_question(message.chat.id, message.from_user.id)


def send_quiz_question(chat_id, user_id):
    '''Отправка вопроса викторины'''
    question = quiz_manager.get_current_question(user_id)

    if not question:
        # Викторина завершена
        result = quiz_manager.get_result(user_id)
        result_msg = quiz.get_quiz_result_message(result)

        bot.send_message(chat_id, result_msg, parse_mode='html')

        # Предлагаем посмотреть профессии
        markup = types.InlineKeyboardMarkup()
        profile_professions = quiz.CAREER_PROFILES[result['profile']]['professions']
        for profession in profile_professions[:3]:
            markup.add(types.InlineKeyboardButton(
                f"🔍 {profession}",
                callback_data=f"search_{profession}"
            ))

        bot.send_message(chat_id, "Хочешь узнать больше о этих профессиях?",
                        reply_markup=markup)

        quiz_manager.end_quiz(user_id)
        return

    # Отправляем вопрос с кнопками
    markup = types.InlineKeyboardMarkup(row_width=1)
    for idx, option in enumerate(question['options']):
        markup.add(types.InlineKeyboardButton(
            option['text'],
            callback_data=f"quiz_{idx}"
        ))

    bot.send_message(chat_id, question['question'], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    '''Обработчик всех callback кнопок'''
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    # Функция для безопасного ответа на callback (игнорирует ошибки с истекшими кнопками)
    def safe_answer(message=""):
        try:
            bot.answer_callback_query(call.id, message)
        except:
            pass  # Игнорируем ошибки с устаревшими callback

    # Обработка настроек города
    if data.startswith('city_'):
        city_id = int(data.split('_')[1])
        update_user_settings(user_id, city_id=city_id)
        city_name = stats_advanced.VacancyStats.CITIES.get(city_id, 'Неизвестно')
        safe_answer(f"Город изменен на: {city_name}")
        bot.edit_message_text("✅ Настройки сохранены!", chat_id, call.message.message_id)

    # Обработка настроек опыта
    elif data.startswith('exp_'):
        experience = data.split('_')[1]
        update_user_settings(user_id, experience=experience)
        safe_answer("Опыт работы обновлен!")
        bot.edit_message_text("✅ Настройки сохранены!", chat_id, call.message.message_id)

    # Переключение удаленки
    elif data == 'settings_remote':
        settings = get_user_settings(user_id)
        new_value = 0 if settings['remote_only'] else 1
        update_user_settings(user_id, remote_only=new_value)
        status = "включена" if new_value else "выключена"
        safe_answer(f"Удаленка {status}")
        bot.edit_message_text("✅ Настройки сохранены!", chat_id, call.message.message_id)

    # Открытие меню настроек
    elif data == 'settings_city':
        bot.edit_message_text("Выбери город:", chat_id, call.message.message_id,
                             reply_markup=get_cities_keyboard())

    elif data == 'settings_exp':
        bot.edit_message_text("Выбери опыт работы:", chat_id, call.message.message_id,
                             reply_markup=get_experience_keyboard())

    # Поиск профессии
    elif data.startswith('search_'):
        profession = data[7:]  # Убираем 'search_'
        process_search_query(call.message, profession)
        safe_answer(f"Ищу: {profession}")

    # Викторина
    elif data.startswith('quiz_'):
        answer_idx = int(data.split('_')[1])
        quiz_manager.add_answer(user_id, answer_idx)
        safe_answer("✅")
        bot.delete_message(chat_id, call.message.message_id)
        send_quiz_question(chat_id, user_id)


def process_search_query(message, query):
    '''Обработка поискового запроса'''
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    chat_id = message.chat.id

    # Сохраняем последний запрос
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]['last_query'] = query

    # Получаем настройки
    settings = get_user_settings(user_id)

    bot.send_message(chat_id, f"🔍 Ищу вакансии: <b>{query}</b>...", parse_mode='html')

    try:
        # Создаем статистику
        stats = stats_advanced.VacancyStats(
            query,
            city_id=settings['city_id'],
            experience=settings['experience'] if settings['experience'] != 'all' else None,
            remote_only=settings['remote_only']
        )

        # Отправляем текстовую статистику
        msg = stats_advanced.format_stats_message(stats)
        bot.send_message(chat_id, msg, parse_mode='html')

        # Создаем и отправляем график
        if stats.create_salary_histogram('salaries.png'):
            with open('salaries.png', 'rb') as photo:
                bot.send_photo(chat_id, photo)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка при получении данных: {str(e)}\n"
                                  "Попробуй другой запрос или проверь настройки.")


def process_comparison(message, professions):
    '''Обработка сравнения профессий'''
    chat_id = message.chat.id
    settings = get_user_settings(message.from_user.id)

    if len(professions) < 2:
        bot.send_message(chat_id, "❌ Нужно минимум 2 профессии для сравнения!")
        return

    if len(professions) > 4:
        bot.send_message(chat_id, "❌ Максимум 4 профессии для сравнения!")
        return

    bot.send_message(chat_id, "⏳ Собираю данные для сравнения...")

    try:
        # Создаем статистику для каждой профессии
        all_stats = []
        for prof in professions:
            prof = prof.strip()
            stats = stats_advanced.VacancyStats(
                prof,
                city_id=settings['city_id'],
                experience=settings['experience'] if settings['experience'] != 'all' else None,
                remote_only=settings['remote_only']
            )
            all_stats.append(stats)

        # Создаем сравнительный график
        if len(all_stats) > 1:
            main_stats = all_stats[0]
            other_stats = all_stats[1:]
            main_stats.create_comparison_chart(other_stats, 'comparison.png')

            with open('comparison.png', 'rb') as photo:
                bot.send_photo(chat_id, photo,
                             caption=f"⚖️ Сравнение: {', '.join(professions)}")

        # Текстовое сравнение
        msg = "📊 <b>Сравнение профессий:</b>\n\n"
        for stats in all_stats:
            basic = stats.get_basic_stats()
            if basic:
                msg += f"<b>{stats.query}</b>\n"
                msg += f"  Медиана: {basic['median']:,} ₽\n"
                msg += f"  Среднее: {basic['mean']:,} ₽\n"
                msg += f"  Вакансий: {basic['count']}\n\n"

        bot.send_message(chat_id, msg, parse_mode='html')

    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {str(e)}")


@bot.message_handler(content_types=['text'])
def text_handler(message):
    '''Обработчик текстовых сообщений'''
    user_id = message.from_user.id
    text = message.text.strip()

    # Проверяем состояние пользователя
    if user_id in user_states:
        state_data = user_states.get(user_id, {})

        if state_data.get('state') == 'waiting_compare':
            professions = [p.strip() for p in text.split(',')]
            process_comparison(message, professions)
            user_states[user_id]['state'] = None
            return

    # Обработка кнопок главного меню
    if text == '🔍 Поиск вакансий':
        bot.send_message(message.chat.id,
                        "Напиши название профессии, например:\n"
                        "• программист\n• дизайнер\n• аналитик данных")
        return

    elif text == '⚖️ Сравнить профессии':
        compare_command(message)
        return

    elif text == '🎯 Тест на профориентацию':
        quiz_command(message)
        return

    elif text == '⚙️ Настройки':
        settings(message)
        return

    elif text == 'ℹ️ Помощь':
        help_command(message)
        return

    # Обычный поисковый запрос
    else:
        process_search_query(message, text)


if __name__ == '__main__':
    print("🤖 Бот запущен!")
    print("✅ Все системы готовы!\n")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
