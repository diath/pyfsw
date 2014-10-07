from flask import session, Response

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from random import randint
from io import BytesIO

from pyfsw import app, db
from pyfsw import FONT_PATH

@app.route('/captcha')
def route_captcha():
	code = ''
	while len(code) < 5:
		code += chr(randint(65, 90))

	session['captcha'] = code.lower()
	code = list(code)

	image = Image.new(mode='RGBA', size=(168, 30), color=(255, 255, 255, 255))
	font  = ImageFont.truetype(FONT_PATH, 20)
	draw  = ImageDraw.Draw(image)

	x = randint(15, 25)
	y = 0

	for char in code:
		y = randint(1, 5)
		c = (randint(25, 150), randint(25, 150), randint(25, 150))

		draw.text((x, y), char, c, font=font)
		x += randint(15, 35)

	buffer = BytesIO()
	image.save(buffer, format='PNG')
	buffer = buffer.getvalue()

	return Response(buffer, content_type='image/png; charset=UTF-8')
