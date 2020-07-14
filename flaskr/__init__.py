import os

from flask import Flask
from flaskr.block import Blockchain,Block
from flask import render_template
from . import auth
from . import db
from . import transaction
from flask import session
from flask import redirect,url_for
from flaskr.global_var import blockchain_global
from flaskr.db import get_db
import json


# session['blockchain']= blockchain


def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
	)

	if test_config is None:
		
		app.config.from_pyfile('config.py', silent=True)
	else:
		app.config.from_mapping(test_config)
	try:
		os.makedirs(app.instance_path)
	except OSError:	
		pass

	@app.route('/')
	def index():
		return redirect(url_for('auth.login'))
	
	# @app.route('/create_documents')
	# def create_documents():
	# 	return render_template('create_documents.html')

	def create_chain_from_dump(chain_dump):
		generated_blockchain = Blockchain(2)
		generated_blockchain.generate_root_block()
		for idx, block_data in enumerate(chain_dump):
			if idx == 0:
				continue  
			block = Block(int(block_data["index"]),
						block_data["data"],
						block_data["timestamps"],
						block_data["previous_block"],
						block_data["nonce"])
			block.hash = block.compute_hash()
			proof = block_data['hash']
			added,b = generated_blockchain.add_block(block, proof)
			if not added:
				raise Exception("The chain dump is tampered!!")
		return generated_blockchain

	@app.route('/home')
	def home():
		global blockchain_global
		if session.get('user_id') is None:
			return redirect(url_for('auth.login'))
		user_id = session.get('user_id')
		db = get_db()
		if session.get('username') is None:
			block = []
			return render_template('home.html',blockchain=blockchain_global)
		else:
			block = db.execute('SELECT last_blockchain FROM block_chain WHERE username = ?',(session['username'])).fetchall()
		for i in block:
			#print(i[0])
			res = i[0]
		print(res)
		user_block = create_chain_from_dump(json.loads(res))
		return render_template('home.html',blockchain=user_block)
	db.init_app(app)

	app.register_blueprint(auth.bp)
	app.register_blueprint(transaction.bp)

	return app
