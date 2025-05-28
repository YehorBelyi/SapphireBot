from aiogram.types import InputMediaPhoto
from database.orm_query import orm_get_banner, orm_get_categories, orm_get_products, orm_delete_product, \
    orm_get_user_carts, orm_delete_from_cart, orm_reduce_product_in_cart, orm_add_to_cart
from keyboards.inline import get_user_main_btns, get_user_catalog_btns, get_products_btns, get_user_cart
from sqlalchemy.ext.asyncio import AsyncSession
from utils.paginator import Paginator

async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)

    return image, kbds

async def catalog(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds

def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["< Prev"] = "previous"

    if paginator.has_next():
        btns["> Next"] = "next"

    return btns

async def products(session, level, category, page):
    products = await orm_get_products(session, category_id=category)

    paginator = Paginator(products, page=page)
    # Returns first element of list
    product = paginator.get_page()[0]

    image = InputMediaPhoto(media=product.image,
                            caption=f"<b>{product.name}</b>\n"
                                    f"<b>{product.description}</b>\n"
                                    f"Price: {round(product.price, 2)}\n"
                                    f"Product {paginator.page} out of {paginator.pages}"
                            )
    paginations_btns = pages(paginator)

    kbds = get_products_btns(level=level,
                             category=category,
                             page=page,
                             pagination_btns=paginations_btns,
                             product_id=product.id)

    return image, kbds

async def carts(session, level, menu_name, page, user_id, product_id):
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, product_id)

    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(media=banner.image, caption=banner.description)

        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )
    else:
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity*cart.product.price, 2)
        total_price = round(sum(cart.quantity*cart.product.price for cart in carts), 2)
        image = InputMediaPhoto(media=cart.product.image,
                                caption=f"<b>{cart.product.name}</b>\n"
                                        f"{cart.product.price}UAH x {cart.quantity} = {cart_price}UAH\n"
                                        f"Product {paginator.page} out of {paginator.pages}\n"
                                        f"Total Price: {total_price}\n")

        paginations_btns = pages(paginator)
        kbds = get_user_cart(level=level,
                             page=page,
                             pagination_btns=paginations_btns,
                             product_id=cart.product.id)

    return image, kbds

async def get_menu_content(session: AsyncSession,
                           level: int,
                           menu_name: str,
                           category:int | None = None,
                           page:int | None = None,
                           product_id:int | None = None,
                           user_id:int | None = None,):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)