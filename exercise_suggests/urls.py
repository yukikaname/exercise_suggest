"""exercise_suggestsのURLパターンの定義"""

from django.urls import path

from . import views

app_name = 'exercise_suggests'
urlpatterns = [
	# 入力フォーム
	path('', views.form, name='form'),
	path('result/', views.result_page, name='result_page'),
]