"""
Mathematics module handler for the Streamlit application.
"""

import streamlit as st
import re
from typing import List, Optional, Callable
from .db_server import make_request
from .ui_components import (
    ColorManager, TaskRenderer, LayoutManager, SVGProcessor
)
from .user_config import user_manager
from .constants import MATH_TASKS_CONFIG, FOR_LANGUAGE, S3_BUCKET_NAMES
from .openai_answer_check import check_answer_math


class MathematicsHandler:
    """Handles mathematics tasks and interactions."""
    
    def __init__(self, add_info_who_did_function: Callable):
        """Initialize with required callback functions."""
        self.add_info_who_did = add_info_who_did_function
    
    def handle_mathematics_section(self, username: str) -> None:
        """Handle the mathematics section of the application."""
        tasks = self._get_available_math_tasks(username)
        task = st.selectbox('Choose Task: ', tasks, key='math_task_selectobox')
        
        nums = self._get_available_numbers(username)
        num = st.selectbox('Choose Num: ', nums, key='math_num_selectobox')
        
        if task != '' and num != '':
            self._display_math_task(username, task, num)
    
    def _get_available_math_tasks(self, username: str) -> List[str]:
        """Get available math tasks for the user."""
        return user_manager.get_math_tasks(username)
    
    def _get_available_numbers(self, username: str) -> List[str]:
        """Get available numbers for math tasks."""
        if username != 'demo':
            return [''] + list(range(1, 242))
        else:
            return [''] + list(range(1, 4))
    
    def _display_math_task(self, username: str, task: str, num: int) -> None:
        """Display the selected math task and handle interactions."""
        task_content = self._get_math_task_content(task, num)
        if not task_content:
            st.error("Task not found")
            return
        
        full_task_content = FOR_LANGUAGE + task_content
        student_task_content = self._prepare_student_content(task_content)
        
        ColorManager.initialize_font_color()
        color = ColorManager.change_color_name(st.session_state['font_color'])
        
        full_task_content = ColorManager.update_task_colors(
            full_task_content, current_task=task, current_num=num
        )
        student_task_content = ColorManager.update_task_colors(
            student_task_content, current_task=task, current_num=num
        )
        
        font_changed, admin_button = LayoutManager.create_task_header(
            task, num, 'Change the Font'
        )
        
        if font_changed:
            old_color = st.session_state.get('font_color', '#000000')
            full_task_content = full_task_content.replace(
                f'color: {old_color}', 
                f"color: {st.session_state['font_color']}"
            )
            student_task_content = student_task_content.replace(
                f'color: {old_color}', 
                f"color: {st.session_state['font_color']}"
            )
            color = ColorManager.change_color_name(st.session_state['font_color'])
        
        if username == 'admin':
            self._handle_admin_view(task, num, full_task_content, color, admin_button)
        else:
            self._handle_student_view(task, num, student_task_content, color)
    
    def _get_math_task_content(self, task: str, num: int) -> Optional[str]:
        """Get math task content from database."""
        try:
            table_name = MATH_TASKS_CONFIG[task]['table_name']
            request = f'SELECT task FROM {table_name} WHERE task_id = {num}'
            result = make_request(request, 'maths')
            return result[0][0] if result else None
        except Exception as e:
            st.error(f"Error loading task: {e}")
            return None
    
    def _prepare_student_content(self, task_content: str) -> str:
        """Prepare content for student view (remove solutions)."""
        try:
            index = task_content.index('Задание ')
            return FOR_LANGUAGE + task_content[index:]
        except ValueError:
            return FOR_LANGUAGE + task_content
    
    def _handle_admin_view(self, task: str, num: int, content: str, 
                          color: str, admin_button: bool) -> None:
        """Handle admin view with additional functionality."""
        try:
            variant_match = re.findall(r'Вариант: \d+', content)
            if variant_match:
                find_task_num = variant_match[0]
                st.write(find_task_num)
                variant_num = int(re.findall(r'\d+', find_task_num)[0])
                task_number = self._get_task_number(task, variant_num)
                st.write('Number of task: ', task_number)
                
                if admin_button:
                    self.add_info_who_did("Math", variant_num, int(task_number))
        except (IndexError, ValueError):
            pass
        
        processed_content = SVGProcessor.replace_svg_links(
            content, task, num, color, S3_BUCKET_NAMES
        )
        
        from .constants import STYLE_SVG
        TaskRenderer.render_task_content(
            processed_content, height=400, style_prefix=STYLE_SVG
        )
        
        self._handle_answer_checking(task, num)
    
    def _handle_student_view(self, task: str, num: int, content: str, color: str) -> None:
        """Handle student view."""
        processed_content = SVGProcessor.replace_svg_links(
            content, task, num, color, S3_BUCKET_NAMES
        )
        
        from .constants import STYLE_SVG
        TaskRenderer.render_task_content(
            processed_content, height=400, style_prefix=STYLE_SVG
        )
        
        self._handle_answer_checking(task, num)
    
    def _handle_answer_checking(self, task: str, num: int) -> None:
        """Handle answer checking for specific math tasks."""
        if task in ['Стереометрия']:
            try:
                table_name = MATH_TASKS_CONFIG[task]['table_name']
                request = f'SELECT answer_final FROM {table_name}_answers WHERE task_id = {num}'
                result = make_request(request, 'maths')
                if result:
                    answer = result[0][0]
                    check_answer_math(answer, task)
            except Exception:
                pass
    
    def _get_task_number(self, task: str, variant_num: int) -> str:
        """Get task number based on task type and variant."""
        task_number_map = {
            'Тригонометрия': {
                'range1': (201, 357, '13'),
                'range2': (432, float('inf'), '13'),
                'default': '12'
            },
            'Стереометрия': {
                'range1': (201, 357, '14'),
                'range2': (432, float('inf'), '14'),
                'default': '13'
            },
            'Неравенство': {
                'range1': (201, 357, '15'),
                'range2': (432, float('inf'), '15'),
                'default': '14'
            },
            'Параметр': {
                'range1': (201, 357, '18'),
                'range2': (432, float('inf'), '18'),
                'default': '17'
            },
            'Последняя': {
                'range1': (201, 357, '19'),
                'range2': (432, float('inf'), '19'),
                'default': '18'
            },
            'Планиметрия': {
                'range1': (201, 432, '16'),
                'range2': (432, float('inf'), '17'),
                'default': '16'
            },
            'Экономика': {
                'range1': (201, 357, '17'),
                'range2': (358, 432, '15'),
                'range3': (432, float('inf'), '16'),
                'default': '17'
            }
        }
        
        if task not in task_number_map:
            return '1'
        
        config = task_number_map[task]
        
        if 'range1' in config:
            start, end, number = config['range1']
            if start <= variant_num <= end:
                return number
        
        if 'range2' in config:
            start, end, number = config['range2']
            if variant_num > start:
                return number
        
        if 'range3' in config:
            start, end, number = config['range3']
            if start < variant_num <= end:
                return number
        
        return config.get('default', '1')


class MathTaskManager:
    """Manages mathematics task data and caching."""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_math_task_cached(task: str, num: int) -> Optional[str]:
        """Get math task content with caching."""
        try:
            table_name = MATH_TASKS_CONFIG[task]['table_name']
            request = f'SELECT task FROM {table_name} WHERE task_id = {num}'
            result = make_request(request, 'maths')
            return result[0][0] if result else None
        except Exception:
            return None


def create_mathematics_handler(add_info_who_did_func: Callable) -> MathematicsHandler:
    """Factory function to create MathematicsHandler instance."""
    return MathematicsHandler(add_info_who_did_func)
