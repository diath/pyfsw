from flask import render_template, redirect, url_for, flash, request
from flask.ext.sqlalchemy import Pagination

from time import time

from pyfsw import app, db
from pyfsw import current_user, login_required
from pyfsw import Player
from pyfsw import ForumCategory, ForumBoard, ForumThread, ForumPost
from pyfsw import POST_COOLDOWN

@app.route('/forum')
def route_forum():
	categories = ForumCategory.query.all()

	for category in categories:
		for board in category.boards:
			threads = db.session().query(ForumThread.id).filter(ForumThread.board_id == board.id).count()
			board.threads = threads

	return render_template('forum/main.htm', categories=categories)

@app.route('/forum/<int:board>/<int:page>', methods=['GET'])
def route_forum_board(board, page):
	board = ForumBoard.query.filter(ForumBoard.id == board).first()
	if not board:
		return redirect(url_for('route_forum'))

	total = db.session().query(ForumThread.id).filter(ForumThread.board_id == board.id).count()
	perpage = 20

	threads = ForumThread.query.filter(ForumThread.board_id == board.id)

	if page == 1:
		threads = threads.order_by(ForumThread.pinned.desc())

	threads = threads.order_by(ForumThread.lastpost.desc())
	threads = threads.offset((page - 1) * perpage)
	threads = threads.limit(perpage).all()

	for thread in threads:
		posts = db.session().query(ForumPost.id).filter(ForumPost.thread_id == thread.id).count()
		thread.posts = posts

	user = current_user()
	characters = None

	if user:
		characters = db.session().query(Player.id, Player.name).filter(Player.account_id == user.id).all()

	pagination = Pagination(threads, page, perpage, total, threads)

	return render_template(
		'forum/board.htm', board=board, threads=threads, characters=characters,
		pagination=pagination, perpage=perpage, page=page
	)

@app.route('/forum/<int:id>', methods=['POST'])
@login_required
def route_forum_board_post(id):
	board = ForumBoard.query.filter(ForumBoard.id == id).first()
	if not board:
		flash('The board you are trying to create a thread on does not exist.', 'error')
		return redirect(url_for('route_forum'))

	subject = request.form.get('subject', '', type=str)
	character = request.form.get('character', 0, type=int)
	content = request.form.get('content', '', type=str)
	error = False

	user = current_user()
	found = False
	for player in user.players:
		if player.id == character:
			found = True
			break

	if board.locked:
		flash('You can not create a thread in a locked board.', 'error')
		error = True

	if not found:
		flash('You can not post from a character that does not belong to you.', 'error')
		error = True

	timestamp = int(time())
	if user.lastpost + POST_COOLDOWN > timestamp:
		flash('You must wait {} seconds before posting again.'.format(POST_COOLDOWN), 'error')
		error = True

	if len(subject) < 5:
		flash('Yout thread subject must be at least 5 characters long', 'error')
		error = True

	if len(content) < 15:
		flash('Your thread content must be at least 15 characters long.', 'error')
		error = True

	if not error:
		if len(content) > 512:
			content = content[:512]

		content = content.strip()
		content = ' '.join(content.split())

		thread = ForumThread()
		thread.subject = subject
		thread.timestamp = timestamp
		thread.board_id = id
		thread.locked = 0
		thread.pinned = 0
		thread.lastpost = timestamp
		thread.author_id = character
		thread.content = content

		user.lastpost = timestamp
		player.postcount = player.postcount + 1

		db.session().add(thread)
		db.session().commit()

		return redirect(url_for('route_forum_thread', thread=thread.id, page=1))

	return redirect(url_for('route_forum_board', board=id, page=1))

@app.route('/forum/thread/<int:thread>/<int:page>', methods=['GET'])
def route_forum_thread(thread, page):
	thread = ForumThread.query.filter(ForumThread.id == thread).first()
	if not thread:
		return redirect(url_for('route_forum'))

	player = db.session().query(
		Player.name, Player.level, Player.vocation, Player.town_id, Player.group_id, Player.postcount,
		Player.looktype, Player.lookhead, Player.lookbody, Player.looklegs, Player.lookfeet, Player.lookaddons
	).filter(Player.id == thread.author_id).first()
	if player:
		thread.player = player

	total = db.session().query(ForumPost.id).filter(ForumPost.thread_id == thread.id).count()
	perpage = 3

	posts = ForumPost.query.filter(ForumPost.thread_id == thread.id)
	posts = posts.order_by(ForumPost.timestamp.asc())
	posts = posts.offset((page - 1) * perpage)
	posts = posts.limit(perpage).all()

	for post in posts:
		player = db.session().query(
			Player.name, Player.level, Player.vocation, Player.town_id, Player.group_id, Player.postcount,
			Player.looktype, Player.lookhead, Player.lookbody, Player.looklegs, Player.lookfeet, Player.lookaddons
		).filter(Player.id == post.author_id).first()
		if player:
			post.player = player

	user = current_user()
	characters = None

	if user:
		characters = db.session().query(Player.id, Player.name).filter(Player.account_id == user.id).all()

	pagination = Pagination(posts, page, perpage, total, posts)

	return render_template(
		'forum/thread.htm', thread=thread, posts=posts, characters=characters,
		pagination=pagination, perpage=perpage, page=page
	)

@app.route('/forum/thread/<int:id>', methods=['POST'])
@login_required
def route_forum_thread_post(id):
	thread = ForumThread.query.filter(ForumThread.id == id).first()
	if not thread:
		flash('The thread you are trying to reply to does not exist.', 'error')
		return redirect(url_for('route_forum'))

	character = request.form.get('character', 0, type=int)
	content = request.form.get('content', '', type=str)
	error = False

	user = current_user()
	found = False
	for player in user.players:
		if player.id == character:
			found = True
			break

	if thread.locked:
		flash('You can not post in a locked thread.', 'error')
		error = True

	if not found:
		flash('You can not post from a character that does not belong to you.', 'error')
		error = True

	timestamp = int(time())
	if user.lastpost + POST_COOLDOWN > timestamp:
		flash('You must wait {} seconds before posting again.'.format(POST_COOLDOWN), 'error')
		error = True

	if len(content) < 4:
		flash('Your reply must be at least 4 characters long.', 'error')
		error = True

	if not error:
		if len(content) > 512:
			content = content[:512]

		content = content.strip()
		content = ' '.join(content.split())

		post = ForumPost()
		post.author_id = character
		post.content = content
		post.timestamp = timestamp
		post.thread_id = id

		thread.lastpost = timestamp
		user.lastpost = timestamp
		player.postcount = player.postcount + 1

		db.session().add(post)
		db.session().commit()

	return redirect(url_for('route_forum_thread', thread=id, page=1))
