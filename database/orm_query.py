import math
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload

from database.models import Product, Cart, Category, Banner, User, History, Employee, Role
from database.redis_client import redis_client

# === Admin panel ===
async def orm_add_product(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        description=data["desc"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()

async def orm_get_products(session: AsyncSession, category_id: int):
    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_product(session: AsyncSession, product_id: int):
    key = f"product:{product_id}:"
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    product = result.scalar()

    if product:
        data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "image": product.image,
            "category_id": product.category_id,
        }
        print(data)
        await redis_client.set(key, json.dumps(data), ex=300)
        return data
    return None

async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Product).where(Product.id == product_id).values(
        name=data["name"],
        description=data["desc"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    await session.execute(query)
    await session.commit()
    await redis_client.delete(f"product:{product_id}")

async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()
    await redis_client.delete(f"product:{product_id}")

# === Roles methods ===
async def orm_add_employee(session: AsyncSession, data: dict):
    query = select(Employee).where(Employee.user_id == user_id)


# === User methods ===
async def orm_add_user(session: AsyncSession,
                       user_id: int,
                       first_name: str | None = None,
                       last_name: str | None = None,
                       phone: str | None = None):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone,))
        await session.commit()

# === Cart methods ===
async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        await redis_client.delete(f"cart:{user_id}")
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1))
        await session.commit()
    await redis_client.delete(f"cart:{user_id}")

async def orm_get_user_carts(session: AsyncSession, user_id: int):
    key = f"cart:{user_id}"
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    query = select(Cart).where(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    carts = result.scalars().all()

    data = [
        {
            "product_id": cart.product.id,
            "name": cart.product.name,
            "price": float(cart.product.price),
            "image": cart.product.image,
            "quantity": cart.quantity
        }
        for cart in carts
    ]
    await redis_client.set(key, json.dumps(data), ex=300)
    return data

async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()
    await redis_client.delete(f"cart:{user_id}")

async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        await redis_client.delete(f"cart:{user_id}")
        return True
    else:
        await orm_remove_from_cart(session, user_id, product_id)
        await session.commit()
        await redis_client.delete(f"cart:{user_id}")
        return False

async def orm_flush_cart(session: AsyncSession, user_id: int):
    query = delete(Cart).where(Cart.user_id == user_id)
    await session.execute(query)
    await session.commit()
    await redis_client.delete(f"cart:{user_id}")

# === Order history ===
async def orm_add_order_to_history(session: AsyncSession, user_id: int, user_orders: list):
    session.add_all([History(user_id=user_id, product_id=item["product_id"]) for item in user_orders])
    await session.commit()

async def orm_get_order_history(session: AsyncSession, user_id: int):
    query = select(History).where(History.user_id == user_id).options(joinedload(History.product))
    result = await session.execute(query)
    return result.scalars().all()



# === Banner methods ===
async def orm_add_banner_description(session: AsyncSession, data: dict):
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()

async def orm_update_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()
    await redis_client.delete(f"banner:{name}")

async def orm_get_banner(session: AsyncSession, page:str):
    key = f"banner:{page}"
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    banner =  result.scalar()

    if banner:
        data = {
            "id": banner.id,
            "name": banner.name,
            "image":banner.image,
            "description": banner.description
        }
        await redis_client.set(key, json.dumps(data), ex=300)
        return data
    return None

async def orm_get_page_description(session: AsyncSession):
    key = "page_descriptions"
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    query = select(Banner)
    result = await session.execute(query)
    banners = result.scalars().all()

    data = [
        {
            "id": b.id,
            "name": b.name,
            "image": b.image,
            "description": b.description
        }
        for b in banners
    ]
    await redis_client.set(key, json.dumps(data), ex=300)
    return data

# === Category methods ===
async def orm_get_categories(session: AsyncSession):
    key = "categories"
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    query = select(Category)
    result = await session.execute(query)
    categories = result.scalars().all()

    data = [
        {
            "id": c.id,
            "name": c.name
        }
        for c in categories
    ]
    await redis_client.set(key, json.dumps(data), ex=300)
    return data

async def orm_insert_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()

# === Roles methods ===
async def orm_add_roles(session: AsyncSession, roles: list):
    query = select(Role)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Role(name=role) for role in roles])
    await session.commit()

async def orm_get_roles(session: AsyncSession):
    key = "roles"
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    query = select(Role)
    result = await session.execute(query)
    roles = result.scalars().all()

    data = [
        {
            "id": r.id,
            "name": r.name
        }
        for r in roles
    ]
    await redis_client.set(key, json.dumps(data), ex=300)
    return data

async def orm_add_employee(session: AsyncSession, data: dict):
    query = select(Employee).where(Employee.user_id == int(data["user_id"])).options(joinedload(Employee.role))
    result = await session.execute(query)
    if result.first():
        return

    obj = Employee(
        user_id=int(data["user_id"]),
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        role_id=int(data["role_id"]),
    )

    session.add(obj)
    await session.commit()

async def orm_get_employees(session: AsyncSession):
    key = "employees"
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)

    query = select(Employee).options(joinedload(Employee.role))
    result = await session.execute(query)
    employees = result.scalars().all()

    data = [
        {
            "id": e.id,
            "user_id": e.user_id,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "phone": e.phone,
            "role_id": e.role_id,
        }
        for e in employees
    ]
    print(data)
    await redis_client.set(key, json.dumps(data))
    return data