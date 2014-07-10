from flask import render_template, redirect, url_for, flash

from pyfsw import app, db
from pyfsw import Player
from pyfsw import ForumCategory, ForumBoard, ForumThread, ForumPost

@app.route('/forum')
def route_forum():
	categories = ForumCategory.query.all()

	for category in categories:
		for board in category.boards:
			threads = db.session().query(ForumThread.id).filter(ForumThread.board_id == board.id).count()
			board.threads = threads

	return render_template('forum/main.htm', categories=categories)

@app.route('/forum/<int:board>')
def route_forum_board(board):
	board = ForumBoard.query.filter(ForumBoard.id == board).first()
	if not board:
		return redirect(url_for('route_forum'))

	threads = ForumThread.query.all()

	for thread in threads:
		posts = db.session().query(ForumPost.id).filter(ForumPost.thread_id == thread.id).count()
		thread.posts = posts

	return render_template('forum/board.htm', board=board, threads=threads)

@app.route('/forum/thread/<int:thread>')
def route_forum_thread(thread):
	thread = ForumThread.query.filter(ForumThread.id == thread).first()
	if not thread:
		return redirect(url_for('route_forum'))

	player = db.session().query(
		Player.name, Player.level, Player.vocation, Player.town_id,
		Player.looktype, Player.lookhead, Player.lookbody, Player.looklegs, Player.lookfeet, Player.lookaddons
	).filter(Player.id == thread.author_id).first()
	thread.player = player

	posts = ForumPost.query.filter(ForumPost.thread_id == thread.id).all()
	for post in posts:
		player = db.session().query(
			Player.name, Player.level, Player.vocation, Player.town_id,
			Player.looktype, Player.lookhead, Player.lookbody, Player.looklegs, Player.lookfeet, Player.lookaddons
		).filter(Player.id == post.author_id).first()
		post.player = player

	return render_template('forum/thread.htm', thread=thread, posts=posts)
