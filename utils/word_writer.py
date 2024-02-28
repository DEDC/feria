# Python
import io
import re
from decimal import Decimal
from datetime import date
# python-openxl
from docx import Document
# Django
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.timezone import localtime
from django.utils import formats
# num2words
from num2words import num2words

def generate_physical_document(request_):
    f = open('static/docs/contrato_fisica.docx', 'rb')
    document = Document(f)
    buffer = io.BytesIO()
    price_places = request_.solicitud_lugar.aggregate(price=Sum('precio'))['price']
    price_iva = round(price_places * Decimal(0.16))
    month = formats.date_format(date.today(), 'F')
    day = formats.date_format(date.today(), 'j')
    data = {
        '<razon_social>': request_.nombre,
        '<address>': '{} {} {}'.format(request_.calle, request_.no_calle, request_.codigo_postal),
        '<colony>': request_.colonia,
        '<town>': request_.municipio,
        '<estate>': request_.get_estado_display(),
        '<rfc>': request_.rfc_txt.upper() if request_.rfc_txt else '',
        '<price_places>': intcomma(price_places),
        '<price_places_text>': num2words(price_places, lang='es').upper(),
        '<price_iva>': intcomma(price_iva),
        '<price_iva_text>': num2words(price_iva, lang='es').upper(),
        '<price_places_iva>': intcomma(price_places + price_iva),
        '<price_places_iva_text>': num2words(price_places + price_iva, lang='es').upper(),
        '<day>': day,
        '<month>': month,
        '<name_user>': request_.usuario.get_full_name()
    }
    for p in document.paragraphs:
        if '<table_places>' in p.text:
            table = document.add_table(rows=1, cols=5, style="Table Grid")
            heading_row = table.rows[0].cells
            # add headings
            heading_row[0].text = "No."
            heading_row[1].text = "Zona"
            heading_row[2].text = "m2"
            heading_row[3].text = "Licencia de Alcohol"
            heading_row[4].text = "Terraza"
            for place in request_.solicitud_lugar.all():
                row = table.add_row().cells
                row[0].text = place.nombre
                row[1].text = place.get_zona_display()
                row[2].text = str(place.m2)
                row[3].text = "Sí" if place.extras.filter(tipo='alcohol').exists() else 'No'
                row[4].text = "Sí" if place.extras.filter(tipo='terrazas').exists() else 'No'
            p._p.addnext(table._tbl)
            p.text = ''
        for k, v in data.items():
            regex = re.compile(k)
            paragraph_replace_text(p, regex, v)
    f.close()
    document.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    response["Content-Disposition"] = 'attachment; filename = "CONTRATO_{}.docx"'.format(request_.folio)
    return response


def paragraph_replace_text(paragraph, regex, replace_str):
    """Return `paragraph` after replacing all matches for `regex` with `replace_str`.

    `regex` is a compiled regular expression prepared with `re.compile(pattern)`
    according to the Python library documentation for the `re` module.
    """
    # --- a paragraph may contain more than one match, loop until all are replaced ---
    while True:
        text = paragraph.text
        match = regex.search(text)
        if not match:
            break

        # --- when there's a match, we need to modify run.text for each run that
        # --- contains any part of the match-string.
        runs = iter(paragraph.runs)
        start, end = match.start(), match.end()

        # --- Skip over any leading runs that do not contain the match ---
        for run in runs:
            run_len = len(run.text)
            if start < run_len:
                break
            start, end = start - run_len, end - run_len

        # --- Match starts somewhere in the current run. Replace match-str prefix
        # --- occurring in this run with entire replacement str.
        run_text = run.text
        run_len = len(run_text)
        run.text = "%s%s%s" % (run_text[:start], replace_str, run_text[end:])
        end -= run_len  # --- note this is run-len before replacement ---

        # --- Remove any suffix of match word that occurs in following runs. Note that
        # --- such a suffix will always begin at the first character of the run. Also
        # --- note a suffix can span one or more entire following runs.
        for run in runs:  # --- next and remaining runs, uses same iterator ---
            if end <= 0:
                break
            run_text = run.text
            run_len = len(run_text)
            run.text = run_text[end:]
            end -= run_len

    # --- optionally get rid of any "spanned" runs that are now empty. This
    # --- could potentially delete things like inline pictures, so use your judgement.
    # for run in paragraph.runs:
    #     if run.text == "":
    #         r = run._r
    #         r.getparent().remove(r)

    return paragraph