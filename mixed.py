from flask import Flask, jsonify, request, session

app = Flask(__name__)


class AuthError(Exception):
    pass


class InvalidEmailDomain(Exception):
    pass


class MaxVoucherException(Exception):
    pass


class VoucherAlreadySent(Exception):
    pass


class Voucher:
    customer_id: int
    points: int
    is_active: bool
    email: str


class Customer:
    id: int
    is_vip: bool


def get_customer_id_from_token(request):
    customer_id = ...  # get from token
    return customer_id


def get_customer(request, session):
    customer_id = get_customer_id_from_token(request)
    return session.query(Customer).get(customer_id)


def send_voucher_mail(email: str) -> None:
    # send email with voucher
    return


AVAILABLE_DOMAINS = ["test.com", "db.test"]
MAX_VOUCHERS = 3


@app.route("/vouchers", methods=["POST"])
def send_voucher(self):
    current_customer = get_customer(request)
    if not current_customer:
        raise AuthError()

    email = request.get_json()["email"]
    if email.split("@")[1] not in AVAILABLE_DOMAINS:
        raise InvalidEmailDomain()

    if (
        session.query(Voucher).filter_by(customer_id=current_customer.id)
        >= MAX_VOUCHERS
    ):
        raise MaxVoucherException()
    if (
        session.query(Voucher)
        .filter_by(customer_id=current_customer.id, email=email)
        .first()
    ):
        raise VoucherAlreadySent()
    voucher_points = 10 if current_customer.is_vip else 3
    voucher = Voucher(points=voucher_points, customer_id=current_customer.id)
    session.add(voucher)
    session.commit()
    send_voucher_mail(email)


@app.route("/vouchers", methods=["GET"])
def vouchers(self):
    current_customer = get_customer(request)
    if not current_customer:
        raise AuthError()

    is_active = bool(request.args.get("is_active", 0))
    vouchers = session.query(Voucher).filter_by(customer_id=current_customer.id)
    if is_active:
        vouchers = vouchers.filter_by(is_active=is_active)
    return jsonify([{"is_active": v.is_active, "points": v.points} for v in vouchers])
