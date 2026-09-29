import re
from datetime import date, timedelta


GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "greetings",
    "sousdey",
    "suosdey",
}


THANKS = {
    "thank",
    "thanks",
    "thank you",
    "thankyou",
    "many thanks",
    "ok thanks",
    "okay thanks",
    "appreciate it",
}


FAREWELLS = {
    "bye",
    "goodbye",
    "see you",
    "see you soon",
    "good night",
}


ROOM_RATES = {
    "low": {
        "label": "Low season",
        "full_khmer_house": 300,
        "suite_double": 120,
        "twin_garden": 100,
        "bungalow_family": 100,
    },
    "high": {
        "label": "High season",
        "full_khmer_house": 350,
        "suite_double": 135,
        "twin_garden": 120,
        "bungalow_family": 125,
    },
}

PEAK_SUPPLEMENTS = {
    "full_khmer_house": 30,
    "suite_double": 15,
    "twin_garden": 15,
    "bungalow_family": 15,
}

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


DIRECT_CONTACT_ANSWER = (
    "For the fastest confirmation, please contact Secret Lake House directly:\n"
    "- Phone: +855 902 986 87\n"
    "- WhatsApp: +855 11 969 568\n"
    "- Telegram: @secretlakehousekampot\n"
    "- Email: info@secretlakehouse.com"
)


KNOWLEDGE_BASE = [
    {
        "name": "room rates",
        "keywords": [
            "walk",
            "walk-in",
            "walking",
            "online booking",
            "online price",
            "price",
            "prices",
            "rate",
            "rates",
            "cost",
            "how much",
            "room price",
            "room prices",
            "accommodation price",
            "suite price",
            "bungalow price",
            "extra bed",
            "expensive",
            "costly",
            "cheap",
            "cheaper",
            "low season",
            "high season",
            "season",
            "peak season",
        ],
        "answer": "Room prices are shown by season.",
    },
    {
        "name": "rooms",
        "keywords": [
            "room",
            "rooms",
            "stay",
            "accommodation",
            "sleep",
            "bed",
            "beds",
            "suite",
            "khmer house",
            "bungalow",
            "family room",
            "friend room",
            "twin",
            "double",
            "garden view",
            "how many people",
            "capacity",
            "occupancy",
        ],
        "answer": (
            "Secret Lake House has four rooms in total:\n"
            "- Khmer House: two Suite Double rooms upstairs and one Twin Garden View room downstairs\n"
            "- Bungalow Family Room: one king size bed plus one bunk bed, suitable for up to 4 guests\n"
            "- Bungalow Friend Room: two bunk beds for friends or small groups\n"
            "Only Suite rooms can add an extra bed or extra person, subject to availability."
        ),
    },
    {
        "name": "booking",
        "keywords": [
            "book",
            "booking",
            "reserve",
            "reservation",
            "availability",
            "available",
            "confirm",
            "confirmation",
            "direct booking",
            "dates",
            "tonight",
            "tomorrow",
            "this weekend",
            "next week",
            "deposit",
        ],
        "answer": (
            "Bookings are confirmed only after Secret Lake House accepts the request through an official "
            "channel and any required deposit or full payment is received. Please send your dates, guest "
            "count, preferred room or dining hut, and contact details through the Contact or Booking page, "
            "or message us on WhatsApp or Telegram for the fastest reply."
        ),
    },
    {
        "name": "direct booking benefits",
        "keywords": [
            "best rate",
            "direct",
            "book direct",
            "welcome cocktail",
            "cocktail",
            "commission",
            "benefit",
            "promotion",
            "offer",
        ],
        "answer": (
            "When guests book direct with Secret Lake House, they can speak with our team before arrival "
            "and receive a complimentary signature welcome cocktail. Direct booking also helps avoid "
            "third-party confusion, especially for room details, dinner reservations, and arrival timing."
        ),
    },
    {
        "name": "restaurant",
        "keywords": [
            "restaurant",
            "food",
            "foods",
            "menu",
            "khmer food",
            "western food",
            "vegan",
            "vegetarian",
            "drink",
            "drinks",
            "bar",
            "coffee",
            "breakfast",
            "lunch",
            "dinner",
            "cocktail",
            "pepper",
            "food price",
            "drink price",
            "eat",
            "dining",
        ],
        "answer": (
            "Our restaurant is beside the swimming pool on the lake bank. We serve Khmer comfort dishes, "
            "Western choices, drinks, vegan options, and Kampot pepper flavors. For exact food and drink "
            "prices, visitors can open the quick-loading Full Food Menu, Khmer Food Menu, and Vegan Food "
            "Menu on the Dining page. Dinner is available by advance booking only."
        ),
    },
    {
        "name": "dietary needs",
        "keywords": [
            "vegan",
            "vegetarian",
            "allergy",
            "allergic",
            "gluten",
            "halal",
            "no pork",
            "spicy",
            "not spicy",
            "diet",
            "special food",
            "kids meal",
        ],
        "answer": (
            "We have vegan and vegetarian menu options and can try to help with dietary requests when "
            "we know in advance. Please tell the team about allergies, no-pork requests, spice level, "
            "children's meals, or other food needs before arriving so the kitchen can advise properly."
        ),
    },
    {
        "name": "dining huts",
        "keywords": [
            "hut",
            "huts",
            "table",
            "pavilion",
            "bamboo",
            "bamboo hut",
            "dining hut",
            "poolside table",
            "lake view table",
            "reserve table",
            "reservation",
            "water",
            "overwater",
            "sunset dinner",
        ],
        "answer": (
            "You can reserve a poolside restaurant table, one of three wooden huts with grass roofs over "
            "the water, the Bamboo Hut, or a lake-view table. A small 1.2m-wide bridge leads from the "
            "poolside restaurant area toward the overwater wooden huts. Dinner and special tables are best "
            "reserved in advance."
        ),
    },
    {
        "name": "hours",
        "keywords": [
            "open",
            "opening",
            "hour",
            "hours",
            "time",
            "close",
            "closing",
            "when open",
            "dinner time",
            "lunch time",
            "breakfast time",
        ],
        "answer": (
            "Secret Lake House is open daily from 7:00am to 9:00pm. Dinner is accepted by advance "
            "booking only, so it is best to reserve before arriving."
        ),
    },
    {
        "name": "check in out",
        "keywords": [
            "check in",
            "check-in",
            "check out",
            "check-out",
            "arrival",
            "early arrival",
            "early check",
            "late checkout",
            "late check-out",
            "leave room",
            "noon",
        ],
        "answer": (
            "Standard check-in is 2:00pm and standard check-out is 12:00 noon. Early check-in from "
            "6:00am to 2:00pm or late check-out from noon to 6:00pm may be charged up to 50% of the "
            "room rate, subject to availability. Very early arrival or very late departure may require "
            "a full-night charge."
        ),
    },
    {
        "name": "children",
        "keywords": [
            "child",
            "children",
            "kid",
            "kids",
            "baby",
            "infant",
            "family",
            "extra person",
            "extra child",
            "cot",
            "breakfast child",
        ],
        "answer": (
            "Families are welcome. Infants aged 0-4 can usually stay free when sharing existing bedding "
            "with parents. Children aged 5-11 may have a child breakfast or lodging supplement when "
            "applicable. Guests aged 12 and above are normally treated as adults for extra person or "
            "extra bed charges. Please confirm family details before booking."
        ),
    },
    {
        "name": "cancellation",
        "keywords": [
            "cancel",
            "cancellation",
            "refund",
            "change booking",
            "amend",
            "amendment",
            "no show",
            "no-show",
            "shortened stay",
            "early departure",
            "minimum stay",
        ],
        "answer": (
            "Cancellation terms depend on season and booking type. Low season usually allows free "
            "cancellation 14 days or more before arrival; high season usually requires 21 days or more. "
            "Peak periods and special bookings may require longer notice or a 2-night minimum stay. "
            "No-shows, early departures, and shortened stays may still be charged. The team will confirm "
            "the exact terms with your booking."
        ),
    },
    {
        "name": "payment",
        "keywords": [
            "pay",
            "payment",
            "deposit",
            "cash",
            "bank",
            "bank transfer",
            "aba",
            "credit card",
            "invoice",
            "settle",
        ],
        "answer": (
            "Secret Lake House may request a deposit or full payment before arrival, especially for "
            "advance or last-minute bookings. Payment can be confirmed directly with the team and may "
            "include cash, bank transfer, or another approved method. Please do not send payment until "
            "the team confirms the correct booking and payment details."
        ),
    },
    {
        "name": "location",
        "keywords": [
            "where",
            "location",
            "map",
            "road",
            "drive",
            "direction",
            "directions",
            "address",
            "how to get",
            "kampot",
            "secret lake",
            "road 1331",
            "kaunsat",
            "toek chhou",
            "la plantation",
            "bo tree",
            "starling",
            "sindora",
            "pepperhill",
        ],
        "answer": (
            "Secret Lake House is on Road 1331 at Secret Lake, Kaunsat Village, Toek Chhou District, "
            "Kampot, Cambodia. We are around 12km from Kampot, on the route to La Plantation and Bo "
            "Tree Farm. Use the Google Maps button on the Contact page for live directions."
        ),
    },
    {
        "name": "transport",
        "keywords": [
            "transport",
            "transfer",
            "pickup",
            "pick up",
            "taxi",
            "tuk tuk",
            "tuktuk",
            "driver",
            "parking",
            "motorbike",
            "bicycle",
            "road condition",
        ],
        "answer": (
            "Guests can drive, come by motorbike, arrange a tuk-tuk or taxi, or ask us for local arrival "
            "guidance before leaving Kampot. Please message the team for current road updates, parking "
            "details, or help coordinating transport."
        ),
    },
    {
        "name": "pool",
        "keywords": [
            "pool",
            "swim",
            "swimming",
            "lake",
            "day pass",
            "day visit",
            "deck",
            "sunbed",
            "lounge",
            "relax",
            "waterfront",
        ],
        "answer": (
            "The swimming pool sits on the lake bank with mountain and water views. Visitors can enjoy "
            "the poolside restaurant, garden, deck, and lake atmosphere. Please contact us first for "
            "current day-visit details, pool use, and table availability."
        ),
    },
    {
        "name": "experiences",
        "keywords": [
            "experience",
            "activity",
            "activities",
            "tour",
            "bike",
            "bicycle",
            "motorbike",
            "pepper trail",
            "pepper farm",
            "pepper plantation",
            "rice",
            "rice field",
            "countryside",
            "sunset",
            "photo",
            "view",
            "rural",
        ],
        "answer": (
            "Secret Lake House is a natural base for the Kampot pepper trail, countryside roads, rice "
            "fields, Secret Lake views, pool days, and slow rural exploration by bicycle or motorbike. "
            "Guests can visit nearby pepper farms, return to the lakefront deck, and enjoy regional "
            "dishes with Kampot pepper flavors."
        ),
    },
    {
        "name": "about hospitality",
        "keywords": [
            "story",
            "hospitality",
            "service",
            "services",
            "team",
            "staff",
            "local",
            "khmer",
            "slow down",
            "connect",
            "quality",
            "ingredient",
        ],
        "answer": (
            "Secret Lake House is a boutique lakeside accommodation and restaurant built around calm "
            "hospitality, local character, and honest food. It is a place to slow down, connect, enjoy "
            "good dishes and drinks, and experience Secret Lake, Kampot pepper country, gardens, poolside "
            "dining, and warm Khmer service."
        ),
    },
    {
        "name": "special occasions",
        "keywords": [
            "birthday",
            "anniversary",
            "celebration",
            "honeymoon",
            "romantic",
            "private dinner",
            "group",
            "event",
            "surprise",
            "cake",
        ],
        "answer": (
            "For birthdays, anniversaries, small groups, romantic meals, or special surprises, please "
            "contact Secret Lake House in advance. The team can advise on suitable tables, huts, timing, "
            "food, drinks, and what is possible for your date."
        ),
    },
    {
        "name": "accessibility",
        "keywords": [
            "access",
            "accessibility",
            "wheelchair",
            "elderly",
            "stairs",
            "step",
            "mobility",
            "bridge",
            "safe",
            "safety",
        ],
        "answer": (
            "Please message us before arrival if a guest has mobility needs, elderly guests, young "
            "children, or safety concerns. Some rooms and dining areas involve stairs, garden paths, "
            "or a 1.2m-wide bridge toward the overwater huts, so the team can advise the best option."
        ),
    },
    {
        "name": "contact",
        "keywords": [
            "phone",
            "whatsapp",
            "telegram",
            "contact",
            "email",
            "call",
            "message",
            "social",
            "facebook",
            "instagram",
            "youtube",
            "tiktok",
            "reel",
            "video",
        ],
        "answer": DIRECT_CONTACT_ANSWER,
    },
    {
        "name": "privacy",
        "keywords": [
            "privacy",
            "personal information",
            "data",
            "information",
            "details",
            "guest details",
        ],
        "answer": (
            "Secret Lake House uses guest details to answer enquiries, confirm bookings, prepare stays "
            "or dining reservations, and share important updates. Guest information is not sold. For "
            "privacy questions, email info@secretlakehouse.com or message WhatsApp +855 11 969 568."
        ),
    },
]


def normalize(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def clean_words(text):
    return normalize(re.sub(r"[^a-zA-Z0-9\s$+-]", " ", text))


def is_phrase_match(message, phrases):
    clean = clean_words(message)
    return clean in phrases or any(phrase in clean for phrase in phrases)


def is_exact_phrase_match(message, phrases):
    clean = clean_words(message)
    return any(re.search(rf"\b{re.escape(phrase)}\b", clean) for phrase in phrases)


def is_greeting(message):
    clean = clean_words(message)
    return clean in GREETINGS or any(clean.startswith(f"{greeting} ") for greeting in GREETINGS)


def is_thanks(message):
    return is_phrase_match(message, THANKS)


def is_farewell(message):
    return is_exact_phrase_match(message, FAREWELLS)


def get_conversation_reply(message):
    clean = clean_words(message)
    if not clean:
        return None

    if any(phrase in clean for phrase in ["how are you", "how are u", "how do you do", "are you ok", "are you okay"]):
        return (
            "I am doing well, thank you for asking. I am here and ready to help with Secret Lake House. "
            "Are you looking for rooms, food, pool, or directions?"
        )

    if any(phrase in clean for phrase in ["how old are you", "your age", "what age are you", "age are you"]):
        return (
            "I do not really have an age like a person. I am the Secret Lake House Admin helper, "
            "here to answer simple questions about rooms, food, drinks, the pool, and directions."
        )

    if any(phrase in clean for phrase in ["what is your name", "who are you", "your name", "are you admin"]):
        return (
            "I am Secret Lake House Admin, a small chat helper for our guests. "
            "You can ask me about rooms, prices, food, drinks, opening hours, and how to find us."
        )

    booking_phrases = [
        "how can book your room",
        "how can i book your room",
        "how can we book your room",
        "how to book your room",
        "how do i book your room",
        "how do we book your room",
        "can i book a room",
        "can we book a room",
        "book your room",
        "book a room",
        "reserve a room",
        "room booking",
        "make a booking",
        "make reservation",
        "make a reservation",
    ]
    if any(phrase in clean for phrase in booking_phrases):
        return (
            "Yes, you can book a room directly with Secret Lake House. "
            "Please send your stay date, number of guests, preferred room, and your phone, WhatsApp, Telegram, or email. "
            "You can use the Contact or Booking page, or message us on WhatsApp +855 11 969 568, Telegram @secretlakehousekampot, "
            "or phone +855 902 986 87. The room is confirmed after our team checks availability and confirms the booking."
        )

    menu_phrases = [
        "see your menu",
        "see the menu",
        "view your menu",
        "view the menu",
        "show me menu",
        "show me the menu",
        "open menu",
        "send menu",
        "food menu",
        "drink menu",
        "can i see your menu",
        "can we see your menu",
        "do you have menu",
    ]
    if any(phrase in clean for phrase in menu_phrases):
        return (
            "Yes, of course. You can see our menus on the Dining page. "
            "There are quick-loading menus for the full food menu, Khmer food, and vegan food. "
            "We serve Khmer dishes, Western choices, drinks, coffee, cocktails, and Kampot pepper flavors."
        )

    restaurant_location_phrases = [
        "where is your restaurant",
        "where is the restaurant",
        "restaurant location",
        "restaurant address",
        "where can we eat",
        "where can i eat",
    ]
    if any(phrase in clean for phrase in restaurant_location_phrases):
        return (
            "Our restaurant is at Secret Lake House, beside the swimming pool on the lake bank. "
            "We are on Road 1331 at Secret Lake, about 12km from Kampot, on the way to La Plantation and Bo Tree Farm."
        )

    location_phrases = [
        "where are you",
        "where is secret lake house",
        "where is your place",
        "your location",
        "your address",
        "send location",
        "share location",
    ]
    if any(phrase in clean for phrase in location_phrases):
        return (
            "We are at Secret Lake House on Road 1331, Secret Lake, Kaunsat Village, Toek Chhou District, Kampot. "
            "It is about 12km from Kampot. You can use the Google Maps button on the Contact page for live directions."
        )

    return None


def season_from_month_day(month, day):
    if month == 12 and day >= 20:
        return "peak"
    if month == 1 and day <= 4:
        return "peak"
    if month > 10 or month < 4:
        return "high"
    if month == 10 and day >= 15:
        return "high"
    if month == 4 and day < 1:
        return "high"
    return "low"


def extract_month_day(message):
    clean = clean_words(message)
    for name, month in MONTHS.items():
        match = re.search(rf"\b{name}\s+(\d{{1,2}})(?:st|nd|rd|th)?\b", clean)
        if match:
            return month, int(match.group(1))
        match = re.search(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{name}\b", clean)
        if match:
            return month, int(match.group(1))

    match = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-]\d{2,4})?\b", clean)
    if match:
        first = int(match.group(1))
        second = int(match.group(2))
        if first > 12:
            return second, first
        return first, second

    return None


def detect_rate_season(message):
    clean = clean_words(message)
    if any(word in clean for word in ["peak", "festival", "khmer new year", "chinese new year", "pchumben", "pchum ben", "water festival"]):
        return "peak"
    if "high season" in clean:
        return "high"
    if "low season" in clean:
        return "low"
    if "today" in clean:
        today = date.today()
        return season_from_month_day(today.month, today.day)
    if "tomorrow" in clean:
        tomorrow = date.today() + timedelta(days=1)
        return season_from_month_day(tomorrow.month, tomorrow.day)

    month_day = extract_month_day(clean)
    if month_day:
        return season_from_month_day(*month_day)
    return "all"


def asks_for_season_details(message):
    clean = clean_words(message)
    return any(
        phrase in clean
        for phrase in [
            "high season",
            "low season",
            "peak season",
            "season detail",
            "season details",
            "which season",
            "what season",
            "expensive",
            "too expensive",
            "why expensive",
            "why so expensive",
            "costly",
            "cheap",
            "cheaper",
        ]
    )


def format_rate_list(season_key, peak=False, show_season=False):
    rates = ROOM_RATES["high" if peak else season_key]
    full_khmer_house = rates["full_khmer_house"]
    suite_double = rates["suite_double"]
    twin_garden = rates["twin_garden"]
    bungalow_family = rates["bungalow_family"]

    if peak:
        full_khmer_house += PEAK_SUPPLEMENTS["full_khmer_house"]
        suite_double += PEAK_SUPPLEMENTS["suite_double"]
        twin_garden += PEAK_SUPPLEMENTS["twin_garden"]
        bungalow_family += PEAK_SUPPLEMENTS["bungalow_family"]

    heading = "Walk-in and online room prices:"
    if show_season:
        heading = ("Peak season" if peak else rates["label"]) + " walk-in and online room prices:"

    return (
        f"{heading}\n"
        f"- Full Khmer House: ${full_khmer_house}\n"
        f"- Khmer House Suite Double: ${suite_double}\n"
        f"- Khmer House Twin Garden View: ${twin_garden}\n"
        f"- Bungalow Family Room: ${bungalow_family}\n"
        "- Extra bed for Suite rooms: $25 per night"
    )


def get_room_rate_answer(message):
    season = detect_rate_season(message)
    show_season = asks_for_season_details(message)
    if season == "low":
        return format_rate_list("low", show_season=show_season)
    if season == "high":
        return format_rate_list("high", show_season=show_season)
    if season == "peak":
        return format_rate_list("high", peak=True, show_season=show_season)
    if show_season:
        return (
            "Prices can change between low season, high season, and special holiday periods. "
            "Please tell me when you are planning to stay, and I can show the correct room prices for that time."
        )
    return (
        "May I know when you are planning to stay? Room prices depend on the stay date, "
        "and I can show the correct walk-in and online prices once I know your planned date."
    )


def looks_like_stay_date_reply(message):
    clean = clean_words(message)
    if not clean:
        return False
    if clean in {"today", "tomorrow", "tonight"}:
        return True
    return extract_month_day(clean) is not None


def score_topic(message, topic):
    clean = clean_words(message)
    tokens = set(clean.split())
    score = 0
    for keyword in topic["keywords"]:
        if (" " in keyword and keyword in clean) or keyword in tokens:
            score += 2 if " " in keyword else 1
    return score


def get_bot_response(message):
    clean = normalize(message)
    if re.search(r"\b(map|maps|directions?|location|address)\b|\bhow (?:can i |do i |to )(?:get|go|come|drive|reach)\b|\bwhere (?:are you|is (?:your|the) (?:restaurant|hotel)|is secret lake house)\b", clean):
        return {
            "answer": "Here is the Google Maps location for Secret Lake House, Road 1331, Secret Lake, Kampot. Open the map and tap Directions to plan your journey.\nhttps://maps.app.goo.gl/HqZ7ZgmsNyLfpesu6",
            "needs_follow_up": False,
        }
    if not clean:
        return {
            "answer": "Hi there. I am happy to help. Are you looking for rooms, food, pool, or directions?",
            "needs_follow_up": False,
        }

    conversation_reply = get_conversation_reply(clean)
    if conversation_reply:
        return {"answer": conversation_reply, "needs_follow_up": False}

    if is_greeting(clean):
        return {
            "answer": "Hi there. Welcome to Secret Lake House. I am happy to help. Are you looking for rooms, food, pool, directions, or a booking?",
            "needs_follow_up": False,
        }

    if is_thanks(clean):
        return {
            "answer": "You are most welcome. Please let me know if you would like help with rooms, food and drinks, directions, or booking details.",
            "needs_follow_up": False,
        }

    if is_farewell(clean):
        return {
            "answer": "Goodbye, and thank you for contacting Secret Lake House. We hope to welcome you by the lake soon.",
            "needs_follow_up": False,
        }

    if looks_like_stay_date_reply(clean):
        return {"answer": get_room_rate_answer(clean), "needs_follow_up": False}

    ranked = sorted(
        ((score_topic(clean, topic), topic) for topic in KNOWLEDGE_BASE),
        key=lambda item: item[0],
        reverse=True,
    )
    best_score, best_topic = ranked[0]

    if best_score > 0:
        if best_topic["name"] == "room rates":
            return {"answer": get_room_rate_answer(clean), "needs_follow_up": False}
        return {"answer": best_topic["answer"], "needs_follow_up": False}

    return {
        "answer": (
            "I may not know that yet, but I can still help with rooms, prices, food and drinks, dining huts, "
            "pool visits, opening hours, directions, bookings, children, and special occasions. "
            "You can ask me in a simple way, like: room price, menu, location, or opening hours."
        ),
        "needs_follow_up": False,
    }
