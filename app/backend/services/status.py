from repositories.logs import SendLogsRepository


class StatusService:
    def __init__(self, logs: SendLogsRepository):
        self._logs = logs

    def resumen(self) -> dict:
        return {
            'enviados': self._logs.contar('whatsapp'),
            'emails_enviados': self._logs.contar('email'),
            'ig_enviados': self._logs.contar('instagram'),
        }
