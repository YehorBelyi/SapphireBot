from sqlalchemy import String, Text, Float, DateTime, func, Integer, Nullable, Numeric, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Default SqlAlchemy class to begin with
class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

# Our model for operating with products
class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(6,2), nullable=False)
    image: Mapped[str] = mapped_column(String(150))

    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
    category: Mapped["Category"] = relationship(backref="product")

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int]

    user: Mapped["User"] = relationship(backref="cart")
    product: Mapped["Product"] = relationship(backref="cart")

class History(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)

    user: Mapped["User"] = relationship(backref="history")
    product: Mapped["Product"] = relationship(backref="history")

# Models for role handling
class Role(Base):
    __tablename__ = 'role'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

class Employee(Base):
    __tablename__ = 'employee'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('role.id', ondelete='CASCADE'), nullable=False)

    role: Mapped["Role"] = relationship(backref="employee")