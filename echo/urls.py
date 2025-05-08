from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/<int:book_id>', views.delete, name='delete'),
    path('edit/<int:book_id>', views.edit, name='edit'),
    path('add', views.add, name='add'),
    path('signUp', views.signUp, name='signUp'),
    path('logIn', views.logIn, name='logIn'),
    path('logOut', views.logOut, name='logOut'),
    path('profile', views.profile, name='profile'),
    path('add_to_cart/<int:book_id>', views.add_to_cart, name='add_to_cart'),
    path('cart', views.cart, name='cart'),
    path('place_order', views.place_order, name='place_order'),
    path('order_history', views.order_history, name='order_history'),
    path('update_quantity/<int:book_id>',
         views.update_quantity, name='update_quantity'),
    path('delete_from_cart/<int:book_id>',
         views.delete_from_cart, name='delete_from_cart'),
    path('clear_cart', views.clear_cart, name='clear_cart'),
]
