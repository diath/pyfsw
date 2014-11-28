from flask import redirect, render_template, request, url_for, flash, session

from time import time

from pyfsw import app, db
from pyfsw import admin_required, current_user
from pyfsw import News, ForumBoard, ForumThread, Player

@app.route('/admin/news/compose', methods=['GET'])
@admin_required
def route_admin_news_compose():
	user = current_user()
	boards = ForumBoard.query.all()

	return render_template(
		'admin/news/compose.htm',
		characters=user.players, boards=boards
	)

@app.route('/admin/news/compose', methods=['POST'])
@admin_required
def route_admin_news_compose_post():
	title = request.form.get('title', '')
	content = request.form.get('content', '')
	thread_content = request.form.get('threadContent', '')
	poster_id = request.form.get('poster', 0)
	board_id = request.form.get('board', 0)
	error = False

	if len(title) == 0:
		flash('The news title cannot be empty.', 'error')
		error = True

	if len(content) == 0:
		flash('The news content cannot be empty.', 'error')
		error = True

	if len(thread_content) == 0:
		flash('The thread content cannot be empty.', 'error')
		error = True

	if not error:
		content = content.strip()
		content = ' '.join(content.split())

		timestamp = int(time())

		thread = ForumThread()
		thread.subject = title
		thread.timestamp = timestamp
		thread.board_id = board_id
		thread.locked = 0
		thread.pinned = 0
		thread.lastpost = timestamp
		thread.author_id = poster_id
		thread.content = thread_content

		db.session().add(thread)
		db.session().commit()

		news = News()
		news.timestamp = timestamp
		news.header = title
		news.content = content
		news.author_id = poster_id
		news.thread_id = thread.id

		db.session().add(news)
		db.session().commit()

		flash('The news has been posted successfully.', 'success')

	return redirect(url_for('route_admin_news_compose'))

@app.route('/admin/news/manage', methods=['GET'])
@admin_required
def route_admin_news_manage():
	news = News.query.all()

	for entry in news:
		player = db.session().query(Player.name).filter(Player.id == entry.author_id).first()
		if player:
			entry.author = player.name

	return render_template(
		'admin/news/manage.htm',
		news = news
	)

@app.route('/admin/news/edit/<int:id>', methods=['GET'])
@admin_required
def route_admin_news_edit(id):
	news = News.query.filter(News.id == id).first()
	user = current_user()
	boards = ForumBoard.query.all()
	news.thread_content = db.session().query(ForumThread.content).filter(ForumThread.id == news.thread_id).first().content

	return render_template(
		'admin/news/edit.htm',
		news = news, characters = user.players, boards = boards
	)

@app.route('/admin/news/edit/<int:id>', methods=['POST'])
@admin_required
def route_admin_news_edit_post(id):
	news = News.query.filter(News.id == id).first()

	news.header = request.form.get('title', '')
	news.content = request.form.get('content', '')
	news.author_id = request.form.get('poster', 0)

	thread = ForumThread.query.filter(ForumThread.id == news.thread_id).first()
	thread.content = request.form.get('threadContent', '')

	db.session().commit()
	flash('The news has been edited.', 'success')

	return redirect(url_for('route_admin_news_manage'))

@app.route('/admin/news/delete/<int:id>', methods=['GET'])
@admin_required
def route_admin_news_delete(id):
	news = News.query.filter(News.id == id).first()
	thread = ForumThread.query.filter(ForumThread.id == news.thread_id).first()

	db.session().delete(news)
	db.session().delete(thread)

	db.session().commit()
	flash('The news has been deleted.', 'success')

	return redirect(url_for('route_admin_news_manage'))
