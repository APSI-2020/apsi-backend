from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_JUSTIFY
from datetime import datetime
import io


class TicketPdfGenerator:
    def generate(self, participant, event):
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        payload = dict(participant_id=participant.id, event_id=event.id)
        qrw = QrCodeWidget(payload)

        # getBounds returns boundary as array: b[0], b[1], b[2], b[3] = x1, y1, x2, y2
        b = qrw.getBounds()

        width = b[2] - b[0]
        height = b[3] - b[1]

        d = Drawing(290, 290, transform=[290. / width, 0, 0, 290. / height, 0, 0])
        d.add(qrw)
        im = Image(d, 2 * inch, 2 * inch)

        pdfmetrics.registerFont(TTFont('Verdana', 'Vera.ttf'))
        pdfmetrics.registerFont(TTFont('Verdana-Bold', 'VeraBd.ttf'))
        pdfmetrics.registerFont(TTFont('Verdana-Italic', 'VeraIt.ttf'))
        pdfmetrics.registerFont(TTFont('Verdana-BoldItalic', 'VeraBI.ttf'))
        addMapping('verdana', 0, 0, 'Verdana')
        addMapping('verdana', 1, 0, 'Verdana-Bold')
        addMapping('verdana', 0, 1, 'Verdana-Italic')
        addMapping('verdana', 1, 1, 'Verdana-BoldItalic')

        story = []
        start_date = event.start.strftime("%d/%m/%Y %H:%M")
        end_date = event.end.strftime("%d/%m/%Y %H:%M")
        now_dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', fontSize=10, leading=12, alignment=TA_JUSTIFY, fontName='Verdana'))
        styles.add(ParagraphStyle(name='Standard', fontSize=10, leading=12, fontName='Verdana'))
        ptext = '<font size="12">Wygenerowano dnia: %s</font>' % now_dt_string
        story.append(Paragraph(ptext, styles["Standard"]))
        story.append(Spacer(1, 12))
        ptext = '<font size="12">Użytkownik: %s</font>' % participant.get_full_name()
        story.append(Paragraph(ptext, styles["Standard"]))
        story.append(Spacer(1, 24))
        ptext = u'<font size="12">To jest twoja wejściówka na wydarzenie <b>%s</b>! \
                Podczas wydarzenia możesz zostać poproszony o pokazanie wejściówki, dlatego \
                pamiętaj aby mieć ją zawsze przy sobie. Wejściówkę możesz wydrukować lub \
                okazać na urządzeniu elektronicznym.</font>' % event.name
        story.append(Paragraph(ptext, styles["Justify"]))
        story.append(Spacer(1, 12))
        ptext = '<font size="12">Start wydarzenia: %s</font>' % start_date
        story.append(Paragraph(ptext, styles["Justify"]))
        ptext = '<font size="12">Koniec: %s</font>' % end_date
        story.append(Paragraph(ptext, styles["Standard"]))
        story.append(Spacer(1, 60))
        story.append(im)

        doc.build(story)

        buffer.seek(0)

        return buffer
