# Async Python Lesson 5

Чатик с графическим интерфейсом (Tkinter)

Учебный проект в рамках курса "Асинхронный Python"
на [Девмане](https://dvmn.org/modules/async-python/)

## Quick start

**\*poetry required**

```
# clone project from github
git clone https://github.com/nobbynobbs/async-python-5.git
cd async-python-5
# install dependencies
poetry install --no-dev
# play with apps
poetry run minechat --help  # show help for chat client
poetry run minechat -t=YOUR_TOKEN # run chat client with token
poetry run registration     # registration client
```

## Настройки

В `minechat` настройки можно передать через аргументы командной строки
или переменные окружения.

В таблице приведены имена переменных окружения и
значения по умолчанию, используемые если не переданы
ни флаги, ни переменные окружения:

|       VARIABLE       | DEFAULT VALUE        |
|:--------------------:|----------------------|
|MINECHAT_READER       |minechat.dvmn.org:5000|
|MINECHAT_WRITER       |minechat.dvmn.org:5050|
|MINECHAT_TOKEN        |None                  |
|MINECHAT_LOGGING_LEVEL|INFO                  |
|MINECHAT_HISTORY_PATH |history.txt           |

## Баг

Фишка с кнопкой для копированием токена в буфер обмена
задумывалась как удобная, но оказалось,
что значение оттуда исчезает после завершения приложения :sad:
