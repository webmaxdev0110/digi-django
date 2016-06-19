"""
PDF To Image Converter Class.
The base of this script was derived from the pdfpeek package by David Brenneman:
http://pypi.python.org/pypi/collective.pdfpeek
Simply wanted something in a single file. Could use a bit of adjustments in
how files are saved, but this was mostly playing around to see how previewing PDF files works.
Requires pyPDF and PIL to do the essential reading.
Usage:
    pdfimage = ConvertToImage()
    pdf = open('test.pdf').read()
    images = pdfimage.generate_images(pdf)
`images` will contain a tuple list of the raw image data as well as the location
of the file as a String for each page generated.
"""

import os
import subprocess
import StringIO
import logging
import sys
import pyPdf
from PIL import Image

logger = logging.getLogger('pdfConvertor')


class ConvertToImage(object):
    def __init__(self,
                 base_path='.',
                 quality='1',
                 graphicsAlphaBits='2',
                 textAlphaBits='1'):
        """
        `base_path` is the directory in which the images will be saved. Current by default
        `quality` should generally be pretty high, or you will get a very artifacted image.
        `graphicsAlphaBits` and `textAlphaBits` control the oversampling. Leave this as 4 unless
                            you know what you're doing.
        """

        self.base_path = base_path
        self.quality = quality
        self.graphicsAlphaBits = graphicsAlphaBits
        self.textAlphaBits = textAlphaBits

    def _options_to_list(self, page_number):
        first_page = page_number
        last_page = page_number

        return ["gs",
                # "-q",
                "-sDEVICE=jpeg",
                "-dJPEGQ=%s" % self.quality,
                "-dGraphicsAlphaBits=%s" % self.graphicsAlphaBits,
                "-dTextAlphaBits=%s" % self.textAlphaBits,
                "-dNumRenderingThreads=4"
                ] + \
               [
                   "-dFirstPage=%s" % first_page,
                   "-dLastPage=%s" % last_page,
                   "-sOutputFile=%stdout",
                   "-",
               ]

    def transform(self, pdf_data_string, page_number):
        image = None

        gs_cmd = self._options_to_list(page_number)

        gs_process = subprocess.Popen(gs_cmd, stdout=sys.stdout, stdin=subprocess.PIPE)
        gs_process.stdin.write(pdf_data_string)

        image = gs_process.communicate()[0]
        gs_process.stdin.close()

        return_code = gs_process.returncode
        if return_code > 0:
            logger.warn("Ghostscript process didn't quite work! Error Code: %s" % return_code)

        return image

    def generate_images(self, pdf_data_string):
        page_count = 0
        page_number = 0
        images = []
        pdf = None
        pdf_data_string = str(pdf_data_string)

        # Need to catch expected errors (not a PDF) here.
        try:
            pdf = pyPdf.PdfFileReader(StringIO.StringIO(pdf_data_string))
        except:
            logger.warn("Error opening PDF file.")

        if pdf.isEncrypted:
            try:
                decrypt = pdf.decrypt("")
                if decrypt == 0:
                    logger.warn("This PDF is password protected.")
            except NotImplementedError:
                logger.warn("Document uses an unsupported encryption method.")

        if pdf:
            page_count = pdf.getNumPages()

            if page_count > 0:
                for page in range(page_count):
                    # Humans don't understand a page number that's zero, well not most anyways.
                    page_number = page + 1
                    raw_image = self.transform(pdf_data_string, page_number)
                    output_file = os.path.join(self.base_path, "%s.jpg" % page_number)
                    # Use PIL to generate a jpeg from the raw data
                    image_thumb = Image.open(StringIO.StringIO(raw_image))
                    image_thumb.save(output_file, "JPEG")
                    images.append((image_thumb, output_file))

        return images