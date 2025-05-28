from aiogram.types import InputMediaPhoto
from database.orm_query import orm_get_banner, orm_get_categories, orm_get_products, Paginator
from keyboards.inline import get_user_main_btns, get_user_catalog_btns, get_products_btns
from sqlalchemy.ext.asyncio import AsyncSession

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

async def get_menu_content(session: AsyncSession,
                           level: int,
                           menu_name: str,
                           category:int | None = None,
                           page:int | None = None,):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)