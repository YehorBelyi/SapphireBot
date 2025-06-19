from idlelib.undo import Command

from aiogram.fsm.state import StatesGroup, State
from database.orm_query import orm_get_order_history, orm_add_order_to_history, orm_get_user_carts, orm_flush_cart
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import CallbackQuery, PreCheckoutQuery, SuccessfulPayment, LabeledPrice
from aiogram import F, Router, Bot
from aiogram.types import Message
import os
import dotenv
import asyncio

payment_router = Router()
payment_timers = {}

class PaymentProcessing(StatesGroup):
    process_payment = State()

@payment_router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message="Something went wrong")

@payment_router.message(F.successful_payment)
async def success(message: Message, session: AsyncSession):
    task = payment_timers.pop(message.chat.id, None)
    if task:
        task.cancel()
        user_orders = await orm_get_user_carts(session, message.from_user.id)
        print(user_orders)
        await orm_add_order_to_history(session=session, user_id=message.from_user.id, user_orders=user_orders)
        await message.answer("✅ Thanks! Your products have been added to your order history.")
        await orm_flush_cart(session=session, user_id=message.from_user.id)

async def process_payment(session: AsyncSession, user_id: int, callback: CallbackQuery):
    chat_id = callback.message.chat.id

    user_orders = await orm_get_user_carts(session, user_id)

    await callback.message.delete()
    payment_message = await callback.message.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"SapphirePayment",
        description=f"️⭐ You have 5 minutes to complete your payment. Keep in mind that once the timer runs out, your payment will be canceled!",
        payload="product_payload",
        provider_token=os.getenv("PAYMENT_TOKEN"),
        currency=os.getenv("CURRENCY"),
        prices=[LabeledPrice(label="Pay", amount=sum(item["price"]*item["quantity"] for item in user_orders)*100)])

    task = asyncio.create_task(timer(chat_id=chat_id, bot=callback.bot, payment_message_id=payment_message.message_id))
    payment_timers[chat_id] = task

async def timer(chat_id:int, bot: Bot, payment_message_id: int):
    try:
        await asyncio.sleep(300)
        await bot.delete_message(chat_id=chat_id, message_id=payment_message_id)
        await bot.send_message(chat_id, "❌ Your 5 minutes have run out! The payment has been canceled. Try again later.")
        payment_timers.pop(chat_id, None)
    except asyncio.CancelledError:
        print("Timer is out")
        pass