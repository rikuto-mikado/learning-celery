from celery_app.tasks import heavy_process

result = heavy_process.delay("Expert User")

print(f"Task ID: {result.id}")
print(f"Current State: {result.state}")

try:
    final_value = result.get(timeout=10)
    print(f"Result: {final_value}")
except Exception as e:
    print(f"Task failed: {e}")
