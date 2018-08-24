from django.test import TestCase
from products.models import Product, ProductPrice, GiftCard


class ProductPriceTestCase(TestCase):
    '''
        id |  code  | amount | date_start |  date_end
    ----+--------+--------+------------+------------
      2 | 10OFF  |   1000 | 2018-07-01 |
      3 | 50OFF  |   5000 | 2018-07-01 |
      4 | 250OFF |  25000 | 2018-12-01 | 2019-01-01
    '''
    def setUp(self):
        Product.objects.create(name='Big Widget', code='big_widget', price=100000)
        Product.objects.create(name='Small Widget', code='sm_widget', price=9900)
        GiftCard.objects.create(code='10OFF',amount=1000, date_start='2018-07-01', date_end=None)
        GiftCard.objects.create(code='50OFF',amount=5000, date_start='2018-07-01', date_end=None)
        GiftCard.objects.create(code='250OFF',amount=25000, date_start='2018-12-01', date_end='2019-01-01')

    def get_price(self, productCode=None, date=None, giftCardCode=None):
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

    def test_giftcard(self):
        self.assertEqual(self.get_price('sm_widget','2018-01-01', '10OFF')['price'], 99.0)
        self.assertEqual(self.get_price('sm_widget','2018-07-02', '10OFF')['price'], 89.0)
        self.assertEqual(self.get_price('sm_widget','2018-01-01', '50OFF')['price'], 99.0)
        self.assertEqual(self.get_price('sm_widget','2018-07-02', '50OFF')['price'], 49.0)
        self.assertEqual(self.get_price('big_widget','2018-12-15', '250OFF')['price'], 750.0)
        self.assertEqual(self.get_price('big_widget','2019-11-23', '250OFF')['price'], 1200.0)

    def test_bad_date(self):
        self.assertEqual(self.get_price('sm_widget','2018-13-01')['error'], True)

    def test_invalid_code(self):
        self.assertEqual(self.get_price('foo','2018-13-01')['error'], True)

    def test_no_values(self):
        self.assertEqual(self.get_price()['error'], True)
