import os
import json
import time
import ast
import getpass
import random
import math
import curses
from copy import deepcopy
from microkernel import Microkernel

# =========================
# VIRTUAL DISK SYSTEM
# =========================
DISK_FILE = "nova_disk.json"
DISK_BACKUP_FILE = DISK_FILE + ".bak"
VERSION = "NOVA-DOS CORE v2.0"
ANSI_RESET = "\033[0m"
COLOR_CODES = {
    "black": 0,
    "blue": 4,
    "green": 2,
    "cyan": 6,
    "red": 1,
    "magenta": 5,
    "yellow": 3,
    "white": 7,
    "bright_black": 8,
    "bright_red": 9,
    "bright_green": 10,
    "bright_yellow": 11,
    "bright_blue": 12,
    "bright_magenta": 13,
    "bright_cyan": 14,
    "bright_white": 15,
}
FONT_STYLES = {
    "normal": "0",
    "bold": "1",
    "underline": "4",
    "inverse": "7",
}

default_disk = {
    "users": {
        "admin": {"password": "admin"}
    },
    "directories": ["/", "/docs", "/games", "/system", "/users"],
    "files": {
        "/readme.txt": (
            "Welcome to NOVA-DOS CORE v2.0\n"
            "Type HELP for a detailed list of commands.\n"
            "Use COLOR and FONT to customize the display.\n"
            "Explore /docs for guides and built-in program help.\n"
        ),
        "/welcome.txt": (
            "=== NOVA-DOS WELCOME ===\n"
            "This virtual DOS-like shell supports file management, programs, and customization.\n"
            "Commands are designed to feel like a classic DOS environment.\n"
        ),
        "/docs/commands.txt": (
            "FILE SYSTEM:\n"
            "  DIR [path]  LIST directory contents\n"
            "  TYPE <file>  DISPLAY file contents\n"
            "  EDIT <file>  CREATE or EDIT a file\n"
            "  COPY <src> <dst>  COPY file\n"
            "  MOVE <src> <dst>  RENAME or MOVE file\n"
            "  DEL <file>  DELETE a file\n"
            "  MD <dir>  MAKE directory\n"
            "  RD <dir>  REMOVE empty directory\n"
            "  REN <src> <dst>  RENAME file or directory\n"
            "  TREE [path]  SHOW directory tree\n"
            "  FIND <term>  SEARCH files for text\n"
            "\n"
            "SYSTEM:\n"
            "  VER  SHOW system version\n"
            "  DATE  SHOW current date\n"
            "  TIME  SHOW current time\n"
            "  PROMPT [text]  CHANGE shell prompt\n"
            "  USER  SHOW current user\n"
            "  SYSINFO  SHOW system information\n"
            "  MEMORY  SHOW virtual memory status\n"
            "  FORMAT  FORMAT virtual disk\n"
            "  LANG <EN|RU>  SWITCH display language\n"
            "  CLS  CLEAR screen\n"
            "\n"
            "PROGRAMS:\n"
            "  CALC  Calculator\n"
            "  NOTE  Notepad\n"
            "  ASCII  ASCII art viewer\n"
            "  CLOCK  Digital clock\n"
            "  ENCODE  Text encoder utility\n"
            "  PANEL  System control panel\n"
            "  BANK  Bank manager and budget calculator\n"
            "\n"
            "GAMES:\n"
            "  GUESS  Number guessing game\n"
            "  RPS  Rock-Paper-Scissors\n"
            "  HANG  Hangman word game\n"
            "  SNAKE  Snake\n"
            "  TETRIS  Tetris\n"
            "  PONG  Pong game\n"
            "  BREAKOUT  Breakout game\n"
            "  TICTACTOE  Tic-Tac-Toe\n"
            "  SPACEINVADERS  Space Invaders\n"
            "  TREX  T-Rex Run game\n"
            "\n"
            "CUSTOMIZATION:\n"
            "  COLOR <fg> [bg]  Set text and background color\n"
            "  FONT <style>  Set display style (normal, bold, underline, inverse)\n"
        ),
        "/docs/commands_ru.txt": (
            "ФАЙЛОВАЯ СИСТЕМА:\n"
            "  DIR [path]  ПОКАЗАТЬ содержимое каталога\n"
            "  TYPE <file>  ПОКАЗАТЬ содержимое файла\n"
            "  EDIT <file>  СОЗДАТЬ или ОТРЕДАКТИРОВАТЬ файл\n"
            "  COPY <src> <dst>  КОПИРОВАТЬ файл\n"
            "  MOVE <src> <dst>  ПЕРЕМЕСТИТЬ или ПЕРЕИМЕНОВАТЬ файл\n"
            "  DEL <file>  УДАЛИТЬ файл\n"
            "  MD <dir>  СОЗДАТЬ каталог\n"
            "  RD <dir>  УДАЛИТЬ каталог\n"
            "  REN <src> <dst>  ПЕРЕИМЕНОВАТЬ файл или каталог\n"
            "  TREE [path]  ПОКАЗАТЬ дерево каталогов\n"
            "  FIND <term>  ПОИСК по содержимому и именам файлов\n"
            "\n"
            "СИСТЕМА:\n"
            "  VER  ПОКАЗАТЬ версию системы\n"
            "  DATE  ПОКАЗАТЬ текущую дату\n"
            "  TIME  ПОКАЗАТЬ текущее время\n"
            "  PROMPT [text]  УСТАНОВИТЬ текст подсказки\n"
            "  USER  ПОКАЗАТЬ текущего пользователя\n"
            "  SYSINFO  ПОКАЗАТЬ информацию о системе\n"
            "  MEMORY  ПОКАЗАТЬ статус виртуальной памяти\n"
            "  FORMAT  ОТФОРМАТИРОВАТЬ виртуальный диск\n"
            "  LANG <EN|RU>  ПЕРЕКЛЮЧИТЬ язык интерфейса\n"
            "  CLS  ОЧИСТИТЬ экран\n"
            "\n"
            "ПРОГРАММЫ:\n"
            "  CALC  Калькулятор\n"
            "  NOTE  Блокнот\n"
            "  ASCII  Просмотр ASCII-графики\n"
            "  CLOCK  Цифровые часы\n"
            "  ENCODE  Утилита кодирования текста\n"
            "  PANEL  Панель управления\n"
            "  BANK  Банковский менеджер и калькулятор бюджета\n"
            "\n"
            "ИГРЫ:\n"
            "  GUESS  Игра угадай число\n"
            "  RPS  Камень-ножницы-бумага\n"
            "  HANG  Виселица\n"
            "  SNAKE  Змейка\n"
            "  TETRIS  Тетрис\n"
            "  PONG  Пинг-понг\n"
            "  BREAKOUT  Сломай блоки\n"
            "  TICTACTOE  Крестики-нолики\n"
            "  SPACEINVADERS  Космические захватчики\n"
            "  TREX  Бег динозавра\n"
            "\n"
            "НАСТРОЙКИ:\n"
            "  COLOR <fg> [bg]  Установить цвет текста и фона\n"
            "  FONT <style>  Установить стиль шрифта (normal, bold, underline, inverse)\n"
        ),
        "/games/README.TXT": (
            "NOVA-DOS GAME SUITE\n"
            "  GUESS  Play the number guessing game.\n"
            "  RPS  Play rock-paper-scissors.\n"
            "  HANG  Play a simple hangman game.\n"
            "  SNAKE  Play the snake game.\n"
            "  TETRIS  Play the tetris game.\n"
            "  PONG  Play pong game.\n"
            "  BREAKOUT  Play breakout game.\n"
            "  TICTACTOE  Play tic-tac-toe vs AI.\n"
            "  SPACEINVADERS  Play space invaders.\n"
            "  TREX  Play T-Rex run game.\n"
            "  ASCII  View retro ASCII patterns and screen tests.\n"
        ),
        "/system/drivers.txt": (
            "Installed virtual drivers:\n"
            "  keyboard.sys\n"
            "  display.sys\n"
            "  disk.sys\n"
            "  bios.sys\n"
        )
    },
    "current_user": None,
    "bank": {},
    "current_dir": "/",
    "prompt": "NOVA-DOS",
    "settings": {
        "text_color": "white",
        "bg_color": "black",
        "font": "bold",
        "language": "EN"
    }
}


TRANSLATIONS = {
    "EN": {
        "boot_title": "NOVA-DOS CORE v2.0",
        "boot_message": "Booting NOVA-DOS...",
        "system_ready": "System ready.",
        "login_title": "=== LOGIN SYSTEM ===",
        "user_prompt": "User: ",
        "password_prompt": "Password: ",
        "login_success": "Login successful.",
        "login_failed": "Login failed. Try again.",
        "format_auth_start": "Enter credentials to start format process.",
        "format_auth_confirm": "Confirm credentials to complete formatting.",
        "user_not_found": "User not found.",
        "user_exists": "Target username already exists.",
        "user_renamed": "User renamed to {username}.",
        "password_updated": "Password updated.",
        "password_mismatch": "Passwords do not match.",
        "rename_user_usage": "Usage: RENUSER <old> <new>",
        "change_password_usage": "Usage: CHPASS [user]",
        "password_prompt_new": "New password: ",
        "password_prompt_confirm": "Confirm password: ",
        "unknown_command": "Unknown command: {cmd}. Type HELP for commands.",
        "exit_message": "Shutting down NOVA-DOS...",
        "format_confirm": "Format virtual disk? All files will be erased (Y/N): ",
        "format_cancel": "Format canceled.",
        "format_done": "Disk formatted.",
        "prompt_set": "Prompt set to {prompt}",
        "language_set": "Language set to {lang}",
        "language_invalid": "Invalid language. Use EN or RU.",
        "help_header": "NOVA-DOS COMMANDS",
        "help_file_usage": "Usage: TYPE <file>",
        "help_edit_usage": "Usage: EDIT <file>",
        "help_copy_usage": "Usage: COPY <src> <dst>",
        "help_move_usage": "Usage: MOVE <src> <dst>",
        "help_del_usage": "Usage: DEL <file>",
        "help_md_usage": "Usage: MD <dir>",
        "help_rd_usage": "Usage: RD <dir>",
        "login_error": "Please enter a numeric value.",
        "file_not_found": "File not found.",
        "directory_not_found": "Directory not found.",
        "dir_exists": "Directory already exists.",
        "cannot_remove_root": "Cannot remove root directory.",
        "dir_not_empty": "Directory is not empty.",
        "file_deleted": "File deleted.",
        "file_copied": "File copied.",
        "file_moved": "File moved.",
        "dir_created": "Directory created: {target}",
        "dir_removed": "Directory removed: {target}",
        "saved_to": "Saved to {path}",
        "color_set": "Text color set to {fg}, background set to {bg}.",
        "font_set": "Font style set to {style}.",
        "press_exit": "Type EXIT to return to shell.",
        "syntax_error": "Syntax error or unsupported expression.",
        "guess_prompt": "Guess a number 1-100 (or EXIT): ",
        "guess_reveal": "The number was {number}.",
        "too_low": "Too low.",
        "too_high": "Too high.",
        "guess_win": "Correct! You guessed it in {attempts} attempts.",
        "notepad_save": "Type END on a new line to save.",
        "panel_view": "View current settings",
        "panel_reset": "Reset colors and font",
        "panel_guide": "Show built-in command guide",
        "font_usage": "Usage: FONT <normal|bold|underline|inverse>",
        "calculator_title": "=== CALCULATOR MODE ===",
        "notepad_title": "=== NOTEPAD MODE ===",
        "ascii_title": "=== ASCII ART VIEWER ===",
        "guess_title": "NUMBER GUESSING GAME",
        "panel_title": "SYSTEM CONTROL PANEL",
        "menu_select": "Select option [1-5]: ",
        "return_shell": "Return to shell",
        "settings_info": "Text color: {color}\nBackground: {bg}\nFont style: {font}",
        "reset_display": "Display reset to default bold white on black.",
        "choose_option": "Please choose {options}.",
        "help_text": (
            "\nFILE SYSTEM:\n"
            "  DIR [path]          list directory contents\n"
            "  TREE [path]         show folder tree\n"
            "  TYPE <file>         display file with line numbers\n"
            "  EDIT <file>         create or edit a file\n"
            "  COPY <src> <dst>    copy a file\n"
            "  MOVE <src> <dst>    move or rename a file\n"
            "  REN <src> <dst>     rename a file or directory\n"
            "  DEL <file>          delete a file\n"
            "  MD <dir>            make directory\n"
            "  RD <dir>            remove directory\n"
            "  FIND <term>         search contents and filenames\n"
            "\nSYSTEM:\n"
            "  VER                 show system version\n"
            "  DATE                show current date\n"
            "  TIME                show current time\n"
            "  PROMPT [text]       set shell prompt text\n"
            "  USER                show current user\n"
            "  SYSINFO             display system information\n"
            "  MEMORY              display virtual memory status\n"
            "  FORMAT              format the virtual disk\n"
            "  LANG <EN|RU>        switch display language\n"
            "  CLS                 clear screen\n"
            "  HELP or ?           show this help text\n"
            "  EXIT or QUIT        exit NOVA-DOS\n"
            "\nPROGRAMS:\n"
            "  CALC                calculator\n"
            "  NOTE                notepad\n"
            "  ASCII               retro ASCII art viewer\n"
            "  CLOCK               digital clock refresher\n"
            "  ENCODE              text encode/decode utility\n"
            "  PANEL               system control panel\n"
            "  BANK               bank manager and budget calculator\n"
            "  RUN <file.py>       execute Python code from file\n"
            "  PAINT                simple paint program\n"
            "  PROGRAMS             list programs\n"
            "  ADDPROG <path> <name>  register a file as a program (requires auth)\n"
            "  DELPROG <name|path>    remove a program you added (requires auth)\n"
            "  ADDGAME <path> <name>  register a file as a game (requires auth)\n"
            "  DELGAME <name|path>    remove a game you added (requires auth)\n"
            "  LAUNCH <name|path>     launch a registered program or game\n"
            "\nGAMES:\n"
            "  GUESS               number guessing game\n"
            "  RPS                 rock-paper-scissors\n"
            "  HANG                hangman word game\n"
            "  SNAKE               snake game\n"
            "  TETRIS              tetris game\n"
            "  PONG                pong game\n"
            "  BREAKOUT            breakout game\n"
            "  TICTACTOE           tic-tac-toe vs AI\n"
            "  SPACEINVADERS       space invaders\n"
            "  TREX                t-rex run game\n"
            "\nCUSTOMIZATION:\n"
            "  COLOR <fg> [bg]     set text and background color\n"
            "  FONT <style>        set font style (normal bold underline inverse)\n"
            "  RENUSER <old> <new>  rename a user login\n"
            "  CHPASS [user]        change a user password\n"
            "  PASSWD [user]        change a user password\n"
        )
    },
    "RU": {
        "boot_title": "NOVA-DOS CORE v2.0",
        "boot_message": "Загрузка NOVA-DOS...",
        "system_ready": "Система готова.",
        "login_title": "=== СИСТЕМА ВХОДА ===",
        "user_prompt": "Пользователь: ",
        "password_prompt": "Пароль: ",
        "login_success": "Вход выполнен.",
        "login_failed": "Ошибка входа. Попробуйте снова.",
        "format_auth_start": "Введите данные для начала форматирования.",
        "format_auth_confirm": "Подтвердите данные, чтобы завершить форматирование.",
        "user_not_found": "Пользователь не найден.",
        "user_exists": "Целевое имя пользователя уже существует.",
        "user_renamed": "Учётная запись переименована в {username}.",
        "password_updated": "Пароль обновлён.",
        "password_mismatch": "Пароли не совпадают.",
        "rename_user_usage": "Использование: RENUSER <old> <new>",
        "change_password_usage": "Использование: CHPASS [user]",
        "password_prompt_new": "Новый пароль: ",
        "password_prompt_confirm": "Подтвердите пароль: ",
        "unknown_command": "Неизвестная команда: {cmd}. Введите HELP для списка команд.",
        "exit_message": "Выключение NOVA-DOS...",
        "format_confirm": "Отформатировать виртуальный диск? Все файлы будут удалены (Y/N): ",
        "format_cancel": "Форматирование отменено.",
        "format_done": "Диск отформатирован.",
        "prompt_set": "Подсказка установлена на {prompt}",
        "language_set": "Язык переключен на {lang}",
        "language_invalid": "Недопустимый язык. Используйте EN или RU.",
        "help_header": "КОМАНДЫ NOVA-DOS",
        "help_file_usage": "Использование: TYPE <file>",
        "help_edit_usage": "Использование: EDIT <file>",
        "help_copy_usage": "Использование: COPY <src> <dst>",
        "help_move_usage": "Использование: MOVE <src> <dst>",
        "help_del_usage": "Использование: DEL <file>",
        "help_md_usage": "Использование: MD <dir>",
        "help_rd_usage": "Использование: RD <dir>",
        "login_error": "Введите числовое значение.",
        "file_not_found": "Файл не найден.",
        "directory_not_found": "Каталог не найден.",
        "dir_exists": "Каталог уже существует.",
        "cannot_remove_root": "Невозможно удалить корневой каталог.",
        "dir_not_empty": "Каталог не пуст.",
        "file_deleted": "Файл удален.",
        "file_copied": "Файл скопирован.",
        "file_moved": "Файл перемещен.",
        "dir_created": "Каталог создан: {target}",
        "dir_removed": "Каталог удален: {target}",
        "saved_to": "Сохранено в {path}",
        "color_set": "Текст: {fg}, фон: {bg}.",
        "font_set": "Стиль шрифта установлен: {style}.",
        "press_exit": "Введите EXIT для выхода в оболочку.",
        "syntax_error": "Синтаксическая ошибка или неподдерживаемое выражение.",
        "guess_prompt": "Угадайте число от 1 до 100 (или EXIT): ",
        "guess_reveal": "Число было {number}.",
        "too_low": "Слишком мало.",
        "too_high": "Слишком много.",
        "guess_win": "Верно! Вы угадали за {attempts} попыток.",
        "notepad_save": "Введите END на новой строке, чтобы сохранить.",
        "panel_view": "Просмотреть текущие настройки",
        "panel_reset": "Сбросить цвет и шрифт",
        "panel_guide": "Показать встроенное руководство",
        "font_usage": "Использование: FONT <normal|bold|underline|inverse>",
        "calculator_title": "=== РЕЖИМ КАЛЬКУЛЯТОРА ===",
        "notepad_title": "=== РЕЖИМ БЛОКНОТА ===",
        "ascii_title": "=== ПРОСМОТР ASCII ===",
        "guess_title": "ИГРА УГАДАЙ ЧИСЛО",
        "panel_title": "ПАНЕЛЬ УПРАВЛЕНИЯ СИСТЕМОЙ",
        "menu_select": "Выберите опцию [1-5]: ",
        "return_shell": "Вернуться в оболочку",
        "settings_info": "Цвет текста: {color}\nФон: {bg}\nСтиль шрифта: {font}",
        "reset_display": "Дисплей сброшен на стандартный жирный белый по черному.",
        "choose_option": "Пожалуйста, выберите {options}.",
        "help_text": (
            "\nФАЙЛОВАЯ СИСТЕМА:\n"
            "  DIR [path]          показать содержимое каталога\n"
            "  TREE [path]         показать дерево каталогов\n"
            "  TYPE <file>         показать файл с номерами строк\n"
            "  EDIT <file>         создать или отредактировать файл\n"
            "  COPY <src> <dst>    скопировать файл\n"
            "  MOVE <src> <dst>    переместить или переименовать файл\n"
            "  REN <src> <dst>     переименовать файл или каталог\n"
            "  DEL <file>          удалить файл\n"
            "  MD <dir>            создать каталог\n"
            "  RD <dir>            удалить каталог\n"
            "  FIND <term>         поиск по содержимому и именам файлов\n"
            "\nСИСТЕМА:\n"
            "  VER                 показать версию системы\n"
            "  DATE                показать текущую дату\n"
            "  TIME                показать текущее время\n"
            "  PROMPT [text]       установить текст подсказки\n"
            "  USER                показать текущего пользователя\n"
            "  SYSINFO             показать информацию о системе\n"
            "  MEMORY              показать статус виртуальной памяти\n"
            "  FORMAT              отформатировать виртуальный диск\n"
            "  LANG <EN|RU>        переключить язык интерфейса\n"
            "  CLS                 очистить экран\n"
            "  HELP or ?           показать эту справку\n"
            "  EXIT or QUIT        выйти из NOVA-DOS\n"
            "\nПРОГРАММЫ:\n"
            "  CALC                калькулятор\n"
            "  NOTE                блокнот\n"
            "  ASCII               просмотр ASCII-графики\n"
            "  CLOCK               цифровые часы\n"
            "  ENCODE              утилита кодирования текста\n"
            "  PANEL               панель управления\n"
            "  BANK               банковский менеджер и калькулятор бюджета\n"
            "  RUN <file.py>       выполнить код Python из файла\n"
            "  PAINT                простая программа рисования\n"
            "  PROGRAMS             список программ\n"
            "  ADDPROG <path> <name>  зарегистрировать файл как программу (требуется авторизация)\n"
            "  DELPROG <name|path>    удалить программу, которую вы добавили (требуется авторизация)\n"
            "  ADDGAME <path> <name>  зарегистрировать файл как игру (требуется авторизация)\n"
            "  DELGAME <name|path>    удалить игру, которую вы добавили (требуется авторизация)\n"
            "  LAUNCH <name|path>     запустить зарегистрированную программу или игру\n"
            "\nИГРЫ:\n"
            "  GUESS               игра \"Угадай число\"\n"
            "  RPS                 камень-ножницы-бумага\n"
            "  HANG                виселица\n"
            "  SNAKE               змейка\n"
            "  TETRIS              тетрис\n"
            "  PONG                пинг-понг\n"
            "  BREAKOUT            сломай блоки\n"
            "  TICTACTOE           крестики-нолики\n"
            "  SPACEINVADERS       космические захватчики\n"
            "  TREX                бег динозавра\n"
            "\nНАСТРОЙКА:\n"
            "  COLOR <fg> [bg]     установить цвет текста и фона\n"
            "  FONT <style>        установить стиль шрифта (normal bold underline inverse)\n"
            "  RENUSER <old> <new>  переименовать учетную запись\n"
            "  CHPASS [user]        изменить пароль пользователя\n"
            "  PASSWD [user]        изменить пароль пользователя\n"
        )
    }
}


# Instantiate microkernel to manage disk and sandboxed execution
kernel = Microkernel(DISK_FILE, default_disk=default_disk)


def save_disk():
    try:
        kernel.save_disk(disk)
    except Exception as e:
        echo(f"Failed to save disk: {e}", fg="bright_red")


def t(key, **kwargs):
    lang = disk.get("settings", {}).get("language", "EN")
    text = TRANSLATIONS.get(lang, TRANSLATIONS["EN"]).get(key)
    if text is None:
        text = TRANSLATIONS["EN"].get(key, key)
    return text.format(**kwargs)


disk = kernel.load_disk()

# Ensure essential disk keys exist to avoid KeyError when printing before
# main initialization (e.g., boot sequence may call styling helpers).
if "settings" not in disk:
    disk["settings"] = deepcopy(default_disk["settings"])
if "directories" not in disk:
    disk["directories"] = deepcopy(default_disk["directories"])
if "files" not in disk:
    disk["files"] = deepcopy(default_disk["files"])
if "users" not in disk:
    disk["users"] = deepcopy(default_disk["users"])
if "current_dir" not in disk:
    disk["current_dir"] = deepcopy(default_disk["current_dir"])
if "prompt" not in disk:
    disk["prompt"] = deepcopy(default_disk["prompt"])
if "current_user" not in disk:
    disk["current_user"] = None
if "language" not in disk.get("settings", {}):
    disk["settings"]["language"] = default_disk["settings"]["language"]

# List of user-added programs/games (each entry: {path, display, added_by, kind})
if "user_added_programs" not in disk:
    disk["user_added_programs"] = []
# Persist any added defaults back to the disk file so subsequent runs are consistent
save_disk()


# =========================
# ANSI STYLING HELPERS
# =========================
def color_code(name, is_bg=False):
    if name not in COLOR_CODES:
        return None
    code = COLOR_CODES[name]
    if code < 8:
        return 40 + code if is_bg else 30 + code
    return 100 + (code - 8) if is_bg else 90 + (code - 8)


def style_text(text, fg=None, bg=None, style=None):
    fg = fg or disk["settings"].get("text_color", "white")
    bg = bg or disk["settings"].get("bg_color", "black")
    style = style or disk["settings"].get("font", "bold")

    parts = []
    if style in FONT_STYLES:
        parts.append(FONT_STYLES[style])
    fg_code = color_code(fg, is_bg=False)
    bg_code = color_code(bg, is_bg=True)
    if fg_code is not None:
        parts.append(str(fg_code))
    if bg_code is not None:
        parts.append(str(bg_code))

    return f"\033[{';'.join(parts)}m{text}{ANSI_RESET}"


def echo(text, fg=None, bg=None, style=None, end="\n"):
    print(style_text(text, fg, bg, style), end=end)


def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")


def print_banner():
    # Minimal, non-ASCII banner for faster, cleaner boot
    clear_screen()
    echo("NOVA-DOS CORE v2.0", fg="bright_cyan", style="bold")
    echo(t("boot_message"), fg="bright_yellow")
    time.sleep(0.25)
    echo(t("system_ready") + "\n", fg="white")


# =========================
# AUTH SYSTEM
# =========================
def login():
    echo(t("login_title"), fg="bright_magenta", style="bold")
    while True:
        user = input(style_text(t("user_prompt"), fg="bright_white", style="bold"))
        pw = getpass.getpass(style_text(t("password_prompt"), fg="bright_white", style="bold"))

        if user in disk["users"] and disk["users"][user]["password"] == pw:
            disk["current_user"] = user
            echo(t("login_success") + "\n", fg="bright_green")
            return

        echo(t("login_failed") + "\n", fg="bright_red")


# =========================
# PATH + STORAGE HELPERS
# =========================
def normalize_path(path):
    path = path.replace("\\", "/").strip()
    if path == "":
        return disk["current_dir"]
    if path.startswith("/"):
        normalized = os.path.normpath(path)
    else:
        base = disk["current_dir"].rstrip("/")
        normalized = os.path.normpath(f"{base}/{path}") if base else os.path.normpath(f"/{path}")

    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return normalized


def ensure_directory(path):
    path = normalize_path(path)
    if path == "/":
        if "/" not in disk["directories"]:
            disk["directories"].append("/")
        return

    parts = path.strip("/").split("/")
    current = ""
    for part in parts:
        current += "/" + part
        if current not in disk["directories"]:
            disk["directories"].append(current)


def path_is_dir(path):
    return normalize_path(path) in disk["directories"]


def path_is_file(path):
    return normalize_path(path) in disk["files"]


def get_directory_contents(dir_path):
    dir_path = normalize_path(dir_path)
    if dir_path != "/" and dir_path not in disk["directories"]:
        return None

    prefix = dir_path if dir_path.endswith("/") else f"{dir_path}/"
    contents = {}

    for directory in disk["directories"]:
        if directory == dir_path:
            continue
        if directory.startswith(prefix):
            remainder = directory[len(prefix):].split("/", 1)[0]
            if remainder:
                contents[remainder] = {"type": "DIR"}

    for file_path, content in disk["files"].items():
        if file_path.startswith(prefix):
            remainder = file_path[len(prefix):].split("/", 1)[0]
            if remainder and "/" not in file_path[len(prefix):]:
                contents[remainder] = {"type": "FILE", "size": len(content)}

    return contents


def formatted_size(length):
    if length < 1024:
        return f"{length} bytes"
    if length < 1024 * 1024:
        return f"{length // 1024} KB"
    return f"{length // (1024 * 1024)} MB"


def make_file(path, content):
    path = normalize_path(path)
    parent = os.path.dirname(path)
    ensure_directory(parent)
    disk["files"][path] = content
    save_disk()


def delete_file(path):
    target = normalize_path(path)
    if target in disk["files"]:
        del disk["files"][target]
        save_disk()
        echo("File deleted.", fg="bright_green")
    else:
        echo("File not found.", fg="bright_red")


def copy_file(src, dst):
    source = normalize_path(src)
    destination = normalize_path(dst)
    if source not in disk["files"]:
        echo("Source file not found.", fg="bright_red")
        return

    if path_is_dir(destination):
        destination = normalize_path(os.path.join(destination, os.path.basename(source)).replace("\\", "/"))

    parent = os.path.dirname(destination)
    ensure_directory(parent)
    disk["files"][destination] = disk["files"][source]
    save_disk()
    echo("File copied.", fg="bright_green")


def move_file(src, dst):
    source = normalize_path(src)
    destination = normalize_path(dst)
    if source not in disk["files"]:
        echo("Source file not found.", fg="bright_red")
        return

    if path_is_dir(destination):
        destination = normalize_path(os.path.join(destination, os.path.basename(source)).replace("\\", "/"))

    parent = os.path.dirname(destination)
    ensure_directory(parent)
    disk["files"][destination] = disk["files"][source]
    del disk["files"][source]
    save_disk()
    echo("File moved.", fg="bright_green")


def make_directory(path):
    target = normalize_path(path)
    if target in disk["directories"]:
        echo("Directory already exists.", fg="bright_yellow")
        return
    ensure_directory(target)
    save_disk()
    echo(f"Directory created: {target}", fg="bright_green")


def remove_directory(path):
    target = normalize_path(path)
    if target == "/":
        echo("Cannot remove root directory.", fg="bright_red")
        return
    if target not in disk["directories"]:
        echo("Directory not found.", fg="bright_red")
        return

    prefix = f"{target}/"
    for directory in disk["directories"]:
        if directory != target and directory.startswith(prefix):
            echo("Directory is not empty.", fg="bright_yellow")
            return
    for file_path in disk["files"]:
        if file_path.startswith(prefix):
            echo("Directory is not empty.", fg="bright_yellow")
            return

    disk["directories"].remove(target)
    save_disk()
    echo(f"Directory removed: {target}", fg="bright_green")


def rename_item(src, dst):
    source = normalize_path(src)
    destination = normalize_path(dst)
    if source in disk["files"]:
        copy_file(source, destination)
        delete_file(source)
        echo("File renamed.", fg="bright_green")
        return
    if source in disk["directories"]:
        if destination in disk["directories"]:
            echo("Destination already exists.", fg="bright_yellow")
            return
        disk["directories"].append(destination)
        for directory in list(disk["directories"]):
            if directory.startswith(source + "/"):
                disk["directories"].append(directory.replace(source, destination, 1))
                disk["directories"].remove(directory)
        for file_path in list(disk["files"]):
            if file_path.startswith(source + "/"):
                disk["files"][file_path.replace(source, destination, 1)] = disk["files"].pop(file_path)
        disk["directories"].remove(source)
        save_disk()
        echo("Directory renamed.", fg="bright_green")
        return
    echo("Source not found.", fg="bright_red")


def find_text(term):
    term = term.lower()
    results = []
    for path, content in disk["files"].items():
        if term in path.lower() or term in content.lower():
            results.append(path)
    if results:
        for entry in sorted(results):
            echo(entry, fg="bright_cyan")
    else:
        echo("No matches found.", fg="bright_yellow")


def get_directory_tree(dir_path, prefix=""):
    contents = get_directory_contents(dir_path)
    if contents is None:
        return ""
    result = ""
    items = sorted(contents.items())
    for index, (name, entry) in enumerate(items):
        branch = "└── " if index == len(items) - 1 else "├── "
        result += f"{prefix}{branch}{name}\n"
        if entry["type"] == "DIR":
            next_path = normalize_path(f"{dir_path}/{name}")
            ext = "    " if index == len(items) - 1 else "│   "
            result += get_directory_tree(next_path, prefix + ext)
    return result


def tree_command(path=None):
    target = normalize_path(path if path else disk["current_dir"])
    if not path_is_dir(target):
        echo("Directory not found.", fg="bright_red")
        return
    echo(f"Directory tree for {target}:", fg="bright_white", style="bold")
    print(get_directory_tree(target).rstrip())


def type_file(path):
    target = normalize_path(path)
    if target in disk["files"]:
        content = disk["files"][target]
        for index, line in enumerate(content.splitlines(), start=1):
            echo(f"{index:03}: {line}", fg="bright_white")
    else:
        echo("File not found.", fg="bright_red")


def edit_file(path):
    target = normalize_path(path)
    parent = os.path.dirname(target)
    ensure_directory(parent)
    if target in disk["files"]:
        echo(f"=== Editing {target} ===", fg="bright_cyan", style="bold")
        echo(disk["files"][target], fg="bright_black")
    else:
        echo(f"Creating new file: {target}", fg="bright_yellow")
    echo("Enter text. Type END on a new line to save.", fg="bright_white")
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    disk["files"][target] = "\n".join(lines)
    save_disk()
    echo(f"Saved {target}.", fg="bright_green")


def show_date():
    echo(time.strftime("%Y-%m-%d"), fg="bright_white")


def show_time():
    echo(time.strftime("%H:%M:%S"), fg="bright_white")


def version():
    echo(VERSION, fg="bright_white", style="bold")


def sysinfo():
    echo("SYSTEM INFORMATION", fg="bright_magenta", style="bold")
    echo(f"Version: {VERSION}", fg="bright_white")
    echo(f"Current user: {disk['current_user']}", fg="bright_white")
    echo(f"Current path: {disk['current_dir']}", fg="bright_white")
    echo(f"Files: {len(disk['files'])}", fg="bright_white")
    echo(f"Folders: {len(disk['directories'])}", fg="bright_white")
    echo(f"Disk file: {DISK_FILE}", fg="bright_white")


def memory_status():
    total_files = len(disk["files"])
    total_dirs = len(disk["directories"])
    echo("VIRTUAL MEMORY STATUS", fg="bright_magenta", style="bold")
    echo(f"Allocated file entries: {total_files}", fg="bright_white")
    echo(f"Allocated directory entries: {total_dirs}", fg="bright_white")
    echo(f"Estimated disk size: {sum(len(v) for v in disk['files'].values()) // 1024} KB", fg="bright_white")


def prompt_login_credentials(message=None):
    if message:
        echo(message, fg="bright_white")
    user = input(style_text(t("user_prompt"), fg="bright_white", style="bold"))
    pw = getpass.getpass(style_text(t("password_prompt"), fg="bright_white", style="bold"))
    if user in disk["users"] and disk["users"][user]["password"] == pw:
        return user
    echo(t("login_failed") + "\n", fg="bright_red")
    return None


def format_disk():
    first_user = prompt_login_credentials(t("format_auth_start"))
    if not first_user:
        echo(t("format_cancel"), fg="bright_yellow")
        return

    confirmation = input(style_text(t("format_confirm"), fg="bright_red", style="bold"))
    if confirmation.lower() != "y":
        echo(t("format_cancel"), fg="bright_yellow")
        return

    second_user = prompt_login_credentials(t("format_auth_confirm"))
    if second_user != first_user:
        echo(t("format_cancel"), fg="bright_yellow")
        return

    disk.clear()
    disk.update(deepcopy(default_disk))
    if second_user in disk["users"]:
        disk["current_user"] = second_user
    save_disk()
    echo(t("format_done"), fg="bright_green")


def set_prompt(text):
    if text:
        disk["prompt"] = text
    else:
        disk["prompt"] = "NOVA-DOS"
    save_disk()
    echo(t("prompt_set", prompt=disk["prompt"]), fg="bright_green")


def rename_login(old_name, new_name):
    if old_name not in disk["users"]:
        echo(t("user_not_found"), fg="bright_red")
        return
    if not new_name:
        echo(t("rename_user_usage"), fg="bright_white")
        return
    if new_name in disk["users"]:
        echo(t("user_exists"), fg="bright_yellow")
        return
    disk["users"][new_name] = disk["users"].pop(old_name)
    if disk.get("current_user") == old_name:
        disk["current_user"] = new_name
    save_disk()
    echo(t("user_renamed", username=new_name), fg="bright_green")


def change_password(args):
    username = args[0] if args else disk.get("current_user")
    if not username:
        echo(t("change_password_usage"), fg="bright_white")
        return
    if username not in disk["users"]:
        echo(t("user_not_found"), fg="bright_red")
        return
    new_pw = getpass.getpass(style_text(t("password_prompt_new"), fg="bright_white", style="bold"))
    confirm_pw = getpass.getpass(style_text(t("password_prompt_confirm"), fg="bright_white", style="bold"))
    if new_pw != confirm_pw:
        echo(t("password_mismatch"), fg="bright_red")
        return
    disk["users"][username]["password"] = new_pw
    save_disk()
    echo(t("password_updated"), fg="bright_green")


def set_color(args):
    if not args:
        echo("Usage: COLOR <fg> [bg]", fg="bright_white")
        return
    fg = args[0].lower()
    bg = args[1].lower() if len(args) > 1 else disk["settings"].get("bg_color", "black")
    if fg not in COLOR_CODES or bg not in COLOR_CODES:
        echo("Invalid color. Supported colors: black blue green cyan red magenta yellow white bright_black bright_red bright_green bright_yellow bright_blue bright_magenta bright_cyan bright_white", fg="bright_red")
        return
    disk["settings"]["text_color"] = fg
    disk["settings"]["bg_color"] = bg
    save_disk()
    echo(f"Text color set to {fg}, background set to {bg}.", fg=fg, bg=bg)


def set_font(args):
    if not args:
        echo(t("font_usage"), fg="bright_white")
        return
    style = args[0].lower()
    if style not in FONT_STYLES:
        echo(t("font_usage"), fg="bright_red")
        return
    disk["settings"]["font"] = style
    save_disk()
    echo(t("font_set", style=style), fg="bright_white")


def show_help():
    echo(t("help_header"), fg="bright_cyan", style="bold")
    echo(t("help_text"), fg="bright_white")



def ascii_art():
    echo(t("ascii_title"), fg="bright_cyan", style="bold")
    art = [
        "      .-\"\"-.",
        "     /  _ _  \\",
        "    |  /\\ /\\  |",
        "    |  \\_V_/  |",
        "     \\  '_'  /",
        "      '-.__.-'",
        "   NOVA-DOS RETRO TEST"
    ]
    for line in art:
        echo(line, fg="bright_magenta")

def guess_game():
    echo(t("guess_title"), fg="bright_yellow", style="bold")
    number = random.randint(1, 100)
    attempts = 0
    while True:
        guess = input(style_text(t("guess_prompt"), fg="bright_white"))
        if guess.lower() == "exit":
            echo(t("guess_reveal", number=number), fg="bright_cyan")
            break
        try:
            guess_val = int(guess)
        except ValueError:
            echo(t("login_error"), fg="bright_red")
            continue
        attempts += 1
        if guess_val < number:
            echo(t("too_low"), fg="bright_blue")
        elif guess_val > number:
            echo(t("too_high"), fg="bright_blue")
        else:
            echo(t("guess_win", attempts=attempts), fg="bright_green")
            break


def control_panel():
    echo(t("panel_title"), fg="bright_magenta", style="bold")
    echo("1) " + t("panel_view"), fg="bright_white")
    echo("2) " + t("panel_reset"), fg="bright_white")
    echo("3) " + t("panel_guide"), fg="bright_white")
    echo("4) " + t("return_shell"), fg="bright_white")
    while True:
        choice = input(style_text(t("menu_select"), fg="bright_white"))
        if choice == "1":
            echo(t("settings_info", color=disk['settings']['text_color'], bg=disk['settings']['bg_color'], font=disk['settings']['font']), fg="bright_white")
        elif choice == "2":
            disk["settings"]["text_color"] = "bright_white"
            disk["settings"]["bg_color"] = "black"
            disk["settings"]["font"] = "bold"
            save_disk()
            echo(t("reset_display"), fg="bright_green")
        elif choice == "3":
            guide_file = "/docs/commands_ru.txt" if disk["settings"]["language"] == "RU" else "/docs/commands.txt"
            if guide_file in disk["files"]:
                echo(disk["files"][guide_file], fg="bright_white")
            else:
                echo(t("file_not_found"), fg="bright_yellow")
        elif choice == "4":
            break
        else:
            echo(t("choose_option", options="1-4"), fg="bright_red")


def format_currency(amount):
    return f"${amount:,.2f}"


def parse_amount(value):
    try:
        if isinstance(value, str):
            value = value.strip().replace("$", "").replace(",", "")
        amount = float(value)
        return round(amount, 2)
    except (ValueError, TypeError):
        return None


def ensure_bank_profile(user):
    if "bank" not in disk:
        disk["bank"] = {}
    profile = disk["bank"].setdefault(user, {
        "checking": 1000.0,
        "savings": 500.0,
        "monthly_income": 3000.0,
        "savings_goal": 300.0,
        "budget_categories": {
            "rent": 1000.0,
            "food": 500.0,
            "utilities": 200.0,
            "transport": 150.0,
        },
        "transactions": []
    })
    profile.setdefault("checking", 0.0)
    profile.setdefault("savings", 0.0)
    profile.setdefault("monthly_income", 0.0)
    profile.setdefault("savings_goal", 0.0)
    profile.setdefault("budget_categories", {})
    profile.setdefault("transactions", [])
    return profile


def bank_transaction(user, transaction_type, amount, category="General", note=""):
    profile = ensure_bank_profile(user)
    profile["transactions"].append({
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": transaction_type,
        "amount": round(amount, 2),
        "category": category,
        "note": note,
        "balance": round(profile["checking"] + profile["savings"], 2)
    })
    save_disk()


def bank_show_overview(user):
    profile = ensure_bank_profile(user)
    total = profile["checking"] + profile["savings"]
    total_budgeted = sum(profile["budget_categories"].values())
    spendable = profile["monthly_income"] - total_budgeted
    projected = profile["checking"] + spendable
    safe_spendable = max(0.0, profile["checking"] - profile["savings_goal"])

    echo("=== BANK OVERVIEW ===", fg="bright_cyan", style="bold")
    echo(f"Checking: {format_currency(profile['checking'])}", fg="bright_white")
    echo(f"Savings:  {format_currency(profile['savings'])}", fg="bright_white")
    echo(f"Total funds: {format_currency(total)}", fg="bright_white")
    echo(f"Monthly income: {format_currency(profile['monthly_income'])}", fg="bright_white")
    echo(f"Savings goal: {format_currency(profile['savings_goal'])}", fg="bright_white")
    echo(f"Total budgeted expenses: {format_currency(total_budgeted)}", fg="bright_white")
    echo(f"Spendable (income - expenses): {format_currency(spendable)}", fg="bright_green" if spendable >= 0 else "bright_red")
    echo(f"Safe spendable from checking: {format_currency(safe_spendable)}", fg="bright_white")
    echo(f"Projected month-end checking: {format_currency(projected)}", fg="bright_white")
    echo(f"Available funds: {format_currency(total)}", fg="bright_white")

    if profile["budget_categories"]:
        echo("Budget categories:", fg="bright_white")
        for category, amount in sorted(profile["budget_categories"].items()):
            echo(f"  {category}: {format_currency(amount)}", fg="bright_yellow")
    else:
        echo("No budget categories defined.", fg="bright_yellow")


def bank_deposit(user, amount_text):
    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        echo("Invalid deposit amount.", fg="bright_red")
        return
    profile = ensure_bank_profile(user)
    profile["checking"] += amount
    bank_transaction(user, "deposit", amount, category="Deposit")
    save_disk()
    echo(f"Deposited {format_currency(amount)} into checking.", fg="bright_green")


def bank_withdraw(user, amount_text):
    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        echo("Invalid withdrawal amount.", fg="bright_red")
        return
    profile = ensure_bank_profile(user)
    if amount > profile["checking"]:
        echo("Insufficient checking balance.", fg="bright_red")
        return
    profile["checking"] -= amount
    bank_transaction(user, "withdraw", amount, category="Withdrawal")
    save_disk()
    echo(f"Withdrew {format_currency(amount)} from checking.", fg="bright_green")


def bank_save_money(user, amount_text):
    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        echo("Invalid savings amount.", fg="bright_red")
        return
    profile = ensure_bank_profile(user)
    if amount > profile["checking"]:
        echo("Insufficient checking balance.", fg="bright_red")
        return
    profile["checking"] -= amount
    profile["savings"] += amount
    bank_transaction(user, "save", amount, category="Savings")
    save_disk()
    echo(f"Moved {format_currency(amount)} to savings.", fg="bright_green")


def bank_transfer(user, target_user, amount_text):
    amount = parse_amount(amount_text)
    if amount is None or amount <= 0:
        echo("Invalid transfer amount.", fg="bright_red")
        return
    if target_user not in disk.get("users", {}):
        echo("Target user not found.", fg="bright_red")
        return
    if target_user == user:
        echo("Cannot transfer to yourself.", fg="bright_yellow")
        return
    profile = ensure_bank_profile(user)
    if amount > profile["checking"]:
        echo("Insufficient checking balance.", fg="bright_red")
        return
    profile["checking"] -= amount
    target_profile = ensure_bank_profile(target_user)
    target_profile["checking"] += amount
    bank_transaction(user, "transfer_out", amount, category="Transfer", note=f"to {target_user}")
    bank_transaction(target_user, "transfer_in", amount, category="Transfer", note=f"from {user}")
    save_disk()
    echo(f"Transferred {format_currency(amount)} to {target_user}.", fg="bright_green")


def bank_budget_manager(user):
    profile = ensure_bank_profile(user)
    echo("=== BUDGET CALCULATOR ===", fg="bright_cyan", style="bold")
    echo("Enter amounts to update your budget. Leave blank to keep current values.", fg="bright_white")

    income_input = input(style_text(f"Monthly income [{format_currency(profile['monthly_income'])}]: ", fg="bright_white"))
    if income_input.strip():
        new_income = parse_amount(income_input)
        if new_income is not None:
            profile["monthly_income"] = new_income

    savings_goal_input = input(style_text(f"Savings goal [{format_currency(profile['savings_goal'])}]: ", fg="bright_white"))
    if savings_goal_input.strip():
        new_goal = parse_amount(savings_goal_input)
        if new_goal is not None:
            profile["savings_goal"] = new_goal

    echo("Update budget categories. Enter a category name and amount, or blank to finish.", fg="bright_white")
    while True:
        category = input(style_text("Category name (blank to finish): ", fg="bright_white")).strip()
        if not category:
            break
        amount_input = input(style_text(f"Amount for {category}: ", fg="bright_white"))
        amount = parse_amount(amount_input)
        if amount is None:
            echo("Invalid amount. Please try again.", fg="bright_red")
            continue
        profile["budget_categories"][category] = amount

    save_disk()
    bank_show_overview(user)


def bank_show_transactions(user):
    profile = ensure_bank_profile(user)
    echo("=== TRANSACTION HISTORY ===", fg="bright_cyan", style="bold")
    if not profile["transactions"]:
        echo("No transactions recorded.", fg="bright_yellow")
        return
    for entry in profile["transactions"][-12:]:
        echo(f"{entry['date']} | {entry['type']} | {format_currency(entry['amount'])} | {entry['category']} | {entry['note']}", fg="bright_white")


def bank_manager(args=None):
    user = disk.get("current_user")
    if not user:
        echo("No user logged in.", fg="bright_red")
        return
    ensure_bank_profile(user)
    if args:
        sub = args[0].upper()
        if sub == "BALANCE":
            bank_show_overview(user)
            return
        if sub == "DEPOSIT" and len(args) > 1:
            bank_deposit(user, args[1])
            return
        if sub == "WITHDRAW" and len(args) > 1:
            bank_withdraw(user, args[1])
            return
        if sub == "SAVE" and len(args) > 1:
            bank_save_money(user, args[1])
            return
        if sub == "TRANSFER" and len(args) > 2:
            bank_transfer(user, args[1], args[2])
            return
        if sub == "BUDGET":
            bank_budget_manager(user)
            return
        if sub == "HISTORY":
            bank_show_transactions(user)
            return

    while True:
        echo("=== BANK MANAGER ===", fg="bright_cyan", style="bold")
        echo("1) Account overview", fg="bright_white")
        echo("2) Deposit to checking", fg="bright_white")
        echo("3) Withdraw from checking", fg="bright_white")
        echo("4) Move funds to savings", fg="bright_white")
        echo("5) Transfer to another user", fg="bright_white")
        echo("6) Budget calculator", fg="bright_white")
        echo("7) Transaction history", fg="bright_white")
        echo("8) Exit bank manager", fg="bright_white")

        choice = input(style_text("bank> ", fg="bright_white")).strip()
        if choice == "1":
            bank_show_overview(user)
        elif choice == "2":
            amt = input(style_text("Deposit amount: ", fg="bright_white"))
            bank_deposit(user, amt)
        elif choice == "3":
            amt = input(style_text("Withdraw amount: ", fg="bright_white"))
            bank_withdraw(user, amt)
        elif choice == "4":
            amt = input(style_text("Move to savings amount: ", fg="bright_white"))
            bank_save_money(user, amt)
        elif choice == "5":
            target_user = input(style_text("Transfer to user: ", fg="bright_white")).strip()
            amt = input(style_text("Transfer amount: ", fg="bright_white"))
            bank_transfer(user, target_user, amt)
        elif choice == "6":
            bank_budget_manager(user)
        elif choice == "7":
            bank_show_transactions(user)
        elif choice == "8" or choice.upper() == "EXIT":
            break
        else:
            echo("Please choose a valid bank option.", fg="bright_red")


def boot():
    print_banner()


# =========================
# SHELL ENGINE
# =========================
def shell():
    while True:
        prompt_text = style_text(f"{disk.get('current_user')}@{disk.get('prompt')}{disk.get('current_dir')}> ", fg=disk["settings"].get("text_color"), bg=disk["settings"].get("bg_color"), style=disk["settings"].get("font"))
        try:
            raw = input(prompt_text).strip()
        except (EOFError, KeyboardInterrupt):
            echo("\nShutting down NOVA-DOS...", fg="bright_red")
            save_disk()
            break

        if not raw:
            continue

        force_clear = False
        normalized = raw.strip()
        if normalized.upper().startswith("CLS THEN "):
            force_clear = True
            normalized = normalized[len("CLS THEN "):].strip()
            if not normalized:
                clear_screen()
                continue

        parts = normalized.split()
        cmd = parts[0].upper()
        args = parts[1:]

        if force_clear:
            clear_screen()

        if cmd in ("EXIT", "QUIT", "POWEROFF"):
            echo("Shutting down NOVA-DOS...", fg="bright_red")
            save_disk()
            break

        if cmd == "DIR":
            path = args[0] if args else disk.get("current_dir", "/")
            contents = get_directory_contents(path)
            if contents is None:
                echo("Directory not found.", fg="bright_red")
            else:
                for name, entry in sorted(contents.items()):
                    if entry["type"] == "DIR":
                        echo(f"<DIR> {name}", fg="bright_cyan")
                    else:
                        echo(f"{formatted_size(entry.get('size', 0)):>8} {name}", fg="white")

        elif cmd == "TREE":
            tree_command(args[0] if args else None)

        elif cmd == "TYPE":
            if not args:
                echo("Usage: TYPE <file>", fg="white")
            else:
                type_file(args[0])

        elif cmd == "EDIT":
            if not args:
                echo("Usage: EDIT <file>", fg="white")
            else:
                edit_file(args[0])

        elif cmd == "COPY":
            if len(args) < 2:
                echo("Usage: COPY <src> <dst>", fg="white")
            else:
                copy_file(args[0], args[1])

        elif cmd == "MOVE":
            if len(args) < 2:
                echo("Usage: MOVE <src> <dst>", fg="white")
            else:
                move_file(args[0], args[1])

        elif cmd in ("DEL", "DELETE"):
            if not args:
                echo("Usage: DEL <file>", fg="white")
            else:
                delete_file(args[0])

        elif cmd == "MD":
            if not args:
                echo("Usage: MD <dir>", fg="white")
            else:
                make_directory(args[0])

        elif cmd == "RD":
            if not args:
                echo("Usage: RD <dir>", fg="white")
            else:
                remove_directory(args[0])

        elif cmd == "REN":
            if len(args) < 2:
                echo("Usage: REN <src> <dst>", fg="white")
            else:
                rename_item(args[0], args[1])

        elif cmd == "FIND":
            if not args:
                echo("Usage: FIND <term>", fg="white")
            else:
                find_text(" ".join(args))

        elif cmd == "VER":
            version()

        elif cmd == "DATE":
            show_date()

        elif cmd == "TIME":
            show_time()

        elif cmd == "PROMPT":
            set_prompt(" ".join(args) if args else None)

        elif cmd == "USER":
            echo(f"Current user: {disk.get('current_user')}", fg="white")

        elif cmd == "SYSINFO":
            sysinfo()

        elif cmd == "MEMORY":
            memory_status()

        elif cmd == "FORMAT":
            format_disk()

        elif cmd == "CLS":
            clear_screen()

        elif cmd in ("HELP", "?"):
            show_help()

        elif cmd in ("LANG", "LANGUAGE"):
            if not args:
                echo(t("language_invalid"), fg="bright_red")
            else:
                lang_choice = args[0].upper()
                if lang_choice in ("EN", "RU"):
                    disk["settings"]["language"] = lang_choice
                    save_disk()
                    echo(t("language_set", lang=lang_choice), fg="bright_green")
                else:
                    echo(t("language_invalid"), fg="bright_red")

        elif cmd == "RENUSER":
            if len(args) != 2:
                echo(t("rename_user_usage"), fg="bright_white")
            else:
                rename_login(args[0], args[1])

        elif cmd == "CHPASS" or cmd == "PASSWD":
            change_password(args)

        elif cmd == "CALC":
            calculator()

        elif cmd == "NOTE":
            notepad()

        elif cmd == "ASCII":
            ascii_art()

        elif cmd == "CLOCK":
            clock_program()

        elif cmd == "ENCODE":
            text_encode_tool()

        elif cmd == "BANK":
            bank_manager(args)

        elif cmd == "GUESS":
            guess_game()

        elif cmd == "RPS":
            rock_paper_scissors()

        elif cmd == "HANG":
            hangman_game()

        elif cmd == "SNAKE":
            snake_game()

        elif cmd == "TETRIS":
            tetris_game()

        elif cmd == "PONG":
            pong_game()

        elif cmd == "BREAKOUT":
            breakout_game()

        elif cmd == "TICTACTOE":
            tictactoe_game()

        elif cmd == "SPACEINVADERS":
            space_invaders_game()

        elif cmd == "TREX":
            trex_run_game()

        elif cmd == "FONT":
            set_font([a for a in args])

        elif cmd == "RUN":
            if not args:
                echo("Usage: RUN <filename.py>", fg="white")
            else:
                run_python_file(args[0])

        elif cmd == "PAINT":
            paint_program()

        elif cmd == "PROGRAMS":
            list_programs()

        elif cmd == "ADDPROG":
            if len(args) < 2:
                echo("Usage: ADDPROG <path> <display name>", fg="white")
            else:
                path = args[0]
                display = " ".join(args[1:])
                add_user_program(path, display, kind="program")

        elif cmd == "DELPROG":
            if not args:
                echo("Usage: DELPROG <display or path>", fg="white")
            else:
                delete_user_program(" ".join(args), kind="program")

        elif cmd == "ADDGAME":
            if len(args) < 2:
                echo("Usage: ADDGAME <path> <display name>", fg="white")
            else:
                path = args[0]
                display = " ".join(args[1:])
                add_user_program(path, display, kind="game")

        elif cmd == "DELGAME":
            if not args:
                echo("Usage: DELGAME <display or path>", fg="white")
            else:
                delete_user_program(" ".join(args), kind="game")

        elif cmd == "LAUNCH":
            if not args:
                echo("Usage: LAUNCH <display or path>", fg="white")
            else:
                launch_user_program(" ".join(args))

        else:
            echo(t("unknown_command", cmd=parts[0]), fg="bright_yellow")


# =========================
# PROGRAMS
# =========================
def run_python_file(filename):
    """Execute Python code from a file in the virtual disk using the kernel process manager."""
    file_path = normalize_path(filename)

    if file_path not in disk["files"]:
        echo(f"File not found: {filename}", fg="bright_red")
        return

    code_content = disk["files"][file_path]

    if not filename.lower().endswith(".py"):
        echo("Only .py files can be executed.", fg="bright_yellow")
        return

    try:
        echo(f"Starting process for {filename}...", fg="bright_cyan")
        process = kernel.create_process(code_content, name=file_path, user=disk.get("current_user"), cwd=disk.get("current_dir", "/"))
        kernel.run_process(process.pid)
        echo("", fg="white")
        if process.state == "TERMINATED":
            echo(f"Process {process.pid} finished with exit code {process.exit_code}.", fg="bright_green")
        else:
            echo(f"Process {process.pid} ended in state {process.state}.", fg="bright_yellow")
    except Exception as e:
        echo(f"Error executing {filename}: {str(e)}", fg="bright_red")


def safe_eval(expr, variables=None):
    allowed = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "log": math.log,
        "log10": math.log10,
        "ln": math.log,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "floor": math.floor,
        "ceil": math.ceil,
        "degrees": math.degrees,
        "radians": math.radians,
        "factorial": math.factorial,
        "sum": sum,
    }
    if variables:
        allowed.update(variables)
    return eval(expr, {"__builtins__": None}, allowed)


def render_calc_screen(title, subtitle=None):
    echo("+" + "=" * 52 + "+", fg="bright_cyan")
    echo(f"| {title.center(50)} |", fg="bright_cyan")
    echo("+" + "=" * 52 + "+", fg="bright_cyan")
    if subtitle:
        echo(f"| {subtitle.ljust(50)} |", fg="bright_white")
        echo("+" + "=" * 52 + "+", fg="bright_cyan")


def calculator():
    history = []
    while True:
        render_calc_screen("NOVA-DOS SCIENTIFIC CALCULATOR", "1) Standard  2) Scientific  3) Graph  4) History  5) Exit")
        choice = input(style_text("calculator> ", fg="bright_white", style="bold")).strip()
        if choice.lower() == "exit" or choice == "5":
            break
        if choice == "1" or choice.lower() == "standard":
            render_calc_screen("STANDARD CALCULATOR", "Enter a math expression, or EXIT to return.")
            while True:
                expr = input(style_text("std> ", fg="bright_white", style="bold")).strip()
                if expr.lower() == "exit":
                    break
                try:
                    result = safe_eval(expr)
                    history.append((expr, result))
                    echo(f"= {result}", fg="bright_green")
                except Exception:
                    echo(t("syntax_error"), fg="bright_red")
        elif choice == "2" or choice.lower() == "scientific":
            render_calc_screen("SCIENTIFIC CALCULATOR", "Supported: sin cos tan log ln sqrt exp pi e abs pow")
            while True:
                expr = input(style_text("sci> ", fg="bright_white", style="bold")).strip()
                if expr.lower() == "exit":
                    break
                try:
                    result = safe_eval(expr)
                    history.append((expr, result))
                    echo(f"= {result}", fg="bright_green")
                except Exception:
                    echo(t("syntax_error"), fg="bright_red")
        elif choice == "3" or choice.lower() == "graph":
            render_calc_screen("GRAPHING CALCULATOR", "Enter f(x) and range. Use x variable and supported math functions.")
            expr = input(style_text("y = ", fg="bright_white", style="bold")).strip()
            if expr.lower() == "exit" or not expr:
                continue
            if expr.lower().startswith("y="):
                expr = expr[2:].strip()
            x_start = input(style_text("x start [-10]: ", fg="bright_white", style="bold")).strip()
            x_end = input(style_text("x end [10]: ", fg="bright_white", style="bold")).strip()
            try:
                x0 = float(x_start) if x_start else -10.0
                x1 = float(x_end) if x_end else 10.0
            except ValueError:
                echo("Invalid range values.", fg="bright_red")
                continue
            if x1 <= x0:
                echo("End must be greater than start.", fg="bright_red")
                continue
            graph_data = []
            sample_count = 60
            for i in range(sample_count + 1):
                x = x0 + (x1 - x0) * i / sample_count
                try:
                    y = safe_eval(expr, {"x": x})
                    if isinstance(y, complex):
                        y = None
                except Exception:
                    y = None
                graph_data.append((x, y))
            valid_y = [y for _, y in graph_data if isinstance(y, (int, float)) and math.isfinite(y)]
            if not valid_y:
                echo("Unable to plot this expression.", fg="bright_red")
                continue
            y_min = min(valid_y)
            y_max = max(valid_y)
            if y_min == y_max:
                y_min -= 1
                y_max += 1
            height = 20
            width = 60
            canvas = [[" " for _ in range(width)] for _ in range(height)]
            y_span = y_max - y_min
            x0_col = None
            y0_row = None
            if x0 <= 0 <= x1:
                x0_col = int((0 - x0) / (x1 - x0) * (width - 1))
            if y_min <= 0 <= y_max:
                y0_row = int((y_max - 0) / y_span * (height - 1))
            for col, (x, y) in enumerate(graph_data):
                if y is None or not isinstance(y, (int, float)) or not math.isfinite(y):
                    continue
                row = int((y_max - y) / y_span * (height - 1))
                if 0 <= row < height and 0 <= col < width:
                    canvas[row][col] = "*"
            for row in range(height):
                if y0_row is not None and row == y0_row:
                    for col in range(width):
                        if canvas[row][col] == " ":
                            canvas[row][col] = "-"
                if x0_col is not None and 0 <= x0_col < width:
                    if canvas[row][x0_col] == " ":
                        canvas[row][x0_col] = "|"
                    elif canvas[row][x0_col] == "-":
                        canvas[row][x0_col] = "+"
            render_calc_screen("GRAPH RESULT", f"{expr} on [{x0:.2f}, {x1:.2f}]")
            for row in range(height):
                line = "".join(canvas[row])
                y_label = y_max - (y_span * row / (height - 1))
                echo(f"{y_label:7.2f} | {line}", fg="bright_white")
            echo(" " * 9 + "+" + "".join(["-" for _ in range(width)]), fg="bright_cyan")
            x_label_left = f"{x0:.2f}"
            x_label_right = f"{x1:.2f}"
            space_between = max(1, width - len(x_label_left) - len(x_label_right))
            echo(f"{x_label_left}{' ' * space_between}{x_label_right}", fg="bright_white")
        elif choice == "4" or choice.lower() == "history":
            render_calc_screen("CALC HISTORY", "Most recent results shown below.")
            if not history:
                echo("No history yet.", fg="bright_yellow")
            else:
                for expr, result in history[-12:]:
                    echo(f"{expr} = {result}", fg="bright_white")
            input(style_text("Press ENTER to return.", fg="bright_white"))
        else:
            echo("Choose 1-5 or type EXIT.", fg="bright_red")


def notepad():
    echo(t("notepad_title"), fg="bright_cyan", style="bold")
    echo(t("notepad_save"), fg="bright_white")
    text = []
    while True:
        line = input()
        if line == "END":
            break
        text.append(line)

    note_path = normalize_path("note.txt")
    ensure_directory(os.path.dirname(note_path))
    disk["files"][note_path] = "\n".join(text)
    save_disk()
    echo(t("saved_to", path=note_path), fg="bright_green")


def rock_paper_scissors():
    echo("=== ROCK-PAPER-SCISSORS ===", fg="bright_cyan", style="bold")
    choices = ["rock", "paper", "scissors"]
    while True:
        player = input(style_text("Choose rock, paper, or scissors (or EXIT): ", fg="bright_white")).lower()
        if player == "exit":
            return
        if player not in choices:
            echo("Invalid choice.", fg="bright_red")
            continue
        computer = random.choice(choices)
        echo(f"COMPUTER: {computer}", fg="bright_yellow")
        if player == computer:
            echo("Draw! Try again.", fg="bright_blue")
        elif (player == "rock" and computer == "scissors") or \
             (player == "paper" and computer == "rock") or \
             (player == "scissors" and computer == "paper"):
            echo("You win!", fg="bright_green")
        else:
            echo("You lose.", fg="bright_red")


def hangman_game():
    echo("=== HANGMAN ===", fg="bright_cyan", style="bold")
    words = ["nova", "system", "disk", "terminal", "python"]
    word = random.choice(words)
    hidden = ["_" for _ in word]
    attempts = 6
    guessed = set()
    while attempts > 0 and "".join(hidden) != word:
        echo(f"Word: {' '.join(hidden)}", fg="bright_white")
        echo(f"Attempts left: {attempts}", fg="bright_yellow")
        guess = input(style_text("Guess a letter or the full word: ", fg="bright_white")).lower()
        if guess == "exit":
            return
        if len(guess) == 1:
            if guess in guessed:
                echo("Already guessed.", fg="bright_blue")
                continue
            guessed.add(guess)
            if guess in word:
                for idx, char in enumerate(word):
                    if char == guess:
                        hidden[idx] = guess
                echo("Good guess!", fg="bright_green")
            else:
                attempts -= 1
                echo("Wrong guess.", fg="bright_red")
        elif guess == word:
            hidden = list(word)
            break
        else:
            attempts -= 1
            echo("Wrong guess.", fg="bright_red")
    if "".join(hidden) == word:
        echo(f"You won! The word was {word}.", fg="bright_green")
    else:
        echo(f"Game over. The word was {word}.", fg="bright_red")


def snake_game():
    def place_food(snake):
        while True:
            y = random.randint(1, 18)
            x = random.randint(1, 38)
            if (y, x) not in snake:
                return (y, x)

    def draw(win, snake, food, score):
        win.erase()
        win.border()
        win.addstr(0, 2, f" Score: {score} ")
        for index, (y, x) in enumerate(snake):
            ch = "@" if index == 0 else "o"
            try:
                win.addch(y, x, ch)
            except curses.error:
                pass
        fy, fx = food
        win.addch(fy, fx, "*")
        win.refresh()

    def snake_runner(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.keypad(1)
        win = curses.newwin(20, 40, 0, 0)
        win.keypad(1)
        win.nodelay(1)

        keys = {
            curses.KEY_UP: (-1, 0),
            curses.KEY_DOWN: (1, 0),
            curses.KEY_LEFT: (0, -1),
            curses.KEY_RIGHT: (0, 1),
            ord('w'): (-1, 0),
            ord('s'): (1, 0),
            ord('a'): (0, -1),
            ord('d'): (0, 1),
        }

        snake = [(10, 20), (10, 19), (10, 18)]
        direction = (0, 1)
        food = place_food(snake)
        score = 0
        speed = 0.12
        paused = False

        draw(win, snake, food, score)
        while True:
            ch = win.getch()
            if ch != -1:
                if ch in (ord('q'), 27):
                    break
                if ch == ord('p'):
                    paused = not paused
                if ch in keys and not paused:
                    nd = keys[ch]
                    if nd != (-direction[0], -direction[1]):
                        direction = nd
            if paused:
                time.sleep(0.05)
                continue

            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if head[0] <= 0 or head[0] >= 19 or head[1] <= 0 or head[1] >= 39 or head in snake:
                msg = f" GAME OVER - Score: {score} (q to quit) "
                win.addstr(10, max(2, 20 - len(msg) // 2), msg)
                win.nodelay(0)
                while True:
                    c = win.getch()
                    if c in (ord('q'), 27):
                        return
                break

            snake.insert(0, head)
            if head == food:
                score += 1
                food = place_food(snake)
                speed = max(0.03, speed * 0.97)
            else:
                snake.pop()

            draw(win, snake, food, score)
            time.sleep(speed)

    try:
        curses.wrapper(snake_runner)
    except Exception as e:
        echo(f"Snake game error: {e}", fg="bright_red")


def tetris_game():
    shapes = [
        [[(0, 1), (0, 0), (0, 2), (0, 3)], [(-1, 2), (0, 2), (1, 2), (2, 2)]],
        [[(0, 0), (0, 1), (1, 0), (1, 1)]],
        [[(0, 1), (1, 0), (1, 1), (1, 2)], [(0, 1), (1, 1), (1, 2), (2, 1)], [(1, 0), (1, 1), (1, 2), (2, 1)], [(0, 1), (1, 0), (1, 1), (2, 1)]],
        [[(0, 2), (1, 0), (1, 1), (1, 2)], [(0, 1), (1, 1), (2, 1), (2, 2)], [(1, 0), (1, 1), (1, 2), (2, 0)], [(0, 0), (0, 1), (1, 1), (2, 1)]],
        [[(0, 0), (1, 0), (1, 1), (1, 2)], [(0, 1), (1, 1), (2, 1), (2, 0)], [(1, 0), (1, 1), (1, 2), (2, 2)], [(0, 2), (0, 1), (1, 1), (2, 1)]],
        [[(0, 1), (0, 2), (1, 0), (1, 1)], [(0, 1), (1, 1), (1, 2), (2, 2)]],
        [[(0, 0), (0, 1), (1, 1), (1, 2)], [(0, 2), (1, 2), (1, 1), (2, 1)]],
    ]

    class Piece:
        def __init__(self, shape):
            self.shape = shape
            self.rot = 0
            self.blocks = shape[self.rot]
            self.y = 0
            self.x = 3

        def rotate(self):
            self.rot = (self.rot + 1) % len(self.shape)
            self.blocks = self.shape[self.rot]

    def valid(board, piece, dy=0, dx=0):
        for by, bx in piece.blocks:
            y = piece.y + by + dy
            x = piece.x + bx + dx
            if x < 0 or x >= 10 or y >= 20:
                return False
            if y >= 0 and board[y][x]:
                return False
        return True

    def lock(board, piece):
        for by, bx in piece.blocks:
            y = piece.y + by
            x = piece.x + bx
            if 0 <= y < 20 and 0 <= x < 10:
                board[y][x] = 1

    def clear_lines(board):
        new_board = [row for row in board if any(cell == 0 for cell in row)]
        cleared = 20 - len(new_board)
        for _ in range(cleared):
            new_board.insert(0, [0] * 10)
        return new_board, cleared

    def draw(win, board, piece, score, next_shape):
        win.erase()
        win.border()
        win.addstr(0, 2, f" Score: {score} ")
        for y in range(20):
            for x in range(10):
                win.addch(y + 1, x + 1, "#" if board[y][x] else " ")
        for by, bx in piece.blocks:
            y = piece.y + by
            x = piece.x + bx
            if y >= 0:
                try:
                    win.addch(y + 1, x + 1, "#")
                except curses.error:
                    pass
        win.addstr(1, 12, "Next:")
        for by, bx in next_shape[0]:
            try:
                win.addch(3 + by, 13 + bx, "#")
            except curses.error:
                pass
        win.refresh()

    def tetris_runner(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.keypad(1)
        win = curses.newwin(22, 22, 0, 0)
        win.keypad(1)
        win.nodelay(1)

        board = [[0] * 10 for _ in range(20)]
        piece = Piece(random.choice(shapes))
        next_piece = random.choice(shapes)
        score = 0
        drop_time = time.time()
        speed = 0.5

        while True:
            ch = win.getch()
            if ch in (ord('q'), 27):
                break
            if ch == curses.KEY_LEFT and valid(board, piece, dx=-1):
                piece.x -= 1
            if ch == curses.KEY_RIGHT and valid(board, piece, dx=1):
                piece.x += 1
            if ch == curses.KEY_DOWN and valid(board, piece, dy=1):
                piece.y += 1
                drop_time = time.time()
            if ch == curses.KEY_UP:
                old_rot = piece.rot
                piece.rotate()
                if not valid(board, piece):
                    piece.rot = old_rot
                    piece.blocks = piece.shape[piece.rot]

            if time.time() - drop_time >= speed:
                if valid(board, piece, dy=1):
                    piece.y += 1
                else:
                    lock(board, piece)
                    board, cleared = clear_lines(board)
                    score += cleared * 100
                    piece = Piece(next_piece)
                    next_piece = random.choice(shapes)
                    if not valid(board, piece):
                        msg = f" GAME OVER - Score: {score} (q to quit) "
                        win.addstr(10, 1, msg[:18])
                        win.nodelay(0)
                        while True:
                            c = win.getch()
                            if c in (ord('q'), 27):
                                return
                drop_time = time.time()

            draw(win, board, piece, score, next_piece)
            time.sleep(0.02)

    try:
        curses.wrapper(tetris_runner)
    except Exception as e:
        echo(f"Tetris game error: {e}", fg="bright_red")


def clock_program():
    echo("=== DIGITAL CLOCK ===", fg="bright_cyan", style="bold")
    echo(t("press_exit"), fg="bright_white")
    try:
        while True:
            echo(time.strftime("%H:%M:%S"), fg="bright_green", end="\r")
            time.sleep(1)
    except KeyboardInterrupt:
        echo("", end="\n")


def text_encode_tool():
    echo("=== TEXT ENCODER ===", fg="bright_cyan", style="bold")
    echo("Enter text to encode or decode. Type EXIT to return.", fg="bright_white")
    while True:
        text = input(style_text("text> ", fg="bright_white"))
        if text.lower() == "exit":
            return
        rot13 = text.translate(str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
        ))
        echo(f"ROT13: {rot13}", fg="bright_green")
        encoded = text.encode("utf-8").hex()
        echo(f"HEX: {encoded}", fg="bright_yellow")


# =========================
# NEW TERMINAL GAMES
# =========================
def pong_game():
    """Simple Pong game using curses"""
    def runner(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        h, w = 20, 60
        win = curses.newwin(h, w, 0, 0)
        win.nodelay(1)
        
        p1_y = h // 2 - 2
        p2_y = h // 2 - 2
        ball_y, ball_x = h // 2, w // 2
        vel_y, vel_x = 1, 1
        p1_score, p2_score = 0, 0
        
        while True:
            ch = win.getch()
            if ch == ord('q'):
                break
            if ch == ord('w') and p1_y > 1:
                p1_y -= 1
            if ch == ord('s') and p1_y < h - 5:
                p1_y += 1
            if ch == ord('i') and p2_y > 1:
                p2_y -= 1
            if ch == ord('k') and p2_y < h - 5:
                p2_y += 1
            
            ball_y += vel_y
            ball_x += vel_x
            
            if ball_y <= 0 or ball_y >= h - 1:
                vel_y = -vel_y
            
            if 1 <= ball_x <= 2 and p1_y <= ball_y <= p1_y + 4:
                vel_x = -vel_x
                p1_score += 1
            
            if w - 3 <= ball_x <= w - 2 and p2_y <= ball_y <= p2_y + 4:
                vel_x = -vel_x
                p2_score += 1
            
            if ball_x < 0 or ball_x >= w:
                ball_y, ball_x = h // 2, w // 2
                vel_y, vel_x = 1, 1
            
            win.erase()
            win.border()
            win.addstr(0, 2, f" PONG - P1: {p1_score} P2: {p2_score} (Q quit) ")
            
            for i in range(5):
                try:
                    win.addch(p1_y + i, 2, '|')
                except:
                    pass
                try:
                    win.addch(p2_y + i, w - 3, '|')
                except:
                    pass
            
            try:
                win.addch(ball_y, ball_x, 'O')
            except:
                pass
            
            win.refresh()
            time.sleep(0.05)
    
    try:
        curses.wrapper(runner)
    except Exception as e:
        echo(f"Pong error: {e}", fg="bright_red")


def breakout_game():
    """Simple Breakout game"""
    def runner(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        h, w = 24, 60
        win = curses.newwin(h, w, 0, 0)
        win.nodelay(1)
        
        paddle_x = w // 2 - 3
        ball_y, ball_x = h - 4, w // 2
        vel_y, vel_x = -1, 1
        score = 0
        lives = 3
        
        bricks = []
        for row in range(3):
            for col in range(0, w - 2, 6):
                bricks.append([row + 2, col + 1, True])
        
        while lives > 0 and any(b[2] for b in bricks):
            ch = win.getch()
            if ch == ord('q'):
                break
            if ch == curses.KEY_LEFT and paddle_x > 1:
                paddle_x -= 2
            if ch == curses.KEY_RIGHT and paddle_x < w - 8:
                paddle_x += 2
            
            ball_y += vel_y
            ball_x += vel_x
            
            if ball_x <= 1 or ball_x >= w - 2:
                vel_x = -vel_x
            if ball_y <= 1:
                vel_y = -vel_y
            
            if paddle_x <= ball_x <= paddle_x + 6 and ball_y == h - 3:
                vel_y = -vel_y
                score += 10
            
            for brick in bricks:
                if brick[2] and brick[0] <= ball_y <= brick[0] + 1 and brick[1] <= ball_x <= brick[1] + 4:
                    brick[2] = False
                    vel_y = -vel_y
                    score += 50
            
            if ball_y >= h - 1:
                lives -= 1
                ball_y, ball_x = h - 4, w // 2
                vel_y, vel_x = -1, 1
            
            win.erase()
            win.border()
            win.addstr(0, 2, f" BREAKOUT - Score: {score} Lives: {lives} (Q quit) ")
            
            for brick in bricks:
                if brick[2]:
                    for x in range(brick[1], brick[1] + 5):
                        try:
                            win.addch(brick[0], x, '#')
                        except:
                            pass
            
            for x in range(paddle_x, paddle_x + 7):
                try:
                    win.addch(h - 2, x, '=')
                except:
                    pass
            
            try:
                win.addch(ball_y, ball_x, 'O')
            except:
                pass
            
            win.refresh()
            time.sleep(0.05)
    
    try:
        curses.wrapper(runner)
    except Exception as e:
        echo(f"Breakout error: {e}", fg="bright_red")


def tictactoe_game():
    """Tic-Tac-Toe game against simple AI"""
    echo("=== TIC-TAC-TOE ===", fg="bright_cyan", style="bold")
    board = [' ' for _ in range(9)]
    
    def print_board():
        echo("", fg="white")
        for i in range(3):
            echo(f"  {board[i*3]} | {board[i*3+1]} | {board[i*3+2]}", fg="bright_white")
            if i < 2:
                echo("  ---------", fg="bright_white")
    
    def check_winner(b):
        lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b_idx, c in lines:
            if b[a] == b[b_idx] == b[c] != ' ':
                return b[a]
        return None
    
    def ai_move():
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                if check_winner(board) == 'O':
                    return
                board[i] = ' '
        
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                if check_winner(board) == 'X':
                    board[i] = 'O'
                    return
                board[i] = ' '
        
        if board[4] == ' ':
            board[4] = 'O'
            return
        
        for i in [0, 2, 6, 8]:
            if board[i] == ' ':
                board[i] = 'O'
                return
        
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                return
    
    while True:
        print_board()
        winner = check_winner(board)
        if winner:
            echo(f"Player {winner} wins!", fg="bright_green")
            break
        if all(b != ' ' for b in board):
            echo("Draw!", fg="bright_yellow")
            break
        
        while True:
            try:
                pos = int(input("Your move (1-9) or 0 to exit: ")) - 1
                if pos == -1:
                    return
                if 0 <= pos < 9 and board[pos] == ' ':
                    board[pos] = 'X'
                    break
                echo("Invalid move!", fg="bright_red")
            except:
                echo("Enter a number 1-9", fg="bright_red")
        
        winner = check_winner(board)
        if winner or all(b != ' ' for b in board):
            print_board()
            if winner:
                echo(f"Player {winner} wins!", fg="bright_green")
            else:
                echo("Draw!", fg="bright_yellow")
            break
        
        ai_move()


def space_invaders_game():
    """Simple Space Invaders game"""
    def runner(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        h, w = 24, 60
        win = curses.newwin(h, w, 0, 0)
        win.nodelay(1)
        
        player_x = w // 2
        player_y = h - 2
        score = 0
        enemies = [[2, i * 8, 1] for i in range(7)]
        bullets = []
        enemy_bullets = []
        game_over = False
        
        move_counter = 0
        
        while not game_over:
            ch = win.getch()
            if ch == ord('q'):
                break
            if ch == curses.KEY_LEFT and player_x > 1:
                player_x -= 1
            if ch == curses.KEY_RIGHT and player_x < w - 2:
                player_x += 1
            if ch == ord(' '):
                bullets.append([player_y - 1, player_x])
            
            bullets = [[y-1, x] for y, x in bullets if y > 0]
            enemy_bullets = [[y+1, x] for y, x in enemy_bullets if y < h - 1]
            
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if bullet[0] == enemy[0] and bullet[1] == enemy[1]:
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 10
                        break
            
            for enemy in enemies:
                if enemy[0] >= player_y:
                    game_over = True
            
            for bullet in enemy_bullets:
                if bullet[0] == player_y and bullet[1] == player_x:
                    game_over = True
            
            move_counter += 1
            if move_counter % 20 == 0:
                for enemy in enemies:
                    enemy[1] += 2
                    if random.random() < 0.3 and len(enemy_bullets) < 5:
                        enemy_bullets.append([enemy[0] + 1, enemy[1]])
                
                if move_counter % 100 == 0:
                    for enemy in enemies:
                        enemy[0] += 1
            
            win.erase()
            win.border()
            win.addstr(0, 2, f" SPACE INVADERS - Score: {score} (Q quit) ")
            
            for enemy in enemies:
                try:
                    win.addch(enemy[0], enemy[1], '¥')
                except:
                    pass
            
            for bullet in bullets:
                try:
                    win.addch(bullet[0], bullet[1], '|')
                except:
                    pass
            
            for bullet in enemy_bullets:
                try:
                    win.addch(bullet[0], bullet[1], 'V')
                except:
                    pass
            
            try:
                win.addch(player_y, player_x, 'A')
            except:
                pass
            
            win.refresh()
            time.sleep(0.05)
        
        if game_over:
            echo(f"Game Over! Final Score: {score}", fg="bright_red")
    
    try:
        curses.wrapper(runner)
    except Exception as e:
        echo(f"Space Invaders error: {e}", fg="bright_red")


def trex_run_game():
    """Simple T-Rex Run game"""
    def runner(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        h, w = 20, 60
        win = curses.newwin(h, w, 0, 0)
        win.nodelay(1)
        
        trex_y = h - 3
        trex_x = 5
        is_jumping = False
        jump_vel = 0
        score = 0
        obstacles = [[h - 3, w - 5]]
        game_over = False
        
        while not game_over:
            ch = win.getch()
            if ch == ord('q'):
                break
            if ch == ord(' ') and not is_jumping:
                is_jumping = True
                jump_vel = -3
            
            if is_jumping:
                trex_y += jump_vel
                jump_vel += 1
                if trex_y >= h - 3:
                    trex_y = h - 3
                    is_jumping = False
            
            obstacles = [[y, x-1] for y, x in obstacles if x > 0]
            
            new_obstacles = []
            for obs in obstacles:
                if obs[1] > 0:
                    new_obstacles.append(obs)
                    if obs[1] == trex_x and obs[0] == trex_y:
                        game_over = True
            obstacles = new_obstacles
            
            if score % 5 == 0 and score > 0 and (not obstacles or obstacles[-1][1] < w - 20):
                obstacles.append([h - 3, w - 2])
            
            score += 1
            
            win.erase()
            win.border()
            win.addstr(0, 2, f" T-REX RUN - Score: {score // 10} (SPACE jump Q quit) ")
            
            for obs in obstacles:
                try:
                    win.addch(obs[0], obs[1], '█')
                except:
                    pass
            
            try:
                win.addch(trex_y, trex_x, '▲')
            except:
                pass
            
            win.refresh()
            time.sleep(0.05)
        
        if game_over:
            echo(f"Game Over! Final Score: {score // 10}", fg="bright_red")
    
    try:
        curses.wrapper(runner)
    except Exception as e:
        echo(f"T-Rex Run error: {e}", fg="bright_red")


# =========================
# USER-ADDED PROGRAMS / PAINT
# =========================
def paint_program():
    """Simple curses-based paint: WASD to move, P paint, E erase, S save, Q quit"""
    def runner(stdscr):
        curses.curs_set(0)
        h, w = 20, 50
        win = curses.newwin(h + 2, w + 2, 0, 0)
        canvas = [[" " for _ in range(w)] for _ in range(h)]
        y, x = h // 2, w // 2
        while True:
            win.erase()
            win.border()
            win.addstr(0, 2, " PAINT - WASD move P paint E erase S save Q quit ")
            for row in range(h):
                try:
                    win.addstr(1 + row, 1, "".join(canvas[row]))
                except curses.error:
                    pass
            try:
                win.addch(1 + y, 1 + x, "X", curses.A_REVERSE)
            except curses.error:
                pass
            win.refresh()
            ch = win.getch()
            if ch in (ord('q'), ord('Q'), 27):
                break
            if ch in (ord('w'), ord('W')) and y > 0:
                y -= 1
            if ch in (ord('s'), ord('S')) and y < h - 1:
                y += 1
            if ch in (ord('a'), ord('A')) and x > 0:
                x -= 1
            if ch in (ord('d'), ord('D')) and x < w - 1:
                x += 1
            if ch in (ord('p'), ord('P')):
                canvas[y][x] = "#"
            if ch in (ord('e'), ord('E')):
                canvas[y][x] = " "
            if ch in (ord('S'), ord('s')):
                # save to disk
                timestamp = int(time.time())
                path = f"/programs/paint_{timestamp}.txt"
                ensure_directory(os.path.dirname(path))
                disk["files"][path] = "\n".join("".join(r) for r in canvas)
                save_disk()
                echo(f"Saved paint to {path}", fg="bright_green")
                time.sleep(0.6)

    try:
        curses.wrapper(runner)
    except Exception as e:
        echo(f"Paint error: {e}", fg="bright_red")


def list_programs():
    echo("=== PROGRAMS ===", fg="bright_cyan", style="bold")
    built = ["CALC", "NOTE", "ASCII", "CLOCK", "ENCODE", "PANEL", "BANK", "PAINT"]
    for name in built:
        echo(f"{name}", fg="bright_white")
    if disk.get("user_added_programs"):
        echo("\nUser-added programs/games:", fg="bright_yellow")
        for entry in disk["user_added_programs"]:
            echo(f"{entry['display']} -> {entry['path']} (by {entry['added_by']})", fg="bright_white")


def add_user_program(path, display, kind="program"):
    # Authenticate first
    auth = prompt_login_credentials("Enter credentials to add a program.")
    if not auth:
        echo("Authentication failed. Aborting.", fg="bright_yellow")
        return

    target = normalize_path(path)
    if target not in disk["files"]:
        echo("File not found on disk.", fg="bright_red")
        return

    confirm = input(style_text(f"Add {target} as '{display}'? (Y/N): ", fg="bright_white"))
    if confirm.lower() != "y":
        echo("Add cancelled.", fg="bright_yellow")
        return

    entry = {"path": target, "display": display, "added_by": auth, "kind": kind}
    disk.setdefault("user_added_programs", []).append(entry)
    save_disk()
    echo("Program added.", fg="bright_green")


def delete_user_program(display_or_path, kind=None):
    auth = prompt_login_credentials("Enter credentials to delete a program.")
    if not auth:
        echo("Authentication failed. Aborting.", fg="bright_yellow")
        return

    lst = disk.get("user_added_programs", [])
    found = None
    for entry in lst:
        if entry["display"].lower() == display_or_path.lower() or entry["path"] == normalize_path(display_or_path):
            found = entry
            break
    if not found:
        echo("No matching user-added program/game found.", fg="bright_yellow")
        return
    if found.get("added_by") != auth:
        echo("You can only delete programs you added.", fg="bright_red")
        return
    confirm = input(style_text(f"Delete {found['display']} (Y/N): ", fg="bright_white"))
    if confirm.lower() != "y":
        echo("Delete cancelled.", fg="bright_yellow")
        return
    disk["user_added_programs"].remove(found)
    save_disk()
    echo("Program entry removed.", fg="bright_green")


def launch_user_program(display_or_path):
    lst = disk.get("user_added_programs", [])
    found = None
    for entry in lst:
        if entry["display"].lower() == display_or_path.lower() or entry["path"] == normalize_path(display_or_path):
            found = entry
            break
    if not found:
        echo("No such program registered.", fg="bright_yellow")
        return
    path = found["path"]
    # If python file, run; else show file
    if path.lower().endswith('.py'):
        run_python_file(path)
    else:
        type_file(path)


# =========================
# BOOT + RUN
# =========================
if __name__ == "__main__":
    boot()
    if "directories" not in disk:
        disk["directories"] = ["/"]
    if "current_dir" not in disk:
        disk["current_dir"] = "/"
    if "prompt" not in disk:
        disk["prompt"] = "NOVA-DOS"
    if "settings" not in disk:
        disk["settings"] = {"text_color": "white", "bg_color": "black", "font": "bold"}
    login()
    shell()
