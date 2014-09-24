from decimal import Decimal

from django.conf import settings

from carton import module_loading
from carton import settings as carton_settings
from .utils import CartException, get_object

import pickle

class CartItem(object):
    """
    A cart item, with the associated product, its quantity and its price.
    """
    def __init__(self, product, quantity, price_pretax, tax = 0.0):
        # set _product if we have a real model 
        self.product = product            
        self.pk = product.pk
        self.quantity = int(quantity)
        self.price_pretax = Decimal(str(price_pretax))
        self.tax = Decimal(str(tax))
        self.fields = {}
        self.attrs = {}
        for key in carton_settings.CART_STORED_FIELD:
            try:
                self.set_field(key,product.__dict__[key])
            except KeyError:
                # raise error if field is missing from model, otherwise it will be fetched when demand is present
                raise CartException("Stored field %s not found on model" % key)
        # read any additional attributes from the dict
#         if 'carton_attrs' in product:
#             self.attrs = product['carton_attrs']
        #import ipdb; ipdb.set_trace()

    def set_field(self,key,value):
        if key not in carton_settings.CART_STORED_FIELD:
            raise CartException("Tried to set field %s which is not configured as a stored field" % key)
        self.fields[key] = value
    def get_field(self,key):
        if key not in carton_settings.CART_STORED_FIELD:
            raise CartException("Tried to get field %s which is not configured as a stored field" % key)
        # if we have a db object open, then return that - if field isn't stored then fetch it
        if not key in self.fields or self.product is not None:
            self.fields[key] = self.product.__dict__[key]
        return self.fields[key]
        
    def __repr__(self):
        return u'CartItem Object (%s)' % self.product

    @property
    def subtotal(self):
        """
        Subtotal for the cart item.
        """
        return (self.price_pretax + self.tax) * self.quantity
    
    @property
    def subtotal_pretax(self):
        """
        Subtotal for the cart item, pretax.
        """
        return self.price_pretax * self.quantity


class Cart(object):

    """
    A cart that lives in the session.
    """
    def __init__(self, session, session_key=None):
        self._items_dict = {}
        self.session = session
        self.session_key = session_key or carton_settings.CART_SESSION_KEY
            # If a cart representation was previously stored in session, then we
        if self.session_key in self.session:
            # rebuild the cart object from that serialized representation.
            cart_representation = self.session[self.session_key]
            #ids_in_cart = cart_representation.keys()
            #products_queryset = self.get_queryset().filter(pk__in=ids_in_cart)
            for pk,item in cart_representation.iteritems():
                item_from_json = get_object( item )
                self._items_dict[pk] = item_from_json

    def __contains__(self, product):
        """
        Checks if the given product is in the cart.
        """
        return product in self.products

    def get_product_model(self):
        return module_loading.get_product_model()

    def filter_products(self, queryset):
        """
        Applies lookup parameters defined in settings.
        """
        lookup_parameters = getattr(settings, 'CART_PRODUCT_LOOKUP', None)
        if lookup_parameters:
            queryset = queryset.filter(**lookup_parameters)
        return queryset

    def get_queryset(self):
        product_model = self.get_product_model()
        queryset = product_model._default_manager.all()
        queryset = self.filter_products(queryset)
        return queryset

    def update_session(self):
        """
        Serializes the cart data, saves it to session and marks session as modified.
        """
        self.session[self.session_key] = self.cart_serializable
        self.session.modified = True

    def change_price(self, product, price=None, quantity=1):
        """
        Changes the price of a product in the cart. If the 
        product isn't in the cart, the new price is ignored.
        """
        quantity = int(quantity)
        if price == None:
            raise ValueError('Missing price when adding to cart')
        if product.pk in self._items_dict:
            old_prod = self._items_dict[product.pk]
            self.remove(old_prod)
            new_prod = CartItem( old_prod.product, old_prod.quantity, price, old_prod.tax )
            self._items_dict[product.pk] = new_prod
        self.update_session()
        
    def add_tax(self, product, tax = None):
        """
        Add a tax amount to a product. This will
        affect the total price for the product.
        """
        if tax == None:
            raise ValueError('Missing tax in add_tax')
        if product.pk in self._items_dict:
            prod = self._items_dict[product.pk]
            prod.tax = Decimal(str(tax))
        self.update_session()

    def add(self, product, price=None, quantity=1):
        """
        Adds or creates products in cart. For an existing product,
        the quantity is increased and the price is ignored.
        """
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError('Quantity must be at least 1 when adding to cart')
        if product.pk in self._items_dict:
            self._items_dict[product.pk].quantity += quantity
        else:
            if price == None:
                raise ValueError('Missing price when adding to cart')
            self._items_dict[product.pk] = CartItem(product, quantity, price)
        self.update_session()

    def remove(self, product):
        """
        Removes the product.
        """
        if product.pk in self._items_dict:
            del self._items_dict[product.pk]
            self.update_session()

    def remove_single(self, product):
        """
        Removes a single product by decreasing the quantity.
        """
        if product.pk in self._items_dict:
            if self._items_dict[product.pk].quantity <= 1:
                # There's only 1 product left so we drop it
                del self._items_dict[product.pk]
            else:
                self._items_dict[product.pk].quantity -= 1
            self.update_session()

    def clear(self):
        """
        Removes all items.
        """
        self._items_dict = {}
        self.update_session()

    def set_quantity(self, product, quantity):
        """
        Sets the product's quantity.
        """
        quantity = int(quantity)
        if quantity < 0:
            raise ValueError('Quantity must be positive when updating cart')
        if product.pk in self._items_dict:
            self._items_dict[product.pk].quantity = quantity
            if self._items_dict[product.pk].quantity < 1:
                del self._items_dict[product.pk]
            self.update_session()

    @property
    def items(self):
        """
        The list of cart items.
        """
        return self._items_dict.values()

    @property
    def cart_serializable(self):
        """
        The serializable representation of the cart.
        For instance:
        {
            '1': {'pk': 1, 'quantity': 2, price: '9.99'},
            '2': {'pk': 2, 'quantity': 3, price: '29.99'},
        }
        Note how the product pk servers as the dictionary key.
        """
        cart_representation = {}
        for item in self.items:
            product_id = int(item.product.pk)
            cart_representation[product_id] = pickle.dumps(item)
        return cart_representation


    @property
    def items_serializable(self):
        """
        The list of items formatted for serialization.
        """
        return self.cart_serializable.items()

    @property
    def count(self):
        """
        The number of items in cart, that's the sum of quantities.
        """
        return sum([item.quantity for item in self.items])

    @property
    def unique_count(self):
        """
        The number of unique items in cart, regardless of the quantity.
        """
        return len(self._items_dict)

    @property
    def is_empty(self):
        return self.unique_count == 0

    @property
    def products(self):
        """
        The list of associated products.
        """
        return [item.product for item in self.items]

    @property
    def total(self):
        """
        The total value of all items in the cart.
        """
        return sum([item.subtotal for item in self.items])

    @property
    def total_pretax(self):
        """
        The total value of all the items in the cart pre-tax.
        """
        return sum([item.subtotal_pretax for item in self.items])
        

