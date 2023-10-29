from django.db import models


class Student(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='Имя ученика', max_length=255)
    tg_id = models.PositiveIntegerField(verbose_name='Telegram_id', unique=True)
    SKILL_CHOICES = (
        (1, 'Beginner'),
        (2, 'Beginner+'),
        (3, 'Junior'),
    )
    skills = models.PositiveIntegerField(verbose_name='Навыки', choices=SKILL_CHOICES, default=1, db_index=True)
    TIME_CHOICES = (
        (1, '14.00-18.00'),
        (2, '18.00-22.00'),
        (3, 'Any Time'),
    )
    time = models.PositiveIntegerField(verbose_name='Доступное время', choices=TIME_CHOICES, default=3, db_index=True)
    place_residence = models.BooleanField(verbose_name='Дальний восток', default=False)
    is_active = models.BooleanField(verbose_name='Участвует в проекте', default=True)
    email = models.CharField(verbose_name='Почта ученика', max_length=255, default='example@gmail.com')

    def __str__(self):
        return self.name


class Manager(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='Имя менеджера', max_length=255)
    tg_id = models.PositiveIntegerField(verbose_name='Telegram_id', unique=True)
    TIME_CHOICES = (
        (1, 'Утро'),
        (2, 'Вечер'),
    )
    time = models.PositiveIntegerField(verbose_name='Доступное время', choices=TIME_CHOICES, default=3, db_index=True)

    def __str__(self):
        return self.name

class Administrator(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='Имя менеджера', max_length=255)
    tg_id = models.PositiveIntegerField(verbose_name='Telegram_id', unique=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='Название проекта', max_length=255)
    students = models.ManyToManyField(Student, verbose_name='Ученики', related_name='projects')
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name='Менеджер', related_name='projects')
    TIME_CHOICES = [(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') for hour in range(12, 23) for minute in
                    range(0, 60, 30)]
    time = models.CharField(verbose_name='время проведения', max_length=5, choices=TIME_CHOICES, default='12:00')
    date = models.DateField(verbose_name='Дата проведения')
    def __str__(self):
        return self.name
