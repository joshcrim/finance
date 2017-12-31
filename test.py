from wallet import Wallet
import jsonpickle

wallet = Wallet()

p = Wallet()

pa = jsonpickle.loads(jsonpickle.dumps(p))

print(pa)

import pdb
pdb.set_trace()
