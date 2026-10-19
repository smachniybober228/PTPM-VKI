from abc import ABC, abstractmethod

class EmailSenderInterface(ABC):
    @abstractmethod
    def send(self, recipient: str, subject: str, body: str) -> None:
        ...


class EmailSenderStub(EmailSenderInterface):
    def send(self, recipient: str, subject: str, body: str) -> None:
        pass # Имитация отправки