from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('game/', views.GameListView.as_view(), name='game_list'),
    path('game/<int:game_id>/', views.observe, name='observe'),
    path('game/<int:game_id>/take_turn/', views.take_turn, name='take_turn'),
]