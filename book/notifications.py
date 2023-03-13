import telebot
from django.conf import settings
from django.utils import timezone

from borrowing.models import Borrowing, Payment

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


def send_new_borrowing_notification(borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
    book = borrowing.book
    days_borrowed = (
        borrowing.expected_return_date - borrowing.borrow_date
    ).days
    borrowing_amount = book.daily_fee * days_borrowed

    message = f"A new borrowing has been created!\n\n" \
              f"Borrower Name: " \
              f"{borrowing.borrower.first_name} " \
              f"{borrowing.borrower.last_name}\n" \
              f"Amount: ${borrowing_amount}"

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


def send_overdue_borrowings_notification():
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=timezone.now(),
        actual_return_date__isnull=True
    )

    message = "The following borrowings are overdue:\n\n"
    for borrowing in overdue_borrowings:

        if borrowing:
            book = borrowing.book
            days_borrowed = (
                borrowing.expected_return_date - borrowing.borrow_date
            ).days
            borrowing_amount = book.daily_fee * days_borrowed

            message += f"Borrower Name: {borrowing.borrower.first_name} " \
                       f"{borrowing.borrower.last_name}\n" \
                       f"Amount: ${borrowing_amount}\nDue Date: " \
                       f"{borrowing.expected_return_date}\n" \
                       f"The fine is twice the fixed " \
                       f"daily fee for each overdue day!\n\n"

        else:
            message += "No borrowings overdue today!"

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


def send_billing_notification(borrowing_id):

    borrowing = Borrowing.objects.get(id=borrowing_id)
    book = borrowing.book
    days_borrowed = (
            borrowing.expected_return_date - borrowing.borrow_date
    ).days

    message = f"Borrower Name: {borrowing.borrower.first_name} " \
              f"{borrowing.borrower.last_name}\n" \
              f"You have to pay for borrowing the book '{book.title}'\n"

    if borrowing.actual_return_date:
        if days_borrowed > 0 and (
            borrowing.actual_return_date > borrowing.expected_return_date
        ):
            overdue_borrowed = (
                borrowing.actual_return_date - borrowing.expected_return_date
            ).days
            borrow_amount = book.daily_fee * days_borrowed + (
                overdue_borrowed * book.daily_fee * settings.FINE_MULTIPLIER
            )

            message += f"Amount: ${borrow_amount}\n\n"

        if days_borrowed > 0 and (
            borrowing.actual_return_date == borrowing.expected_return_date
        ):
            borrow_amount = days_borrowed * book.daily_fee

            message += f"Amount: ${borrow_amount}\n\n"

        if days_borrowed > 0 and (
            borrowing.actual_return_date < borrowing.expected_return_date
        ):
            days_actual = (
                    borrowing.actual_return_date - borrowing.borrow_date
            ).days
            borrow_amount = days_actual * book.daily_fee

            message += f"Amount: ${borrow_amount}\n\n"

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


def send_successful_payment_notification(payment_id):
    payment = Payment.objects.get(id=payment_id)

    message = f"Payment successful!\n\n" \
              f"Borrower Name: " \
              f"{payment.borrowing.borrower.first_name} " \
              f"{payment.borrowing.borrower.last_name}\n" \
              f"Amount: {payment.money_to_pay}\n"

    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
