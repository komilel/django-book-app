from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/<int:book_id>', views.delete, name='delete'),
    path('edit/<int:book_id>', views.edit, name='edit'),
    path('add', views.add, name='add'),
]
