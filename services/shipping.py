


def get_shipping_cost(warehouse: Warehouse, zipcode: Zipcode) -> int:
    region = "Malmö" if zipcode in Zipcode else "Other"  # Simplified
    return SHIPPING_RULES.get((warehouse, region), 800)  # Default 800 SEK