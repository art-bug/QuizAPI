Для сборки и запуска проекта просто введите команду:
```
docker-compose up
```

Затем зарегистрируйтесь в pgAdmin - localhost:5050 - и создайте сервер:
```
Servers -> Register -> Сервер...
```
Задайте любое имя сервера, а во вкладке Соединение - database-container.
Имя пользователя - postgres, пароль - admin.
Нажмите Сохранить.

Для проверки работоспособности сервера выполните запрос:
```
curl http://localhost:8000/quiz
```

Примеры запросов:
```
curl -d '{"questions_num": "6"}' -H "Content-Type: application/json" http://localhost:8000/quiz | python -m json.tool
```
Пример ответа:
```
{
    "id": 21,
    "answer": "Leica",
    "was_created": "2014-02-11T23:33:48.464000+00:00",
    "question_id": 73322,
    "question": "This German company introduced the first precision miniature 35 mm camera in 1924"
}
```
```
curl -d '{"questions_num": "0"}' -H "Content-Type: application/json" http://localhost:8000/quiz | python -m json.tool
```
Возвращает сообщение о некорректном значении:
```
{
    "message": "ensure this value is greater than or equal to 1"
}
```