from django.urls import path
from . import views

urlpatterns = [
    path('tasks/<int:task_id>/annotation-counts', views.AnnotationAnalyticsView.as_view(), name='annotation-counts'),
]
