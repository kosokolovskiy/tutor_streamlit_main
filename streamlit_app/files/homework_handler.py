"""
Homework module handler for the Streamlit application.
"""

import streamlit as st
from typing import Optional
from .google_files import link_to_var, list_files
from .user_config import user_manager, USERNAME_DICT


class HomeworkHandler:
    """Handles homework display and management."""
    
    def handle_homework_section(self, username: str) -> None:
        """Handle the homework section of the application."""
        # Determine which student's homework to show
        username_chosen = self._get_homework_username(username)
        
        # Display homework
        self._display_homework(username_chosen)
    
    def _get_homework_username(self, username: str) -> str:
        """Get the username for homework display (admin can choose)."""
        if username == 'admin':
            # Admin can choose any student
            student_options = ['admin'] + list(USERNAME_DICT.keys())
            return st.selectbox(
                'Choose the student: ', 
                student_options,
                key='homework_student_selector'
            )
        else:
            return username
    
    def _display_homework(self, username: str) -> None:
        """Display homework for the specified user."""
        try:
            homework_files = list_files(username, 'Homework')
            if not homework_files:
                st.error('No homework files found')
                return
            
            homework_file = homework_files[0][:-4]
            
            shared_link = link_to_var(homework_file)
            
            embeddable_link = shared_link.replace("/view?usp=sharing", "/preview")
            
            self._render_homework_pdf(embeddable_link)
            
        except FileNotFoundError:
            st.error('File Not Found')
        except IndexError:
            st.error('No homework files available')
        except Exception as e:
            st.error(f'Error loading homework: {str(e)}')
    
    def _render_homework_pdf(self, embeddable_link: str) -> None:
        """Render homework PDF with custom styling."""
        pdf_css = """
            <style>
            .pdf-container {
                text-align: center;
                margin-bottom: 5em;
                height: 100vh;
                overflow: auto;
            }
            .pdf-container iframe {
                width: 80%;
                height: 80%;
                border: none;
            }
            </style>
        """
        
        pdf_html = f"""
            <div class="pdf-container">
                <iframe src="{embeddable_link}" type="application/pdf"></iframe>
            </div>
        """
        
        st.markdown(pdf_css, unsafe_allow_html=True)
        st.markdown(pdf_html, unsafe_allow_html=True)


class HomeworkValidator:
    """Validates homework-related operations."""
    
    @staticmethod
    def validate_user_access(username: str, target_username: str) -> bool:
        """Validate if user can access target user's homework."""
        if username == 'admin':
            return True
        
        return username == target_username
    
    @staticmethod
    def validate_homework_file(filename: str) -> bool:
        """Validate homework file format."""
        if not filename:
            return False
        
        return filename.lower().endswith('.pdf')
    
    @staticmethod
    def validate_google_drive_link(link: str) -> bool:
        """Validate Google Drive link format."""
        if not link:
            return False
        
        return 'drive.google.com' in link or 'docs.google.com' in link


class HomeworkManager:
    """Manages homework files and metadata."""
    
    @staticmethod
    def get_available_students() -> list:
        """Get list of students with homework access."""
        return list(USERNAME_DICT.keys())
    
    @staticmethod
    def get_homework_info(username: str) -> Optional[dict]:
        """Get homework information for a user."""
        try:
            files = list_files(username, 'Homework')
            if not files:
                return None
            
            return {
                'username': username,
                'files': files,
                'file_count': len(files),
                'latest_file': files[0] if files else None
            }
        except Exception:
            return None
    
    @staticmethod
    def format_homework_link(google_drive_link: str, link_type: str = 'preview') -> str:
        """Format Google Drive link for different display types."""
        if link_type == 'preview':
            return google_drive_link.replace("/view?usp=sharing", "/preview")
        elif link_type == 'edit':
            return google_drive_link.replace("/view?usp=sharing", "/edit")
        elif link_type == 'download':
            if '/d/' in google_drive_link:
                file_id = google_drive_link.split('/d/')[1].split('/')[0]
                return f"https://drive.google.com/uc?export=download&id={file_id}"
        
        return google_drive_link


class HomeworkCache:
    """Manages homework caching for better performance."""
    
    @staticmethod
    def get_cached_homework_list(username: str) -> Optional[list]:
        """Get cached homework file list."""
        cache_key = f'homework_files_{username}'
        return st.session_state.get(cache_key)
    
    @staticmethod
    def cache_homework_list(username: str, files: list, ttl_minutes: int = 30) -> None:
        """Cache homework file list."""
        cache_key = f'homework_files_{username}'
        timestamp_key = f'homework_timestamp_{username}'
        
        import time
        st.session_state[cache_key] = files
        st.session_state[timestamp_key] = time.time()
    
    @staticmethod
    def is_cache_valid(username: str, ttl_minutes: int = 30) -> bool:
        """Check if cached homework data is still valid."""
        timestamp_key = f'homework_timestamp_{username}'
        
        if timestamp_key not in st.session_state:
            return False
        
        import time
        cached_time = st.session_state[timestamp_key]
        current_time = time.time()
        
        return (current_time - cached_time) < (ttl_minutes * 60)
    
    @staticmethod
    def clear_homework_cache(username: str = None) -> None:
        """Clear homework cache for specific user or all users."""
        if username:
            keys_to_remove = [
                f'homework_files_{username}',
                f'homework_timestamp_{username}'
            ]
        else:
            keys_to_remove = [
                key for key in st.session_state.keys() 
                if key.startswith('homework_files_') or key.startswith('homework_timestamp_')
            ]
        
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]


def create_homework_handler() -> HomeworkHandler:
    """Factory function to create HomeworkHandler instance."""
    return HomeworkHandler()
