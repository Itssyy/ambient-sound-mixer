# 🎵 Ambient Sound Mixer

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![Русский](https://img.shields.io/badge/lang-Русский-red.svg)](docs/translations/README.ru.md)

</div>

Ambient Sound Mixer - это элегантное приложение для создания расслабляющей атмосферы через микширование различных ambient звуков. Идеально подходит для работы, медитации или отдыха.

<div align="center">
<img src="docs/images/preview.png" alt="Preview" width="600"/>
</div>

## ✨ Основные возможности

### 🎚️ Базовые функции
- Воспроизведение до 3 звуков одновременно
- Точная регулировка громкости (0-100%)
- Сохранение и загрузка пользовательских миксов
- Современный минималистичный интерфейс
- Умный автобаланс громкости

### 🌊 Эффекты
- **Эффект дыхания**
  - Имитация морских волн через модуляцию громкости
  - Настраиваемая интенсивность (±20%)
  - Регулируемая скорость (3-8 секунд)

- **Динамическое панорамирование**
  - Плавное перемещение звука между каналами
  - Настраиваемый интервал (2-5 секунд)
  - Полный контроль над стерео-позицией

## 🎧 Поддерживаемые форматы

### Аудио
- WAV (16/24/32 бит)
- 44.1 кГц
- Стерео/Моно

### Рекомендации
- Размер файла: до 50 МБ
- Длительность: 1-5 минут
- Формат: несжатый WAV

## 🚀 Быстрый старт

### Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ambient-sound-mixer.git
cd ambient-sound-mixer
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### Запуск
```bash
python src/main.py
```

## 💻 Системные требования

- Windows 10/11
- Python 3.8+
- 4 ГБ RAM
- Звуковая карта с поддержкой стерео

## 🎨 Скриншоты

<div align="center">
<img src="docs/images/screenshot1.png" alt="Screenshot 1" width="400"/>
<img src="docs/images/screenshot2.png" alt="Screenshot 2" width="400"/>
</div>

## 🛠️ Разработка

### Установка инструментов разработчика
```bash
pip install -r requirements-dev.txt
```

### Запуск тестов
```bash
pytest tests/
```

### Проверка кода
```bash
flake8 src/
black src/
mypy src/
```

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## 🤝 Участие в проекте

Мы приветствуем ваше участие! Пожалуйста, ознакомьтесь с [руководством по участию](CONTRIBUTING.md) для получения дополнительной информации.

## 🙏 Благодарности

- [pygame](https://www.pygame.org/) - за аудио движок
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - за современные UI компоненты
- Всем, кто внес свой вклад в проект
