"""Charge once using receipts stored with the current game save."""
import json


class PaymentUncertain(RuntimeError):
    pass


class HouseholdPayment:
    def __init__(self, receipts, context, funds_for, remove):
        self.receipts = receipts
        self.context = context
        self.funds_for = funds_for
        self.remove = remove

    def __call__(self, save_id, household_id, order_id, amount):
        if self.context() != (save_id, household_id):
            raise ValueError('The ordering household or save has changed')
        if type(amount) is not int or amount <= 0:
            raise ValueError('Payment must be a positive whole amount')
        key = json.dumps([save_id, household_id, order_id])
        with self.receipts.transaction(write=False) as data:
            prior = data.get('payments', {}).get(key)
        if prior is not None:
            if prior['amount'] != amount:
                raise ValueError('Payment amount changed for the same order')
            if prior['status'] == 'paid':
                return True
            raise PaymentUncertain('An interrupted payment needs review before another charge')
        funds = self.funds_for()
        before = funds.money
        if before < amount:
            return False
        with self.receipts.transaction() as data:
            data.setdefault('payments', {})[key] = dict(amount=amount, status='pending')
        # No yielding is permitted between this debit and recording its result.
        try:
            self.remove(amount)
        except Exception:
            if before - funds.money != amount:
                raise PaymentUncertain('The payment result could not be confirmed')
        removed = before - funds.money
        if removed not in (0, amount):
            raise PaymentUncertain('The household balance changed unexpectedly')
        with self.receipts.transaction() as data:
            if removed == amount:
                data['payments'][key]['status'] = 'paid'
            else:
                del data['payments'][key]
        return removed == amount
