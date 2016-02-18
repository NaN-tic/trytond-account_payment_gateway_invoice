# This file is part account_payment_gateway_invoice module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

from trytond.transaction import Transaction


__all__ = ['AccountPaymentGatewayTransaction']
__metaclass__ = PoolMeta


class AccountPaymentGatewayTransaction:
    __name__ = 'account.payment.gateway.transaction'

    @classmethod
    def _get_origin(cls):
        res = super(AccountPaymentGatewayTransaction, cls)._get_origin()
        res.append('account.invoice')
        return res

    @classmethod
    def confirm(cls, transactions):
        pool = Pool()
        Invoice = pool.get('account.invoice')
        PayInvoice = pool.get('account.invoice.pay', type='wizard')

        to_update = []
        for transaction in transactions:
            if isinstance(transaction.origin, Invoice):
                invoice = transaction.origin
                Invoice.workflow_to_posted([invoice])
                if not invoice.amount_to_pay:
                    continue
                with Transaction().set_context({'active_id': invoice.id}):
                    session_id, _, _ = PayInvoice.create()
                    pay_invoice = PayInvoice(session_id)
                    pay_invoice.start.currency = transaction.currency
                    pay_invoice.start.currency_digits = (transaction
                        .currency_digits)
                    pay_invoice.start.description = transaction.description
                    pay_invoice.start.journal = transaction.gateway.journal
                    pay_invoice.start.date = transaction.date
                    pay_invoice.start.amount = transaction.amount
                    if invoice.total_amount != transaction.amount:
                        min_percent_writeoff = invoice.total_amount * (1 -
                            transaction.gateway.writeoff_amount_percent)
                        max_percent_writeoff = invoice.total_amount * (1 +
                            transaction.gateway.writeoff_amount_percent)
                        [setattr(pay_invoice.ask, f, v)
                            for f, v in pay_invoice.default_ask(None)
                                .iteritems()]

                        if (min_percent_writeoff < transaction.amount <
                                max_percent_writeoff
                                or transaction.amount > invoice.amount_to_pay):
                            pay_invoice.ask.type = 'writeoff'
                            pay_invoice.ask.journal_writeoff = (transaction
                                .gateway.journal_writeoff)
                        else:
                            pay_invoice.ask.type = 'partial'
                        pay_invoice.transition_pay()
                    PayInvoice.delete(session_id)
                to_update.append(transaction)

        super(AccountPaymentGatewayTransaction, cls).confirm(to_update)
