import streamlit as st
import pandas as pd
from files.aws.aws_funcs import *
from files.db_server import make_request
import os


try:
    S3_BUCKET_NAME_PROJECTS = os.environ['S3_BUCKET_NAME_PROJECTS']
    AWS_ACCESS_KEY_PROJECTS = os.environ['AWS_ACCESS_KEY_PROJECTS']
    AWS_SECRET_KEY_PROJECTS = os.environ['AWS_SECRET_KEY_PROJECTS']
except:
    pass


TASKS_NUMBER_ALL = {
        1: 0,
        2: 134,
        3: 141,
        4: 0,
        5: 213,
        6: 162,
        7: 179,
        8: 309,
        9: 228,
        10: 0, 
        11: 134,
        12: 257,
        13: 64,
        14: 342,
        15: 302,
        16: 210,
        17: 237,
        18: 184,
        19: 134,
        20: 134,
        21: 134,
        22: 101,
        23: 277,
        24: 208,
        25: 324,
        26: 135,
        27: 180
    }

def get_tasks_dict():
    file = get_from_s3('students/student_tasks.csv')
    return pd.read_csv(file['Body'], index_col='Student')

def give_tasks(username):
    df = get_tasks_dict()
    student_tasks_dict = df.apply(
        lambda row: {int(task): TASKS_NUMBER_ALL[int(task)] for task, in_work in row.items() if in_work},
        axis=1
    ).to_dict()

    return student_tasks_dict[username]


def get_user_information() -> dict:
    query = "SELECT StudentID, Name FROM Students"
    results = make_request(query, 'tasks_done')
    return {username.lower(): user_id for user_id, username in results}


USERNAME_DICT = get_user_information()

MATH_TASKS_CONFIG = {
    'Тригонометрия': {
        'table_name': 'math_tasks_trig',
        's3_bucket': 'trigonometriya'
    },
    'Стереометрия': {
        'table_name': 'math_tasks_stereo',
        's3_bucket': 'math_tasks_stereo'
    },
    'Неравенство': {
        'table_name': 'math_tasks_ineq',
        's3_bucket': 'math_tasks_ineq'
    },
    'Планиметрия': {
        'table_name': 'math_tasks_plan',
        's3_bucket': 'math_tasks_plan'
    },
    'Экономика': {
        'table_name': 'math_tasks_econ',
        's3_bucket': 'math_tasks_econ'
    },
    'Параметр': {
        'table_name': 'math_tasks_param',
        's3_bucket': 'math_tasks_param'
    },
    'Последняя': {
        'table_name': 'math_tasks_last',
        's3_bucket': 'math_tasks_last'
    }
}

TABLE_NAMES = {task: config['table_name'] for task, config in MATH_TASKS_CONFIG.items()}
S3_BUCKET_NAMES = {task: config['s3_bucket'] for task, config in MATH_TASKS_CONFIG.items()}


FOR_LANGUAGE = '''
                <!DOCTYPE html>
                    <head>
                            <meta charset="utf-8">
                            <title>Tasks</title>
                        <style>
                            html *,
                            hr {
                                font-size: 16px;
                                line-height: 2.625;
                                color: #000000;
                                font-family: Nunito, sans-serif;
                                text-align: justify;
                            }

                            hr {
                                display: block;
                                margin-top: 0em;
                                margin-bottom: 1.5em;
                                margin-left: auto;
                                margin-right: auto;
                                border-style: inset;
                                border-width: 1px;
                                width: 100%;
                            }

                            ::selection {
                                background-color: #000;
                                color: #fff;
                            }
                            table {
                                border-collapse: collapse; /* This removes spacing between table cells */
                                width: 100%;
                                border: 2px solid black; /* Border around the table */
                            }

                            th, td {
                                border: 1px solid black; /* Border around header cells and data cells */
                                padding: 8px; /* Add some padding for cell content */
                                text-align: left; /* Align text within cells */
                            }

                            th {
                                background-color: #f2f2f2; /* Background color for header cells */
                            }
                        </style>
                    </head>
    '''

STYLE_SVG = '''
                <style>
                    .white-background {
                        background-color: white; /* Set background color to white */
                        display: inline-block; /* Ensure the div behaves as an inline element */
                        padding: 2px; /* Optional: to create some space around the image */
                    }
                    img.tex {
                        vertical-align: middle; /* Adjust the alignment as needed */
                        background-color: white; /* This will only affect the area of the img element */
                    }
                </style>
    '''
    
