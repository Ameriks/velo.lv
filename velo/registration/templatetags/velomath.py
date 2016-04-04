from django import template
from payment.utils import get_participant_fee_from_price, get_insurance_fee_from_insurance

register = template.Library()


@register.filter(is_safe=False)
def addfloat(value, arg):
    """Adds the arg to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        try:
            return value + arg
        except Exception:
            return ''


@register.filter(is_safe=False)
def getParticipationFeePrice(price, competition):
    return get_participant_fee_from_price(competition, price)


@register.filter(is_safe=False)
def getInsurancePrice(insurance, competition):
    if not insurance:
        return None
    return get_insurance_fee_from_insurance(competition, insurance)

