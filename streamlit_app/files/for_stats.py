from time import time
from files.db_server import  make_request
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def get_statistic_image(student_id, TASKS_DICT):
    tasks_done = []
    total_done = []

    total = make_request(
        f'''
        SELECT
                variant
                , COUNT(*)
            FROM
                Main
            WHERE
                StudentID = {student_id}
                AND Subject = 'Inf'
            GROUP BY
                variant
    ''', 'tasks_done'
    )
    start = time()
    tasks_done = [elem[0] for elem in total]
    total_done = [elem[1] for elem in total]
    finish = time()

    plt.clf()
    plt.cla()

    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

    tasks = tasks_done
    percentages = total_done
    full_percentage = [100] * len(tasks)

    count = 0
    partial_percentages = []
    for task, numbers in TASKS_DICT.items():
        if task in tasks:
            partial_percentages.append(total_done[count] / numbers * 100)
            count += 1

    plt.barh(tasks, full_percentage, color='lightgray', edgecolor='none')

    plt.barh(tasks, partial_percentages, color='lightblue', edgecolor='none')

    plt.xlabel('Percentage, %')
    plt.ylabel('Task')
    plt.title('Task Completion Rates')

    plt.yticks(tasks)
    plt.xticks(range(0, 101, 10))

    count = 0
    for task, numbers in TASKS_DICT.items():
        if task in tasks:
            plt.text(90, task, f"{numbers}", va='center', ha='left')
            plt.text(80, task, f"{total_done[count] / numbers * 100:.3} %", va='center', ha='left')
            plt.text(70, task, f"{total_done[count]} / {numbers}", va='center', ha='left')
            count += 1

    
    buf = io.BytesIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    buf.seek(0)
    to_send = buf.getvalue()
    # Return the buffer value
    return to_send, finish - start

##############################################################

def get_statistic_image_math(student_id, TASKS_DICT):

    inquery = f'''
    WITH temp AS (
        SELECT 
            variant,
            num,
            CASE
                WHEN (variant BETWEEN 201 AND 357 OR variant > 432) AND num = 13 THEN 'Тригонометрия'
                WHEN (variant BETWEEN 201 AND 357 OR variant > 432) AND num = 14 THEN 'Стереометрия'
                WHEN (variant BETWEEN 201 AND 357 OR variant > 432) AND num = 15 THEN 'Неравенство'
                WHEN (variant BETWEEN 201 AND 357 OR variant > 432) AND num = 18 THEN 'Параметр'
                WHEN (variant BETWEEN 201 AND 357 OR variant > 432) AND num = 19 THEN 'Последняя'
                WHEN variant BETWEEN 201 AND 357 AND num = 16 THEN 'Планиметрия'
                WHEN variant BETWEEN 201 AND 357 AND num = 17 THEN 'Экономика'
                WHEN variant > 432 AND num = 16 THEN 'Экономика'
                WHEN variant > 432 AND num = 17 THEN 'Планиметрия'
                WHEN variant BETWEEN 358 AND 432 AND num = 12 THEN 'Тригонометрия'
                WHEN variant BETWEEN 358 AND 432 AND num = 13 THEN 'Стереометрия'
                WHEN variant BETWEEN 358 AND 432 AND num = 14 THEN 'Неравенство'
                WHEN variant BETWEEN 358 AND 432 AND num = 15 THEN 'Экономика'
                WHEN variant BETWEEN 358 AND 432 AND num = 16 THEN 'Планиметрия'
                WHEN variant BETWEEN 358 AND 432 AND num = 17 THEN 'Параметр'
                WHEN variant BETWEEN 358 AND 432 AND num = 18 THEN 'Последняя'
                ELSE 'Other'
            END AS sub
        FROM
            Main
        WHERE 
            Subject = 'Math'
            AND StudentID = {student_id}
    )
    SELECT
        sub,
        COUNT(*)
    FROM
        temp
    GROUP BY
        sub
    '''

    total = make_request(inquery, db_name='tasks_done')
    total_1 = {elem[0]: elem[1] for elem in total if elem[0] in TABLE_NAMES.keys()}

    plt.clf()
    plt.cla()

    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)

    full_percentage = [100] * len(total_1)

    plt.barh(list(range(1, len(total_1) + 1)), full_percentage, color='lightgray', edgecolor='none')

    plt.barh(list(range(1, len(total_1) + 1)), [elem / 241 * 100 for elem in total_1.values()] , color='lightblue', edgecolor='none')

    plt.xlabel('Percentage, %')
    plt.ylabel('Task')
    plt.title('Task Completion Rates')

    plt.yticks(list(range(1, len(total_1) + 1)), list(total_1.keys()))
    plt.xticks(range(0, 101, 10))

    for idx, (name, number) in enumerate(total_1.items()):
        
        plt.text(80, idx + 1, f"{number} / 241", va='center', ha='left')

    buf = io.BytesIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    buf.seek(0)
    to_send = buf.getvalue()

    return to_send, 0



