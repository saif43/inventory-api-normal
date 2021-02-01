from django.urls import path, include
from user import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("profile", views.UserListView, "profile")
router.register("search", views.SearchedUserView, "search")
router.register("otp", views.UserOTPView, "otp")

app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserAPIView.as_view(), name="create"),
    path("", include(router.urls)),
    path("token/", views.CreateTokenView.as_view(), name="token"),
    path("me/", views.ManageUserView.as_view(), name="me"),
]