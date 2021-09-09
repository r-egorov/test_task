import json

from django.urls import reverse

from .test_base import BaseTest
from ..models import Balance, Transaction


class TestViews(BaseTest):
    def test_get_balance_no_data_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "daata": {
                "user_id": 12
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_get_balance_no_user_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "data": {
                "uiid": 12
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_get_balance_no_such_user(self):
        """
        Has to return 404 NOT FOUND HTTP-response
        """
        payload = {
            "data": {
                "user_id": 12
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

    def test_get_balance_ok(self):
        """
        Has to return 200 OK HTTP-response and the balance of the user
        """
        payload = {
            "data": {
                "user_id": self.user_ids[1]
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.data.get("data")
        self.assertEqual(data.get("balance"), 2000)

    def test_change_balance_no_data_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user_id=self.user_ids[1])
        payload = {
            "daata": {
                "user_id": self.user_ids[1],
                "amount": 2000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)
        updated_balance = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_no_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user_id=self.user_ids[1])
        payload = {
            "data": {
                "user_iid": self.user_ids[1],
                "amount": 2000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)
        updated_balance = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_no_amount_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user_id=self.user_ids[1])
        payload = {
            "data": {
                "user_id": self.user_ids[1],
                "amoount": 2000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)
        updated_balance = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_no_such_user(self):
        """
        Has to return 404 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        payload = {
            "data": {
                "user_id": 999,
                "amount": -3000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

    def test_change_balance_first_deposit(self):
        """
        Has to return 201 CREATED HTTP-response,
        create a user
        """
        user_id = 999
        amount = 3000
        payload = {
            "data": {
                "user_id": user_id,
                "amount": amount
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 201)
        balance = Balance.objects.get(user_id=user_id)
        self.assertEqual(balance.balance, amount)
        self.assertEqual(balance.user_id, user_id)

    def test_change_balance_overdraft(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user_id=self.user_ids[1])
        payload = {
            "data": {
                "user_id": self.user_ids[1],
                "amount": -999999
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_ok(self):
        """
        Has to return 200 OK HTTP-response and change the balance
        """
        initial_balance = Balance.objects.get(user_id=self.user_ids[1])
        payload = {
            "data": {
                "user_id": self.user_ids[1],
                "amount": -1000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        updated_balance = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(initial_balance.balance - updated_balance.balance, 1000)

    def test_make_transfer_no_data_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "daata": {
                "source_id": self.user_ids[1],
                "target_id": self.user_ids[0],
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_source_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "data": {
                "soource_id": self.user_ids[1],
                "target_id": self.user_ids[0],
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_target_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "data": {
                "source_id": self.user_ids[1],
                "taarget_id": self.user_ids[0],
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_amount_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "data": {
                "source_id": self.user_ids[1],
                "target_id": self.user_ids[0],
                "ammount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_such_user(self):
        """
        Has to return 404 NOT FOUND HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])

        payload = {
            "data": {
                "source_id": 99999,
                "target_id": self.user_ids[0],
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "data": {
                "source_id": self.user_ids[1],
                "target_id": 99999,
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_overdraft(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "data": {
                "source_id": self.user_ids[1],
                "target_id": self.user_ids[0],
                "amount": 9999999
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_negative_amount(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "data": {
                "source_id": self.user_ids[1],
                "target_id": self.user_ids[0],
                "amount": -500
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_ok(self):
        """
        Has to return 200 OK HTTP-response and change the balances
        """
        initial_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        initial_balance1 = Balance.objects.get(user_id=self.user_ids[1])

        payload = {
            "data": {
                "source_id": self.user_ids[1],
                "target_id": self.user_ids[0],
                "amount": 1000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)

        updated_balance0 = Balance.objects.get(user_id=self.user_ids[0])
        self.assertEqual(updated_balance0.balance - initial_balance0.balance, 1000)

        updated_balance1 = Balance.objects.get(user_id=self.user_ids[1])
        self.assertEqual(initial_balance1.balance - updated_balance1.balance, 1000)

    def test_get_transactions_no_data_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "daata": {
                "user_id": 1,
                "sort_by": "date"
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-transactions"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_get_transactions_no_user_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "data": {
                "usser_id": 1,
                "sort_by": "date"
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-transactions"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_get_transactions_no_sort_by_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "data": {
                "user_id": 1,
                "sortt_by": "date"
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-transactions"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_get_transactions_invalid_sort_by_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "data": {
                "user_id": 1,
                "sort_by": "ddate"
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-transactions"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_get_transactions_no_such_user(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "data": {
                "user_id": 1432,
                "sort_by": "date"
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-transactions"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)