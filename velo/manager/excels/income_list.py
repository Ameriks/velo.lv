from io import BytesIO

import xlwt

from velo.core.models import Competition
from velo.payment.models import Transaction
from django.db import connection


def create_income_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)

    cursor = connection.cursor()
    cursor.execute("""
Select to_char(tr.created, 'YYYY-MM-DD') as diena, pay.competition_id, sum(tr.amount) from payment_transaction tr 
left outer join payment_payment pay on pay.id = tr.payment_id
where pay.competition_id in %s and tr.status=%s
group by diena, pay.competition_id
order by diena, pay.competition_id""", [competition.get_ids(), Transaction.STATUSES.ok])

    competition_mapping = {competition.id: str(competition), competition.parent_id: str(competition.parent)}

    output = BytesIO()

    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet("Sheet")
    sheet.write(0, 0, "Datums")
    sheet.write(0, 1, "Sacensības")
    sheet.write(0, 2, "Ienākošie banku maksājumi")
    for index, row in enumerate(cursor.fetchall(), start=1):
        sheet.write(index, 0, row[0])
        sheet.write(index, 1, competition_mapping.get(row[1]))
        sheet.write(index, 2, row[2])
    wbk.save(output)
    return output
