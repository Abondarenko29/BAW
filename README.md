# BAW - запуск проєкту
Щоб запустити проєкт треба:
1.Зареєструватися на twillio (ціль - надсилання перевірки по sms), vonage.
2.Створити config.py у папці python_files та написати туди такі змінні:
password - пароль для flask.config["SECRET_KEY"];
account_sid, auth_token, verify_sid - Ви їх знайдете у twillio.
key, secret - Публічний та секретний ключ у vonage.
3.Створити папку files.
4.Запустити у діректорії python_files/dbs такі файли: users_db.py, price.py, bank.py.
5.Запустити у діректорії python_files/dbs/zwjazok такі файли: users_price.py, price_bank.py.
