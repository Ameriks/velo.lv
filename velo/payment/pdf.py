import os
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Spacer, Image
from reportlab.lib.units import mm


from reportlab.lib.colors import HexColor
from reportlab.platypus import Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.barcode import code128

from io import BytesIO

from velo.core.pdf import InvoiceCanvas
from velo.payment.pdf_utils import BreakingParagraph
from velo.payment.skaitlis import num_to_text

class PS(ParagraphStyle):
    def __init__(self, name, parent=None, **kw):
        self.defaults.update({"fontName": "Ubuntu"})
        ParagraphStyle.__init__(self, name, parent, **kw)


normal = PS(name='normal', fontSize=8)


class InvoiceGenerator(object):
    invoice = None
    competition = None
    payment = None
    pdf = None
    doc = None
    top_widths = None
    elements = None
    styles = None
    months_lv = {1: "janvāris", 2: "februāris", 3: "marts", 4: "aprīlis", 5: "maijs", 6: "jūnijs", 7: "jūlijs",
                 8: "augusts", 9: "septembris", 10: "oktobris", 11: "novembris", 12: "decembris"}

    def __init__(self, invoice_data, competition, payment=None):
        self.invoice = invoice_data
        self.competition = competition
        self.payment = payment
        self.pdf = BytesIO()
        self.doc = SimpleDocTemplate(self.pdf, pagesize=A4, topMargin=15, bottomMargin=80, leftMargin=15, rightMargin=15, showBoundary=0)
        self.elements = []

        self.styles = {
            'h1': PS(name='Heading1', fontSize=14, leading=16, alignment=TA_CENTER),
            'normal': PS(name='normal', fontSize=8),
        }
        self.top_widths = list((self.doc.width * 0.15, self.doc.width * 0.30, self.doc.width * 0.15,
                                self.doc.width * 0.1, self.doc.width * 0.05, self.doc.width * 0.10,
                                self.doc.width * 0.15,), )

    def _build_top(self):
        width = self.doc.width
        invoice_date = self.invoice.get('invoice_date')

        if self.payment and self.payment.status != 30:
            title = "Avansa rēķins"
        else:
            title = "Rēķins"

        im = None
        if self.invoice.get('organiser_data').get('logo'):
            adv = os.path.join(settings.MEDIA_ROOT, "adverts", self.invoice.get('organiser_data').get('logo'))
            im = Image(adv, 100, 35)
        # self.elements.append(im)

        data = [[im if im else '', Paragraph(title, self.styles.get('h1')), 'Nr.', self.invoice.get('name')],
                ['', invoice_date, '', '']]

        header_table = Table(data, colWidths=list((width / 4.0, width / 2.0, width / 16.0, (width * 3) / 16.0,), ))
        header_table.setStyle(
            TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (3, 0), (3, 0), 'LEFT'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (3, 0), (3, 0), 0.25, colors.darkgray),
                ('FONT', (0, 0), (-1, -1), 'Ubuntu'),
                ('SPAN', (0, 0), (0, 1)),
            ]))
        self.elements.append(header_table)

    def _build_sender_top(self):
        organiser_data = self.invoice.get('organiser_data')
        data = [
            ['Pakalpojumu sniedzējs', organiser_data.get('name'), '', '', '', 'Reģ.nr.', organiser_data.get('number')],
            ['Juridiskā adrese', organiser_data.get('juridical_address'), '', '', '', 'PVN reģ.nr.',
             organiser_data.get('vat')], ]

        data.append(['Norēķinu rekvizīti', organiser_data.get('account_name'), organiser_data.get('account_code'), 'Konts', '%s %s' % (organiser_data.get('account_number'), self.invoice.get('currency'))])

        self.elements.append(Table(data, colWidths=self.top_widths, style=TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONT', (0, 0), (-1, -1), 'Ubuntu'),
            ('ALIGN', (5, 0), (5, 1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONT', (1, 0), (1, -1), 'UbuntuB'),
            ('FONT', (6, 0), (6, 1), 'UbuntuB'),
            ('SPAN', (1, 0), (4, 0),),
            ('SPAN', (1, 1), (4, 1),),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.darkgray),
        ])))

    def _build_receiver_top(self):
        client_data = self.invoice.get('client_data')
        data = [
            ['Pakalpojumu saņēmējs', client_data.get('name'), '', '', '', '', ''],
            ['Juridiskā adrese', client_data.get('juridical_address'), '', '', '', 'Reģ.nr.',
             client_data.get('number')],
            ['Pasta adrese', client_data.get('office_address'), '', '', '', 'PVN reģ.nr.', client_data.get('vat')],
        ]

        self.elements.append(Table(data, colWidths=self.top_widths, style=TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Ubuntu'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('SPAN', (1, 0), (4, 0),),
            ('SPAN', (1, 1), (4, 1),),
            ('SPAN', (1, 2), (4, 2),),
            ('FONT', (1, 0), (1, 2), 'UbuntuB'),
            ('FONT', (6, 1), (6, 2), 'UbuntuB'),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.darkgray),
        ])))

    def _build_info_top(self):

        data = [
            ['Saimn. darījums', self.invoice.get('activity'), '', 'Speciālās atzīmes', '', '', ''],
            ['Samaksas veids', self.invoice.get('payment_type'), '', Paragraph(self.invoice.get('comments'), self.styles.get('normal')), '', '', ''],
            ['Samaksāt līdz', self.invoice.get('due_date'), '', '', '', '', ''],
        ]

        self.elements.append(Table(data, colWidths=self.top_widths, style=TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Ubuntu'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),

            ('SPAN', (1, 0), (2, 0),),
            ('SPAN', (1, 1), (2, 1),),
            ('SPAN', (1, 2), (2, 2),),

            ('SPAN', (3, 0), (6, 0),),
            ('SPAN', (3, 1), (6, 2),),
            ('VALIGN', (3, 1), (-1, -1), 'TOP'),

            ('LINEBEFORE', (3, 0), (3, -1), 0.5, colors.darkgray),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.darkgray),
        ])))

    def _build_items(self):
        table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(0xededed)),
                ('FONT', (0, 0), (-1, 0), 'UbuntuB'),
                ('FONT', (0, 1), (-1, -1), 'Ubuntu'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, len(self.invoice.get('items'))), 0.25, colors.darkgray),
                ('INNERGRID', (0, 0), (-1, len(self.invoice.get('items'))), 0.25, colors.darkgray)
            ]

        columns = [
            ('order', 'Nr.\nP.K.'),
            ('description', 'Nosaukums'),
            ('units', 'Mēr-\nvienība'),
            ('amount', 'Daudz.'),
            ('price', 'Cena'),
            ('total_round', 'Summa, %s' % self.invoice.get('currency')),
        ]

        data = []
        data.append([Paragraph(title, self.styles.get('normal')) for col, title in columns])
        items_total_price = 0
        item_order = 0
        for item in self.invoice.get('items'):
            item_order += 1
            item_list = []
            for col, title in columns:
                val = item.get(col)
                if col == 'order' and val is None:
                    val = str(item_order)
                elif col == 'code' and val is None:
                    val = ""
                elif col in ('amount', 'price'):
                    if val == int(val):
                        val = int(val)
                    elif round(int(val), 6) == round(int(val), 2):
                        val = round(int(val), 2)
                elif col == 'total_round':
                    total = float(item.get('amount')) * float(item.get('price'))
                    val = '{0:.2f}'.format(float(total))
                    items_total_price += total
                item_list.append(BreakingParagraph(str(val), self.styles.get('normal')))
            data.append(item_list)

        final_amount = items_total_price
        invoice_big = int(final_amount)
        invoice_small = (final_amount - invoice_big) * 100

        column_count = len(data[0])

        item_list = [''] * column_count

        item_list[1] = Paragraph("%s %s un %i %s." % (
            num_to_text(invoice_big).capitalize(), self.invoice.get('currency'), invoice_small, "centi"), normal)

        item_list[3] = 'Kopā'

        final_amount_col = 5

        item_list[final_amount_col] = '{0:.2f}'.format(float(items_total_price))

        table_style.append(('SPAN', (3, len(data)), (final_amount_col-1, len(data)),),)
        data.append(item_list)

        if self.invoice.get('organiser_data', {}).get('vat'):

            bez_pvn = round(items_total_price / 1.21, 2)
            pvn = round(float(items_total_price) - bez_pvn, 2)

            item_list = [''] * column_count
            item_list[3] = 'Cena bez PVN'
            final_amount_col = 5
            item_list[final_amount_col] = '{0:.2f}'.format(bez_pvn)
            table_style.append(('SPAN', (3, len(data)), (final_amount_col-1, len(data)),),)
            data.append(item_list)

            item_list = [''] * column_count
            item_list[3] = 'PVN 21%'
            final_amount_col = 5
            item_list[final_amount_col] = '{0:.2f}'.format(pvn)
            table_style.append(('SPAN', (3, len(data)), (final_amount_col-1, len(data)),),)
            data.append(item_list)



        item_list = [''] * column_count

        item_list[1] = Paragraph("Rēķins sagatavots elektroniski un derīgs bez paraksta.", normal)

        item_list[3] = 'Pavisam kopā'
        item_list[final_amount_col] = '{0:.2f}'.format(float(items_total_price))
        table_style.append(('SPAN', (3, len(data)), (final_amount_col-1, len(data)),),)
        table_style.append(('FONT', (3, len(data)), (-1, len(data)), 'UbuntuB'),)

        data.append(item_list)

        item_table = Table(data, colWidths=list((self.doc.width * 0.05,
                                                 self.doc.width * (0.31 + 0.08*4),
                                                 self.doc.width * 0.08)), )

        item_table.setStyle(TableStyle(table_style))

        self.elements.append(item_table)

        self.elements.append(Spacer(2 * mm, 2 * mm))

        data = [
            [code128.Code128("*%s*%s*" % (self.invoice.get('name'), str(final_amount)), humanReadable=1),
             'Vēlam veiksmīgu un pozitīvām emocijām bagātu sezonu!']
        ]

        bottom_table = Table(data, colWidths=(self.doc.width*0.3, self.doc.width*0.7))
        bottom_table.setStyle(
            TableStyle([
                ('FONT', (0, 0), (-1, -1), 'UbuntuB'),
                ('SIZE', (0, 0), (-1, -1), 14),
            ]))

        self.elements.append(bottom_table)

    def _build_footer(self):
        if self.competition.id in (89, 90, 91, 92, 93, 94, 95, 96, 97):
            adv = os.path.join(settings.MEDIA_ROOT, "adverts", "2019_invoice_adv_toyota.jpg")
            im = Image(adv, 567, 90)
            self.elements.append(im)

    def build(self):
        self._build_top()
        self._build_sender_top()
        self._build_receiver_top()
        self._build_info_top()
        self._build_items()
        self.elements.append(Spacer(10 * mm, 10 * mm))
        # self.elements.append(Paragraph("", normal))
        self._build_footer()

        self.doc.build(self.elements, canvasmaker=InvoiceCanvas)
        self.pdf.seek(0)
        return self.pdf
