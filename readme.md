# Сервис аутентификации на FastAPI

* **/create-user** — регистрация пользователя с добавлением данных в Redis.

* **/auth/login** — логин.

* **/auth/logout** — логаут.

* **/auth/refresh** — обновление токена и инвалидация старых.

Ролевая модель с проверкой доступа на уровне API:

* **/protected/admin-only** — доступ только для админов.

* **/protected/users** — доступ только для пользователей.

* **/protected/role-based** — динамический выбор роли в зависимости от пользователя, отправляющего запрос.

Система позволяет гибко управлять правами доступа в зависимости от назначенной роли, что упрощает поддержку и масштабирование.

В качестве дополнительной меры защиты реализована валидация IP-адреса отправителя запроса, что позволяет проверять легитимность запроса с токеном.