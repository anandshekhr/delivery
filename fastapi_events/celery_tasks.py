from celery import Celery
celery_app = Celery('events', broker='redis://redis:6379/0', backend='redis://redis:6379/1')

@celery_app.task(bind=True, name="process_event_task",autoretry_for=(Exception,),retry_backoff=True, max_retries=5)
def process_event(event_data: dict):
    print("Async Processing event:", event_data['event_type'])