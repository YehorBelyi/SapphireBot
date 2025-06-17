from database.orm_query import orm_get_order_history, orm_add_order_to_history, orm_get_user_carts, orm_flush_cart
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import CallbackQuery, PreCheckoutQuery, SuccessfulPayment, LabeledPrice
from aiogram import F, Router
from aiogram.types import Message
import os
import dotenv

payment_router = Router()
user_orders = []

@payment_router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message="Something went wrong")

@payment_router.message(F.successful_payment)
async def success(message: Message, session: AsyncSession):
    await orm_add_order_to_history(session, user_orders)
    await message.answer("Дякуємо! Придбання додано до історії ваших замовлень :)")
    user_orders.clear()
    await orm_flush_cart(session=session, user_id=message.chat.id)

async def process_payment(session: AsyncSession, user_id: int, callback_action: CallbackQuery):
    user_orders.clear()
    user_orders.extend(await orm_get_user_carts(session, user_id))
    print(user_orders)

    await callback_action.message.delete()
    await callback_action.message.bot.send_invoice(
        chat_id=callback_action.message.chat.id,
        title=f"payment test",
        description=f"Якщо все влаштовує, перейдіть до оплати замовлення будь-ласка!",
        payload="product_payload",
        provider_token=os.getenv("PAYMENT_TOKEN"),
        currency=os.getenv("CURRENCY"),
        prices=[LabeledPrice(label="Оплата", amount=sum(item.product.price*item.quantity for item in user_orders)*100)])