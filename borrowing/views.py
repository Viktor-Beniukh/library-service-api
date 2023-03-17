

import stripe

from datetime import date, datetime

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# from book.permissions import IsAdminOrIfAuthenticatedReadOnly
from book.notifications import send_successful_payment_notification

from book.views import LibraryPagination
from borrowing.models import Borrowing, Payment
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
    BorrowingReturnBookSerializer,
    PaymentSerializer,
    PaymentUpdateSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY
BASE_URL = "http://127.0.0.1:8000"


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "borrower")
    serializer_class = BorrowingSerializer
    pagination_class = LibraryPagination
    # permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        # is_status = self.request.user.is_staff
        user_id_str = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset

        if user_id_str:
            queryset = queryset.filter(borrower_id=int(user_id_str))

        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)

        # if is_status is False:
        #     queryset = queryset.filter(borrower=self.request.user)

        return queryset

    def get_serializer_class(self):

        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "update":
            return BorrowingUpdateSerializer

        if self.action == "return_book":
            return BorrowingReturnBookSerializer

        return BorrowingSerializer

    @action(methods=["GET", "POST"], detail=True, url_path="return")
    def return_book(self, request, pk=None):
        borrowing = get_object_or_404(Borrowing, pk=pk)

        if request.method == "GET":
            serializer = self.get_serializer(borrowing, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if borrowing.actual_return_date is not None:
                    raise ValidationError(
                        "This book has already been returned"
                    )

                borrowing.actual_return_date = timezone.now()
                borrowing.save()
                book = borrowing.book
                book.inventory += 1
                book.save()

                return Response(
                    {"status": "Your book was successfully returned"},
                    status=status.HTTP_200_OK
                )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id&is_active",
                type={"type": "list", "items": [
                    {"type": "number"}, {"type": "bool"}
                ]},
                description="Filter by users id and is_active "
                            "(ex. ?user_id=1&is_active=True)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer
    pagination_class = LibraryPagination
    # permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    #
    # def get_queryset(self):
    #     if self.request.user.is_staff:
    #         return Payment.objects.select_related("borrowing")
    #     return Payment.objects.filter(
    #         borrowing__borrower=self.request.user
    #     )

    def get_serializer_class(self):
        if self.action == "update":
            return PaymentUpdateSerializer

        return PaymentSerializer


def create_checkout_session(request, payment_id):
    payment = Payment.objects.get(pk=payment_id)

    if payment.status_payment == payment.PAID:
        return JsonResponse(
            {
                "message": "I'm sorry, you’ve already paid to borrow this book"
            }
        )

    else:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(payment.money_to_pay * 100),
                        "product_data": {
                            "name": payment.borrowing.book.title,
                            "description": "Borrowing book fee",
                        },
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=BASE_URL + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=BASE_URL + (
                "/cancelled?session_id={CHECKOUT_SESSION_ID}"
            ),
        )

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

        return redirect(payment.session_url)


def payment_success(request):
    session_id = request.GET.get("session_id")
    payment = Payment.objects.get(session_id=session_id)
    payment.status_payment = Payment.PAID

    if (
        payment.borrowing.actual_return_date
        > payment.borrowing.expected_return_date
    ):
        payment.type_payment = Payment.FINE

    payment.save()

    send_successful_payment_notification(payment_id=payment.id)

    return JsonResponse(
        {"message": "Payment successful!"}
    )


def payment_cancel(request):
    session_id = request.GET.get("session_id")
    payment = Payment.objects.get(session_id=session_id)
    payment.status_payment = Payment.CANCELLED
    payment.save()

    return JsonResponse(
        {
            "message": "Payment cancelled. "
                       "The payment can be paid a bit later "
                       "(but the session is available for only 24h)"
        }
    )


def payment_expired(request):
    session_id = request.GET.get("session_id")
    payment = get_object_or_404(Payment, session_id=session_id)
    session = stripe.checkout.Session.retrieve(session_id)

    if session.expires_at < datetime.now(timezone.utc):
        payment.status_payment = Payment.EXPIRED
        payment.save()

        return JsonResponse({"message": "Payment expired."})
