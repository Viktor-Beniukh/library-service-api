import telebot
from django.conf import settings
from django.utils import timezone

from borrowing.models import Borrowing, Payment

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


def send_new_borrowing_notification(borrowing_id: int) -> None:
    borrowing = Borrowing.objects.get(id=borrowing_id)
    days_borrowed = (
        borrowing.expected_return_date - borrowing.borrow_date
    ).days
    borrowing_amount = borrowing.book.daily_fee * days_borrowed

    message = (
        f"A new borrowing has been created!\n\n"
        f"Borrower Name: "
        f"{borrowing.borrower.first_name} "
        f"{borrowing.borrower.last_name}\n"
        f"Amount: ${borrowing_amount}"
    )

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


def send_overdue_borrowings_notification() -> None:
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=timezone.now(),
        actual_return_date__isnull=True
    )

    message = "The following borrowings are overdue:\n\n"
    for borrowing in overdue_borrowings:

        if borrowing:
            days_borrowed = (
                borrowing.expected_return_date - borrowing.borrow_date
            ).days
            borrowing_amount = borrowing.book.daily_fee * days_borrowed

            message += (
                f"Borrower Name: "
                f"{borrowing.borrower.first_name} "
                f"{borrowing.borrower.last_name}\n"
                f"Amount: ${borrowing_amount}\nDue Date: "
                f"{borrowing.expected_return_date}\n"
                f"The fine is twice the fixed daily "
                f"fee for each overdue day!\n\n"
            )

        else:
            message += "No borrowings overdue today!"

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


def send_successful_payment_notification(payment_id: int) -> None:
    payment = Payment.objects.get(id=payment_id)

    message = (
        f"Payment successful!\n\n"
        f"Borrower Name: "
        f"{payment.borrowing.borrower.first_name} "
        f"{payment.borrowing.borrower.last_name}\n"
        f"Amount: {payment.money_to_pay}\n"
    )

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
