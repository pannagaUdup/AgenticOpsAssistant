from dataclasses import dataclass

from app.schemas.account import AccountResponse


@dataclass(frozen=True, slots=True)
class Account:
    id: str
    name: str
    status: str
    tier: str

    @classmethod
    def from_response(cls, response: AccountResponse) -> Account:
        return cls(
            id=response.id,
            name=response.name,
            status=response.status,
            tier=response.tier,
        )