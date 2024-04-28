from sqlalchemy import create_engine, MetaData, Table, Column, String, Boolean, Float, DateTime, Integer
from sqlalchemy.sql.schema import Column
from database import Base

metadata = MetaData()


feedback_table = Table(
    "feedback",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("timestamp", DateTime, nullable=False),
    Column("program", String),
    Column("question_1", String),
    Column("question_2", String),
    Column("question_3", String),
    Column("question_4", String),
    Column("question_5", String),
    Column("is_relevant", Integer),
    Column("is_relevant_proc", Float),
    Column("is_positive", Integer),
    Column("is_positive_proc", Float),
    Column("object", String),
    Column("object_proc", Float),
    Column("metodist_positive_ind_1_present", Integer),
    Column("metodist_positive_ind_2_knowledgepractice", Integer),
    Column("metodist_positive_ind_3_knowledge", Integer),
    Column("professor_positive__ind_1_speach", Integer),
    Column("professor_positive__ind_2_material", Integer),
    Column("professor_positive__ind_3_communication", Integer),
    Column("metodist_negative_ind_1_badexamples", Integer),
    Column("metodist_negative_ind_2_badmaterial", Integer),
    Column("metodist_negative_ind_3_badknowledge", Integer),
    Column("professor_negative__ind_1_badspeach", Integer),
    Column("professor_negative__ind_2_badmaterial", Integer),
    Column("professor_negative__ind_3_badcommunication", Integer),
    Column("professorname", String),
    Column("metodistname", String),
    Column("is_critical", String))

