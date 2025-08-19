# tracker/urls.py
from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_state, name='search_state'),
    path('all-states/', views.all_states_data, name='all_states'),
    path('api/state/<str:state>/', views.api_state_data, name='api_state_data'),
]