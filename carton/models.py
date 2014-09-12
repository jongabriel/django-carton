
'''
Base class for the cart items.
'''
class Product(object):
    def __init__(self, custom_id, name, price):
        self.custom_id = custom_id
        self.pk = custom_id
        self.name = name
        self.price = price

    def __unicode__(self):
        return self.name
