import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def api_request(correct_answer, user_input, subject):
    STUDENT_PROMPTS = {
        'Стереометрия': {
            'student_answer': lambda student: f''' Convert expression to latex expression: {student}. Output only latex form''',

            'final': lambda correct, student: f'''Compare these two expressions: {correct} and {student}. 
                            If there are two options of answer: 'а)' or 'б)':
                                - if only 'а)' correct - write 'а)' - Yes.
                                - if only 'б)' correct - write 'б)' - Yes.
                                - if both are correct - Yes
                            Otherewise say only 'Yes' if they are the same and 'No' otherwise.
                        ''',
        }, 
        

        'Неравенство': {
            'student_answer': lambda student: f''' Convert expression to latex: {student}. Output only latex form''',
            

            'final': lambda correct, student: f'''Compare these two expressions: {correct} and {student}. 
                            Do both expressions represent the same set? Say only "Yes" if they are the same and "No" if not.
                        '''
        },

        'Экономика': {
            'student_answer': lambda student: f''' Convert expression to latex: {student}. Output only latex form''',

            'final': lambda correct, student: f'''Get rid of all spaces and letters and Compare these two expressions: {correct} and {student}. 
                                Say only 'Yes' if they are the same and 'No' otherwise.
                        '''
        }
    }


    try:

        response_student = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "I convert mathematical expressions of different forms to LaTex format and other way around with no words except the result. Be very careful about brackets - interval, semiinterval and so on",
                },
                {'role': 'user', 'content': STUDENT_PROMPTS[subject]['student_answer'](user_input)},

            ],
            temperature=0,
            max_tokens=100,
        )


        response_final = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": '''I am comparing mathematical expressions written in LaTex and saying if they are same or not. 
                    ''',
                },
                {'role': 'user', 'content': STUDENT_PROMPTS[subject]['final'](correct_answer, response_student.choices[0].message.content)},

            ],
            temperature=0,
            max_tokens=100,
        )

        return [correct_answer, response_student.choices[0].message.content, response_final.choices[0].message.content]
    except Exception as e:
        st.error(str(e))
        return f"An error occurred: {str(e)}"

def process_answer(answer):
    answer = answer\
                    .replace('\xad', '')\
                    .replace('левая круг­лая скоб­ка', '(')\
                    .replace('пра­вая квад­рат­ная скоб­ка', ']')\
                    .replace('левая квад­рат­ная скоб­ка', '[')\
                    .replace('пра­вая круг­лая скоб­ка', ')')\
                    .replace('дробь: чис­ли­тель:', '\\frac{')\
                    .replace(', зна­ме­на­тель:', '}{')\
                    .replace('конец дроби', '}')\
                    .replace('конец ар­гу­мен­та', '}')\
                    .replace('на­ча­ло ар­гу­мен­та: ', '{')\
                    .replace('ко­рень из', '\\sqrt')\
                    .replace('минус', '-')\
                    .replace('плюс', '+')\
                    .replace('бес­ко­неч­ность', '\\infty')\
                    .replace(';', ',')\
                    .replace(' right]', ']')\
                    .replace(' left[', '[')\
                    .replace(' right)', ')')\
                    .replace(' left(', '(')\
                    .replace(' left) ', ')')\
                    .replace('левая фи­гур­ная скоб­ка', '\\{')\
                    .replace('пра­вая фи­гур­ная скоб­ка', '\\}')\
                    .replace('логарифм основание', '\\log_{')\
                    .replace('аргумент', '}')\
                    .replace(' корень ', '\\sqrt{')\
                    .replace(')', '})')
    return answer

def a_and_b(answer, subject):
    if ' DELIM ' in answer:
        return answer.strip(' DELIM ').split(' DELIM ')
    return answer, None
    

def button_to_check(correct_answer, text, subject):
    user_input = st.text_input(f'Your Answer for {text}', '')
    if st.button(f'Check My Answer for {text}'):
            for _ in range(1):
                feedback = api_request(correct_answer, user_input, subject)
                if 'Yes' in feedback[2]:
                    st.success('Correct!')
                    st.markdown('***Correct Answer:***')
                    st.markdown(f'$${feedback[0]}$$')
                else:
                    st.error('Try Again!')
                    

                st.markdown('***Your Answer:***')
                st.markdown(f'$${feedback[1]}$$')  

    

def check_answer_math(correct_expr, subject):
    st.title('Math Answer Checker with LLM Feedback')

    if correct_expr == 'No answer':
        st.info('Unfortunately, for this task there is no answer')
        return 0

    correct_lst = a_and_b(correct_expr, subject)

    if correct_lst[0] is not None and correct_lst[1] is not None:
        col1, col2 = st.columns([1, 1])
        with col1:
            button_to_check(correct_lst[0], 'A', subject)

        with col2:
            button_to_check(correct_lst[1], 'B', subject)

    elif correct_lst[0] is not None:
        button_to_check(correct_lst[0], 'A', subject)

    elif correct_lst[1] is not None:
        button_to_check(correct_lst[1], 'B', subject)

    else:
        button_to_check(correct_expr, '', subject)
    
                


if __name__ == '__main__':
    check_answer_math('1', '1')