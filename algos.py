import pandas as pd
import psycopg2
from database import *
from models import *
from sqlalchemy.orm import Session
import random
from transformers import pipeline
from difflib import get_close_matches

professors = { 'Основы программирования' : ["Иванов", "Петров"],
               'Продвинутые техники программирования' : ["Кузнецова", "Васильева"],
               'Новейшие тенденции в IT': ['Михайлова', 'Попов'],
               'ChatGPT для обучения' : ['Васильев', 'Соколов'],
               'Знакомство с языком Python' : ['Новиков', 'Федоров'],
                'Java api браузеров' : ['Морозов', 'Алексеев'],
'Управление персоналом' : ['Михайлов', 'Попов']
              }

metodists = {
                'Основы программирования' : "Лебедев",
               'Продвинутые техники программирования' : 'Семенов',
               'Новейшие тенденции в IT': 'Егоров',
               'ChatGPT для обучения' : 'Козлов',
               'Знакомство с языком Python' : 'Степанов',
                'Java api браузеров' : 'Никитин',
                'Управление персоналом' : 'Егоров'
}
def load_model(path_to_folder_with_model, device=None):
    model = pipeline('text-classification',
                   model=path_to_folder_with_model,
                   tokenizer='DeepPavlov/rubert-base-cased-conversational',
                   framework='pt',
                   device=device)
    return model

def predict(model, feedback):
    return model(feedback[1] + ' ' + feedback[3])

pos_model = load_model('pos_neg_model')
obj_model = load_model('object_model')
rel_model = load_model('relevant_model')

def words_in_sentence(words, sentence):
    for word in words:
        if get_close_matches(word, sentence.split()):
            return 1
    return 0


def insertt():

    df = pd.read_csv('train_data.csv')
    conn = psycopg2.connect(database='vk', user='postgres', host='localhost', password='1712')
    #conn = psycopg2.connect(database='vk', user='aleksandralekseev', host='localhost', password='')
    cur = conn.cursor()

    cur.execute("delete from feedback;")

    conn.commit()
    cur.close()
    conn.close()
    #
    # Вставляем данные из датафрейма в таблицу базы данных
    for index, row in df.iterrows():

        db = SessionLocal()
        feedback = [row['question_1'], row['question_2'],  row['question_3'], row['question_4'], row['question_5']]
        pos = predict(pos_model, feedback)
        obj = predict(obj_model, feedback)
        rel = predict(rel_model, feedback)
        ob = {
            'webinar' : '0',
            'program': '1',
            'tutor' : '2'
        }

        out = {
            "timestamp": row['timestamp'],
            "program": row['question_1'],
            "question_1": "10",
            "question_2": row['question_2'],
            "question_3": row['question_3'],
            "question_4": row['question_4'],
            "question_5": row['question_5'],
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
            "professorname": random.choice(professors[row['question_1']]),
            "metodistname": metodists[row['question_1']],
            'is_critical': 0
        }

        words = ['проблемы', 'подключение', 'ужасно', 'отвратительный', 'игнорируют', 'не отвечают', 'поддержка']
        if words_in_sentence(words, '  '.join(feedback)):
            out['is_critical'] = 1

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
                words = ['впечатляющий', 'интересный', 'захватывающий', 'познавательный', 'увлекательно', 'простой',
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
                out['metodist_negative_ind_1_badexamples'] = words_in_sentence(words, feedback[2] + ' ' + feedback[3])
                words = ['неактуально', 'неинтересно', 'фигня']
                out['metodist_negative_ind_2_badmaterial'] = words_in_sentence(words, feedback[2] + ' ' + feedback[3])
                words = ['устаревший', 'неактуальный', 'плохой']
                out['metodist_negative_ind_3_badknowledge'] = words_in_sentence(words, feedback[2] + ' ' + feedback[3])
            elif obj == 'tutor':
                words = ['скучный', 'трудности', 'сложный', 'монотонный', 'запутанный', 'мало']
                out['professor_negative__ind_1_badspeach'] = words_in_sentence(words, feedback[2] + ' ' + feedback[3])
                words = ['плохо', 'грубый']
                out['professor_negative__ind_3_badcommunication'] = words_in_sentence(words,
                                                                                      feedback[2] + ' ' + feedback[3])
                words = ['не знает', 'неактуально', 'не разбирается']
                out['professor_negative__ind_2_badmaterial'] = words_in_sentence(words, feedback[2] + ' ' + feedback[3])

        # Вставка данных
        insert_statement = feedback_table.insert().values(out)
        db.execute(insert_statement)
        db.commit()
        db.close()

        break


# def to_bd():
#     df = pd.read_csv('train_data_z.csv', sep=';')
#     conn = psycopg2.connect(database='vk', user='aleksandralekseev', host='localhost', password='')
#     cur = conn.cursor()
#
#     cur.execute("delete from feedback;")
#
#     conn.commit()
#     cur.close()
#     conn.close()
# #
#     # Вставляем данные из датафрейма в таблицу базы данных
#     for index, row in df.iterrows():
#         #print(row['Адрес'])
#         db = SessionLocal()
#
#         data = {
#             "timestamp": row['timestamp'],
#             "program": row['question_1'],
#             "question_1": "1",
#             "question_2": row['question_2'],
#             "question_3": row['question_3'],
#             "question_4": row['question_4'],
#             "question_5": row['question_5'],
#             "is_relevant": row['is_relevant'],
#             "is_relevant_proc": 0.85,
#             "is_positive": row['is_positive'],
#             "is_positive_proc": 0.92,
#             "object": row['object'],
#             "object_proc": 0.78,
#             "metodist_positive_ind_1_present": 0,
#             'metodist_positive_ind_2_knowledgepractice': 0,
#             "metodist_positive_ind_3_knowledge": 0,
#             "professor_positive__ind_1_speach": 0,
#             "professor_positive__ind_2_material": 0,
#             "professor_positive__ind_3_communication": 0,
#             "metodist_negative_ind_1_badexamples": 0,
#             "metodist_negative_ind_2_badmaterial": 0,
#             "metodist_negative_ind_3_badknowledge": 0,
#             "professor_negative__ind_1_badspeach": 0,
#             "professor_negative__ind_2_badmaterial": 0,
#             "professor_negative__ind_3_badcommunication": 0,
#             "professorname":  random.choice(professors[row['question_1']]),
#             "metodistname": metodists[row['question_1']]
#
#         }
#
#         # Вставка данных
#         insert_statement = feedback_table.insert().values(data)
#         db.execute(insert_statement)
#         db.commit()
#         db.close()



if __name__ == "__main__":
    insertt()
    #algoritm()
    #to_bd_day_tasks()
#     to_bd_workers()
#     to_bd_timesheet()
