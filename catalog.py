from urllib.parse import quote_plus


CATALOG = {
    "home": [
        {
            "category": "Lighting",
            "name": "LED ceiling light",
            "base": 1800,
            "platform": "Amazon",
            "keywords": "LED ceiling light home",
        },
        {
            "category": "Lighting",
            "name": "Warm table lamp",
            "base": 1200,
            "platform": "IKEA",
            "keywords": "warm table lamp",
        },
        {
            "category": "Furniture",
            "name": "Compact dining table",
            "base": 8500,
            "platform": "IKEA",
            "keywords": "compact dining table",
        },
        {
            "category": "Furniture",
            "name": "Accent lounge chair",
            "base": 6500,
            "platform": "Amazon",
            "keywords": "accent lounge chair",
        },
        {
            "category": "Cooling",
            "name": "Energy-efficient ceiling fan",
            "base": 3200,
            "platform": "Amazon",
            "keywords": "energy efficient ceiling fan",
        },
        {
            "category": "Decor",
            "name": "Minimal wall art set",
            "base": 1600,
            "platform": "Flipkart",
            "keywords": "minimal wall art set",
        },
        {
            "category": "Storage",
            "name": "Modular storage unit",
            "base": 4800,
            "platform": "IKEA",
            "keywords": "modular storage unit",
        },
    ],

    "party": [
        {
            "category": "Catering",
            "name": "Home-style meal package",
            "base": 350,
            "platform": "Swiggy",
            "keywords": "party catering meal package",
        },
        {
            "category": "Catering",
            "name": "Snack and beverage package",
            "base": 180,
            "platform": "Zomato",
            "keywords": "party snacks beverage",
        },
        {
            "category": "Decoration",
            "name": "Balloon and backdrop set",
            "base": 2500,
            "platform": "Amazon",
            "keywords": "party balloon backdrop",
        },
        {
            "category": "Entertainment",
            "name": "Board games/cards bundle",
            "base": 1200,
            "platform": "Amazon",
            "keywords": "board games cards",
        },
        {
            "category": "Entertainment",
            "name": "Small music setup",
            "base": 3000,
            "platform": "Flipkart",
            "keywords": "portable party speaker",
        },
        {
            "category": "Venue",
            "name": "Budget accommodation room",
            "base": 1800,
            "platform": "OYO",
            "keywords": "budget hotel room",
        },
        {
            "category": "Contingency",
            "name": "Unexpected-expense reserve",
            "base": 1000,
            "platform": "PocketSmart",
            "keywords": "party contingency",
        },
    ],

    "jewelry": [
        {
            "category": "Earrings",
            "name": "Minimal drop earrings",
            "base": 900,
            "platform": "Amazon",
            "keywords": "minimal drop earrings",
        },
        {
            "category": "Necklace",
            "name": "Classic pendant necklace",
            "base": 1600,
            "platform": "Flipkart",
            "keywords": "classic pendant necklace",
        },
        {
            "category": "Bracelet",
            "name": "Slim charm bracelet",
            "base": 1200,
            "platform": "Amazon",
            "keywords": "slim charm bracelet",
        },
        {
            "category": "Set",
            "name": "Occasion jewelry set",
            "base": 2800,
            "platform": "Flipkart",
            "keywords": "occasion jewelry set",
        },
        {
            "category": "Earrings",
            "name": "Statement festive earrings",
            "base": 1900,
            "platform": "Amazon",
            "keywords": "statement festive earrings",
        },
    ],
}


def search_url(
    platform: str,
    keywords: str,
) -> str:

    query = quote_plus(keywords)

    urls = {
        "Amazon":
            f"https://www.amazon.in/s?k={query}",

        "Flipkart":
            f"https://www.flipkart.com/search?q={query}",

        "IKEA":
            f"https://www.ikea.com/in/en/search/?q={query}",

        "Swiggy":
            f"https://www.swiggy.com/search?query={query}",

        "Zomato":
            f"https://www.zomato.com/search?query={query}",

        "OYO":
            f"https://www.oyorooms.com/search?location={query}",

        "PocketSmart":
            "#",
    }

    return urls.get(platform, "#")


def fallback_recommendations(
    planner: str,
    budget: float,
    preferences: dict,
):
    catalog = CATALOG[planner]

    if planner == "party":
        guests = max(
            1,
            int(preferences.get("guests", 1)),
        )

        scored = []

        for item in catalog:
            price = item["base"]

            if item["category"] == "Catering":
                price *= guests

            scored.append(
                (
                    item,
                    price,
                )
            )

        chosen = []
        running = 0.0

        for item, raw in scored:
            price = raw

            if item["category"] == "Contingency":
                price = max(
                    0,
                    round(budget * 0.10, 2),
                )

            if running + price <= budget:
                chosen.append(
                    (
                        item,
                        price,
                    )
                )

                running += price

        if not chosen:
            item = catalog[0]

            chosen = [
                (
                    item,
                    min(
                        budget,
                        item["base"] * guests,
                    ),
                )
            ]

    else:
        scored = sorted(
            catalog,
            key=lambda x: x["base"],
        )

        chosen = []
        running = 0.0

        wanted = (
            preferences.get("items", [])
            if planner == "home"
            else []
        )

        for item in scored:
            match = any(
                w.lower() in item["name"].lower()
                or item["category"].lower()
                in w.lower()
                for w in wanted
            )

            if wanted and not match:
                continue

            if running + item["base"] <= budget:
                chosen.append(
                    (
                        item,
                        float(item["base"]),
                    )
                )

                running += item["base"]

        if not chosen:
            for item in scored:
                if (
                    running + item["base"]
                    <= budget
                ):
                    chosen.append(
                        (
                            item,
                            float(item["base"]),
                        )
                    )

                    running += item["base"]

                if len(chosen) >= 4:
                    break

    items = []

    for item, price in chosen:
        items.append(
            {
                "category": item["category"],
                "name": item["name"],
                "description": (
                    f"Budget-aware "
                    f"{item['category'].lower()} "
                    "option for the selected plan."
                ),
                "estimated_price": round(
                    price,
                    2,
                ),
                "quantity": 1,
                "platform": item["platform"],
                "search_url": search_url(
                    item["platform"],
                    item["keywords"],
                ),
                "reason": (
                    "Selected from the built-in "
                    "catalog because it fits "
                    "the available budget."
                ),
            }
        )

    total = round(
        sum(
            item["estimated_price"]
            for item in items
        ),
        2,
    )

    return items, total