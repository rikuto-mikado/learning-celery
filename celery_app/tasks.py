from .main import app
import time


@app.task(bind=True, max_retries=3)
def heavy_process(self, name):
    try:
        print("Executing task: {self.request.id}")
        time.sleep(5)
        return {"status": "success", "message": f"Hello {name}"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
