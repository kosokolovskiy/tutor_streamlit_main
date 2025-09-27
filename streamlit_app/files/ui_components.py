"""
UI components and utilities for the Streamlit application.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Tuple, Optional


class ColorManager:
    """Manages color themes and font colors for the application."""
    
    @staticmethod
    def change_color(color: str) -> str:
        """Toggle between black and white colors."""
        return '#FFFFFF' if color == '#000000' else '#000000'
    
    @staticmethod
    def change_color_name(color: str) -> str:
        """Get color name from hex value."""
        return 'black' if color == '#000000' else 'white'
    
    @staticmethod
    def change_color_right(color: str) -> Tuple[int, int, int]:
        """Get RGB values for background color."""
        if color == '#FFFFFF':
            return 15, 17, 22
        else:
            return 255, 255, 255
    
    @staticmethod
    def initialize_font_color() -> str:
        """Initialize font color in session state."""
        if 'font_color' not in st.session_state:
            st.session_state['font_color'] = '#000000'
        return st.session_state['font_color']
    
    @staticmethod
    def update_task_colors(task_text: str, current_task: Optional[str] = None, 
                          current_num: Optional[int] = None) -> str:
        """Update task text colors based on current state."""
        font_color = ColorManager.initialize_font_color()
        
        # Handle task change
        if current_task is not None:
            if 'curr_task' not in st.session_state:
                st.session_state['curr_task'] = current_task
            elif st.session_state['curr_task'] != current_task:
                if font_color == '#FFFFFF':
                    task_text = task_text.replace('color: #000000', f"color: {font_color}")
                else:
                    task_text = task_text.replace('color: #FFFFFF', f"color: {font_color}")
                st.session_state['curr_task'] = current_task
        
        if current_num is not None:
            if 'curr_num' not in st.session_state:
                st.session_state['curr_num'] = current_num
            elif st.session_state['curr_num'] != current_num:
                if font_color == '#FFFFFF':
                    task_text = task_text.replace('color: #000000', f"color: {font_color}")
                else:
                    task_text = task_text.replace('color: #FFFFFF', f"color: {font_color}")
                st.session_state['curr_num'] = current_num
        
        return task_text


class TaskRenderer:
    """Handles rendering of tasks and content."""
    
    @staticmethod
    def render_task_content(content: str, height: int = 700, 
                           style_prefix: str = "", scrolling: bool = True) -> None:
        """Render task content with proper styling."""
        font_color = st.session_state.get('font_color', '#000000')
        red, green, blue = ColorManager.change_color_right(font_color)
        
        full_content = (
            f"{style_prefix}"
            f"<style>:root {{background-color: rgb({red}, {green}, {blue});}}</style>"
            f"{content}"
        )
        
        components.html(full_content, scrolling=scrolling, height=height)
    
    @staticmethod
    def create_font_change_button(label: str = 'Press me') -> bool:
        """Create a font color change button and handle the color change."""
        change_font_button = st.button(label=label)
        
        if change_font_button:
            old_color = st.session_state.get('font_color', '#000000')
            st.session_state['font_color'] = ColorManager.change_color(old_color)
            return True
        
        return False
    
    @staticmethod
    def show_task_info(task: str, num: int) -> None:
        """Display task information."""
        st.info(f"You chose Number {num} of Task {task}")


class AnswerChecker:
    """Handles answer checking and validation."""
    
    @staticmethod
    def check_answer(user_answer: str, correct_answer: str, 
                    username: str, task: str, num: int, 
                    log_function) -> None:
        """Check user answer and provide feedback."""
        user_answer = user_answer.strip()
        
        if not user_answer:
            st.info('Enter the answer')
            return
        
        if user_answer == correct_answer:
            st.success("True!")
            if username not in ['admin', 'demo']:
                log_function(user_answer, task, num, username)
        else:
            st.error('Try again')
            if username != 'admin':
                log_function(user_answer, task, num, username)


class LayoutManager:
    """Manages page layout and structure."""
    
    @staticmethod
    def create_task_header(task: str, num: int, 
                          button_label: str = 'Press me') -> Tuple[bool, bool]:
        """Create task header with info and font change button."""
        col1, col2 = st.columns([4, 1])
        
        with col1:
            TaskRenderer.show_task_info(task, num)
        
        st.write("")
        
        with col2:
            font_changed = TaskRenderer.create_font_change_button(button_label)
        
        admin_button = False
        if st.session_state.get('username') == 'admin':
            admin_button = st.button(label='Show Who Done')
        
        return font_changed, admin_button
    
    @staticmethod
    def create_answer_input(key: str, label: str = 'Your answer: ') -> str:
        """Create answer input field."""
        return st.text_input(label, value='', key=key)
    
    @staticmethod
    def create_check_button(key: str, label: str = 'Check') -> bool:
        """Create check answer button."""
        return st.button(label=label, key=key)


class SVGProcessor:
    """Processes SVG links and images."""
    
    @staticmethod
    def replace_svg_links(content: str, task: str, num: int, 
                         color: str, s3_bucket_names: dict) -> str:
        """Replace SVG links with S3 bucket links."""
        import re
        
        mask = r'https:\/\/ege\.sdamgia\.ru/formula/svg/\w+/\w+\.svg'
        all_links = re.findall(mask, content)
        
        for idx, link_mask in enumerate(all_links):
            s3_link = (
                f'https://kosokolovsky-bucket-svgs.s3.eu-central-1.amazonaws.com/'
                f'{s3_bucket_names[task]}/z{num}im{idx + 1}{color}.svg'
            )
            content = content.replace(link_mask, s3_link, 1)
        
        return content


class SessionManager:
    """Manages session state and caching."""
    
    @staticmethod
    def get_or_create_svg_cache(cache_key: str, generator_func, *args) -> str:
        """Get SVG from cache or create new one."""
        user_key = f'user_{st.session_state.get("username", "unknown")}'
        
        if cache_key not in st.session_state or st.session_state.get('user') != user_key:
            svg_data, _ = generator_func(*args)
            import base64
            svg_base64 = base64.b64encode(svg_data).decode('utf-8')
            svg_html = f'''
                <div style="justify-content: center; align-items: center;">
                <img src="data:image/svg+xml;base64,{svg_base64}" alt="SVG" style="height: automatic;width: 100%;">
                </div>
            '''
            st.session_state[cache_key] = svg_html
            st.session_state['user'] = user_key
        
        return st.session_state[cache_key]
