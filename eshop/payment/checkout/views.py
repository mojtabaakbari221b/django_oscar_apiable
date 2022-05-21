import logging
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.shortcuts import render
from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.checkout import views
from oscar.apps.checkout import models
import logging
from django.http import HttpResponse, Http404
from azbankgateways import bankfactories, models as bank_models, default_settings as settings



class PaymentDetailsView(CorePaymentDetailsView):
    template_name = 'oscar/checkout/payment_details.html'
    def submit(self, order_total):
        return order_total

def go_to_gateway_view(request, *args, **kwargs):
    total_amount = PaymentDetailsView()
    amount = total_amount.submit(10000)
    factory = bankfactories.BankFactory()
    try:
        bank = factory.create(bank_models.BankType.ZARINPAL) # or factory.create(bank_models.BankType.ZARINPAL) or set identifier
        bank.set_request(request)
        bank.set_amount(amount)
        bank_record = bank.ready()
        
        return bank.redirect_gateway()
    except AZBankGatewaysException as e:
        logging.critical(e)
        raise e
    
def callback_gateway_view(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    # در این قسمت باید از طریق داده هایی که در بانک رکورد وجود دارد، رکورد متناظر یا هر اقدام مقتضی دیگر را انجام دهیم
    if bank_record.is_success:
        # پرداخت با موفقیت انجام پذیرفته است و بانک تایید کرده است.
        # می توانید کاربر را به صفحه نتیجه هدایت کنید یا نتیجه را نمایش دهید.
        return HttpResponse("پرداخت با موفقیت انجام شد.")

    # پرداخت موفق نبوده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.
    return HttpResponse("پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.")

factory = bankfactories.BankFactory()

# غیر فعال کردن رکورد های قدیمی
bank_models.Bank.objects.update_expire_records()

# مشخص کردن رکوردهایی که باید تعیین وضعیت شوند
for item in bank_models.Bank.objects.filter_return_from_bank():
    bank = factory.create(bank_type=item.bank_type, identifier=item.bank_choose_identifier)
    bank.verify(item.tracking_code)     
    bank_record = bank_models.Bank.objects.get(tracking_code=item.tracking_code)
    if bank_record.is_success:
        logging.debug("This record is verify now.", extra={'pk': bank_record.pk})

