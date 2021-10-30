from locust import HttpLocust, TaskSet, task

bot = """# random bot
a = rand % 4

if a is 0 {
  move = east
}
if a is 1 {
  move = west
}
if a is 2 {
  move = north
}
if a is 3 {
  move = south
}
"""


class UserBehavior(TaskSet):
    def on_start(self):
        """on_start is called when a Locust start before any task is scheduled"""
        self.login()

    def login(self):
        pass
        # self.client.post("/login", {"username":"ellen_key", "password":"education"})

    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.post("/sim", json={"code": bot, "seed": ""})


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
