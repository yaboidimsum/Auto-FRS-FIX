from django.db import models

# Create your models here.
class Schedule(models.Model):
    name = models.CharField(max_length=256)
    subject_code = models.CharField(max_length=256)
    day = models.CharField(max_length=256)
    start_hour = models.CharField(max_length=256)
    end_hour = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class SubjectsAvailable(models.Model):
    name = models.CharField(max_length=256)
    subject_code = models.CharField(max_length=256)
    semester = models.CharField(max_length=256)
    sks = models.IntegerField()
    day = models.CharField(max_length=256)
    start_hour = models.IntegerField()
    end_hour = models.IntegerField()
    class_name = models.CharField(max_length=256)
    lecturer = models.CharField(max_length=256)
    status = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class UserSemester(models.Model):
    semester = models.IntegerField()

    def __int__(self):
        return self.semester

