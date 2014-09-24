from django.core.urlresolvers import reverse
from django.test import TestCase
from carton.tests.models import Product

import json

try:
    from django.test import override_settings
except ImportError:
    from  django.test.utils import override_settings


class CartTests(TestCase):

    def setUp(self):
        self.deer = Product(name='deer', price=10.0, custom_id=1)
        self.moose = Product(name='moose', price=20.0, custom_id=2)
        self.url_add = reverse('carton-tests-add')
        self.url_show = reverse('carton-tests-show')
        self.url_remove = reverse('carton-tests-remove')
        self.url_remove_single = reverse('carton-tests-remove-single')
        self.url_quantity = reverse('carton-tests-set-quantity')
        self.url_clear = reverse('carton-tests-clear')
        self.url_get_total = reverse('carton-tests-get-total')
        self.url_changeprice = reverse('carton-tests-change_price')
        self.url_addtax = reverse('carton-tests-add_tax')
        self.deer_data = {'product_id': self.deer.custom_id}
        self.moose_data = {'product_id': self.moose.custom_id}

    def test_product_is_added(self):
        self.client.post(self.url_add, self.deer_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '1 deer for $10.0')
 
    def test_multiple_products_are_added(self):
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '1 deer for $10.0')
        self.assertContains(response, '1 moose for $20.0')
 
    def test_quantity_increases(self):
        self.client.post(self.url_add, self.deer_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '1 deer')
        self.deer_data['quantity'] = 2
        self.client.post(self.url_add, self.deer_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '3 deer')
 
    def test_items_are_counted_properly(self):
        self.deer_data['quantity'] = 2
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, 'items count: 3')
        self.assertContains(response, 'unique count: 2')
 
    def test_price_is_updated(self):
        # Let's give a discount: $1.5/product. That's handled on the test views.
        self.deer_data['quantity'] = 2
        self.deer_data['discount'] = 1.5
        self.client.post(self.url_add, self.deer_data)
        response = self.client.get(self.url_show)
        # subtotal = 10*2 - 1.5*2
        self.assertContains(response, '2 deer for $17.0')
 
    def test_products_are_removed_all_together(self):
        self.deer_data['quantity'] = 3
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        remove_data = {'product_id': self.deer.pk}
        self.client.post(self.url_remove, remove_data)
        response = self.client.get(self.url_show)
        self.assertNotContains(response, 'deer')
        self.assertContains(response, 'moose')
 
    def test_single_product_is_removed(self):
        self.deer_data['quantity'] = 3
        self.client.post(self.url_add, self.deer_data)
        remove_data = {'product_id': self.deer.pk}
        self.client.post(self.url_remove_single, remove_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '2 deer')
 
    def test_quantity_is_overwritten(self):
        self.deer_data['quantity'] = 3
        self.client.post(self.url_add, self.deer_data)
        self.deer_data['quantity'] = 4
        self.client.post(self.url_quantity, self.deer_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '4 deer')
 
    def test_cart_items_are_cleared(self):
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        self.client.post(self.url_clear)
        response = self.client.get(self.url_show)
        self.assertNotContains(response, 'deer')
        self.assertNotContains(response, 'moose')

    def test_check_total(self):
        self.client.post(self.url_add, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 10.0, "price didn't match: %s=10.0" %deer_total)

        #add another deer
        self.client.post(self.url_add, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer2_total = resp_dict['total_cost']
        self.assertEqual(float(deer2_total), 20.0, "price didn't match: %s=20.0" %deer2_total)

        #add a moose
        self.client.post(self.url_add, self.moose_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer2_and_moose_total = resp_dict['total_cost']
        self.assertEqual(float(deer2_and_moose_total), 40.0, "price didn't match: %s=40.0" %deer2_and_moose_total)

        #now remove a deer
        self.client.post(self.url_remove_single, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer1_and_moose_total = resp_dict['total_cost']
        self.assertEqual(float(deer1_and_moose_total), 30.0, "price didn't match: %s=30.0" %deer1_and_moose_total)

    def test_change_price(self):
        self.client.post(self.url_add, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 10.0, "price didn't match: %s=10.0" %deer_total)
 
        #change the price to reflect tax
        self.deer_data['price'] = 11.00
        self.client.post(self.url_changeprice, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 11.0, "price didn't match: %s=11.0" %deer_total)
 
        #add another deer
        self.client.post(self.url_add, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer2_total = resp_dict['total_cost']
        self.assertEqual(float(deer2_total), 22.0, "price didn't match: %s=22.0" %deer2_total)
 
        #they want it shipped somewhere without tax. change the price back to $10
        self.deer_data['price'] = 10.00
        self.client.post(self.url_changeprice, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 20.0, "price didn't match: %s=20.0" %deer_total)
 
        self.client.post(self.url_add, self.moose_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer2_and_moose_total = resp_dict['total_cost']
        self.assertEqual(float(deer2_and_moose_total), 40.0, "price didn't match: %s=40.0" %deer2_and_moose_total)
 
        #change the price to reflect tax
        self.deer_data['price'] = 11.00
        self.client.post(self.url_changeprice, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 42.0, "price didn't match: %s=42.0" %deer_total)
 
    def test_add_tax(self):
        #add a deer
        self.client.post(self.url_add, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 10.0, "price didn't match: %s=10.0" %deer_total)
        
        #then add some tax to it
        self.deer_data['tax'] = 0.50
        self.client.post(self.url_addtax,self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 10.5, "price didn't match: %s=10.5" %deer_total)
        
        #add a moose
        self.client.post(self.url_add, self.moose_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer2_and_moose_total = resp_dict['total_cost']
        self.assertEqual(float(deer2_and_moose_total), 30.5, "price didn't match: %s=30.5" %deer2_and_moose_total)
        
        #change the price of the deer. tax stays the same
        self.deer_data['price'] = 11.00
        self.client.post(self.url_changeprice, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer_total = resp_dict['total_cost']
        self.assertEqual(float(deer_total), 31.5, "price didn't match: %s=31.5" %deer_total)
        
        #add tax for the moose
        '''
        Deer @ 11 + tax of 0.50 = 11.50
        Moose @ 20 + tax of 1.25 = 21.25
        Total = 31.75
        '''
        self.moose_data['tax'] = 1.25
        self.client.post(self.url_addtax, self.moose_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer2_and_moose_total = resp_dict['total_cost']
        self.assertEqual(float(deer2_and_moose_total), 32.75, "price didn't match: %s=32.75" %deer2_and_moose_total)
        
        #finally, we need 2 deer
        self.client.post(self.url_add, self.deer_data)
        resp = self.client.get(self.url_get_total)
        resp_dict = json.loads(resp.content)
        deer2_total = resp_dict['total_cost']
        self.assertEqual(float(deer2_total), 44.25, "price didn't match: %s=44.25" %deer2_total)
        
        
