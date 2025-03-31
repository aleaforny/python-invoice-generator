import requests
import json
import pytz
import locale
from locale import getlocale
from tzlocal import get_localzone

from datetime import datetime


class InvoiceClientConfig:
    api_key: str
    date_format: str
    locale: str | None
    timezone: str
    endpoint_url: str

    def __init__(
        self,
        api_key: str,
        date_format: str = "%d %b %Y",
        locale: str | None = getlocale()[0] or None,
        timezone: str = str(get_localzone()),
        endpoint_url: str = "https://invoice-generator.com",
    ):
        self.api_key = api_key
        self.date_format = date_format
        self.locale = locale
        self.timezone = timezone
        self.endpoint_url = endpoint_url


class InvoiceGenerator:
    """API Object for Invoice-Generator tool - https://invoice-generator.com/"""

    # Below are the default template parameters that can be changed (see https://github.com/Invoiced/invoice-generator-api/)
    TEMPLATE_PARAMETERS = [
        "header",
        "to_title",
        "ship_to_title",
        "invoice_number_title",
        "date_title",
        "payment_terms_title",
        "due_date_title",
        "purchase_order_title",
        "quantity_header",
        "item_header",
        "unit_cost_header",
        "amount_header",
        "subtotal_title",
        "discounts_title",
        "tax_title",
        "shipping_title",
        "total_title",
        "amount_paid_title",
        "balance_title",
        "terms_title",
        "notes_title",
    ]

    def __init__(
        self,
        config: InvoiceClientConfig,
        sender: str,
        to: str,
        logo=None,
        ship_to=None,
        number=None,
        payments_terms=None,
        due_date=None,
        notes: str | None = None,
        terms=None,
        currency: str = "USD",
        date: datetime | None = None,
        discounts: float = 0,
        tax: float = 0,
        shipping: float = 0,
        amount_paid: float = 0,
    ):
        """Object constructor"""
        self.logo = logo
        self.config = config
        self.sender = sender
        self.to = to
        self.ship_to = ship_to
        self.number = number
        self.currency = currency
        self.custom_fields = []
        self.date = date or datetime.now(tz=pytz.timezone(self.config.timezone))
        self.payment_terms = payments_terms
        self.due_date = due_date
        self.items = []
        self.fields = {"tax": "%", "discounts": False, "shipping": False}
        self.discounts = discounts
        self.tax = tax
        self.shipping = shipping
        self.amount_paid = amount_paid
        self.notes = notes
        self.terms = terms
        self.template = {}

    def _to_json(self):
        """
        Parsing the object as JSON string
        Please note we need also to replace the key sender to from, as per expected in the API but incompatible with from keyword inherent to Python
        We are formatting here the correct dates
        We are also resetting the two list of Objects items and custom_fields so that it can be JSON serializable
        Finally, we are handling template customization with its dict
        """
        locale.setlocale(locale.LC_ALL, self.config.locale)
        object_dict = self.__dict__.copy()
        object_dict["from"] = object_dict.get("sender")
        object_dict["date"] = self.date.strftime(self.config.date_format)
        if object_dict["due_date"] is not None:
            object_dict["due_date"] = self.due_date.strftime(self.config.date_format)
        object_dict.pop("sender")
        for index, item in enumerate(object_dict["items"]):
            object_dict["items"][index] = item.__dict__
        for index, custom_field in enumerate(object_dict["custom_fields"]):
            object_dict["custom_fields"][index] = custom_field.__dict__
        for template_parameter, value in self.template.items():
            object_dict[template_parameter] = value
        object_dict.pop("template")
        object_dict.pop("config")
        return json.dumps(object_dict)

    def add_custom_field(self, name=None, value=None):
        """Add a custom field to the invoice"""
        self.custom_fields.append(CustomField(name=name, value=value))

    def add_item(self, name=None, quantity=0, unit_cost=0.0, description=None):
        """Add item to the invoice"""
        self.items.append(
            Item(
                name=name,
                quantity=quantity,
                unit_cost=unit_cost,
                description=description,
            )
        )

    def download(self, file_path):
        """Directly send the request and store the file on path"""
        json_string = self._to_json()
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
        }
        if self.config.locale:
            headers["Accept-Language"] = self.config.locale
        response = requests.post(
            self.config.endpoint_url,
            json=json.loads(json_string),
            stream=True,
            headers=headers,
        )
        if response.status_code == 200:
            open(file_path, "wb").write(response.content)
        else:
            raise Exception(
                f"Invoice download request returned the following message:{response.json()} Response code = {response.status_code} "
            )

    def set_template_text(self, template_parameter, value):
        """If you want to change a default value for customising your invoice template, call this method"""
        if template_parameter in InvoiceGenerator.TEMPLATE_PARAMETERS:
            self.template[template_parameter] = value
        else:
            raise ValueError(
                "The parameter {} is not a valid template parameter. See docs.".format(
                    template_parameter
                )
            )

    def toggle_subtotal(self, tax="%", discounts=False, shipping=False):
        """Toggle lines of subtotal"""
        self.fields = {"tax": tax, "discounts": discounts, "shipping": shipping}


class Item:
    """Item object for an invoice"""

    def __init__(self, name, quantity, unit_cost, description=""):
        """Object constructor"""
        self.name = name
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.description = description


class CustomField:
    """Custom Field object for an invoice"""

    def __init__(self, name, value):
        """Object constructor"""
        self.name = name
        self.value = value
