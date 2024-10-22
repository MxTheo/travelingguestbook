from io import BytesIO
from PIL import Image
from django import template
from django.urls import reverse
from qr_code.qrcode.maker import make_qr, QRCodeOptions

register = template.Library()

@register.simple_tag
def qr_url_from_url(url_name, *args, **kwargs):
    url = reverse(url_name, args=args, kwargs=kwargs)
    qr_code_options = QRCodeOptions(version=10, error_correction='L', size=30)
    qr_image = make_qr(url, qr_code_options=qr_code_options, force_text=True)
    qr_image_path = f"static/qr_codes/{url_name}.png"
    qr_image.save(qr_image_path)
    return qr_image_path
