class ReportController:
    def __init__(self, service) -> None:
        self.service = service

    def summary(self) -> dict:
        return self.service.summary()

    def user(self, user_id: int) -> dict:
        return self.service.user_report(user_id)
