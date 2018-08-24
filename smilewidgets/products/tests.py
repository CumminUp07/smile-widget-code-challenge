from django.test import TestCase
from products.models import Product, ProductPrice, GiftCard


class ProductPriceTestCase(TestCase):
    def setUp(self):
        Product.objects.create(name='Big Widget', code='big_widget', price=100000)
        Product.objects.create(name='Small Widget', code='sm_widget', price=9900)

    def get_price(self, productCode, date, giftCardCode=None):
        return ProductPrice().get_price(productCode, date, giftCardCode)

    def test_2018_regular_prices(self):
        self.assertEqual(self.get_price('sm_widget','2018-01-01')['price'], 99.0)
        self.assertEqual(self.get_price('big_widget','2018-01-01')['price'], 1000.0)

    def test_black_friday(self):
        self.assertEqual(self.get_price('sm_widget','2018-11-23')['price'], 0.0)
        self.assertEqual(self.get_price('big_widget','2018-11-23')['price'], 800.0)
        self.assertEqual(self.get_price('sm_widget','2018-11-24')['price'], 0.0)
        self.assertEqual(self.get_price('big_widget','2018-11-24')['price'], 800.0)
        self.assertEqual(self.get_price('sm_widget','2018-11-25')['price'], 0.0)
        self.assertEqual(self.get_price('big_widget','2018-11-25')['price'], 800.0)

    def test_2019_price_increase(self):
        self.assertEqual(self.get_price('sm_widget','2019-11-23')['price'], 125.0)
        self.assertEqual(self.get_price('big_widget','2019-11-23')['price'], 1200.0)
