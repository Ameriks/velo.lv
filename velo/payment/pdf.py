# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Spacer
from reportlab.lib.units import mm


from reportlab.lib.colors import HexColor
from reportlab.platypus import Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.barcode import code128

from io import BytesIO

from velo.payment.pdf_utils import BreakingParagraph


def numbers_in_latvian(number):
    str_number = ''
    names = {
        0: 'nulle', 1: 'viens', 2: 'divi', 3: 'trīs', 4: 'četri', 5: 'pieci', 6: 'seši', 7: 'septiņi', 8: 'astoņi', 9: 'deviņi',
        10: 'desmit', 11: 'vienpadsmit', 12: 'divpadsmit', 13: 'trīspadsmit', 14: 'četrpadsmit', 15: 'piecpadsmit',
        16: 'sešpadsmit', 17: 'septiņpadsmit', 18: 'astoņpadsmit', 19: 'deviņpadsmit',
        20: 'div', 30: 'trīs', 40: 'četr', 50: 'piec', 60: 'seš', 70: 'septiņ', 80: "astoņ", 90: 'deviņ'
    }
    number = abs(number)
    ones = number % 10
    tens = (number - ones) % 100
    hundreds = (number - number % 100) // 100
    if 0 < number < 100:
        if number == 0:
            str_number = names[ones]
        elif number < 10:
            str_number = names[number]
        if tens == 10:
            str_number = ('%s' % (names[tens+ones]))
        elif number < 100:
            str_number = ('%sdesmit %s' % (names[tens], '' if ones == 0 else names[ones]))
    elif hundreds == 1:
        str_number = 'viens simts ' + str_number
    elif number < 1000:
        str_number = ('%s simti ' % names[hundreds]) + str_number
    else:
        str_number = str(number)

    return str_number


class PS(ParagraphStyle):
    def __init__(self, name, parent=None, **kw):
        self.defaults.update({"fontName": "Ubuntu"})
        ParagraphStyle.__init__(self, name, parent, **kw)


normal = PS(name='normal', fontSize=8)


class InvoiceGenerator(object):
    invoice = None
    pdf = None
    doc = None
    top_widths = None
    elements = None
    styles = None
    months_lv = {1: "janvāris", 2: "februāris", 3: "marts", 4: "aprīlis", 5: "maijs", 6: "jūnijs", 7: "jūlijs",
                 8: "augusts", 9: "septembris", 10: "oktobris", 11: "novembris", 12: "decembris"}

    def __init__(self, invoice):
        self.invoice = invoice
        self.pdf = BytesIO()
        self.doc = SimpleDocTemplate(self.pdf, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=20, rightMargin=20, showBoundary=0)
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
        invoice_timestamp = self.invoice.get('invoice_date')

        invoice_date = "%d.gada %d.%s" % (invoice_timestamp.year, invoice_timestamp.day, self.months_lv.get(invoice_timestamp.month))
        title = "Rēķins"

        data = [['', Paragraph(title, self.styles.get('h1')), 'Nr.', self.invoice.get('name')],
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
            ['Samaksāt līdz', self.invoice.get('due_date').strftime('%Y-%m-%d'), '', '', '', '', ''],
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

        column_count = len(data[0])

        item_list = [''] * column_count
        item_list[3] = 'Kopā'

        final_amount_col = 5

        item_list[final_amount_col] = '{0:.2f}'.format(float(items_total_price))

        table_style.append(('SPAN', (3, len(data)), (final_amount_col-1, len(data)),),)
        data.append(item_list)

        item_list = [''] * column_count
        item_list[3] = 'Pavisam kopā'
        item_list[final_amount_col] = '{0:.2f}'.format(float(items_total_price))
        table_style.append(('SPAN', (3, len(data)), (final_amount_col-1, len(data)),),)
        table_style.append(('FONT', (3, len(data)), (-1, len(data)), 'UbuntuB'),)

        data.append(item_list)

        final_amount = items_total_price

        item_table = Table(data, colWidths=list((self.doc.width * 0.05,
                                                 self.doc.width * (0.31 + 0.08*4),
                                                 self.doc.width * 0.08)), )

        item_table.setStyle(TableStyle(table_style))

        self.elements.append(item_table)

        invoice_big = int(final_amount)
        invoice_small = (final_amount - invoice_big) * 100

        self.elements.append(Paragraph("%s %s un %i %s." % (
            numbers_in_latvian(invoice_big).capitalize(), self.invoice.get('currency'), invoice_small, "centi"), normal))

        self.elements.append(Spacer(2 * mm, 2 * mm))
        self.elements.append(code128.Code128("*%s*%s*" % (self.invoice.get('name'), str(final_amount)), humanReadable=1))

    def _build_footer(self):
        self.elements.append(Spacer(2 * mm, 2 * mm))
        self.elements.append(Paragraph("Rēķins sagatavots elektroniski un derīgs bez paraksta.", normal))

    def build(self):
        self._build_top()
        self._build_sender_top()
        self._build_receiver_top()
        self._build_info_top()
        self._build_items()
        self.elements.append(Spacer(10 * mm, 10 * mm))
        self.elements.append(Paragraph("", normal))

        self._build_footer()
        self.doc.build(self.elements)
        self.pdf.seek(0)
        return self.pdf
