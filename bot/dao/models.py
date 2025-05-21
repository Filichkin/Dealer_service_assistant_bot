from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, text, ForeignKey
from bot.dao.database import Base, str_uniq


class User(Base):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    dealer_code: Mapped[str]
    email: Mapped[str_uniq]
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False
        )

    approved: Mapped[bool] = mapped_column(
        default=False,
        server_default=text('true'),
        nullable=False
        )
    is_admin: Mapped[bool] = mapped_column(
        default=False,
        server_default=text('false'),
        nullable=False
        )

    purchases: Mapped[List['Payment']] = relationship(
        'Payment',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class Payment(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    price: Mapped[int]
    payment_id: Mapped[str] = mapped_column(unique=True)
    user: Mapped['User'] = relationship(
        'User',
        back_populates='payments'
        )

    def __repr__(self):
        return (
            f'<Payment(id={self.id}, user_id={self.user_id}, '
            f'date={self.created_at})>'
            )
