from django.contrib import admin
from django import forms

from .models import Student, Manager, Project


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'skills',
        'place_residence',
    ]


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'time',
    ]


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = []

    def __init__(self, *args, **kwargs):
        super(ProjectAdminForm, self).__init__(*args, **kwargs)
        existing_students_ids = Project.objects.exclude(pk=self.instance.pk).values_list('students__id', flat=True)
        self.fields['students'].queryset = Student.objects.filter(is_active=True).exclude(id__in=existing_students_ids)

class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = [
        'name',
        'manager',
        'time',
    ]
admin.site.register(Project, ProjectAdmin)



