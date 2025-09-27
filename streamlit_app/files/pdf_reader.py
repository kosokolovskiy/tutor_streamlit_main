import streamlit as st
import streamlit.components.v1 as components
import base64


def pdf_widget(file_path):
    st.title('Homework')

    st.markdown("""
        <style>
        .pdf-container {
            text-align: center;
            margin-bottom: 5em;
        }
        .pdf-container iframe {
            margin-left: auto;
            margin-right: auto;
            display: block;
        }
        </style>
    """, unsafe_allow_html=True)

    pdf_file_path = file_path

    with open(pdf_file_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')

    pdf_display = f'''
    <div class="pdf-container">
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="500" type="application/pdf"></iframe>
    </div>
    '''
    
    st.markdown(pdf_display, unsafe_allow_html=True)