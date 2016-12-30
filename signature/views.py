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
        style_to_font = {
            'swift': 'MsSwift6.ttf',
            'lincoln': 'Lincoln8.ttf',
            'steve': 'SteveJobsFin6.ttf'
        }
        font_name = style_to_font.get(style, 'MsSwift6.ttf')
        c_w, c_h = canvas_size = (800, 330,)

        image = Image.new('RGBA', canvas_size, (255, 255, 255, 0,))
        draw = ImageDraw.Draw(image)
        fontsize = 10  # starting font canvas_size
        # portion of image width you want text width to be
        img_fraction = 0.7
        fonts_path = os.path.join(settings.BASE_DIR, 'static/fonts')
        font_path = os.path.join(fonts_path, font_name)
        font = ImageFont.truetype(font_path, fontsize)
        while font.getsize(text)[0] < img_fraction * image.size[0]:
            # iterate until the text canvas_size is just larger than the criteria
            fontsize += 1
            font = ImageFont.truetype(font_path, fontsize)

        f_w, f_h = font.getsize(text)

        # optionally de-increment to be sure it is less than criteria
        fontsize -= 1
        font = ImageFont.truetype(font_path, fontsize)
        draw.text(((c_w - f_w) / 2, (c_h - f_h) / 2), text, font=font, fill=(0,0,0,))

        watermark = Image.new("RGBA", image.size)
        # Get an ImageDraw object so we can draw on the image
        waterdraw = ImageDraw.ImageDraw(watermark, "RGBA")
        # Place the text at (10, 10) in the upper left corner. Text will be white.
        waterdraw.text((10, 10), "The Image Project", fill=(0,0,0,0))

        # Get the watermark image as grayscale and fade the image
        # See <http://www.pythonware.com/library/pil/handbook/image.htm#Image.point>
        #  for information on the point() function
        # Note that the second parameter we give to the min function determines
        #  how faded the image will be. That number is in the range [0, 256],
        #  where 0 is black and 256 is white. A good value for fading our white
        #  text is in the range [100, 200].
        watermask = watermark.convert("L").point(lambda x: min(x, 100))
        # Apply this mask to the watermark image, using the alpha filter to
        #  make it transparent
        watermark.putalpha(watermask)
        # Paste the watermark (with alpha layer) onto the original image and save it
        image.paste(watermark, None, watermark)
        response = HttpResponse(content_type="image/png")
        image.save(response, "png")
        return response
