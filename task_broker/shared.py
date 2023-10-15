from celery import Celery

broker_url = "amqp://127.0.0.1:35672"
redis_url = "redis://127.0.0.1:36379"
app = Celery('tasks', broker=broker_url, backend=redis_url, broker_transport_options={'socket_timeout': 3}, backend_transport_options={'socket_timeout': 3})