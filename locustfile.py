from locust import HttpUser, task, between
import random

class SistemaReportesUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def home(self):
        self.client.get("/")

    @task(3)
    def enviar_reporte(self):
        codigo = random.choice(["ABC123", "TEST01", "COD999"])
        descripcion = f"Prueba automática de reporte {random.randint(100,999)}"
        self.client.post("/enviar_reporte", data={
            "codigo": codigo,
            "descripcion": descripcion
        })

    @task(1)
    def ver_reportes(self):
        codigo = random.choice(["ABC123", "TEST01", "COD999"])
        self.client.post("/ver_reportes", data={
            "codigo": codigo
        })
