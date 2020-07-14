from hashlib import sha256
import json
import time
import flaskr.documents

"""
	Store data format : 
	1. Entire document.
	2. Hash of a document.

	Entire document format :
	[{
		"author" : "",
		"timestamps" : "",
		"content" : "",
		"comment" : "",
		"hash" : ""
	}]

	Hash of a doc format :
	[{
		"timestamps" : "",
		"comment" : "",
		"hash" : ""
	}]

"""


class Block:
	def __init__(self,index,data,timestamps,previous_block,nonce=0):
		self.index = index
		self.timestamps = timestamps
		self.previous_block = previous_block
		self.nonce = nonce
		self.data = data
		self.hash = ""
	
	def compute_hash(self):
		#print(self.__dict__)
		block_string = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_string.encode()).hexdigest()
	
	def show(self):
		return "Index : "+str(self.index)+" Data : "+str(self.data)+" Hash : "+str(self.compute_hash())+" Nonce : "+str(self.nonce)

class Blockchain:
	def __init__(self,difficulty):
		self.chain = []
		self.unconfirmed_documents = []
		self.difficulty = difficulty
		self.no_docs = 0
	
	def generate_root_block(self):
		root_block = Block(0,[],"0","0")
		self.calc_proof(root_block)
		root_block.hash = root_block.compute_hash()
		self.chain.append(root_block)
	
	def get_last_block(self):
		return self.chain[-1]

	def calc_proof(self,block):
		block.nonce = 0
		computed_hash = block.compute_hash()
		while not computed_hash.startswith('0'*self.difficulty):
			block.nonce += 1
			computed_hash = block.compute_hash()
		return computed_hash

	def check_proof(self,block,proof):
		return (block.hash==proof) and (proof.startswith('0'* self.difficulty))

	def add_block(self,block,proof):
		if block.previous_block != self.get_last_block().hash:
			return False,1
		if not self.check_proof(block,proof):
			return False,2
		block.hash = proof
		self.chain.append(block)
		self.no_docs += 1
		return True,1
	
	def add_unconfirmed_documents(self,document):
		self.unconfirmed_documents.append(document)

	def mine(self):
		if self.unconfirmed_documents == []:
			return False
		
		new_block = Block(self.get_last_block().index+1,self.unconfirmed_documents,time.time(),self.get_last_block().hash)
		proof = self.calc_proof(new_block)
		new_block.hash = new_block.compute_hash()
		self.add_block(new_block,proof)
		self.unconfirmed_documents = []
		return True

	def check_blockchain_valid(self):
		res = True
		first_block = "0"
		for block in range(1,len(self.chain)):
			g = self.chain[block]
			temp = self.calc_proof(g)
			if temp != self.chain[block].hash:
				res = False
				break
		return res

			


	