from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ["Sport", "Daily"]

page_description = {
    "main": "Welcome to the Sapphire Shop!",
    "about": "We are online shop. We work 24 per 7.",
    "payment": as_marked_section(
        Bold("Payment methods:"),
        "With credit card",
        "After receiving product",
        "At shop",
        marker="✅ ",
    ).as_html(),
    "shipping":as_list(
        as_marked_section(
            Bold("Shipping methods:"),
            "Courier",
            "Will pick up by myself",
            "I just wanna eat here",
            marker="✅ ",
        ),
        as_marked_section(Bold("You can't:"), "By mail", "Other variants", marker="❌ "),
        sep="\n-----------------------------------\n",
    ).as_html(),
    "catalog":"Available categories: ",
    "cart": "You haven't chosen anything yet!"
}