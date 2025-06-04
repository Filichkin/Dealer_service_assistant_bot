from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.dao.database import Base


class User(Base):
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False
        )

    payments: Mapped[List['Payment']] = relationship(
        'Payment',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class Service(Base):
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    hidden_content: Mapped[str] = mapped_column(Text)
    payments: Mapped[List['Payment']] = relationship(
        'Payment',
        back_populates='service',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f"<Service(id={self.id}, name='{self.name}', price={self.price})>"
            )


class Payment(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))
    price: Mapped[int]
    payment_id: Mapped[str] = mapped_column(unique=True)
    expire: Mapped[datetime]
    user: Mapped['User'] = relationship(
        'User',
        back_populates='payments'
        )
    service: Mapped['Service'] = relationship(
        'Service',
        back_populates='payments'
        )


class VehicleData(Base):
    local_vin: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
        )
    dkd_vin: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
        )
    dist_code: Mapped[str]
    warranty_start_date: Mapped[str]
    engine_number: Mapped[str]
    transmission_number: Mapped[str]
    key_number: Mapped[str]
    body_color: Mapped[str]

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class PartsData(Base):
    part_number: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
        )
    descriprion: Mapped[str]
    ellias_count: Mapped[int]
    mobis_count: Mapped[str]

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'


class MaintenanceData(Base):
    vin: Mapped[str] = mapped_column(
        Text,
        nullable=False
        )
    type: Mapped[str]
    dealer_code: Mapped[str]
    maintenance_date: Mapped[str]
    odometer: Mapped[int]

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id})'
