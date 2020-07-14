from flaskr.block import Blockchain

global blockchain_global
global peer
blockchain_global = Blockchain(2)
peer = set()
blockchain_global.generate_root_block()