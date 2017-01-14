from django.http import HttpResponse
from django.shortcuts import render
import os
# Create your views here.
from django.views.generic import View
from PIL import (
    ImageFont,
    ImageDraw,
    Image,
)
from django.conf import settings



class SignatureView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        style=kwargs.get('style', 'swift')
        text=kwargs.get('text', 'Welcome to emondo.io')
        # Prepend a space to deal with
        # letter "J" to be drawn off canvas
        text = ' ' + text + ' '
        style_to_font = {
            'swift': 'MsSwift6.ttf',
            'lincoln': 'Lincoln8.ttf',
            'steve': 'SteveJobsFin6.ttf'
        }
        font_name = style_to_font.get(style, 'MsSwift6.ttf')
        # Render the text 4 times larger and shrink down to original size
        # to get antialias
        rendering_multiply = 4
        c_h = 330 * rendering_multiply
        fontsize = 10  # starting font canvas_size
        # portion of image width you want text width to be
        img_fraction = 0.7
        fonts_path = os.path.join(settings.BASE_DIR, 'static/fonts')
        font_path = os.path.join(fonts_path, font_name)
        font = ImageFont.truetype(font_path, fontsize)
        while font.getsize(text)[1] < img_fraction * c_h:
            # iterate until the text canvas_size is just larger than the criteria
            fontsize += 1
            font = ImageFont.truetype(font_path, fontsize)

        f_w, f_h = font.getsize(text)

        # optionally de-increment to be sure it is less than criteria
        #fontsize -= 1
        #font = ImageFont.truetype(font_path, fontsize)

        c_w = f_w + 100
        canvas_size = (c_w, c_h)
        image = Image.new('RGBA', canvas_size, (255, 255, 255, 0,))
        draw = ImageDraw.Draw(image)

        draw.text(((c_w - f_w) / 2, (c_h - f_h) / 2), text, font=font, fill=(0,0,0,))

        response = HttpResponse(content_type="image/png")
        image = image.resize((c_w / rendering_multiply, c_h / rendering_multiply,), resample=Image.ANTIALIAS)
        image.save(response, "png")
        return response
