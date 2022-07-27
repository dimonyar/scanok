from django.db import models


class DocHeadDocStatus(models.IntegerChoices):

    New = -1, 'Новый'
    Out = 0, 'отправлен на ТСД'
    Inpogress = 1, 'В работе'
    Completed = 2, 'Завершен'
    Completed_with_errors = 3, 'Завершен с ошибками'
    Reloaded = 4, 'Повторно загруженный'
    Synchronised = 5, 'Синхронизирован'
    Received = 6, 'получен ТСД'
    Annulled = 7, 'анулирован ТСД'


class DocHeadDocType(models.IntegerChoices):
    Arrival = 1, 'Приходный'
    Expense = 2, 'Расходный'
    Inventory = 3, 'Инвентаризация'
    Move = 4, 'перемещение'
    Decomm = 5, 'списание'
    Return = 6, 'возврат'
