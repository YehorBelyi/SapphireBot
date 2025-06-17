async def process_payment(callback_action):
    await callback_action.message.answer("order")
    await callback_action.message.delete()