import os
import subprocess
import sys
import webbrowser

def run_command(command):
    """Выполняет команду и выводит результат"""
    print(f"\n>> Выполняем: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print("Результат:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Ошибка:")
        print(e.stderr)
        return False

def setup_github():
    """Настройка GitHub репозитория"""
    # Проверяем установлен ли Git
    if not run_command("git --version"):
        print("Git не установлен! Установите Git с https://git-scm.com/downloads")
        return

    # Получаем имя пользователя GitHub
    username = input("\nВведите ваше имя пользователя GitHub: ")
    repo_name = "ambient-sound-mixer"
    
    # Открываем страницу создания репозитория
    repo_url = f"https://github.com/new"
    print(f"\nОткрываем браузер для создания репозитория...")
    webbrowser.open(repo_url)
    
    input("\nПосле создания репозитория нажмите Enter для продолжения...")

    # Инициализируем Git и добавляем файлы
    commands = [
        "git init",
        "git add .",
        'git commit -m "Initial commit: Ambient Sound Mixer v1.0.0"',
        "git branch -M main",
        f"git remote add origin https://github.com/{username}/{repo_name}.git",
        "git push -u origin main"
    ]

    for command in commands:
        if not run_command(command):
            print("\nПроизошла ошибка. Проверьте сообщение выше.")
            return

    print("\n✨ Репозиторий успешно создан и код загружен!")
    print(f"\nВаш репозиторий доступен по адресу: https://github.com/{username}/{repo_name}")
    
    # Открываем репозиторий в браузере
    webbrowser.open(f"https://github.com/{username}/{repo_name}")

if __name__ == "__main__":
    setup_github()
