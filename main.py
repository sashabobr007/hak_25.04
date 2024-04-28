from fastapi import FastAPI, Depends, File, UploadFile, Response
import uvicorn
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from database import get_db
from models import *
import pandas as pd
from requests import get
import psycopg2


sql_query = "SELECT * FROM feedback"

# Connect to the PostgreSQL database
#conn = psycopg2.connect(database='vk', user='aleksandralekseev', host='localhost', password='')
conn = psycopg2.connect(database='vk', user='postgres', host='localhost', password='1712')

# Create a cursor object
cursor = conn.cursor()

# Execute the SQL query
cursor.execute(sql_query)

# Fetch all rows from the result set
rows = cursor.fetchall()

# Get column names from the cursor description
column_names = [desc[0] for desc in cursor.description]

# Close the cursor and connection
cursor.close()
conn.close()

# Create a Pandas DataFrame from the fetched data
df = pd.DataFrame(rows, columns=column_names)

# Print or use the DataFrame as needed
df.to_csv('df.csv')

df.to_excel('df.xlsx')

dict1 = {'percent_of_good_reviews': df[df.program == 'Основы программирования'].is_positive.mean(),
         'percent_like_present': df[df.program == 'Основы программирования']['metodist_positive_ind_1_present'].mean(),
         'percent_like_knowledgepractice': df[df.program == 'Основы программирования']['metodist_positive_ind_2_knowledgepractice'].mean(),
         'percent_like_knowledge': df[df.program == 'Основы программирования']['metodist_positive_ind_3_knowledge'].mean()}

dict2 = {'percent_of_good_reviews': df[df.program == 'Основы программирования'].is_positive.mean(),
         'percent_of_bad_reviews': 1 - df[df.program == 'Основы программирования'].is_positive.mean(),
         'percent_of_good_inf_reviews': df[df.program == 'Основы программирования'].is_relevant.mean(),
         'percent_of_bad_inf_reviews': 1 - df[df.program == 'Основы программирования'].is_relevant.mean(),
         'percent_object_0': (df[df.program == 'Основы программирования'].object == 0).mean(),
         'percent_object_1': (df[df.program == 'Основы программирования'].object == 1).mean(),
         'percent_object_2': (df[df.program == 'Основы программирования'].object == 2).mean(),
         'percent_notlike_present': 1 - df[df.program == 'Основы программирования']['metodist_positive_ind_1_present'].mean(),
         'percent_notlike_knowledgePractice': 1 - df[df.program == 'Основы программирования']['metodist_positive_ind_2_knowledgepractice'].mean(),
         'percent_notlike_knowledge': 1 - df[df.program == 'Основы программирования']['metodist_positive_ind_3_knowledge'].mean(),
         'marks_good': ((df[df.program == 'Основы программирования'].is_positive == 1) & (df[df.program == 'Основы программирования'].is_positive_proc > 0.75)).mean(),
         'marks_middle': ((df[df.program == 'Основы программирования'].is_positive == 1) & (df[df.program == 'Основы программирования'].is_positive_proc <= 0.75)).mean(),
         'marks_bad': (df[df.program == 'Основы программирования'].is_positive == 0).mean()}

dict6 = {'percent_of_good_reviews': df[df.program == 'Основы программирования'].is_positive.mean(),
         'percent_like_present': df[df.program == 'Основы программирования']['professor_positive__ind_1_speach'].mean(),
         'percent_like_knowledgepractice': df[df.program == 'Основы программирования']['professor_positive__ind_2_material'].mean(),
         'percent_like_knowledge': df[df.program == 'Основы программирования']['professor_positive__ind_3_communication'].mean()}

dict7 = {'percent_of_good_reviews': df[df.program == 'Основы программирования'].is_positive.mean(),
         'percent_of_bad_reviews': 1 - df[df.program == 'Основы программирования'].is_positive.mean(),
         'percent_of_good_inf_reviews': df[df.program == 'Основы программирования'].is_relevant.mean(),
         'percent_of_bad_inf_reviews': 1 - df[df.program == 'Основы программирования'].is_relevant.mean(),
         'percent_object_0': (df[df.program == 'Основы программирования'].object == 0).mean(),
         'percent_object_1': (df[df.program == 'Основы программирования'].object == 1).mean(),
         'percent_object_2': (df[df.program == 'Основы программирования'].object == 2).mean(),
         'percent_notlike_present': 1 - df[df.program == 'Основы программирования']['professor_positive__ind_1_speach'].mean(),
         'percent_notlike_knowledgePractice': 1 - df[df.program == 'Основы программирования']['professor_positive__ind_2_material'].mean(),
         'percent_notlike_knowledge': 1 - df[df.program == 'Основы программирования']['professor_positive__ind_3_communication'].mean(),
         'marks_good': ((df[df.program == 'Основы программирования'].is_positive == 1) & (df[df.program == 'Основы программирования'].is_positive_proc > 0.75)).mean(),
         'marks_middle': ((df[df.program == 'Основы программирования'].is_positive == 1) & (df[df.program == 'Основы программирования'].is_positive_proc <= 0.75)).mean(),
         'marks_bad': (df[df.program == 'Основы программирования'].is_positive == 0).mean()}

a = 1 - df[df.program == 'Основы программирования']['metodist_positive_ind_1_present'].mean()
b = 1 - df[df.program == 'Основы программирования']['metodist_positive_ind_2_knowledgepractice'].mean()
c = 1 - df[df.program == 'Основы программирования']['metodist_positive_ind_3_knowledge'].mean()

dict3 = {'need_improve': 'Отсутствие структуры вебинара' if a > b and a > c else 'Неактуальный материал' if b > a and b > c else 'Неактуальные примеры',
 'student_suggestion': df[df.program == 'Основы программирования'].question_5.sort_values(key=lambda x: x.str.len()).values[-1]}

dict4 = [{'id': row.id,
          'text': ' '.join(str(row[f'question_{i}']) for i in range(1, 6)),
          'is_positive': 0,
          'relevance': 1,
          'object': row.object}
         for idx, row in df.iterrows() if row.is_critical]

dict5 = [{'id': row.id,
          'text': ' '.join(str(row[f'question_{i}']) for i in range(1, 6)),
          'is_positive': row.is_positive,
          'relevance': row.is_relevant,
          'object': row.object}
         for idx, row in df.iterrows() if row.program == 'Основы программирования']

admin_list_metodist = []
for metodist in df.metodistname.unique():
  mini_df = df[df.metodistname == metodist]
  admin_list_metodist.append({'name': metodist,
                          'programm': df.iloc[0].program,
                          'percent_of_good_reviews': mini_df.is_positive.mean(),
                          'percent_like_present': mini_df.metodist_positive_ind_1_present.mean(),
                          'percent_like_knowledgepractice': mini_df.metodist_positive_ind_2_knowledgepractice.mean(),
                          'percent_like_knowledge': mini_df.metodist_positive_ind_3_knowledge.mean()})

admin_list_teacher = []
for teacher in df.professorname.unique():
  mini_df = df[df.professorname == teacher]
  admin_list_teacher.append({'name': teacher,
                          'programm': df.iloc[0].program,
                          'percent_of_good_reviews': mini_df.is_positive.mean(),
                          'percent_like_present': mini_df. professor_positive__ind_1_speach.mean(),
                          'percent_like_knowledgepractice': mini_df.professor_positive__ind_2_material.mean(),
                          'percent_like_knowledge': mini_df.professor_positive__ind_3_communication.mean()})

# ob = {0: "webinar", 1: "program", 2: "tutor"}
# d = []
# for idx, row in df[df['is_positive'] == 0].sort_values('is_positive_proc')[-3:].iterrows():
#     d.append({'id': row.id,
#          'text': ' '.join(str(row[f'question_{i}']) for i in range(1, 6)),
#          'is_positive': row.is_positive,
#          'relevance': row.is_relevant,
#          'object': ob[row.object]})

df.timestamp = pd.to_datetime(df.timestamp)
start = pd.to_datetime("2024-04-01")
end = pd.to_datetime("2024-04-06")
npc1 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-07")
end = pd.to_datetime("2024-04-12")
npc2 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-13")
end = pd.to_datetime("2024-04-18")
npc3 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-19")
end = pd.to_datetime("2024-04-25")
npc4 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()

graph_1 = [
  {
    "name": "01.04-06.04",
    "NPC": npc1
  },
 {
    "name": "07.04-12.04",
    "NPC": npc2
  },
 {
    "name": "13.04-18.04",
    "NPC": npc3
  },
 {
    "name": "19.04-25.04",
    "NPC": npc4
  }
 ]

met = 'Лебедев'
mini_df = df[df.metodistname == met]

graph_2 = [
  {
    "name": "качество Презентации",
    "val": mini_df.metodist_positive_ind_1_present.mean()
  },
 {
    "name": "Актуальность материала",
    "val": mini_df.metodist_positive_ind_2_knowledgepractice.mean()
  },
 {
    "name": "Актуальные бизнес примеры",
    "val": mini_df.metodist_positive_ind_3_knowledge.mean()
  }
 ]

graph_3=[
  {
    "name": "Плохая структура вебинара",
    "val": mini_df.metodist_negative_ind_1_badexamples.mean()
  },
 {
    "name": "Неактуальный материал",
    "val": mini_df.metodist_negative_ind_2_badmaterial.mean()
  },
 {
    "name": "Неактуальные примеры",
    "val": mini_df.metodist_negative_ind_3_badknowledge.mean()
  }
 ]

graph_4 = [
  {
    "name": "Преподаватель",
    "val": mini_df[mini_df.object == 2].id.count()
  },
 {
    "name": "Вебинар",
    "val": mini_df[mini_df.object == 0].id.count()
  },
 {
    "name": "Программа",
    "val": mini_df[mini_df.object == 1].id.count()
  }
 ]

start = pd.to_datetime("2024-04-01")
end = pd.to_datetime("2024-04-06")
npc1 = mini_df[(mini_df.program == "Основы программирования") & (mini_df.timestamp >= start) & (mini_df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-07")
end = pd.to_datetime("2024-04-12")
npc2 = mini_df[(mini_df.program == "Основы программирования") & (mini_df.timestamp >= start) & (mini_df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-13")
end = pd.to_datetime("2024-04-18")
npc3 = mini_df[(mini_df.program == "Основы программирования") & (mini_df.timestamp >= start) & (mini_df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-19")
end = pd.to_datetime("2024-04-25")
npc4 = mini_df[(mini_df.program == "Основы программирования") & (mini_df.timestamp >= start) & (mini_df.timestamp <= end)].is_positive.mean()

graph_5 = [
  {
    "name": "01.04-06.04",
    "val": npc1
  },
 {
    "name": "07.04-12.04",
    "val": npc2
  },
 {
    "name": "13.04-18.04",
    "val": npc3
  },
 {
    "name": "19.04-25.04",
    "val": npc4
  }
 ]

df.timestamp = pd.to_datetime(df.timestamp)
start = pd.to_datetime("2024-04-01")
end = pd.to_datetime("2024-04-06")
npc1 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-07")
end = pd.to_datetime("2024-04-12")
npc2 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-13")
end = pd.to_datetime("2024-04-18")
npc3 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()
start = pd.to_datetime("2024-04-19")
end = pd.to_datetime("2024-04-25")
npc4 = df[(df.program == "Основы программирования") & (df.timestamp >= start) & (df.timestamp <= end)].is_positive.mean()

graph_6 = [
  {
    "name": "01.04-06.04",
    "NPC": npc1
  },
 {
    "name": "07.04-12.04",
    "NPC": npc2
  },
 {
    "name": "13.04-18.04",
    "NPC": npc3
  },
 {
    "name": "19.04-25.04",
    "NPC": npc4
  }
 ]

met = 'Петров'
mini_df = df[df.professorname == met]

graph_7 = [
  {
    "name": "Доступно объясняет материал",
    "val": mini_df.professor_positive__ind_1_speach.mean()
  },
 {
    "name": "Коммуникабельность",
    "val": mini_df.professor_positive__ind_2_material.mean()
  },
 {
    "name": "Хорошая осведомленность в тематике",
    "val": mini_df.professor_positive__ind_3_communication.mean()
  }
 ]

graph_8=[
  {
    "name": "Плохая речь",
    "val": mini_df.professor_negative__ind_1_badspeach.mean()
  },
 {
    "name": "плохое знание материала",
    "val": mini_df.professor_negative__ind_2_badmaterial.mean()
  },
 {
    "name": "плохая коммуникабельность",
    "val": mini_df.professor_negative__ind_3_badcommunication.mean()
  }
 ]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/MetodistPersonalCard/")
async def read_root():
    return dict1


@app.get("/TeacherPersonalCard/")
async def read_root():
    return dict6

@app.get("/TeacherTotal/")
async def read_root():
    return dict7

@app.get("/MetodistTotal/")
async def read_root():
    return dict2

@app.get("/metodistGetBetter/")
async def read_root():
    return dict3

@app.get("/AdminImportant/")
async def read_root():
    return dict4

@app.get("/metodistList/")
async def read_root():
    return dict5

@app.get("/AdminListMetodist/")
async def read_root():
    return admin_list_metodist

@app.get("/AdminListTeacher/")
async def read_root():
    return admin_list_teacher
#
# @app.get("/MetodistPersonalCard/")
# async def read_root():
#     return d


@app.get("/MetodistGraphs1/")
async def read_root():
    return graph_1

@app.get("/MetodistGraphs2/")
async def read_root():
    return graph_2

@app.get("/MetodistGraphs3/")
async def read_root():
    return graph_3

# @app.get("/MetodistGraphs4/")
# async def read_root():
#     return graph_4

@app.get("/MetodistGraphs5/")
async def read_root():
    return graph_5

@app.get("/TeacherGraphs1/")
async def read_root():
    return graph_6

@app.get("/TeacherGraphs2/")
async def read_root():
    return graph_7

@app.get("/TeacherGraphs3/")
async def read_root():
    return graph_8

@app.get("/exel_data/")
async def exel_analitika():
    filename = "df.xlsx"
    return FileResponse(filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=filename)

@app.get("/exel_analitika/")
async def exel_analitika():
    filename = "df.xlsx"
    return FileResponse(filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=filename)

@app.delete("/")
async def kill():
    os.kill(os.getpid(), 9)
    return {"message": "error"}


if __name__ == "__main__":
    uvicorn.run(app , port=8000)
    #uvicorn.run(app, host='0.0.0.0' , port=8000)
