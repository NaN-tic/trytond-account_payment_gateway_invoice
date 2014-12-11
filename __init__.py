# This file is part account_payment_gateway_invoice module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .gateway import *
from .invoice import *

def register():
    Pool.register(
        AccountPaymentGatewayTransaction,
        Invoice,
        module='account_payment_gateway_invoice', type_='model')
