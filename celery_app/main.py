from celery import Celery

app = Celery("learning-celery", include=["celery_app.tasks"])

app.config_from_object("celery_app.celeryconfig")

if __name__ == "__main__":
    app.start()
