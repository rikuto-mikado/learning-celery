# Celery Architecture

Celery consists of three components: **Producer**, **Broker**, and **Worker**.

```
Producer ──→ Broker ──→ Worker
             (Redis)
```

---

## 1. Producer

The side that sends task requests. It pushes tasks onto the queue without executing them directly.

**In this project:** [producer.py](../producer.py)

```python
from celery_app.tasks import heavy_process

result = heavy_process.delay("Expert User")  # enqueue the task
```

`.delay()` sends the task to the broker and returns immediately. The result can be retrieved later with `.get()`.

---

## 2. Broker

A message queue that sits between the Producer and Worker. The Producer pushes tasks in; the Worker pulls tasks out.

**In this project:** Redis (`redis` service in [docker-compose.yml](../docker-compose.yml))

```yaml
redis:
  image: redis:alpine
```

The connection URL is configured via `CELERY_BROKER_URL` in [celery_app/celeryconfig.py](../celery_app/celeryconfig.py):

```python
broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
```

---

## 3. Worker

Pulls tasks from the broker and executes them.

**In this project:** [celery_app/tasks.py](../celery_app/tasks.py) + the `worker` service in docker-compose.

```python
@app.task(bind=True, max_retries=3)
def heavy_process(self, name):
    time.sleep(5)  # simulate heavy work
    return {"status": "success", "message": f"Hello {name}"}
```

---

## How to Run

### 1. Start Redis and the Worker

```bash
docker compose up --build
```

This starts three containers: `redis`, `worker`, and `app`.

### 2. Run the Producer

Exec into the `app` container and run the producer:

```bash
docker compose exec app python producer.py
```

### Expected output

```
Task ID: <uuid>
Current State: PENDING
Result: {'status': 'success', 'message': 'Hello Expert User'}
```

---

## Full Flow

```
1. producer.py calls heavy_process.delay("Expert User")
        ↓
2. Task is pushed to Redis (Broker)
        ↓
3. Worker pulls the task from Redis and executes heavy_process()
        ↓
4. Result is stored in Redis (Result Backend)
        ↓
5. producer.py retrieves the result via result.get()
```

---

## MEMO in japanese

docker-compose.ymlのworkerサービスに`CELERY_BROKER_URL`や`CELERY_RESULT_BACKEND`といった環境変数として要素を定義しておいて、それをceleryconfig.pyの中で`os.environ.get()`を使って`broker_url`や`result_backend`という変数名で受け取る形にしている。そしてmain.pyの`config_from_object()`というメソッドを通じてceleryconfig.pyのモジュールごとCeleryインスタンスに読み込ませることで設定が反映される。`config_from_object()`はCeleryにおいて設定情報を別のPythonオブジェクト（クラスやモジュール）から読み込むためのメソッドで、モジュール内の変数名がそのままCeleryの設定キーとして認識される。また`@app.task`デコレータは、tasks.pyが`from .main import app`でmain.pyのCeleryインスタンスをインポートして、そのインスタンスのメソッドとして関数をタスク登録するための仕組みになっている。
