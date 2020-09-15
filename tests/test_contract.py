#tests/test_contract.py
import unittest
from decimal import Decimal
from contracting.client import ContractingClient
client = ContractingClient()

initial_args = {
    'vk': 'jeff'
}

with open('./currency.py') as f:
    code = f.read()
    client.submit(code, name='currency')
with open('../contracts/con_token_swap.py') as f:
    code = f.read()
    client.submit(
        code,
        name='con_token_swap',
        constructor_args=initial_args
    )

class MyTestCase(unittest.TestCase):
    con_token_swap = None
    currency_contract = None

    def change_signer(self, name):
        client.signer = name
        self.con_token_swap = client.get_contract('con_token_swap')
        self.currency_contract = client.get_contract('currency')

    def test_1_seed_constructor(self):
        self.change_signer('jeff')
        print("TEST SEED CONSTRUCTOR")

        self.assertEqual(self.con_token_swap.quick_read('operator'), initial_args['vk'])

    def test_2a_disperse(self):
        self.change_signer('jeff')
        print("TEST DISPERSE")

        self.con_token_swap.disperse(
            amount=0.00000007,
            to="stu",
            hash="0x1"
        )

        self.assertEqual(self.con_token_swap.quick_read('seen_hashes', "0x1"), True)
        self.assertEqual(self.currency_contract.quick_read('balances', 'stu'), 0.00000007)

    def test_2b_disperse_assert_already_seen(self):
        self.change_signer('jeff')
        print("TEST DISPERSE - ASSERT HASH ALREADY SEEN")

        self.con_token_swap.disperse(
            amount=0.00000007,
            to="stu",
            hash="0x2"
        )

        self.assertEqual(self.con_token_swap.quick_read('seen_hashes', "0x2"), True)
        self.assertEqual(self.currency_contract.quick_read('balances', 'stu'), 0.00000014)

        self.assertRaises(
            AssertionError,
            lambda: self.con_token_swap.disperse(
                amount=0.00000007,
                to="stu",
                hash="0x2"
            )
        )

        self.assertTrue(self.con_token_swap.quick_read('seen_hashes', "0x2"))
        self.assertEqual(self.currency_contract.quick_read('balances', 'stu'), 0.00000014)

    def test_2c_disperse_assert_operator(self):
        self.change_signer('stu')
        print("TEST DISPERSE - ASSERT OPERATOR")

        self.assertRaises(
            AssertionError,
            lambda: self.con_token_swap.disperse(
                amount=0.00000007,
                to="stu",
                hash="0x3"
            )
        )


    def test_3_withdraw(self):
        self.change_signer('jeff')
        print("TEST WITHDRAW")

        self.assertEqual(self.currency_contract.quick_read('balances', 'jeff'), None)

        self.con_token_swap.withdraw(amount=self.currency_contract.quick_read('balances', 'con_token_swap'))

        self.assertTrue(self.currency_contract.quick_read('balances', 'jeff') > 0)
        self.assertTrue(self.currency_contract.quick_read('balances', 'con_token_swap') == 0)


    def test_4_change_owner(self):
        self.change_signer('jeff')
        print("TEST CHANGE OWNER")

        prev_operator = self.con_token_swap.quick_read('operator')

        self.con_token_swap.change_operator(new_operator='stu')

        curr_operator = self.con_token_swap.quick_read('operator')

        self.assertEqual(curr_operator, 'stu')
        self.assertTrue(curr_operator != prev_operator)

if __name__ == '__main__':
    unittest.main()