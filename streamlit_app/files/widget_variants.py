import streamlit as st
import pathlib
from files.google_files import link_to_var, list_files, link_to_extra_file
import re

def change_name_variant(lst):
    new_lst = []
    for elem in lst:
        res_1 = re.findall('var_\d+', elem)[0]
        new_lst.append(re.sub('var_', 'Variant ', res_1))

    return new_lst

def create_variants_tab_test(username, subject):
    SUBJECT_CONVERTER = {
        'I_': 'Informatics',
        'M_': 'Mathematics'
    }
    if username == 'demo':
        username = 'maria_23_24'
    try:
        variant_names_raw = list_files(username, 'Variant', subject)[::-1]
        if not variant_names_raw:
            return FileNotFoundError
        var_names = [''] + change_name_variant(variant_names_raw)
        var_name = st.selectbox(f'Choose Variant of {SUBJECT_CONVERTER[subject]}: ', var_names, key=SUBJECT_CONVERTER[subject])

        try:
            if var_name != '':
                if subject == 'I_':
                    st.markdown(f'[*Download Files*]({get_link_file(var_names, var_name, variant_names_raw)})')
                _extracted_from_create_variants_tab_test_15(
                    var_names, var_name, variant_names_raw
                )
        except FileNotFoundError:
            st.error('File Not Found')
            return FileNotFoundError

    except FileNotFoundError:
        st.error('No variants are found, contact Konstantin to clarify the situation')
        return FileNotFoundError


def _extracted_from_create_variants_tab_test_15(var_names, var_name, variant_names_raw):
    idx = var_names.index(var_name) - 1
    variant_final_name = variant_names_raw[idx][:-4]
    shared_link = link_to_var(variant_final_name)

    embeddable_link = shared_link.replace("/view?usp=sharing", "/preview")
    st.markdown("""
                        <style>
                            .pdf-container {
                                text-align: center;
                                margin-bottom: 5em;
                                # width: 100%; /* Container takes full width of the parent */
                                height: 100vh; /* Adjust the height as needed */
                                overflow: auto; /* Adds scrollbars if needed */
                                }
                            .pdf-container iframe {
                                width: 80%; /* iframe takes full width of its parent */
                                height: 80%; /* iframe takes full height of its parent */
                                border: none; /* Optional: removes the border */
                        }
                        </style>
                    """, unsafe_allow_html=True)

    pdf_display = f'''
                    <div class="pdf-container">
                        <iframe src="{embeddable_link}" type="application/pdf"></iframe>
                    </div>
                '''
    st.markdown(pdf_display, unsafe_allow_html=True)
    

def get_link_file(var_names, var_name, variant_names_raw):
    idx = var_names.index(var_name) - 1
    return link_to_extra_file(variant_names_raw[idx])


