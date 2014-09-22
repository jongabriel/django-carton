
'''
Base class for the cart items.
'''
class Product(object):
    def __init__(self, pk, name = None, price = None):
        #self.custom_id = custom_id #TODO how is this different from pk?
        self.pk = pk
        self.name = name
        self.price = price

    def __unicode__(self):
        return self.name
