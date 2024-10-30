from aiogram.types import BotCommand

menu = [
    BotCommand(command="/login", description="Войти в аккаунт"),
    BotCommand(command="/register", description="Регистрация"),
    BotCommand(command="/enter_scores", description="Сохранить баллы"),
    BotCommand(command="/view_scores", description="Посмотреть сохраненные баллы")
]
