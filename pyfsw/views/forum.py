from flask import render_template, redirect, url_for, flash, request, session, escape
from flask.ext.sqlalchemy import Pagination

from time import time
from math import ceil

from pyfsw import app, db
from pyfsw import current_user, login_required, admin_required
from pyfsw import Player
from pyfsw import ForumCategory, ForumBoard, ForumThread, ForumPost
from pyfsw import POST_COOLDOWN, ADMIN_ACCOUNT_TYPE, FORUM_LEVEL_REQUIREMENT, FORUM_ACCOUNT_AGE_REQUIREMENT
from pyfsw import THREADS_PER_PAGE, POSTS_PER_PAGE, FORUM_CHARACTER_LIMIT

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
	perpage = THREADS_PER_PAGE

	threads = ForumThread.query.filter(ForumThread.board_id == board.id)

	if session.get('access', 0) != ADMIN_ACCOUNT_TYPE:
		threads = threads.filter(ForumThread.deleted == 0)

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

	if not found:
		flash('You cannot post from a character that does not belong to you.', 'error')
		error = True

	timestamp = int(time())
	if session.get('access', 0) != ADMIN_ACCOUNT_TYPE:
		if board.locked:
			flash('You cannot create a thread in a locked board.', 'error')
			error = True

		if user.lastpost + POST_COOLDOWN > timestamp:
			flash('You must wait {} seconds before posting again.'.format(POST_COOLDOWN), 'error')
			error = True

		if user.creation + (60 * 60 * 24 * FORUM_ACCOUNT_AGE_REQUIREMENT) > timestamp:
			flash('Your account must be at least {} days old to post on the forum.'.format(FORUM_ACCOUNT_AGE_REQUIREMENT), 'error')
			error = True

		if player.level < FORUM_LEVEL_REQUIREMENT:
			flash('Your character must be at least level {} to post on the forum.'.format(FORUM_LEVEL_REQUIREMENT), 'error')
			error = True

		if len(content) < 15:
			flash('Your thread content must be at least 15 characters long.', 'error')
			error = True

	if len(subject) < 5:
		flash('Your thread subject must be at least 5 characters long', 'error')
		error = True

	if not error:
		if len(content) > FORUM_CHARACTER_LIMIT:
			content = content[:FORUM_CHARACTER_LIMIT]

		content = content.strip()
		content = '\n'.join(content.split('\n'))

		content = escape(content)
		content = str(content).replace('\n', '<br>')

		thread = ForumThread()
		thread.subject = subject
		thread.timestamp = timestamp
		thread.board_id = id
		thread.locked = 0
		thread.pinned = 0
		thread.lastpost = timestamp
		thread.author_id = character
		thread.content = content
		thread.deleted = 0

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

	if thread.deleted and session.get('access', 0) != ADMIN_ACCOUNT_TYPE:
		return redirect(url_for('route_forum'))

	player = db.session().query(
		Player.name, Player.level, Player.vocation, Player.town_id, Player.group_id, Player.postcount, Player.signature,
		Player.looktype, Player.lookhead, Player.lookbody, Player.looklegs, Player.lookfeet, Player.lookaddons
	).filter(Player.id == thread.author_id).first()
	if player:
		thread.player = player

	total = db.session().query(ForumPost.id).filter(ForumPost.thread_id == thread.id).count()
	perpage = POSTS_PER_PAGE

	posts = ForumPost.query.filter(ForumPost.thread_id == thread.id)

	if session.get('access', 0) != ADMIN_ACCOUNT_TYPE:
		posts = posts.filter(ForumPost.deleted == 0)

	posts = posts.order_by(ForumPost.timestamp.asc())
	posts = posts.offset((page - 1) * perpage)
	posts = posts.limit(perpage).all()

	for post in posts:
		player = db.session().query(
			Player.name, Player.level, Player.vocation, Player.town_id, Player.group_id, Player.postcount, Player.signature,
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

	if not found:
		flash('You cannot post from a character that does not belong to you.', 'error')
		error = True

	timestamp = int(time())
	if session.get('access', 0) != ADMIN_ACCOUNT_TYPE:
		if thread.deleted:
			flash('You cannot post in a deleted thread.', 'error')
			error = True

		if thread.locked:
			flash('You cannot post in a locked thread.', 'error')
			error = True

		if user.lastpost + POST_COOLDOWN > timestamp:
			flash('You must wait {} seconds before posting again.'.format(POST_COOLDOWN), 'error')
			error = True

		if user.creation + (60 * 60 * 24 * FORUM_ACCOUNT_AGE_REQUIREMENT) > timestamp:
			flash('Your account must be at least {} days old to post on the forum.'.format(FORUM_ACCOUNT_AGE_REQUIREMENT), 'error')
			error = True

		if player.level < FORUM_LEVEL_REQUIREMENT:
			flash('Your character must be at least level {} to post on the forum.'.format(FORUM_LEVEL_REQUIREMENT), 'error')
			error = True

		if len(content) < 4:
			flash('Your reply must be at least 4 characters long.', 'error')
			error = True

	# Redirect page
	page = 1

	if not error:
		if len(content) > FORUM_CHARACTER_LIMIT:
			content = content[:FORUM_CHARACTER_LIMIT]

		content = content.strip()
		content = '\n'.join(content.split('\n'))

		content = escape(content)
		content = str(content).replace('\n', '<br>')

		post = ForumPost()
		post.author_id = character
		post.content = content
		post.timestamp = timestamp
		post.thread_id = id
		post.deleted = 0

		thread.lastpost = timestamp
		user.lastpost = timestamp
		player.postcount = player.postcount + 1

		db.session().add(post)
		db.session().commit()

		posts = db.session().query(ForumPost.id).filter(ForumPost.thread_id == id).count()
		page = ceil(posts / POSTS_PER_PAGE)

		print(posts)
		print(page)

	return redirect(url_for('route_forum_thread', thread=id, page=page))

# Views related to thread/post management
@app.route('/forum/thread/hard/<int:id>')
@admin_required(ADMIN_ACCOUNT_TYPE)
def route_forum_thread_hard(id):
	thread = ForumThread.query.filter(ForumThread.id == id).first()
	if not thread:
		return redirect(url_for('route_forum'))

	if thread.deleted == 0:
		character = Player.query.filter(Player.id == thread.author_id).first()
		character.postcount = character.postcount - 1

	posts = ForumPost.query.filter(ForumPost.thread_id == thread.id).all()
	for post in posts:
		if thread.deleted == 0:
			if post.deleted == 0:
				character = Player.query.filter(Player.id == post.author_id).first()
				character.postcount = character.postcount - 1

		db.session().delete(post)

	db.session().delete(thread)
	db.session().commit()

	flash('The thread has been deleted permanently.', 'success')

	return redirect(url_for('route_forum'))

@app.route('/forum/thread/soft/<int:id>')
@admin_required(ADMIN_ACCOUNT_TYPE)
def route_forum_thread_soft(id):
	thread = ForumThread.query.filter(ForumThread.id == id).first()
	if not thread:
		return redirect(url_for('route_forum'))

	posts = db.session().query(ForumPost.author_id, ForumPost.deleted).filter(ForumPost.thread_id == thread.id).all()

	if thread.deleted:
		character = Player.query.filter(Player.id == thread.author_id).first()
		character.postcount = character.postcount + 1

		for post in posts:
			if post.deleted == 0:
				character = Player.query.filter(Player.id == post.author_id).first()
				character.postcount = character.postcount + 1

		thread.deleted = 0
		flash('The thread has been restored.', 'success')
	else:
		character = Player.query.filter(Player.id == thread.author_id).first()
		character.postcount = character.postcount - 1

		for post in posts:
			if post.deleted == 0:
				character = Player.query.filter(Player.id == post.author_id).first()
				character.postcount = character.postcount - 1

		thread.deleted = 1
		flash('The thread has been soft-deleted.', 'success')

	db.session().commit()
	return redirect(url_for('route_forum_thread', thread=thread.id, page=1))

@app.route('/forum/thread/lock/<int:id>')
@admin_required(ADMIN_ACCOUNT_TYPE)
def route_forum_thread_lock(id):
	thread = ForumThread.query.filter(ForumThread.id == id).first()
	if not thread:
		return redirect(url_for('route_forum'))

	if thread.locked:
		thread.locked = 0
		flash('The thread has been unlocked.', 'success')
	else:
		thread.locked = 1
		flash('The thread has been locked.', 'success')

	db.session().commit()
	return redirect(url_for('route_forum_thread', thread=thread.id, page=1))

@app.route('/forum/thread/pin/<int:id>')
@admin_required(ADMIN_ACCOUNT_TYPE)
def route_forum_thread_pin(id):
	thread = ForumThread.query.filter(ForumThread.id == id).first()
	if not thread:
		return redirect(url_for('route_forum'))

	if thread.pinned:
		thread.pinned = 0
		flash('The thread has been unpinned.', 'success')
	else:
		thread.pinned = 1
		flash('The thread has been pinned.', 'success')

	db.session().commit()
	return redirect(url_for('route_forum_thread', thread=thread.id, page=1))

@app.route('/forum/post/hard/<int:id>')
@admin_required(ADMIN_ACCOUNT_TYPE)
def route_forum_post_hard(id):
	post = ForumPost.query.filter(ForumPost.id == id).first()
	if not post:
		return redirect(url_for('route_forum'))

	thread_id = post.thread_id

	if post.deleted == 0:
		character = Player.query.filter(Player.id == post.author_id).first()
		character.postcount = character.postcount - 1

	db.session().delete(post)
	db.session().commit()

	flash('The post has been deleted permanently.', 'success')
	return redirect(url_for('route_forum_thread', thread=thread_id, page=1))

@app.route('/forum/post/soft/<int:id>')
@admin_required(ADMIN_ACCOUNT_TYPE)
def route_forum_post_soft(id):
	post = ForumPost.query.filter(ForumPost.id == id).first()
	if not post:
		return redirect(url_for('route_forum'))

	thread = ForumThread.query.filter(ForumThread.id == post.thread_id).first()
	if post.deleted:
		if thread.deleted == 0:
			character = Player.query.filter(Player.id == post.author_id).first()
			character.postcount = character.postcount + 1

		post.deleted = 0

		flash('The post has been restored.', 'success')
	else:
		if thread.deleted == 0:
			character = Player.query.filter(Player.id == post.author_id).first()
			character.postcount = character.postcount - 1

		post.deleted = 1

		flash('The post has been soft-deleted.', 'success')

	db.session().commit()

	return redirect(url_for('route_forum_thread', thread=post.thread_id, page=1))
