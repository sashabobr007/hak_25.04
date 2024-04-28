import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging
from aiogram.utils import executor
import os
from dotenv import load_dotenv
import pandas as pd
from requests import get
import psycopg2
from schemas import *
from database import *
from models import *
from sqlalchemy.orm import Session
from new import *
from algos import *
from datetime import datetime



questions = [
    "На шкале от 1 до 10, насколько вы готовы поделиться вашим мнением о вебинаре?",
    "Что вам больше всего понравилось в теме вебинара и почему?",
    "Были ли моменты в вебинаре, которые вызвали затруднения в понимании материала? Можете описать их?",
    "Какие аспекты вебинара, по вашему мнению, нуждаются в улучшении и какие конкретные изменения вы бы предложили?",
    "Есть ли темы или вопросы, которые вы бы хотели изучить более подробно в следующих занятиях?"
]

user_data = {}

def get_keyboard(options):
    buttons = [KeyboardButton(option) for option in options]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


def tel_bot():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher(bot)

    @dp.message_handler(commands=['start'])
    async def start_message(message: types.Message):
       # print(message.chat.id)
       user_id = message.chat.id
       user_data[user_id] = {}
       await message.answer('Здравствуйте, Я Виртуальный помощник по сбору обратной связи от Geekbrains.'
                            ' Недавно вы смотрели вебинар "Основы программирования".')
       await message.answer('Обратная связь помогает нам делать программы и вебинары лучше и совершенствоваться.'
                            ' Пожалуйста, оцените по шкале от 1 до 10, насколько вы готовы поделиться вашим мнением о вебинаре')
       await message.answer(questions[0],
                            reply_markup=get_keyboard(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']))


    @dp.message_handler()
    async def answer_handler(message: types.Message):
        user_id = message.from_user.id
        user_answers = user_data.get(user_id, {})
        current_question_index = len(user_answers)

        if current_question_index < len(questions):
            user_answers[current_question_index] = message.text
            user_data[user_id] = user_answers

            next_question_index = current_question_index + 1
            if next_question_index < len(questions):
                await message.answer(questions[next_question_index])
            else:
                await message.answer("Спасибо за ваши ответы, они помогут нам стать лучше!")
                db = SessionLocal()
                feedback = ['Основы программирования', user_answers[1], user_answers[2], user_answers[3],
                            user_answers[4]]
                pos = predict(pos_model, feedback)
                obj = predict(obj_model, feedback)
                rel = predict(rel_model, feedback)
                ob = {
                    'webinar': '0',
                    'program': '1',
                    'tutor': '2'
                }

                out = {
                    "timestamp": datetime.now(),
                    "program": 'Основы программирования',
                    "question_1": user_answers[0],
                    "question_2": user_answers[1],
                    "question_3": user_answers[2],
                    "question_4": user_answers[3],
                    "question_5": user_answers[4],
                    "is_relevant": int(rel[0]['label'] == 'relevant'),
            "is_relevant_proc": rel[0]['score'],
            "is_positive": int(pos[0]['label'] == 'positive'),
            "is_positive_proc": pos[0]['score'],
            "object": ob[obj[0]['label']],
            "object_proc": obj[0]['score'],
            "metodist_positive_ind_1_present": 0,
            'metodist_positive_ind_2_knowledgepractice': 0,
            "metodist_positive_ind_3_knowledge": 0,
            "professor_positive__ind_1_speach": 0,
            "professor_positive__ind_2_material": 0,
            "professor_positive__ind_3_communication": 0,
            "metodist_negative_ind_1_badexamples": 0,
            "metodist_negative_ind_2_badmaterial": 0,
            "metodist_negative_ind_3_badknowledge": 0,
            "professor_negative__ind_1_badspeach": 0,
            "professor_negative__ind_2_badmaterial": 0,
            "professor_negative__ind_3_badcommunication": 0,
                    "professorname": random.choice(professors['Основы программирования']),
                    "metodistname": metodists['Основы программирования'],
                    'is_critical': 0
                }

                words = ['проблемы', 'подключение', 'ужасно', 'отвратительный', 'игнорируют', 'не отвечают',
                         'поддержка']
                if words_in_sentence(words, '  '.join(feedback)):
                    out['is_critical'] = 1
                    #return out

                # if rel_model(feedback)[0]['label'] == 'not_relevant':
                #     return out

                positive = pos_model(feedback)[0]['label'] == 'positive'
                obj = obj_model(feedback)[0]['label']

                if positive:
                    if obj == 'webinar':
                        words = ['увлекательно', 'простой', 'понятный', 'спасибо']
                        out['metodist_positive_ind_1_present'] = words_in_sentence(words, feedback[1])
                        words = ['карьера', 'работа', 'собеседование', 'будущее']
                        out['metodist_positive_ind_2_knowledgepractice'] = max(words_in_sentence(['нет'], feedback[2]),
                                                                               words_in_sentence(words, feedback[1]))
                        words = ['актуальный', 'современный', 'полезный']
                        out['metodist_positive_ind_3_knowledge'] = words_in_sentence(words, feedback[1])
                    elif obj == 'tutor':
                        words = ['впечатляющий', 'интересный', 'захватывающий', 'познавательный', 'увлекательно',
                                 'простой',
                                 'понятный', 'спасибо']
                        out['professor_positive__ind_1_speach'] = words_in_sentence(words, feedback[1])
                        words = ['отвечает', 'помогает', 'помощь', 'лучший', 'купите мне шаурму']
                        out['professor_positive__ind_3_communication'] = max(words_in_sentence(['нет'], feedback[2]),
                                                                             words_in_sentence(words, feedback[1]))
                        words = ['актуальный', 'современный', 'полезный']
                        out['professor_positive__ind_2_material'] = words_in_sentence(words, feedback[1])
                else:
                    if obj == 'webinar':
                        words = ['нет структуры', 'непонятно', 'плохо', 'не понял']
                        out['metodist_negative_ind_1_badexamples'] = words_in_sentence(words,
                                                                                       feedback[2] + ' ' + feedback[3])
                        words = ['неактуально', 'неинтересно', 'фигня']
                        out['metodist_negative_ind_2_badmaterial'] = words_in_sentence(words,
                                                                                       feedback[2] + ' ' + feedback[3])
                        words = ['устаревший', 'неактуальный', 'плохой']
                        out['metodist_negative_ind_3_badknowledge'] = words_in_sentence(words,
                                                                                        feedback[2] + ' ' + feedback[3])
                    elif obj == 'tutor':
                        words = ['скучный', 'трудности', 'сложный', 'монотонный', 'запутанный', 'мало']
                        out['professor_negative__ind_1_badspeach'] = words_in_sentence(words,
                                                                                       feedback[2] + ' ' + feedback[3])
                        words = ['плохо', 'грубый']
                        out['professor_negative__ind_3_badcommunication'] = words_in_sentence(words,
                                                                                              feedback[2] + ' ' +
                                                                                              feedback[3])
                        words = ['не знает', 'неактуально', 'не разбирается']
                        out['professor_negative__ind_2_badmaterial'] = words_in_sentence(words,
                                                                                         feedback[2] + ' ' + feedback[
                                                                                             3])

                # Вставка данных
                insert_statement = feedback_table.insert().values(out)
                db.execute(insert_statement)
                db.commit()
                db.close()


        else:
            await message.answer("Вы уже ответили на все вопросы.\nНажмите /start чтобы оставить отзыв заново.")

    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    tel_bot()