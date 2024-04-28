import pandas as pd
df = pd.read_csv('df-2.csv')
dict6 = {'percent_of_good_reviews': df[df.program == 'Основы программирования'].is_positive.mean(),
             'percent_like_present': df[df.program == 'Основы программирования'][
                 'professor_positive__ind_1_speach'].mean(),
             'percent_like_knowledgepractice': df[df.program == 'Основы программирования'][
                 'professor_positive__ind_2_material'].mean(),
             'percent_like_knowledge': df[df.program == 'Основы программирования'][
                 'professor_positive__ind_3_communication'].mean()}

df = pd.DataFrame.from_dict(dict6, orient='index')
df.to_excel('df_analitika.xlsx')