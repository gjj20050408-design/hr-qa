"""Celery 异步任务配置"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "hr_policy_qa",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=["app.tasks.document_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    # 可在这里配置定时任务
}
