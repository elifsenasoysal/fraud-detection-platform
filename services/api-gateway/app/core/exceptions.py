"""
API Gateway — Custom Exception Classes
"""

from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {user_id}",
        )


class TransactionNotFoundException(HTTPException):
    def __init__(self, transaction_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction not found: {transaction_id}",
        )


class ServiceUnavailableException(HTTPException):
    def __init__(self, service: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {service}",
        )
