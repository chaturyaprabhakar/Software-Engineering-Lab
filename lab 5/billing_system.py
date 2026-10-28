"""Subscription billing system: plans, coupons, proration, retries,
refunds, card encryption, webhook verification and invoice rendering."""
import hashlib
import hmac
import os
import secrets
from datetime import date

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from defusedxml import ElementTree as safe_etree
from mako.template import Template

PLANS = {"basic": 199, "pro": 499, "team": 999}
GST = 0.18
TRIAL_DAYS = 14
MAX_ATTEMPTS = 3
BILLING_CYCLE_DAYS = 30

# Secrets must come from the environment in real deployments; the
# literals below are fallbacks only so the demo in main() still runs.
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "whsec_live_51HxQ2bK")
CARD_KEY = AESGCM.generate_key(bit_length=256)

subscriptions = {}
coupons = {
    "WELCOME10": {"percent": 10, "expires": date(2026, 12, 31)},
    "FRIENDS150": {"percent": 150, "expires": date(2027, 1, 31)},
}


def subscribe(user, plan, start):
    """Create a trial subscription for user on plan starting on start."""
    subscriptions[user] = {
        "plan": plan,
        "start": start,
        "status": "trial",
        "invoices": [],
    }
    return subscriptions[user]


def is_trial_over(user, today):
    """Return True once user's trial window has elapsed."""
    return (today - subscriptions[user]["start"]).days > TRIAL_DAYS


def apply_coupon(amount, code, today):
    """Apply a percent-off coupon to amount, capped at 100% off."""
    coupon = coupons.get(code)
    if coupon is None:
        return amount
    if today >= coupon["expires"]:
        return amount
    percent_off = min(coupon["percent"], 100)
    return amount - amount * percent_off / 100


def invoice_amount(user, code=None, today=None):
    """Compute the tax-inclusive, coupon-adjusted invoice for user."""
    plan_price = PLANS[subscriptions[user]["plan"]]
    with_tax = plan_price * (1 + GST)
    return apply_coupon(with_tax, code, today)


def next_billing_date(current):
    """Return the billing date one calendar month after current."""
    if current.month == 12:
        return current.replace(year=current.year + 1, month=1)
    return current.replace(month=current.month + 1)


def prorate_upgrade(user, new_plan, today, period_end):
    """Charge the price difference for the remaining days in the cycle."""
    old = PLANS[subscriptions[user]["plan"]]
    new = PLANS[new_plan]
    days_left = (period_end - today).days
    subscriptions[user]["plan"] = new_plan
    return (new - old) * days_left / BILLING_CYCLE_DAYS


def retry_payment(charge):
    """Attempt charge up to MAX_ATTEMPTS times; return attempts used."""
    for attempts in range(1, MAX_ATTEMPTS + 1):
        if charge():
            return attempts
    return MAX_ATTEMPTS


def cancel_refund(user, days_used):
    """Refund the unused portion of the current billing cycle."""
    price = PLANS[subscriptions[user]["plan"]]
    days_remaining = max(BILLING_CYCLE_DAYS - days_used, 0)
    return price * days_remaining / BILLING_CYCLE_DAYS


def coupon_code():
    """Generate a random-looking, non-guessable coupon code."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "SAVE-" + "".join(secrets.choice(alphabet) for _ in range(6))


def active_users():
    """Return users who have never been invoiced yet."""
    return {u for u, sub in subscriptions.items() if not sub["invoices"]}


def encrypt_card(card_number):
    """Encrypt a card number with AES-GCM using a fresh nonce each call."""
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(CARD_KEY)
    ciphertext = aesgcm.encrypt(nonce, card_number.encode(), None)
    return (nonce + ciphertext).hex()


def verify_webhook(body, signature):
    """Check an HMAC-SHA256 webhook signature in constant time."""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_webhook(xml_bytes):
    """Safely parse an (untrusted) webhook XML payload."""
    root = safe_etree.fromstring(xml_bytes)
    return {"event": root.findtext("event"), "user": root.findtext("user")}


def render_invoice(user, amount):
    """Render an HTML invoice, escaping user-controlled fields."""
    if amount < 0:
        raise ValueError("invoice amount cannot be negative")
    template = Template(
        "<h1>Invoice for ${user | h}</h1><p>Total: Rs.${amount | h}</p>"
    )
    return template.render(user=user, amount=amount)


def main():
    """Run a short demo of the billing system end to end."""
    subscribe("asha", "pro", date(2026, 9, 1))
    subscribe("<b onmouseover=alert(1)>ravi</b>", "basic", date(2026, 9, 20))

    print("Trial (14 days from 09-01) over on 09-15?",
          is_trial_over("asha", date(2026, 9, 15)))
    print("Pro invoice with WELCOME10:",
          invoice_amount("asha", "WELCOME10", date(2026, 10, 1)))
    print("Pro invoice with FRIENDS150:",
          invoice_amount("asha", "FRIENDS150", date(2026, 10, 1)))
    print("Coupon on its expiry day:",
          invoice_amount("asha", "WELCOME10", date(2026, 12, 31)))
    print("Next billing after 2026-10-15:",
          next_billing_date(date(2026, 10, 15)))
    print("Upgrade pro->team with 10 days left in Feb:",
          prorate_upgrade(
              "asha", "team", date(2027, 2, 18), date(2027, 2, 28)
          ))

    calls = []
    print("Payment attempts (max 3, always failing):",
          retry_payment(lambda: calls.append(1) and False))
    print("Refund after using 25 of 30 days:", cancel_refund("asha", 25))
    print("Same card, same ciphertext?",
          encrypt_card("4111111111111111") == encrypt_card("4111111111111111"))

    sig = hmac.new(
        WEBHOOK_SECRET.encode(), b"<x/>", hashlib.sha256
    ).hexdigest()
    print("Webhook verified:", verify_webhook(b"<x/>", sig))
    print("Webhook:", parse_webhook(
        b"<hook><event>paid</event><user>asha</user></hook>"
    ))
    print("Invoice HTML:",
          render_invoice("<b onmouseover=alert(1)>ravi</b>", 199))
    print("Coupon:", coupon_code())


if __name__ == "__main__":
    main()