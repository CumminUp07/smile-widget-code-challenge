from django.shortcuts import render
from products.models import ProductPrice
from django.http import JsonResponse

def get_price(request, productCode=None, date=None, giftCardCode=None):
    # accept url parameters and GET data
    if productCode is None:
        productCode = request.GET.get('productCode')

    if date is None:
        date = request.GET.get('date')
        
    if giftCardCode is None:
        giftCardCode = request.GET.get('giftCardCode')
    return JsonResponse(ProductPrice().get_price(productCode, date, giftCardCode))
