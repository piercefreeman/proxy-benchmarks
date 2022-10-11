from locust import FastHttpUser, HttpUser, events, task
from locust.runners import MasterRunner, WorkerRunner


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    # Fix issue on 
    if isinstance(environment.runner, MasterRunner):
        environment.stats.use_response_times_cache = True
    if isinstance(environment.runner, WorkerRunner):
        environment.stats.use_response_times_cache = True


#class WebsiteUser(FastHttpUser):
class WebsiteUser(HttpUser):
    @task
    def index(self):
        self.client.get("/handle", verify=False)