from django.urls import path

from sso.views import SingleSignOn, SingleSignOnConfirm, SingleSignOnLogIn

urlpatterns = [
    path('sso/get-session/', SingleSignOn.as_view(), name="sso-create"),
    path('sso/confirm/', SingleSignOnConfirm.as_view(), name="sso-confirm"),
    path('sso/login/', SingleSignOnLogIn.as_view(), name="sso-login"),
]
