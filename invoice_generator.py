import requests
import json
import pytz
import locale

from datetime import datetime


class InvoiceGenerator:
    """ API Object for Invoice-Generator tool - https://invoice-generator.com/ """

    URL = "https://invoice-generator.com"
    DATE_FORMAT = "%d %b %Y"
    LOCALE = "fr_FR"
    TIMEZONE = "Europe/Paris"

    def __init__(self, sender, to,
                 logo=None,
                 ship_to=None,
                 number=None,
                 payments_terms=None,
                 due_date=None,
                 notes=None,
                 terms=None,
                 currency="USD",
                 date=datetime.now(tz=pytz.timezone(TIMEZONE)),
                 discounts=0,
                 tax=0,
                 shipping=0,
                 amount_paid=0,
                 ):
        """ Object constructor """
        self.logo = logo
        self.sender = sender
        self.to = to
        self.ship_to = ship_to
        self.number = number
        self.currency = currency
        self.custom_fields = []
        self.date = date
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

    def _to_json(self):
        """
        Parsing the object as JSON string
        Please note we need also to replace the key sender to from, as per expected in the API but incompatible with from keyword inherent to Python
        We are formatting here the correct dates
        We are also resetting the two list of Objects items and custom_fields so that it can be JSON serializable
        """
        locale.setlocale(locale.LC_ALL, InvoiceGenerator.LOCALE)
        object_dict = self.__dict__
        object_dict['from'] = object_dict.get('sender')
        object_dict['date'] = self.date.strftime(InvoiceGenerator.DATE_FORMAT)
        if object_dict['due_date'] is not None:
            object_dict['due_date'] = self.date.strftime(InvoiceGenerator.DATE_FORMAT)
        object_dict.pop('sender')
        for index, item in enumerate(object_dict['items']):
            object_dict['items'][index] = item.__dict__
        for index, custom_field in enumerate(object_dict['custom_fields']):
            object_dict['custom_fields'][index] = custom_field.__dict__
        return json.dumps(object_dict)

    def add_custom_field(self, name=None, value=None):
        """ Add a custom field to the invoice """
        self.custom_fields.append(CustomField(
            name=name,
            value=value
        ))

    def add_item(self, name=None, quantity=0, unit_cost=0.0, description=None):
        """ Add item to the invoice """
        self.items.append(Item(
            name=name,
            quantity=quantity,
            unit_cost=unit_cost,
            description=description
        ))

    def download(self, file_path):
        """ Directly send the request and store the file on path """
        json_string = self._to_json()
        response = requests.post(InvoiceGenerator.URL, json=json.loads(json_string), stream=True, headers={'Accept-Language': InvoiceGenerator.LOCALE})
        if response.status_code == 200:
            open(file_path, 'wb').write(response.content)

    def toggle_subtotal(self, tax="%", discounts=False, shipping=False):
        """ Toggle lines of subtotal """
        self.fields = {
            "tax": tax,
            "discounts": discounts,
            "shipping": shipping
        }


class Item:
    """ Item object for an invoice """

    def __init__(self, name, quantity, unit_cost, description=""):
        """ Object constructor """
        self.name = name
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.description = description


class CustomField:
    """ Custom Field object for an invoice """

    def __init__(self, name, value):
        """ Object constructor """
        self.name = name
        self.quantity = value

