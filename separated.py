from flask import Flask, jsonify, request, session

app = Flask(__name__)


class AuthError(Exception):
    pass


class EmailValidationError(Exception):
    pass


class InvalidEmailDomain(Exception):
    pass


class MaxVoucherException(Exception):
    pass


class VoucherAlreadySent(Exception):
    pass


AVAILABLE_DOMAINS = ["test.com", "db.test"]
MAX_VOUCHERS = 3


class Email:
    def __init__(self, email_address: str):
        if "@" not in email_address:
            raise EmailValidationError()
        self.address = email_address

    @property
    def domain(self):
        return self.address.split("@")[1]


class Voucher:
    customer_id: int
    points: int
    is_active: bool


class VoucherSender:
    customer_id: int
    emails: list[str]

    def _check_send(self, email: Email) -> None:
        if email.address in self.emails:
            raise VoucherAlreadySent()
        if len(self.emails) >= MAX_VOUCHERS:
            raise MaxVoucherException()

    def register(self, email: Email, points: int) -> Voucher:
        self._check_send(email)
        self.emails.append(email.address)
        return Voucher(points=points, customer_id=self.customer_id)


def calculate_points(is_vip: bool) -> int:
    return 10 if is_vip else 3


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


def send_voucher(customer: Customer, email: Email):
    voucher_sender = (
        session.query(VoucherSender).filter_by(customer_id=customer.id).first()
    )
    if not voucher_sender:
        voucher_sender = VoucherSender(emails=[], customer_id=customer.id)
        session.add(voucher_sender)
        session.flush()
    voucher_sender.register(email, calculate_points(customer.is_vip))
    send_voucher_mail(email)


def get_vouchers(customer_id: int, **filters):
    vouchers = session.query(Voucher).filter_by(customer_id=customer_id)
    if filters:
        vouchers = vouchers.filter_by(**filters)
    return vouchers


@app.route("/vouchers", methods=["POST"])
def send_voucher(self):
    current_customer = get_customer(request)
    if not current_customer:
        raise AuthError()
    email = Email(request.data["email"])
    if email.domain not in AVAILABLE_DOMAINS:
        raise InvalidEmailDomain()
    send_voucher(current_customer, email)


@app.route("/vouchers", methods=["GET"])
def vouchers(self):
    current_customer = get_customer(request)
    if not current_customer:
        raise AuthError()
    is_active = bool(request.args.get("is_active", 0))
    vouchers = get_vouchers(current_customer.id, is_active=is_active)
    return jsonify([{"is_active": v.is_active, "points": v.points} for v in vouchers])
