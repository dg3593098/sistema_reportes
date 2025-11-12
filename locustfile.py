from locust import HttpUser, task, between

class ReportSystemUser(HttpUser):
    wait_time = between(1, 3)  

    @task(2)
    def enviar_reporte(self):
        self.client.post("/enviar_reporte", data={
            "codigo": "ABC123",
            "descripcion": "Prueba automática de carga"
        })

    @task(1)
    def ver_reportes(self):
        self.client.post("/ver_reportes", data={"codigo": "ABC123"})

    @task(1)
    def home(self):
        self.client.get("/")