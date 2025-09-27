from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from files.constants import USERNAME_DICT

USERNAME_DICT_REVERSE: Dict[int, str] = {
    uid: uname for uname, uid in USERNAME_DICT.items() if uid is not None
}

def uname(uid: Optional[int]) -> str:
    if uid is None:
        return "uid_None"
    return USERNAME_DICT_REVERSE.get(uid, f"uid_{uid}")


class UserRole(Enum):
    """User roles with different permission levels."""
    ADMIN = "admin"
    STUDENT = "student"
    DEMO = "demo"


class MenuOption(Enum):
    """Available menu options."""
    HOMEWORK = "Homework"
    INFORMATICS = "Informatics"
    MATHEMATICS = "Mathematics"
    VARIANTS = "Variants"
    STATISTICS = "Statistics"
    STUDENT_STATISTICS = "Student Statistics"


@dataclass
class UserConfig:
    """Configuration for a single user."""
    username: str
    user_id: Optional[int]
    role: UserRole
    menu_options: List[MenuOption]
    stats_menu: List[str]
    math_tasks: Optional[List[str]] = None
    
    def has_menu_access(self, menu: MenuOption) -> bool:
        return menu in self.menu_options
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def is_demo(self) -> bool:
        return self.role == UserRole.DEMO


class UserManager:
    """Manages user configurations and permissions."""
    def __init__(self):
        self._users = self._initialize_users()

    def _initialize_users(self) -> Dict[str, UserConfig]:
        users: Dict[str, UserConfig] = {}

        def add(uid: Optional[int], role: UserRole, menu: List[MenuOption],
                stats: List[str], math_tasks: Optional[List[str]] = None):
            key = uname(uid)
            users[key] = UserConfig(
                username=key,
                user_id=uid,
                role=role,
                menu_options=menu,
                stats_menu=stats,
                math_tasks=math_tasks
            )

        add(
            uid=5,
            role=UserRole.ADMIN,
            menu=[MenuOption.HOMEWORK, MenuOption.STUDENT_STATISTICS,
                  MenuOption.INFORMATICS, MenuOption.MATHEMATICS,
                  MenuOption.VARIANTS, MenuOption.STATISTICS],
            stats=[' ', 'Completing Tasks', 'Completing Tasks MATH'],
        )

        add(uid=22, role=UserRole.STUDENT,
            menu=[MenuOption.HOMEWORK, MenuOption.INFORMATICS],
            stats=[], math_tasks=[])

        add(uid=21, role=UserRole.STUDENT,
            menu=[MenuOption.HOMEWORK, MenuOption.INFORMATICS],
            stats=[], math_tasks=[])

        add(uid=20, role=UserRole.STUDENT,
            menu=[MenuOption.HOMEWORK, MenuOption.INFORMATICS],
            stats=[], math_tasks=[])

        add(uid=19, role=UserRole.STUDENT,
            menu=[MenuOption.HOMEWORK, MenuOption.INFORMATICS],
            stats=[], math_tasks=[])

        add(uid=1, role=UserRole.STUDENT,
            menu=[MenuOption.HOMEWORK, MenuOption.MATHEMATICS,
                  MenuOption.VARIANTS, MenuOption.STATISTICS],
            stats=[' ', 'Completing Tasks MATH'],
            math_tasks=['Тригонометрия', 'Неравенство', 'Стереометрия',
                        'Экономика', 'Параметр', 'Последняя'])

        add(uid=USERNAME_DICT.get('demo'), role=UserRole.DEMO,
            menu=[MenuOption.HOMEWORK, MenuOption.INFORMATICS,
                  MenuOption.MATHEMATICS, MenuOption.VARIANTS, MenuOption.STATISTICS],
            stats=[' ', 'Completing Tasks', 'Completing Tasks MATH'])


        return users
    
    def get_user(self, username: str) -> Optional[UserConfig]:
        return self._users.get(username)
    
    def get_user_menu(self, username: str) -> List[str]:
        user = self.get_user(username)
        if not user:
            return [MenuOption.HOMEWORK.value, MenuOption.STUDENT_STATISTICS.value, 
                    MenuOption.INFORMATICS.value, MenuOption.MATHEMATICS.value, 
                    MenuOption.VARIANTS.value, MenuOption.STATISTICS.value]
        return [option.value for option in user.menu_options]
    
    def get_user_id(self, username: str) -> Optional[int]:
        user = self.get_user(username)
        return user.user_id if user else None
    
    def get_math_tasks(self, username: str) -> List[str]:
        user = self.get_user(username)
        if not user:
            return ['', 'Тригонометрия', 'Стереометрия', 'Неравенство', 
                    'Экономика', 'Планиметрия', 'Параметр', 'Последняя']
        if user.math_tasks:
            return [''] + user.math_tasks
        return ['', 'Тригонометрия', 'Стереометрия', 'Неравенство', 
                'Экономика', 'Планиметрия', 'Параметр', 'Последняя']
    
    def get_stats_menu(self, username: str) -> List[str]:
        user = self.get_user(username)
        return user.stats_menu if user else []


user_manager = UserManager()

USERNAME_DICT_PUBLIC = {
    username: cfg.user_id
    for username, cfg in user_manager._users.items()
    if cfg.user_id is not None
}

if __name__ == '__main__':
    print(USERNAME_DICT)
    print(USERNAME_DICT_REVERSE)
    print(USERNAME_DICT_PUBLIC)
