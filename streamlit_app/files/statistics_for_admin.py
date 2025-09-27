from datetime import datetime
import pandas as pd
from files.db_server import create_connection as create_connection_mongo
import streamlit as st
from files.aws.aws_funcs import get_from_s3

class StatisticsForAdmin:
    def __init__(self):
        self.df = self.load_data()

    @staticmethod
    @st.cache_data
    def load_data():
        return StatisticsForAdmin.check_inf_answers_mongo()

    def get_student_names(self):
        file = get_from_s3('students/student_tasks.csv')
        return pd.read_csv(file['Body'], index_col='Student').index.to_list()

    def filter_data_interface(self):
        df_filtered = self.df.copy()
        
        student_names = self.get_student_names()
        
        student_names = sorted([
                                name.lower()
                                for name in student_names
                                if any([
                                    '25_26' in name,
                                    '24_26' in name
                                ]) and all([
                                    'ELENA_24_25' not in name,
                                    'NEW_TEST_24_25' not in name,
                                    'LISA_24_25' not in name
                                ])
                            ])

        
        user = st.selectbox('Choose the student: ', student_names, key='user_choice')
        if user:
            df_filtered = df_filtered[df_filtered['USER'] == user]
        
        task = st.text_input(label="Task", key='task_choice')
        if task:
            try:
                task = int(task)
                df_filtered = df_filtered[df_filtered['task'] == task]
            except ValueError:
                st.warning("Task should be a number")
        
        true_value = st.selectbox('Filter True/False: ', ['', True, False], index=1, key='true_choice')
        if true_value != '':
            df_filtered = df_filtered[df_filtered['True?'] == true_value]
        
        sort_column = st.selectbox('Sort by column: ', df_filtered.columns.tolist(), index=3,key='sort_column_choice')
        ascending = st.selectbox('Sort ascending? ', [True, False], index=1, key='ascending_choice')
        
        if sort_column:
            df_filtered = df_filtered.sort_values(by=sort_column, ascending=ascending)
        
        st.dataframe(df_filtered)
    
    @staticmethod
    def drop_cache():
        if st.button("Clear Cache"):
            StatisticsForAdmin.load_data.clear()

    @staticmethod
    def check_inf_answers_mongo():
        client_mongo = create_connection_mongo('log_db')
        db_mongo = client_mongo["log_db"]

        client_mongo_ans = create_connection_mongo('inf_answers')
        db_mongo_ans = client_mongo_ans["inf_answers"]

        cutoff_date = datetime(2024, 9, 1)

        answers_dict = {}
        for task_name in db_mongo_ans.list_collection_names():
            collection = db_mongo_ans.get_collection(task_name)
            answers_dict[task_name] = {doc['num']: doc['ans'] for doc in collection.find({}, {'num': 1, 'ans': 1})}

        results = []

        for coll in db_mongo.logs.aggregate([
                {
                    '$addFields': {
                        'A': '$answer',
                        'D': {
                            '$dateAdd': {
                                'startDate': {
                                    '$dateFromString': {
                                        'dateString': '$date',
                                        'format': '%Y-%m-%d %H-%M-%S'
                                    }
                                },
                                'unit': 'hour',
                                'amount': 3
                            }
                        },
                        'USER': '$username'
                    }
                },
                {'$match': {'D': {'$gt': cutoff_date}}},
                {'$project': {'_id': 0, 'task': 1, 'num': 1, 'A': 1, 'D': 1, 'USER': 1}}
            ]):
            real_ans = answers_dict.get(str(coll["task"]), {}).get(coll["num"])

            coll['True?'] = real_ans == coll['A'] if real_ans is not None else False
            results.append(coll)

        final = pd.DataFrame(results)

        final = final[~final['A'].str.contains(r'QWE', case=False, regex=True, na=False)]
        df = final.reset_index(drop=True)

        return df
