from django.conf.urls import url, patterns


urlpatterns = patterns('carton.tests.views',
    url(r'^show/$', 'show', name='carton-tests-show'),
    url(r'^add/$', 'add', name='carton-tests-add'),
    url(r'^remove/$', 'remove', name='carton-tests-remove'),
    url(r'^remove-single/$', 'remove_single', name='carton-tests-remove-single'),
    url(r'^clear/$', 'clear', name='carton-tests-clear'),
    url(r'^set-quantity/$', 'set_quantity', name='carton-tests-set-quantity'),
    url(r'^gettotal/$', 'get_total', name='carton-tests-get-total'),
    url(r'^changeprice/$', 'change_price', name='carton-tests-change_price'),
    url(r'^addtax/$', 'add_tax', name='carton-tests-add_tax'),
)
