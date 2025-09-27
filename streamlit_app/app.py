import streamlit as st
import os
import yaml
from datetime import datetime
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

from files.constants import give_tasks
from files.db_server import create_connection, make_request
# from files.widget_variants import create_variants_tab_test
from files.statistics_for_admin import StatisticsForAdmin

from files.user_config import user_manager, USERNAME_DICT
from files.informatics_handler import create_informatics_handler
from files.mathematics_handler import create_mathematics_handler
from files.statistics_handler import create_statistics_handler
from files.homework_handler import create_homework_handler

st.set_page_config(layout='wide')


def add_info_who_did(subject: str, variant: int, num: int) -> None:
    """Displays the names of students who completed a specific task variant.

    This function queries the database for students who have completed a given subject, variant, and task number, and displays their names in the Streamlit interface.

    Args:
        subject (str): The subject of the task.
        variant (int): The variant number of the task.
        num (int): The task number.

    Returns:
        None
    """
    lst_names = []

    for name in USERNAME_DICT.keys():
        request_one = f'''
                            SELECT 
                                *
                            FROM
                                Main
                            WHERE
                                StudentID = {USERNAME_DICT[name]}
                                AND Subject = '{subject}'
                                AND Variant = {variant}
                                AND Num = {num}
                        '''

        temp = make_request(request_one, 'tasks_done')
        if  temp != []:
            lst_names.append(name)

    if lst_names != []:
        st.info(lst_names)
    else:
        st.success('Nobody!')
    

def add_log(ans: str, task: str, num: int, username: str) -> None:
    """Logs a student's answer submission to the database.

    This function records the details of a student's answer, including the task, number, answer, date, and username, in the log database.

    Args:
        ans (str): The student's answer.
        task (str): The task identifier.
        num (int): The task number.
        username (str): The student's username.

    Returns:
        None
    """
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H-%M-%S")
    text = {'task': task, 'num': num, 'answer': ans, 'date': formatted_datetime, 'username': username}
    client_log = create_connection("log_db") 
    db_log = client_log['log_db']
    db_log.logs.insert_one(text)


def one_student(username: str):
    """Main function to handle student interface using modular system."""
    user_config = user_manager.get_user(username)
    menu = user_manager.get_user_menu(username)
    menu_for_stats = user_manager.get_stats_menu(username)

    TASK_NUMBERS = give_tasks(username.upper())

    st.session_state['username'] = username

    choice = st.sidebar.radio('Menu', menu, key='main_menu_choice')

    informatics_handler = create_informatics_handler(add_log, add_info_who_did)
    mathematics_handler = create_mathematics_handler(add_info_who_did)
    statistics_handler = create_statistics_handler()
    homework_handler = create_homework_handler()


    if choice == 'Informatics':
        informatics_handler.handle_informatics_section(username, TASK_NUMBERS)

    #########################################################################

    elif choice == 'Mathematics':
        mathematics_handler.handle_mathematics_section(username)

    #########################################################################

    elif choice == 'Homework':
        homework_handler.handle_homework_section(username)


    elif choice == 'Statistics':
        statistics_handler.handle_statistics_section(username, TASK_NUMBERS)

    elif choice == 'Variants':
        try:
            if 'Informatics' in menu:
                create_variants_tab_test(username, 'I_')
        except:
            pass
        try:
            if 'Mathematics' in menu:
                create_variants_tab_test(username, 'M_')
        except:
            pass

    elif choice == 'Student Statistics':
        try:
            obj = StatisticsForAdmin()
            obj.filter_data_interface()
            obj.drop_cache()
        except Exception as e:
            st.error(e)


def main():
    """Initializes and runs the main Streamlit application interface.

    This function sets up user authentication, loads configuration, and displays the appropriate interface based on authentication status.

    Returns:
        None
    """

    if 'config' not in st.session_state:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path) as file:
            st.session_state.config = yaml.load(file, Loader=SafeLoader)


    authenticator = stauth.Authenticate(
        st.session_state.config['credentials'],
        st.session_state.config['cookie']['name'],
        st.session_state.config['cookie']['key'],
        st.session_state.config['cookie']['expiry_days'],
        st.session_state.config['preauthorized']
    )

    name, authentication_status, username = authenticator.login()


    if authentication_status:
        st.write(f'Welcome, *{name}*')
        one_student(username)
        authenticator.logout('Logout', 'main', key='unique_key')

    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')


if __name__ == '__main__':
    
    main()
