import os
import magic
from django.core.exceptions import ValidationError

def validate_pdf_file(file):
    valid_mime_types = ['application/pdf']
    file_mime_type = magic.from_buffer(file.read(2048), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError('No se guardó este documento ya que es de un tipo inválido', code = 'invalid_file_type')

def validate_jpg_file(file):
    valid_mime_types = ['image/jpeg', 'image/jpg']
    file_mime_type = magic.from_buffer(file.read(2048), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError('No se guardó este documento ya que es de un tipo inválido', code = 'invalid_file_type')

def validate_gif_file(file):
    valid_mime_types = ['image/gif']
    file_mime_type = magic.from_buffer(file.read(2048), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError('No se guardó este documento ya que es de un tipo inválido', code = 'invalid_file_type')