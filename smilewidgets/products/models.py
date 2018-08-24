from django.db import models
from datetime import datetime

class Product(models.Model):
    name = models.CharField(max_length=25, help_text='Customer facing name of product')
    code = models.CharField(max_length=10, help_text='Internal facing reference to product')
    price = models.PositiveIntegerField(help_text='Price of product in cents')

    def __str__(self):
        return '{} - {}'.format(self.name, self.code)


class GiftCard(models.Model):
    code = models.CharField(max_length=30)
    amount = models.PositiveIntegerField(help_text='Value of gift card in cents')
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.code, self.formatted_amount)

    @property
    def formatted_amount(self):
        return '${0:.2f}'.format(self.amount / 100)

class ProductPrice(models.Model):

    def get_price(self, productCode=None, date=None, giftCardCode=None,**kwargs):
        # initialize return dict
        resp_dict = {'error':False, 'errorText':'', 'price':None, 'formatted_price': None}

        # get product
        product = Product.objects.filter(code=productCode)

        # set error if no matching product
        if len(product) == 0:
            resp_dict['error'] = True
            resp_dict['errorText'] = "Product code does not exist"

        # set error if more than one matching product
        if len(product) > 1:
            resp_dict['error'] = True
            resp_dict['errorText'] = "There is more than one product with product code {}".format(productCode)


        # parse date string, expecting YYYY-MM-DD
        # wrapped in a try except to handle improperly formatted dates
        try:
            datetime_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except:
            resp_dict['error'] = True
            resp_dict['errorText'] = "The date was improperly formatted. Expecting YYYY-MM-DD"

        # final check to make sure that values are actually set
        if productCode is None or date is None:
            resp_dict['error'] = True
            resp_dict['errorText'] = "productCode and date must be set"

        # continue if no error has been set in resp_dict
        if not resp_dict['error']:
            # no errors here means that there is exactly one result
            product = product.get()

            # get product price
            product_price = product.price/100

            '''conduct checks for special cases, adjust price as needed'''

            # check for black friday sale
            if datetime_obj.year == 2018 and datetime_obj.month == 11 and (datetime_obj.day >= 23 and datetime_obj.day <= 25):
                if productCode == 'big_widget':
                    product_price = 800.0
                if productCode == 'sm_widget':
                    product_price = 0.0

            # check for 2019 price change,
            if datetime_obj.year >= 2019:
                if productCode == 'big_widget':
                    product_price = 1200.0
                if productCode == 'sm_widget':
                    product_price = 125.0

            '''
            SPEC DOES NOT SPECIFY HOW TO HANDLE GIFT CARDS, I WOULD LIKE
            TO CLARIFY. ASSUMING THAT GIFT CARD VALUE WILL BE REMOVED FROM PRICE,
            IF CARD VALUE IS GREATER THAN PRICE, THE PRICE WILL BE SET TO ZERO
            '''

            if giftCardCode is not None:
                # retrieve value of gift card, if card does not exist ignore
                try:
                    gift_card = GiftCard.objects.filter(code=giftCardCode).get()
                    gift_card_value = gift_card.amount/100
                    gift_card_start = gift_card.date_start
                    gift_card_end = gift_card.date_end
                    # parse end only if date present
                    if gift_card_end is None:
                        gift_card_end = datetime_obj

                    if datetime_obj >= gift_card_start and datetime_obj <= gift_card_end:
                        # reduce product_price by gift_card_value and set to zero if negative
                        product_price = product_price - gift_card_value
                        if product_price < 0:
                            product_price = 0
                except Exception as e:
                    # passing as not having a valid gift card does not affect price
                    print(e)
                    pass

            resp_dict['price'] = product_price
            resp_dict['formatted_price'] = '${0:.2f}'.format(product_price)

        # return resp_dict
        return resp_dict
