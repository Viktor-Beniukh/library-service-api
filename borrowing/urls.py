from django.urls import path, include
from rest_framework import routers

from borrowing.views import (
    BorrowingViewSet,
    PaymentViewSet,
    create_checkout_session,
    payment_success,
)

router = routers.DefaultRouter()
router.register("borrowing", BorrowingViewSet)
router.register("payment", PaymentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "payment/<int:payment_id>/create-session/",
        create_checkout_session,
        name="create-session"
    ),
    path("success/", payment_success, name="success"),
]


app_name = "borrowing"
