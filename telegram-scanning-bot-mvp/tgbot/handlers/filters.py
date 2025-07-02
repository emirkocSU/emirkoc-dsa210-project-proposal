"""
Filter Management Handler for Car Listing Bot.
Handles interactive filter setup and management using inline keyboards.
"""

import logging
import json
from typing import Dict, Any, Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db_manager
from filters.custom_filters import user_is_linked, user_is_subscribed

logger = logging.getLogger(__name__)

# Create router for filter-related handlers
router = Router()

# FSM states for filter management
class FilterStates(StatesGroup):
    waiting_for_input = State()

# Car makes mapping (simplified for MVP)
CAR_MAKES = {
    "toyota": "Toyota",
    "honda": "Honda", 
    "bmw": "BMW",
    "mercedes": "Mercedes-Benz",
    "audi": "Audi",
    "volkswagen": "Volkswagen",
    "ford": "Ford",
    "renault": "Renault",
    "peugeot": "Peugeot",
    "hyundai": "Hyundai",
    "nissan": "Nissan",
    "opel": "Opel",
    "fiat": "Fiat",
    "skoda": "Skoda"
}

# Price ranges
PRICE_RANGES = {
    "0-50000": "Up to 50,000 TL",
    "50000-100000": "50,000 - 100,000 TL",
    "100000-200000": "100,000 - 200,000 TL", 
    "200000-300000": "200,000 - 300,000 TL",
    "300000-500000": "300,000 - 500,000 TL",
    "500000-1000000": "500,000 - 1,000,000 TL",
    "1000000+": "1,000,000+ TL"
}

# Year ranges
YEAR_RANGES = {
    "2020-2024": "2020-2024",
    "2015-2019": "2015-2019",
    "2010-2014": "2010-2014",
    "2005-2009": "2005-2009",
    "2000-2004": "2000-2004"
}

# Cities (major Turkish cities)
CITIES = {
    "istanbul": "Istanbul",
    "ankara": "Ankara",
    "izmir": "Izmir",
    "bursa": "Bursa",
    "antalya": "Antalya",
    "adana": "Adana",
    "konya": "Konya",
    "gaziantep": "Gaziantep",
    "kayseri": "Kayseri",
    "mersin": "Mersin"
}

@router.message(Command("filters"), user_is_linked, user_is_subscribed)
async def cmd_filters(message: Message):
    """Handle /filters command to show filter management interface."""
    user = await db_manager.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("❌ Account not found. Please link your account first.")
        return
    
    # Get current filters
    current_filters = await db_manager.get_user_filters(user.id) or {}
    
    # Create filter management interface
    text, keyboard = create_filter_menu(current_filters)
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

def create_filter_menu(filters: Dict[str, Any]) -> tuple[str, InlineKeyboardMarkup]:
    """Create the main filter menu interface."""
    
    # Format current filter values
    make = filters.get('make', 'Not set')
    model = filters.get('model', 'Not set')
    
    # Format year range
    year_min = filters.get('year_min')
    year_max = filters.get('year_max')
    if year_min and year_max:
        year_range = f"{year_min}-{year_max}"
    elif year_min:
        year_range = f"{year_min}+"
    elif year_max:
        year_range = f"Up to {year_max}"
    else:
        year_range = "Not set"
    
    # Format price range
    price_min = filters.get('price_min')
    price_max = filters.get('price_max')
    if price_min and price_max:
        price_range = f"{price_min:,} - {price_max:,} TL"
    elif price_min:
        price_range = f"{price_min:,}+ TL"
    elif price_max:
        price_range = f"Up to {price_max:,} TL"
    else:
        price_range = "Not set"
    
    city = filters.get('city', 'Not set')
    fuel_type = filters.get('fuel_type', 'Not set')
    transmission = filters.get('transmission', 'Not set')
    
    text = (
        "🔍 <b>Your Car Search Filters</b>\n\n"
        f"🚗 <b>Make:</b> {make}\n"
        f"🏷️ <b>Model:</b> {model}\n"
        f"📅 <b>Year:</b> {year_range}\n"
        f"💰 <b>Price:</b> {price_range}\n"
        f"📍 <b>City:</b> {city}\n"
        f"⛽ <b>Fuel:</b> {fuel_type}\n"
        f"⚙️ <b>Transmission:</b> {transmission}\n\n"
        "Tap any filter to change it:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚗 Change Make", callback_data="filter_make"),
            InlineKeyboardButton(text="🏷️ Change Model", callback_data="filter_model")
        ],
        [
            InlineKeyboardButton(text="📅 Change Year", callback_data="filter_year"),
            InlineKeyboardButton(text="💰 Change Price", callback_data="filter_price")
        ],
        [
            InlineKeyboardButton(text="📍 Change City", callback_data="filter_city"),
            InlineKeyboardButton(text="⛽ Change Fuel", callback_data="filter_fuel")
        ],
        [
            InlineKeyboardButton(text="⚙️ Change Transmission", callback_data="filter_transmission")
        ],
        [
            InlineKeyboardButton(text="✅ Save & Activate", callback_data="filter_save"),
            InlineKeyboardButton(text="🗑️ Clear All", callback_data="filter_clear")
        ]
    ])
    
    return text, keyboard

@router.callback_query(F.data == "filter_make")
async def filter_make_callback(callback_query: CallbackQuery):
    """Handle make filter selection."""
    await callback_query.answer()
    
    # Create make selection keyboard
    keyboard_rows = []
    makes_list = list(CAR_MAKES.items())
    
    # Create rows of 2 buttons each
    for i in range(0, len(makes_list), 2):
        row = []
        for j in range(i, min(i + 2, len(makes_list))):
            make_key, make_name = makes_list[j]
            row.append(InlineKeyboardButton(
                text=make_name,
                callback_data=f"set_make_{make_key}"
            ))
        keyboard_rows.append(row)
    
    # Add back button
    keyboard_rows.append([
        InlineKeyboardButton(text="« Back to Filters", callback_data="filter_back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await callback_query.message.edit_text(
        "🚗 <b>Select Car Make</b>\n\n"
        "Choose the car brand you're interested in:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_make_"))
async def set_make_callback(callback_query: CallbackQuery):
    """Handle setting the car make."""
    await callback_query.answer()
    
    # Extract make from callback data
    make_key = callback_query.data.split("set_make_")[1]
    make_name = CAR_MAKES.get(make_key, make_key)
    
    # Get user and update filters
    user = await db_manager.get_user_by_telegram_id(callback_query.from_user.id)
    if not user:
        await callback_query.message.edit_text("❌ Account not found.")
        return
    
    # Get current filters and update make
    current_filters = await db_manager.get_user_filters(user.id) or {}
    current_filters['make'] = make_key
    # Clear model when make changes
    current_filters['model'] = None
    
    # Save updated filters
    await db_manager.update_user_filters(user.id, current_filters)
    
    # Return to main filter menu
    text, keyboard = create_filter_menu(current_filters)
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "filter_price")
async def filter_price_callback(callback_query: CallbackQuery):
    """Handle price filter selection."""
    await callback_query.answer()
    
    # Create price selection keyboard
    keyboard_rows = []
    
    for price_key, price_name in PRICE_RANGES.items():
        keyboard_rows.append([
            InlineKeyboardButton(
                text=price_name,
                callback_data=f"set_price_{price_key}"
            )
        ])
    
    # Add custom price option
    keyboard_rows.append([
        InlineKeyboardButton(text="✏️ Custom Range", callback_data="custom_price")
    ])
    
    # Add back button
    keyboard_rows.append([
        InlineKeyboardButton(text="« Back to Filters", callback_data="filter_back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await callback_query.message.edit_text(
        "💰 <b>Select Price Range</b>\n\n"
        "Choose your budget range:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_price_"))
async def set_price_callback(callback_query: CallbackQuery):
    """Handle setting the price range."""
    await callback_query.answer()
    
    # Extract price range from callback data
    price_key = callback_query.data.split("set_price_")[1]
    
    # Parse price range
    price_min, price_max = None, None
    if price_key == "1000000+":
        price_min = 1000000
    elif "-" in price_key:
        parts = price_key.split("-")
        price_min = int(parts[0])
        price_max = int(parts[1])
    
    # Get user and update filters
    user = await db_manager.get_user_by_telegram_id(callback_query.from_user.id)
    if not user:
        await callback_query.message.edit_text("❌ Account not found.")
        return
    
    # Get current filters and update price
    current_filters = await db_manager.get_user_filters(user.id) or {}
    current_filters['price_min'] = price_min
    current_filters['price_max'] = price_max
    
    # Save updated filters
    await db_manager.update_user_filters(user.id, current_filters)
    
    # Return to main filter menu
    text, keyboard = create_filter_menu(current_filters)
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "filter_year")
async def filter_year_callback(callback_query: CallbackQuery):
    """Handle year filter selection."""
    await callback_query.answer()
    
    # Create year selection keyboard
    keyboard_rows = []
    
    for year_key, year_name in YEAR_RANGES.items():
        keyboard_rows.append([
            InlineKeyboardButton(
                text=year_name,
                callback_data=f"set_year_{year_key}"
            )
        ])
    
    # Add custom year option
    keyboard_rows.append([
        InlineKeyboardButton(text="✏️ Custom Range", callback_data="custom_year")
    ])
    
    # Add back button
    keyboard_rows.append([
        InlineKeyboardButton(text="« Back to Filters", callback_data="filter_back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await callback_query.message.edit_text(
        "📅 <b>Select Year Range</b>\n\n"
        "Choose the year range for your car:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_year_"))
async def set_year_callback(callback_query: CallbackQuery):
    """Handle setting the year range."""
    await callback_query.answer()
    
    # Extract year range from callback data
    year_key = callback_query.data.split("set_year_")[1]
    
    # Parse year range
    parts = year_key.split("-")
    year_min = int(parts[0])
    year_max = int(parts[1])
    
    # Get user and update filters
    user = await db_manager.get_user_by_telegram_id(callback_query.from_user.id)
    if not user:
        await callback_query.message.edit_text("❌ Account not found.")
        return
    
    # Get current filters and update year
    current_filters = await db_manager.get_user_filters(user.id) or {}
    current_filters['year_min'] = year_min
    current_filters['year_max'] = year_max
    
    # Save updated filters
    await db_manager.update_user_filters(user.id, current_filters)
    
    # Return to main filter menu
    text, keyboard = create_filter_menu(current_filters)
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "filter_city")
async def filter_city_callback(callback_query: CallbackQuery):
    """Handle city filter selection."""
    await callback_query.answer()
    
    # Create city selection keyboard
    keyboard_rows = []
    cities_list = list(CITIES.items())
    
    # Create rows of 2 buttons each
    for i in range(0, len(cities_list), 2):
        row = []
        for j in range(i, min(i + 2, len(cities_list))):
            city_key, city_name = cities_list[j]
            row.append(InlineKeyboardButton(
                text=city_name,
                callback_data=f"set_city_{city_key}"
            ))
        keyboard_rows.append(row)
    
    # Add "All Cities" option
    keyboard_rows.append([
        InlineKeyboardButton(text="🌍 All Cities", callback_data="set_city_all")
    ])
    
    # Add back button
    keyboard_rows.append([
        InlineKeyboardButton(text="« Back to Filters", callback_data="filter_back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await callback_query.message.edit_text(
        "📍 <b>Select City</b>\n\n"
        "Choose the city where you want to search:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_city_"))
async def set_city_callback(callback_query: CallbackQuery):
    """Handle setting the city."""
    await callback_query.answer()
    
    # Extract city from callback data
    city_key = callback_query.data.split("set_city_")[1]
    city_value = None if city_key == "all" else city_key
    
    # Get user and update filters
    user = await db_manager.get_user_by_telegram_id(callback_query.from_user.id)
    if not user:
        await callback_query.message.edit_text("❌ Account not found.")
        return
    
    # Get current filters and update city
    current_filters = await db_manager.get_user_filters(user.id) or {}
    current_filters['city'] = city_value
    
    # Save updated filters
    await db_manager.update_user_filters(user.id, current_filters)
    
    # Return to main filter menu
    text, keyboard = create_filter_menu(current_filters)
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "filter_back")
async def filter_back_callback(callback_query: CallbackQuery):
    """Handle back to filters menu."""
    await callback_query.answer()
    
    # Get user and current filters
    user = await db_manager.get_user_by_telegram_id(callback_query.from_user.id)
    if not user:
        await callback_query.message.edit_text("❌ Account not found.")
        return
    
    current_filters = await db_manager.get_user_filters(user.id) or {}
    text, keyboard = create_filter_menu(current_filters)
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "filter_save")
async def filter_save_callback(callback_query: CallbackQuery):
    """Handle saving and activating filters."""
    await callback_query.answer()
    
    user = await db_manager.get_user_by_telegram_id(callback_query.from_user.id)
    if not user:
        await callback_query.message.edit_text("❌ Account not found.")
        return
    
    current_filters = await db_manager.get_user_filters(user.id) or {}
    
    # Check if at least basic filters are set
    if not current_filters.get('make'):
        await callback_query.message.edit_text(
            "⚠️ <b>Incomplete Filters</b>\n\n"
            "Please set at least the car make before saving.\n\n"
            "Use the buttons below to configure your filters:",
            reply_markup=create_filter_menu(current_filters)[1],
            parse_mode="HTML"
        )
        return
    
    # Filters are valid, activate scanning
    await callback_query.message.edit_text(
        "✅ <b>Filters Saved & Activated!</b>\n\n"
        "Your car search is now active. You'll receive automatic alerts when new cars matching your criteria are found.\n\n"
        "🔍 <b>Search Summary:</b>\n"
        f"• Make: {CAR_MAKES.get(current_filters.get('make', ''), 'Any')}\n"
        f"• Price: {format_price_range(current_filters)}\n"
        f"• Year: {format_year_range(current_filters)}\n"
        f"• City: {CITIES.get(current_filters.get('city', ''), 'All cities')}\n\n"
        "💡 <b>Tips:</b>\n"
        "• Alerts are sent in real-time\n"
        "• Each alert includes damage analysis\n"
        "• Use /filters to modify your search\n\n"
        "<i>Happy car hunting! 🚗</i>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "filter_clear")
async def filter_clear_callback(callback_query: CallbackQuery):
    """Handle clearing all filters."""
    await callback_query.answer()
    
    # Confirmation keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, Clear All", callback_data="confirm_clear"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="filter_back")
        ]
    ])
    
    await callback_query.message.edit_text(
        "⚠️ <b>Clear All Filters</b>\n\n"
        "Are you sure you want to clear all your search filters?\n\n"
        "This will stop all car alerts until you set new filters.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "confirm_clear")
async def confirm_clear_callback(callback_query: CallbackQuery):
    """Handle confirmed filter clearing."""
    await callback_query.answer()
    
    user = await db_manager.get_user_by_telegram_id(callback_query.from_user.id)
    if not user:
        await callback_query.message.edit_text("❌ Account not found.")
        return
    
    # Clear filters
    await db_manager.update_user_filters(user.id, {})
    
    # Show empty filter menu
    text, keyboard = create_filter_menu({})
    
    await callback_query.message.edit_text(
        "🗑️ <b>Filters Cleared</b>\n\n"
        "All your search filters have been cleared.\n"
        "Car alerts are now disabled.\n\n" + text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

def format_price_range(filters: Dict[str, Any]) -> str:
    """Format price range for display."""
    price_min = filters.get('price_min')
    price_max = filters.get('price_max')
    
    if price_min and price_max:
        return f"{price_min:,} - {price_max:,} TL"
    elif price_min:
        return f"{price_min:,}+ TL"
    elif price_max:
        return f"Up to {price_max:,} TL"
    else:
        return "Any price"

def format_year_range(filters: Dict[str, Any]) -> str:
    """Format year range for display."""
    year_min = filters.get('year_min')
    year_max = filters.get('year_max')
    
    if year_min and year_max:
        return f"{year_min}-{year_max}"
    elif year_min:
        return f"{year_min}+"
    elif year_max:
        return f"Up to {year_max}"
    else:
        return "Any year"