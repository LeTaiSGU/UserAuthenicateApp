from locust import HttpUser, task, between

class FastapiUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def login(self):
        self.client.post("/auth/login", data={
            "username": "your_email@example.com",
            "password": "your_password"
        })

    @task
    def get_me(self):
        # Đăng nhập lấy token
        response = self.client.post("/auth/login", data={
            "username": "your_email@example.com",
            "password": "your_password"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.client.get("/auth/me", headers={
                "Authorization": f"Bearer {token}"
            })