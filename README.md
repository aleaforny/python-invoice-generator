# python-invoice-generator
Small and easy-to-use library to use **Invoice Generator** API with Python.

You can find more info on https://invoice-generator.com/ (i'm not the owner of it). This API is very nice and allow you to generate invoices on the fly easily with a lot of customization.



Prerequisites
--------
Install the packages from https://github.com/Invoiced/invoice-generator-api/ and follow its instruction.

Code disclaimer
--------
- This is NOT a Python package, just a very small library at its early stage. I created it for my own use, but it can perhaps help some other time, and it can be improved in many ways, so feel free to input your additions!
- You can customize some of the class attribute, such as the date format on the invoice, locale or timezone.
- The file payload is accessible via `response.content`, if the response status code is `200`.
- Perhaps you noted also that the original API parameter `from` had to be changed to `sender` in this library. This is due to the fact that `from` can't be a parameter in Python as it's a **keyword**, but the setting is correctly renamed after being passed as a JSON string when calling the API.
- Read Invoice Generator API docs for complete understanding of the API and the parameters available. **Not ALL paramaters have been tested with this API, so there can be some bugs!**

How-to-use (By example)
--------

The code is documented and there are no different endpoints with this API so there are no so many methods.
1) Create the `config` object
```python
config = InvoiceClientConfig(api_key="YOUR_API_KEY_HERE")
```

2) Create the `Invoice` object
```python
invoice = InvoiceGenerator(
    config=config,
    sender="Invoiced, Inc.",
    to="Parag",
    logo="https://invoiced.com/img/logo-invoice.png",
    number=1,
    notes="Thanks for your business!",
    shipping=50
)
```

3) Add one or several items to it
```python
invoice.add_item(
    name="Starter plan",
    quantity=1,
    unit_cost=99,
)
invoice.add_item(
    name="Fees",
    quantity=1,
    unit_cost=49,
)
```

4) You can basically customise the object after hand (useful if you have to process things after generating the invoice but before actually sending it, perhaps for some async tasks...)
```python
invoice.toggle_subtotal(shipping=True)
```

5) Finally download the file (this will actually call the API). It can be absolute or relative path. 
```python
invoice.download("my-awesome-invoice.pdf")
```

