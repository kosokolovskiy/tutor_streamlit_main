"""
Informatics module handler for the Streamlit application.
"""

import streamlit as st
from typing import List, Optional, Callable
from .db_server import make_request
from .ui_components import (
    ColorManager, TaskRenderer, AnswerChecker, 
    LayoutManager, SessionManager
)
from .user_config import user_manager


class InformaticsHandler:
    """Handles informatics tasks and interactions."""
    
    def __init__(self, add_log_function: Callable, add_info_who_did_function: Callable):
        """Initialize with required callback functions."""
        self.add_log = add_log_function
        self.add_info_who_did = add_info_who_did_function
    
    def handle_informatics_section(self, username: str, task_numbers: dict) -> None:
        """Handle the informatics section of the application."""
        tasks = self._get_available_tasks(username, task_numbers)
        task = st.selectbox('Choose Task: ', tasks, key='inf_task_selectobox')
        
        nums = self._get_available_numbers(username, task, task_numbers)
        num = st.selectbox('Choose Num: ', nums, key='inf_num_selectobox')
        
        if task != '' and num != '':
            self._display_task(username, task, num)
    
    def _get_available_tasks(self, username: str, task_numbers: dict) -> List[str]:
        """Get list of available tasks for the user."""
        return [''] + list(task_numbers.keys())
    
    def _get_available_numbers(self, username: str, task: str, task_numbers: dict) -> List[str]:
        """Get list of available numbers for the selected task."""
        try:
            if username != 'demo':
                max_num = task_numbers.get(task, 1)
                return [''] + list(range(1, max_num))
            else:
                return [''] + list(range(1, 4))
        except (KeyError, TypeError):
            return ['']
    
    def _display_task(self, username: str, task: str, num: int) -> None:
        """Display the selected task and handle interactions."""
        display_task = 19 if task in [20, 21] else task
        
        task_content = self._get_task_content(display_task, num)
        if not task_content:
            st.error("Task not found")
            return
        
        ColorManager.initialize_font_color()
        task_content = ColorManager.update_task_colors(
            task_content, current_task=task, current_num=num
        )
        
        font_changed, admin_button = LayoutManager.create_task_header(task, num)
        
        if font_changed:
            old_color = st.session_state.get('font_color', '#000000')
            task_content = task_content.replace(
                f'color: {old_color}', 
                f"color: {st.session_state['font_color']}"
            )
        
        if admin_button and username == 'admin':
            self.add_info_who_did('Inf', task, num)
        
        TaskRenderer.render_task_content(task_content, height=700)
        
        self._handle_answer_checking(username, display_task, num)
    
    def _get_task_content(self, task: int, num: int) -> Optional[str]:
        """Get task content from database."""
        try:
            request = f'SELECT task FROM t_{task} WHERE num = {num}'
            result = make_request(request, 'inf_tasks')
            return result[0][0] if result else None
        except Exception as e:
            st.error(f"Error loading task: {e}")
            return None
    
    def _get_correct_answer(self, task: int, num: int) -> Optional[str]:
        """Get correct answer from database."""
        try:
            request = f'SELECT task FROM t_{task} WHERE num = {num}'
            result = make_request(request, 'inf_answers')
            return result[0][0] if result else None
        except Exception as e:
            st.error(f"Error loading answer: {e}")
            return None
    
    def _handle_answer_checking(self, username: str, task: int, num: int) -> None:
        """Handle answer input and checking."""
        user_answer = LayoutManager.create_answer_input('prob_answer_text_input')
        
        correct_answer = self._get_correct_answer(task, num)
        if not correct_answer:
            st.error("Could not load correct answer")
            return
        
        check_button = LayoutManager.create_check_button('check_button')
        
        if check_button:
            AnswerChecker.check_answer(
                user_answer, correct_answer, username, task, num, self.add_log
            )
        elif not user_answer.strip():
            st.info('Enter the answer')


class InformaticsTaskManager:
    """Manages informatics task data and caching."""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_task_content_cached(task: int, num: int, db_name: str) -> Optional[str]:
        """Get task content with caching."""
        try:
            request = f'SELECT task FROM t_{task} WHERE num = {num}'
            result = make_request(request, db_name)
            return result[0][0] if result else None
        except Exception:
            return None
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_answer_cached(task: int, num: int, db_name: str) -> Optional[str]:
        """Get correct answer with caching."""
        try:
            request = f'SELECT task FROM t_{task} WHERE num = {num}'
            result = make_request(request, db_name)
            return result[0][0] if result else None
        except Exception:
            return None


class InformaticsValidator:
    """Validates informatics-related inputs and data."""
    
    @staticmethod
    def validate_task_selection(task: str, num: str) -> bool:
        """Validate that both task and number are selected."""
        return task != '' and num != ''
    
    @staticmethod
    def validate_task_number(task: int) -> int:
        """Validate and adjust task number for special cases."""
        return 19 if task in [20, 21] else task
    
    @staticmethod
    def validate_user_permissions(username: str, task: str) -> bool:
        """Validate user permissions for accessing specific tasks."""
        user = user_manager.get_user(username)
        if not user:
            return True
        
        return True


def create_informatics_handler(add_log_func: Callable, 
                             add_info_who_did_func: Callable) -> InformaticsHandler:
    """Factory function to create InformaticsHandler instance."""
    return InformaticsHandler(add_log_func, add_info_who_did_func)
