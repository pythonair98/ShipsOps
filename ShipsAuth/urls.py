from django.urls import path
from .views import login_view,register_view,logout_view,edit_user_view,delete_user_view,user_list_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('user/edit/<int:user_id>/', edit_user_view, name='edit_user'),
    path('user/delete/<int:user_id>/', delete_user_view, name='delete_user'),
    path('user/list/', user_list_view, name='user_list'),
]
# User management URLs

