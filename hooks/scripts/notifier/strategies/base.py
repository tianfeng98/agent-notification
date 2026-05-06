from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    name: str

    @abstractmethod
    def send(
        self,
        *,
        message: str,
        webhook_url: str,
        reason: str,
        summary: str,
        status: str,
        secret: str = "",
    ) -> None:
        raise NotImplementedError
