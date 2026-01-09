import requests
import json
import pandas as pd
from time import sleep
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import seaborn as sns
import converter
import numpy as np

# Настройка стиля графиков
sns.set(style='whitegrid', font_scale=1.2, palette='Set2')
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False


class VacancyStats:
    '''Расширенная статистика по вакансиям'''

    # Словарь городов
    CITIES = {
        1: 'Москва',
        2: 'Санкт-Петербург',
        3: 'Екатеринбург',
        4: 'Новосибирск',
        88: 'Казань',
        66: 'Нижний Новгород',
        113: 'Россия'
    }

    # Опыт работы
    EXPERIENCE = {
        'noExperience': 'Без опыта',
        'between1And3': '1-3 года',
        'between3And6': '3-6 лет',
        'moreThan6': 'Более 6 лет'
    }

    def __init__(self, query, city_id=1, experience=None, remote_only=False):
        '''Инициализация с фильтрами'''
        URL = 'https://api.hh.ru/vacancies'
        params = {
            'area': city_id,
            'page': 0,
            'per_page': 100,
            'text': query
        }

        if experience and experience != 'all':
            params['experience'] = experience

        if remote_only:
            params['schedule'] = 'remote'

        self.query = query
        self.city_id = city_id
        self.city_name = self.CITIES.get(city_id, 'Неизвестно')
        self.df = pd.DataFrame()

        try:
            req = requests.get(URL, params, timeout=10)
            data = json.loads(req.content.decode())
            pages = min(data.get('pages', 0), 20)  # Ограничим 20 страницами

            for page in range(pages):
                params['page'] = page
                req = requests.get(URL, params, timeout=10)
                data = json.loads(req.content.decode())
                self.df = pd.concat([self.df, pd.json_normalize(
                    data['items'])], ignore_index=True)
                sleep(0.5)  # Чтобы не нагружать API

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")

    def prepare_salary_data(self):
        '''Подготовка данных по зарплатам'''
        if len(self.df) == 0:
            return False

        # Рассчитываем среднюю зарплату
        self.df['salary'] = (self.df['salary.from'].fillna(0) +
                            self.df['salary.to'].fillna(0)) / 2

        # Если одно из значений 0, берем другое
        self.df.loc[self.df['salary.from'].isna() & self.df['salary.to'].notna(), 'salary'] = \
            self.df['salary.to']
        self.df.loc[self.df['salary.to'].isna() & self.df['salary.from'].notna(), 'salary'] = \
            self.df['salary.from']

        # Конвертируем в рубли
        self.df['salary'] = self.df.apply(converter.convert_to_rub, axis=1)
        self.df['salary'] = self.df.apply(converter.convert_to_net, axis=1)

        # Фильтруем разумные значения
        self.df = self.df[self.df['salary'] > 0]
        self.df = self.df[self.df['salary'] < 1000000]  # Убираем явные выбросы

        return len(self.df) > 0

    def get_basic_stats(self):
        '''Базовая статистика по зарплатам'''
        if not self.prepare_salary_data():
            return None

        stats = {
            'count': len(self.df),
            'mean': int(self.df['salary'].mean()),
            'median': int(self.df['salary'].median()),
            'min': int(self.df['salary'].min()),
            'max': int(self.df['salary'].max()),
            'std': int(self.df['salary'].std()),
            'percentile_25': int(self.df['salary'].quantile(0.25)),
            'percentile_75': int(self.df['salary'].quantile(0.75))
        }
        return stats

    def get_top_employers(self, limit=5):
        '''Топ работодателей по количеству вакансий'''
        if len(self.df) == 0:
            return []

        employers = self.df['employer.name'].value_counts().head(limit)
        return [(name, count) for name, count in employers.items()]

    def get_top_paid_employers(self, limit=5):
        '''Топ работодателей по зарплате'''
        if not self.prepare_salary_data():
            return []

        avg_salary = self.df.groupby('employer.name')['salary'].mean()
        top_employers = avg_salary.nlargest(limit)
        return [(name, int(salary)) for name, salary in top_employers.items()]

    def get_experience_distribution(self):
        '''Распределение по опыту работы'''
        if 'experience.name' not in self.df.columns:
            return {}

        exp_dist = self.df['experience.name'].value_counts().to_dict()
        return exp_dist

    def get_employment_type_distribution(self):
        '''Распределение по типу занятости'''
        if 'employment.name' not in self.df.columns:
            return {}

        emp_dist = self.df['employment.name'].value_counts().to_dict()
        return emp_dist

    def create_salary_histogram(self, filename='salaries.png'):
        '''Создание гистограммы зарплат'''
        if not self.prepare_salary_data():
            return False

        fig, ax = plt.subplots(figsize=(12, 7))

        # Гистограмма
        ax.hist(self.df['salary'], bins=30, color='#3498db', alpha=0.7, edgecolor='black')

        # Линии для медианы и среднего
        median = self.df['salary'].median()
        mean = self.df['salary'].mean()

        ax.axvline(median, color='red', linestyle='--', linewidth=2, label=f'Медиана: {int(median):,} ₽')
        ax.axvline(mean, color='green', linestyle='--', linewidth=2, label=f'Среднее: {int(mean):,} ₽')

        ax.set_xlabel('Заработная плата (₽)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Количество вакансий', fontsize=12, fontweight='bold')
        ax.set_title(f'Распределение зарплат: {self.query}\n{self.city_name}',
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        # Форматирование оси X
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        return True

    def create_detailed_report(self, filename='report.png'):
        '''Создание детального отчета с несколькими графиками'''
        if not self.prepare_salary_data():
            return False

        fig = plt.figure(figsize=(16, 10))

        # 1. Гистограмма зарплат
        ax1 = plt.subplot(2, 3, 1)
        ax1.hist(self.df['salary'], bins=25, color='#3498db', alpha=0.7, edgecolor='black')
        ax1.axvline(self.df['salary'].median(), color='red', linestyle='--', linewidth=2)
        ax1.set_xlabel('Зарплата (₽)')
        ax1.set_ylabel('Количество')
        ax1.set_title('Распределение зарплат')
        ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))

        # 2. Топ работодателей
        ax2 = plt.subplot(2, 3, 2)
        top_emp = self.get_top_employers(10)
        if top_emp:
            names, counts = zip(*top_emp)
            ax2.barh(range(len(names)), counts, color='#2ecc71')
            ax2.set_yticks(range(len(names)))
            ax2.set_yticklabels([n[:25] + '...' if len(n) > 25 else n for n in names], fontsize=9)
            ax2.set_xlabel('Количество вакансий')
            ax2.set_title('Топ работодателей')
            ax2.invert_yaxis()

        # 3. Опыт работы
        ax3 = plt.subplot(2, 3, 3)
        exp_dist = self.get_experience_distribution()
        if exp_dist:
            colors = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6']
            ax3.pie(exp_dist.values(), labels=exp_dist.keys(), autopct='%1.1f%%',
                   colors=colors, startangle=90)
            ax3.set_title('Распределение по опыту')

        # 4. Тип занятости
        ax4 = plt.subplot(2, 3, 4)
        emp_dist = self.get_employment_type_distribution()
        if emp_dist:
            ax4.bar(range(len(emp_dist)), emp_dist.values(), color='#1abc9c')
            ax4.set_xticks(range(len(emp_dist)))
            ax4.set_xticklabels(emp_dist.keys(), rotation=45, ha='right', fontsize=9)
            ax4.set_ylabel('Количество')
            ax4.set_title('Тип занятости')

        # 5. Box plot зарплат
        ax5 = plt.subplot(2, 3, 5)
        ax5.boxplot(self.df['salary'], vert=True)
        ax5.set_ylabel('Зарплата (₽)')
        ax5.set_title('Статистика зарплат')
        ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))

        plt.suptitle(f'Детальный анализ: {self.query} | {self.city_name}',
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        return True

    def create_comparison_chart(self, other_stats_list, filename='comparison.png'):
        '''Создание сравнительного графика для нескольких профессий'''
        fig, ax = plt.subplots(figsize=(14, 8))

        professions = [self.query] + [s.query for s in other_stats_list]
        medians = []
        means = []

        # Собираем статистику
        all_stats = [self] + other_stats_list
        for stat in all_stats:
            if stat.prepare_salary_data():
                medians.append(stat.df['salary'].median())
                means.append(stat.df['salary'].mean())
            else:
                medians.append(0)
                means.append(0)

        x = np.arange(len(professions))
        width = 0.35

        bars1 = ax.bar(x - width/2, medians, width, label='Медиана', color='#3498db')
        bars2 = ax.bar(x + width/2, means, width, label='Среднее', color='#2ecc71')

        ax.set_xlabel('Профессия', fontsize=12, fontweight='bold')
        ax.set_ylabel('Зарплата (₽)', fontsize=12, fontweight='bold')
        ax.set_title('Сравнение зарплат по профессиям', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(professions, rotation=15, ha='right')
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))

        # Добавляем значения на столбцы
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height/1000)}k',
                           ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        return True


def format_stats_message(stats_obj):
    '''Форматирование сообщения со статистикой'''
    stats = stats_obj.get_basic_stats()

    if not stats:
        return "❌ Не удалось получить статистику. Попробуй другой запрос."

    msg = f"📊 <b>Статистика по запросу: {stats_obj.query}</b>\n"
    msg += f"📍 Город: {stats_obj.city_name}\n\n"

    msg += f"💰 <b>Зарплаты:</b>\n"
    msg += f"  • Найдено вакансий с зарплатой: {stats['count']}\n"
    msg += f"  • Медиана: {stats['median']:,} ₽\n"
    msg += f"  • Среднее: {stats['mean']:,} ₽\n"
    msg += f"  • Минимум: {stats['min']:,} ₽\n"
    msg += f"  • Максимум: {stats['max']:,} ₽\n"
    msg += f"  • 25% перцентиль: {stats['percentile_25']:,} ₽\n"
    msg += f"  • 75% перцентиль: {stats['percentile_75']:,} ₽\n\n"

    # Топ работодателей по зарплате
    top_paid = stats_obj.get_top_paid_employers(5)
    if top_paid:
        msg += f"🏆 <b>Топ работодателей по зарплате:</b>\n"
        for i, (name, salary) in enumerate(top_paid, 1):
            msg += f"  {i}. {name[:40]}{'...' if len(name) > 40 else ''}: {salary:,} ₽\n"
        msg += "\n"

    return msg

