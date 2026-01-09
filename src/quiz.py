'''Модуль викторины для профориентации'''

# Вопросы викторины
QUIZ_QUESTIONS = [
    {
        'question': '1️⃣ Что тебе больше нравится?',
        'options': [
            {'text': 'Работать с людьми 👥', 'traits': ['social', 'communication']},
            {'text': 'Работать с данными 📊', 'traits': ['analytical', 'technical']},
            {'text': 'Создавать что-то новое 🎨', 'traits': ['creative', 'artistic']},
            {'text': 'Решать технические задачи 💻', 'traits': ['technical', 'logical']}
        ]
    },
    {
        'question': '2️⃣ Какая рабочая обстановка тебе ближе?',
        'options': [
            {'text': 'Офис с командой 🏢', 'traits': ['social', 'collaborative']},
            {'text': 'Удаленная работа 🏠', 'traits': ['independent', 'flexible']},
            {'text': 'Путешествия и встречи ✈️', 'traits': ['social', 'dynamic']},
            {'text': 'Тихое место для концентрации 🤫', 'traits': ['focused', 'independent']}
        ]
    },
    {
        'question': '3️⃣ Что тебя больше мотивирует?',
        'options': [
            {'text': 'Помогать людям 🤝', 'traits': ['social', 'helping']},
            {'text': 'Высокая зарплата 💰', 'traits': ['ambitious', 'financial']},
            {'text': 'Творческая свобода 🎭', 'traits': ['creative', 'freedom']},
            {'text': 'Сложные задачи 🧩', 'traits': ['analytical', 'challenging']}
        ]
    },
    {
        'question': '4️⃣ Твои сильные стороны:',
        'options': [
            {'text': 'Общение и убеждение 🗣️', 'traits': ['social', 'leadership']},
            {'text': 'Логика и анализ 🧠', 'traits': ['analytical', 'logical']},
            {'text': 'Креативность 🎨', 'traits': ['creative', 'artistic']},
            {'text': 'Внимание к деталям 🔍', 'traits': ['detail-oriented', 'precise']}
        ]
    },
    {
        'question': '5️⃣ Какие предметы тебе интереснее?',
        'options': [
            {'text': 'Гуманитарные (языки, история) 📚', 'traits': ['social', 'communication']},
            {'text': 'Точные науки (математика, физика) 🔢', 'traits': ['analytical', 'technical']},
            {'text': 'Искусство и дизайн 🎨', 'traits': ['creative', 'artistic']},
            {'text': 'Информатика и технологии 💻', 'traits': ['technical', 'logical']}
        ]
    },
    {
        'question': '6️⃣ Твой идеальный проект:',
        'options': [
            {'text': 'Организовать мероприятие 🎉', 'traits': ['social', 'organizational']},
            {'text': 'Провести исследование 🔬', 'traits': ['analytical', 'research']},
            {'text': 'Создать дизайн или видео 🎬', 'traits': ['creative', 'artistic']},
            {'text': 'Разработать приложение 📱', 'traits': ['technical', 'logical']}
        ]
    },
    {
        'question': '7️⃣ Как ты относишься к рутине?',
        'options': [
            {'text': 'Люблю стабильность ✅', 'traits': ['stable', 'organized']},
            {'text': 'Предпочитаю разнообразие 🎲', 'traits': ['dynamic', 'flexible']},
            {'text': 'Главное - результат 🎯', 'traits': ['goal-oriented', 'ambitious']},
            {'text': 'Нужен баланс ⚖️', 'traits': ['balanced', 'adaptable']}
        ]
    }
]

# Профессиональные профили
CAREER_PROFILES = {
    'technical': {
        'name': 'Техническая сфера 💻',
        'professions': [
            'программист',
            'разработчик',
            'системный администратор',
            'DevOps инженер',
            'тестировщик ПО'
        ],
        'description': 'Тебе подходят технические профессии! Ты любишь решать сложные задачи, работать с кодом и создавать программные решения.'
    },
    'analytical': {
        'name': 'Аналитика и данные 📊',
        'professions': [
            'аналитик данных',
            'data scientist',
            'бизнес-аналитик',
            'финансовый аналитик',
            'исследователь'
        ],
        'description': 'Тебе подходит работа с данными! Ты умеешь находить закономерности, анализировать информацию и делать выводы.'
    },
    'creative': {
        'name': 'Креативная сфера 🎨',
        'professions': [
            'дизайнер',
            'UX/UI дизайнер',
            'моушн-дизайнер',
            'контент-менеджер',
            'маркетолог'
        ],
        'description': 'Тебе подходят творческие профессии! Ты умеешь создавать красивое и оригинальное, мыслишь нестандартно.'
    },
    'social': {
        'name': 'Работа с людьми 👥',
        'professions': [
            'менеджер по продажам',
            'HR-специалист',
            'менеджер проектов',
            'PR-специалист',
            'психолог'
        ],
        'description': 'Тебе подходит работа с людьми! Ты легко находишь общий язык, умеешь убеждать и помогать другим.'
    },
    'balanced': {
        'name': 'Универсал 🌟',
        'professions': [
            'продакт-менеджер',
            'консультант',
            'предприниматель',
            'менеджер проектов',
            'координатор'
        ],
        'description': 'У тебя универсальный профиль! Ты можешь работать в разных сферах, сочетая различные навыки.'
    }
}


def calculate_quiz_result(answers):
    '''Подсчет результатов викторины'''
    trait_scores = {}

    # Подсчитываем баллы по каждой черте
    for answer_idx in answers:
        question_num = answers.index(answer_idx)
        if question_num < len(QUIZ_QUESTIONS):
            question = QUIZ_QUESTIONS[question_num]
            if answer_idx < len(question['options']):
                traits = question['options'][answer_idx]['traits']
                for trait in traits:
                    trait_scores[trait] = trait_scores.get(trait, 0) + 1

    # Определяем доминирующий профиль
    profile_scores = {
        'technical': sum([trait_scores.get(t, 0) for t in ['technical', 'logical']]),
        'analytical': sum([trait_scores.get(t, 0) for t in ['analytical', 'research', 'detail-oriented']]),
        'creative': sum([trait_scores.get(t, 0) for t in ['creative', 'artistic', 'freedom']]),
        'social': sum([trait_scores.get(t, 0) for t in ['social', 'communication', 'helping', 'leadership']]),
        'balanced': sum([trait_scores.get(t, 0) for t in ['balanced', 'adaptable', 'flexible']])
    }

    # Находим профиль с максимальным баллом
    max_profile = max(profile_scores, key=profile_scores.get)

    # Если баллы равномерно распределены - универсал
    if len(set(profile_scores.values())) <= 2:
        max_profile = 'balanced'

    return {
        'profile': max_profile,
        'scores': profile_scores,
        'trait_scores': trait_scores
    }


def get_quiz_result_message(result):
    '''Формирование сообщения с результатом'''
    profile = CAREER_PROFILES[result['profile']]

    message = f"🎯 <b>Результаты теста на профориентацию</b>\n\n"
    message += f"<b>{profile['name']}</b>\n\n"
    message += f"{profile['description']}\n\n"
    message += f"<b>Подходящие профессии:</b>\n"

    for profession in profile['professions']:
        message += f"• {profession}\n"

    message += f"\n💡 Используй команду /search чтобы узнать зарплаты по этим профессиям!"

    return message


class QuizSession:
    '''Класс для управления сессией викторины'''

    def __init__(self):
        self.sessions = {}

    def start_quiz(self, user_id):
        '''Начало викторины'''
        self.sessions[user_id] = {
            'current_question': 0,
            'answers': []
        }

    def get_current_question(self, user_id):
        '''Получение текущего вопроса'''
        if user_id not in self.sessions:
            return None

        session = self.sessions[user_id]
        question_num = session['current_question']

        if question_num >= len(QUIZ_QUESTIONS):
            return None

        return QUIZ_QUESTIONS[question_num]

    def add_answer(self, user_id, answer_idx):
        '''Добавление ответа'''
        if user_id not in self.sessions:
            return False

        self.sessions[user_id]['answers'].append(answer_idx)
        self.sessions[user_id]['current_question'] += 1
        return True

    def is_quiz_complete(self, user_id):
        '''Проверка завершения викторины'''
        if user_id not in self.sessions:
            return False

        return self.sessions[user_id]['current_question'] >= len(QUIZ_QUESTIONS)

    def get_result(self, user_id):
        '''Получение результата викторины'''
        if user_id not in self.sessions:
            return None

        answers = self.sessions[user_id]['answers']
        return calculate_quiz_result(answers)

    def end_quiz(self, user_id):
        '''Завершение викторины'''
        if user_id in self.sessions:
            del self.sessions[user_id]

