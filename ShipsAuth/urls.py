from django.urls import path
from .views import login_view,register_view,logout_view,edit_user_view,delete_user_view,user_list
from .views import activate_user_view, deactivate_user_view, reset_user_password_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('user/edit/<int:user_id>/', edit_user_view, name='edit_user'),
    path('user/delete/<int:user_id>/', delete_user_view, name='delete_user'),
    path('user/list/', user_list, name='user_list_auth'),
    path('user/activate/<int:user_id>/', activate_user_view, name='activate_user'),
    path('user/deactivate/<int:user_id>/', deactivate_user_view, name='deactivate_user'),
    path('user/reset-password/<int:user_id>/', reset_user_password_view, name='reset_user_password'),

]
# User management URLs

