from celery import shared_task


@shared_task
def send_sale_notification(sale_id: int):
    # Implement real notification logic here if needed
    return f"Sale notification queued for {sale_id}"