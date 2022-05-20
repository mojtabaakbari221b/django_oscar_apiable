import logging
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.shortcuts import render
from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.checkout import views
from oscar.apps.checkout import models


class PaymentDetailsView(CorePaymentDetailsView):
    template_name = 'oscar/checkout/payment_details.html'
    def submit(self, user, basket, shipping_address, shipping_method,shipping_charge, billing_address, order_total,payment_kwargs=None, order_kwargs=None, surcharges=None):
      return self.handle_order_placement(
                 user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, surcharges=surcharges, **order_kwargs)


order_total = PaymentDetailsView()

def go_to_gateway_view(request):
    amount = 5000

    # user_mobile_number = '+989112221234' 

    factory = bankfactories.BankFactory()
    try:
        bank = factory.auto_create() # or factory.create(bank_models.BankType.ZARINPAL) or set identifier
        bank.set_request(request)
        bank.set_amount(amount)
        # یو آر ال بازگشت به نرم افزار برای ادامه فرآیند
        bank.set_client_callback_url(reverse('callback-gateway'))
    
        # در صورت تمایل اتصال این رکورد به رکورد فاکتور یا هر چیزی که بعدا بتوانید ارتباط بین محصول یا خدمات را با این
        # پرداخت برقرار کنید. 
        bank_record = bank.ready()
        
        # هدایت کاربر به درگاه بانک
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        # TODO: redirect to failed page.
        raise e
    