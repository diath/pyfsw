from flask import render_template, request, flash, redirect, url_for, get_flashed_messages, send_file
from werkzeug.utils import secure_filename

import re
import os
from time import time
from PIL import Image

from pyfsw import app, db
from pyfsw import UPLOAD_PATH
from pyfsw import current_user, login_required, is_guild_leader
from pyfsw import Player, Guild, GuildInvite, GuildMembership, GuildRank

@app.route('/community/guilds')
def route_community_guilds():
	guilds = Guild.query.all()
	return render_template('community/guilds/list.htm', guilds=guilds, user=current_user())

@app.route('/community/guild/<int:id>')
def route_community_guild(id):
	guild = Guild.query.filter(Guild.id == id).first()
	members = GuildMembership.query.filter(GuildMembership.guild_id == guild.id).all()
	invites = GuildInvite.query.filter(GuildInvite.guild_id == guild.id).all()
	return render_template('community/guilds/view.htm', guild=guild, members=members, invites=invites, leader=is_guild_leader(id))

@app.route('/community/guild/create', methods=['GET'])
@login_required
def route_community_guild_create():
	characters = current_user().players
	return render_template('community/guilds/create.htm', characters=characters)

@app.route('/community/guild/create', methods=['POST'])
@login_required
def route_community_guild_create_post():
	name = request.form.get('name', '', type=str)
	character = request.form.get('character', 0, type=int)
	motd = request.form.get('motd', '', type=str)
	user = current_user()
	error = False

	character = Player.query.filter(Player.id == character).first()
	if not character or character.account_id != user.id:
		flash('You can not create a guild with not your own character.')
		error = True

	if character and character.level < 100:
		flash('The character needs to be at least level 100.')
		error = True

	if character and character.getGuild():
		flash('The character can not be a member of another guild.')
		error = True

	if len(name) < 4 or len(name) > 32:
		flash('The guild name must be between 4 and 32 characters long.')
		error = True

	if re.compile('^[a-zA-Z]$').search(name):
		flash('The guild name may only contain latin characters and spaces (A-Z, a-z).')
		error = True

	if len(name.split(' ')) > 3:
		flash('The guild name may only consist of 3 words.')
		error = True

	guild = Guild.query.filter(Guild.name == name).first()
	if guild:
		flash('The guild name is taken by another guild.')
		error = True

	if error:
		return redirect(url_for('route_community_guild_create'))

	guild = Guild()
	guild.name = name
	guild.ownerid = character.id
	guild.creationdata = int(time())
	guild.motd = motd

	db.session().add(guild)
	db.session().commit()

	rank = db.session.query(GuildRank.id).filter(GuildRank.guild_id == guild.id).filter(GuildRank.level == 3).first()

	membership = GuildMembership()
	membership.player_id = character.id
	membership.guild_id = guild.id
	membership.rank_id = rank[0]

	db.session().add(membership)
	db.session().commit()

	return redirect(url_for('route_community_guild', id=guild.id))

@app.route('/community/guild/<int:id>/invite', methods=['GET'])
@login_required
def route_community_guild_invite(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/invite.htm', id=id)

@app.route('/community/guild/<int:id>/invite', methods=['POST'])
@login_required
def route_community_guild_invite_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	name = request.form.get('name', '', type=str)
	error = False

	player = Player.query.filter(Player.name == name).first()
	if not player:
		flash('The player you are trying to invite does not exist.')
		return redirect(url_for('route_community_guild', id=id))

	membership = GuildMembership.query.filter(GuildMembership.guild_id == id).filter(GuildMembership.player_id == player.id).first()
	if membership:
		flash('The player is already a member of your guild.')
		error = True

	invite = GuildInvite.query.filter(GuildInvite.guild_id == id).filter(GuildInvite.player_id == player.id).first()
	if invite:
		flash('The player is already invited to your guild.')
		error = True

	if not error:
		invite = GuildInvite()
		invite.player_id = player.id
		invite.guild_id = id

		db.session().add(invite)
		db.session().commit()

		flash('The player has been invited.')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/kick', methods=['GET'])
@login_required
def route_community_guild_kick(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	ranks = []
	for rank in GuildRank.query.filter(GuildRank.guild_id == id).all():
		ranks.append(rank.id)

	members = GuildMembership.query.filter(GuildMembership.guild_id == id).filter(GuildMembership.rank_id.notin_(ranks)).all()
	return render_template('community/guilds/kick.htm', id=id, members=members)

@app.route('/community/guild/<int:id>/kick', methods=['POST'])
@login_required
def route_community_guild_kick_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	player = request.form.get('id', 0, type=int)
	membership = GuildMembership.query.filter(GuildMembership.guild_id).filter(GuildMembership.player_id == player).first()
	if not membership:
		return redirect(url_for('route_community_guild', id=id))

	db.session().delete(membership)
	db.session().commit()

	flash('The player has been kicked from the guild.')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/ranks', methods=['GET'])
@login_required
def route_community_guild_ranks(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild'), id=id)

	ranks = GuildRank.query.filter(GuildRank.guild_id == id).all()
	if not ranks:
		return redirect(url_for('route_community_guild'), id=id)

	return render_template('community/guilds/ranks.htm', id=id, ranks=ranks)

@app.route('/community/guild/<int:id>/ranks', methods=['POST'])
@login_required
def route_community_guild_ranks_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild'), id=id)

	for level in range(1, 4):
		value = request.form.get('rank{}'.format(level), '', type=str)
		error = False

		if re.compile('^[a-zA-Z ]$').search(value):
			flash('The rank name may only contain latin characters and spaces (A-Z, a-z).')
			error = True

		if len(value) < 4 or len(value) > 16:
			flash('The rank name must be between 4 and 16 characters long.')
			error = True

		if not error:
			rank = GuildRank.query.filter(GuildRank.guild_id == id).filter(GuildRank.level == level).first()
			rank.name = value

		db.session().commit()

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/motd', methods=['GET'])
@login_required
def route_community_guild_motd(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	guild = Guild.query.filter(Guild.id == id).first()
	if not guild:
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/motd.htm', id=id, motd=guild.motd)

@app.route('/community/guild/<int:id>/motd', methods=['POST'])
@login_required
def route_community_guild_motd_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	guild = Guild.query.filter(Guild.id == id).first()
	if not guild:
		return redirect(url_for('route_community_guild', id=id))

	motd = request.form.get('motd', '', type=str)
	guild.motd = motd

	db.session().commit()
	flash('The guild description has been changed.')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/logo', methods=['GET'])
@login_required
def route_community_guild_logo(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/logo.htm', id=id)

@app.route('/community/guild/<int:id>/logo', methods=['POST'])
@login_required
def route_community_guild_logo_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	file = request.files.get('logo')
	error = False

	if file:
		name = secure_filename(file.filename)
		if len(name) == 0 or not '.' in name and not name.rsplit('.', 1)[1] in ['png', 'gif', 'jpg', 'jpeg']:
			flash('The file extension is not allowed.')
			error = True

		if len(file.getvalue()) > 3 * 1024 * 1024:
			flash('The file size exceeds the limit of 3 MB.')
			error = True

		if file.content_type not in ['image/png', 'image/gif', 'image/jpeg']:
			flash('The file format is not allowed.')
			error = True

		if not error:
			name = os.path.join(UPLOAD_PATH, '{}.png'.format(id))
			file.save(name)

			try:
				image = Image.open(name)
				image.thumbnail((128, 128), Image.ANTIALIAS)
				image.save(name)
			except Exception as e:
				flash('Failed to upload the file.')
				os.remove(name)
				print(e)
				error = True
	else:
		flash('Failed to upload the file.')
		error = True

	if not error:
		flash('The guild logo has been changed.')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/getlogo', methods=['GET'])
def route_community_guild_getlogo(id):
	path = os.path.join(UPLOAD_PATH, '{}.png'.format(id))
	if os.path.isfile(path):
		return send_file(path, 'image/png')

	return send_file(os.path.join(UPLOAD_PATH, 'default.png'), 'image/png')

@app.route('/community/guild/<int:id>/disband', methods=['GET'])
@login_required
def route_community_guild_disband(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/disband.htm', id=id)

@app.route('/community/guild/<int:id>/disband', methods=['POST'])
@login_required
def route_community_guild_disband_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	guild = Guild.query.filter(Guild.id == id).first()
	db.session().delete(guild)
	db.session().commit()

	return redirect(url_for('route_community_guilds'))
