import functools
from flaskr.block import Blockchain
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import json
import time
from flaskr.documents import Document
#from flaskr import blockchain_global
from flaskr.global_var import blockchain_global,peer
from flaskr.db import get_db


bp = Blueprint('transaction', __name__, url_prefix='/transaction')

@bp.route('/sync')
def sync():
	db = get_db()
	chain_data = []
	for block in blockchain_global.chain:
		chain_data.append(block.__dict__)
	block_dump = json.dumps(chain_data)
	#if db.execute('SELECT id FROM block_chain WHERE username = ?', (session.get('user_id'),)).fetchone() is not None:
	db.execute('UPDATE block_chain SET last_blockchain = ? WHERE username = ?',(block_dump,session.get('username')))
	db.commit()
	return redirect(url_for('home'))


@bp.route('/create_block')
def create_block():
	global blockchain_global
	global peer
	if session.get('user_id') is None:
		return redirect(url_for('auth.login'))
	result = blockchain_global.mine()
	if result:
		flash('Done! add block')
	db = get_db()
	chain_data = []
	for block in blockchain_global.chain:
		chain_data.append(block.__dict__)
	block_dump = json.dumps(chain_data)
	#if db.execute('SELECT id FROM block_chain WHERE username = ?', (session.get('user_id'),)).fetchone() is not None:
	db.execute('UPDATE block_chain SET last_blockchain = ? WHERE username = ?',(block_dump,session.get('username')))
	db.commit()
	return redirect(url_for('home'))
	

	

@bp.route('/create_documents', methods=('GET', 'POST'))
def create_documents():
	if session.get('user_id') is None:
		return redirect(url_for('auth.login'))
	global blockchain_global
	if request.method == 'POST':
		author = request.form['username']
		comments = request.form['comments']
		contents = request.form['text_area']
		error = None
		if not author:
			error = 'Author is required.'
		elif not comments:
			error = 'Comments is required.'
		elif not contents:
			error = 'Contents is required.'
		if error is None:
			res = {"author" : author,"timestamps" : time.time(),"content" : contents,"comment" : comments}
			# if session.get('blockchain') == True:
			# 	session['blockchain'].add_unconfirmed_documents(res)
			# else:
			# 	session['blockchain'] = Blockchain(2)
			#res = Document(author,time.time(),contents)
			blockchain_global.add_unconfirmed_documents(res)
			return redirect(url_for('home'))
		flash(error)
	return render_template('transaction/create_documents.html')


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)

	return wrapped_view