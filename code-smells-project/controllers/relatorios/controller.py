class SalesReportController:
    def __init__(self, service):
        self.service = service

    def sales_report(self):
        return {"dados": self.service.build(), "sucesso": True}, 200

