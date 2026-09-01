def calculate_discount(revenue):
    if revenue > 10000:
        return revenue * 0.1
    if revenue > 5000:
        return revenue * 0.05
    if revenue > 1000:
        return revenue * 0.02
    return 0

