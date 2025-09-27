"""
Statistics module handler for the Streamlit application.
"""

import streamlit as st
import base64
from typing import Optional
from .for_stats import get_statistic_image, get_statistic_image_math
from .user_config import user_manager, USERNAME_DICT
from .ui_components import SessionManager


class StatisticsHandler:
    """Handles statistics display and caching."""
    
    def handle_statistics_section(self, username: str, task_numbers: dict) -> None:
        """Handle the statistics section of the application."""
        if username == 'admin':
            st.info("Admin statistics not implemented in this handler")
            return
        
        stats_menu = user_manager.get_stats_menu(username)
        
        if not stats_menu:
            st.info("No statistics available for this user")
            return
        
        stats_choice = st.selectbox(
            'Choose the one you are interested in:', 
            stats_menu, 
            key='stats_selectbox'
        )
        
        if stats_choice == 'Completing Tasks':
            self._display_informatics_statistics(username, task_numbers)
        elif stats_choice == 'Completing Tasks MATH':
            self._display_math_statistics(username, task_numbers)
    
    def _display_informatics_statistics(self, username: str, task_numbers: dict) -> None:
        """Display informatics completion statistics."""
        svg_html = SessionManager.get_or_create_svg_cache(
            'svg_html',
            self._generate_informatics_stats,
            username,
            task_numbers
        )
        
        st.write(svg_html, unsafe_allow_html=True)
    
    def _display_math_statistics(self, username: str, task_numbers: dict) -> None:
        """Display mathematics completion statistics."""
        svg_html = SessionManager.get_or_create_svg_cache(
            'svg_html_math',
            self._generate_math_stats,
            username,
            task_numbers
        )
        
        st.write(svg_html, unsafe_allow_html=True)
    
    def _generate_informatics_stats(self, username: str, task_numbers: dict) -> tuple:
        """Generate informatics statistics SVG."""
        user_id = self._get_user_id_for_stats(username)
        
        return get_statistic_image(student_id=user_id, TASKS_DICT=task_numbers)
    
    def _generate_math_stats(self, username: str, task_numbers: dict) -> tuple:
        """Generate mathematics statistics SVG."""
        user_id = self._get_user_id_for_stats(username)
        
        return get_statistic_image_math(student_id=user_id, TASKS_DICT=task_numbers)
    
    def _get_user_id_for_stats(self, username: str) -> int:
        """Get user ID for statistics, handling demo user special case."""
        if username == 'demo':
            return USERNAME_DICT['maria_23_24']
        else:
            return USERNAME_DICT.get(username, USERNAME_DICT.get('maria_23_24', 5))


class StatisticsCacheManager:
    """Manages statistics caching and invalidation."""
    
    @staticmethod
    def clear_user_cache(username: str) -> None:
        """Clear cached statistics for a specific user."""
        cache_keys = ['svg_html', 'svg_html_math']
        for key in cache_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        # Also clear user marker
        if 'user' in st.session_state:
            del st.session_state['user']
    
    @staticmethod
    def clear_all_cache() -> None:
        """Clear all statistics cache."""
        cache_keys = ['svg_html', 'svg_html_math', 'user']
        for key in cache_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def is_cache_valid(username: str) -> bool:
        """Check if cache is valid for the current user."""
        current_user_key = f'user_{username}'
        cached_user = st.session_state.get('user', '')
        return cached_user == current_user_key


class StatisticsValidator:
    """Validates statistics-related operations."""
    
    @staticmethod
    def validate_user_access(username: str) -> bool:
        """Validate if user has access to statistics."""
        user = user_manager.get_user(username)
        if not user:
            return False
        
        stats_menu = user.stats_menu
        return len(stats_menu) > 1
    
    @staticmethod
    def validate_statistics_type(stats_type: str) -> bool:
        """Validate statistics type."""
        valid_types = ['Completing Tasks', 'Completing Tasks MATH']
        return stats_type in valid_types


def create_statistics_handler() -> StatisticsHandler:
    """Factory function to create StatisticsHandler instance."""
    return StatisticsHandler()
