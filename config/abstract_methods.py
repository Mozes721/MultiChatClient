from abc import ABC, abstractmethod


class LLMMethods(ABC):
    @abstractmethod
    def generate(self, query: str) -> str:
        pass


class BotMethods(ABC):
    @abstractmethod
    def get_response(self, user_message: str) -> str:
        pass
    
    @abstractmethod
    def run(self) -> None:
        pass
