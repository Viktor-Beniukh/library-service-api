from celery import shared_task

from book.notifications import send_overdue_borrowings_notification


@shared_task
def run_send_overdue_borrowings_notification():
    send_overdue_borrowings_notification()
