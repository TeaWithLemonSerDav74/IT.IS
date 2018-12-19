class Cart:
    goods = None
    creation_date = None
    payment_date = None  # date string if paid, None otherwise

    def __init__(self, creation_date):
        self.creation_date = creation_date
        self.goods = []
        self.payment_date = None

    def add(self, item) -> None:
        if self.payment_date:
            raise ValueError("Inserting items in a paid cart is forbidden!")
        else:
            self.goods.append(item)

    def __str__(self):
        return ' '.join(self.goods)

    def __repr__(self):
        return str(self)
