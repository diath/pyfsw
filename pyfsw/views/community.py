from flask import render_template, request

from pyfsw import app, db
from pyfsw import QUESTS, TOWNS, HOUSE_PRICE
from pyfsw import Player, PlayerStorage, House

@app.route('/community/player', methods=['GET'])
def route_community_player_get():
	return render_template('community/player_search.htm')

@app.route('/community/player/<string:name>')
def route_community_player_get_name(name):
	player = Player.query.filter(Player.name == name).first()

	if player is None:
		return render_template('community/player_search.htm', error=True)

	return render_template('community/player_view.htm', player=player, quests=QUESTS)

@app.route('/community/player', methods=['POST'])
def route_community_player_post():
	name = request.form.get('name', '', type=str)
	player = Player.query.filter(Player.name == name).first()

	if player is None:
		return render_template('community/player_search.htm', error=True)

	return render_template('community/player_view.htm', player=player, quests=QUESTS)

@app.route('/community/highscores/<string:type>')
def route_community_highscores(type):
	highscores = Player.query.filter(Player.group_id == 1)
	name = 'Level'

	if type == 'maglevel':
		highscores = highscores.order_by(Player.manaspent.desc())
		name = 'Magic Level'
	elif type == 'fist':
		highscores = highscores.order_By(Player.skill_fist.desc())
		name = 'Club Fighting'
	else:
		highscores = highscores.order_by(Player.experience.desc())

	highscores = highscores.limit(100).all()
	return render_template('community/highscores.htm', type=type, name=name, highscores=highscores)

@app.route('/community/houses/<int:town_id>')
def route_community_houses(town_id):
	houses = House.query.order_by(House.id)

	if town_id != 0:
		houses = houses.filter(House.town_id == town_id)

	return render_template('community/houses.htm', towns=TOWNS, town_id=town_id, price=HOUSE_PRICE, houses=houses.all())

@app.route('/community/staff')
def route_community_staff():
	gms = Player.query.filter(Player.group_id == 3).all()
	tutors = Player.query.filter(Player.group_id == 2).all()

	return render_template('community/staff.htm', gms=gms, tutors=tutors)
