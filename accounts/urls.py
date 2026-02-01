from django.urls import path
from accounts.views import CustomLoginView
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path(
        'senha/',
        PasswordChangeView.as_view(
            template_name='auth/password_change.html',
            success_url='/senha/sucesso/'
        ),
        name='password_change'
    ),

    path(
        'senha/sucesso/',
        PasswordChangeDoneView.as_view(
            template_name='auth/password_change_done.html'
        ),
        name='password_change_done'
    ),
]
