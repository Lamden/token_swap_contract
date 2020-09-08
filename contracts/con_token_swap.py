import currency

operator = Variable()
seen_hashes = Hash()

@construct
def seed(vk: str):
    operator.set(vk)

@export
def disperse(amount: float, to: str, hash: str):
    assert_owner()
    assert seen_hashes[hash] is None, 'Already processed this hash!'
    seen_hashes[hash] = True
    currency.transfer(amount=amount, to=to)

@export
def withdraw(amount: float):
    assert_owner()
    currency.transfer(amount=amount, to=ctx.caller)

@export
def change_operator(new_operator: str):
    assert_owner()
    operator.set(new_operator)

def assert_owner():
    assert ctx.caller == operator.get(), 'Only operator can call!'