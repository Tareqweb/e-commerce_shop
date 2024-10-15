import json
import requests

def get_shipping_slots(ship_to, cart_obj):
    url = 'https://production-api.postmen.com/v3/rates'
    products = []
    ship_to = {
        "contact_name": "Mister Jones",
        "phone": "8777285325",
        "email": "visible.test@example.com",
        "company_name": "Visible SCM",
        "street1": "41 Macintosh Lane",
        "street2": "Building 2",
        "street3": "Reserved for international addresses",
        "city": "Glastonbury",
        "state": "CT",
        "postal_code": "06033",
        "country": "USA",
        "type": "residential"
      }

    for product in cart_obj.cartproduct_set.all():
      products.append({
        "description": product.product.name,
        "item_id": str(product.product.id),
        "quantity": product.quantity,
        "price": {
          "amount": float(product.get_price()),
          "currency": "USD"
        },
        "weight": {
          "value": float(product.product.weight),
          "unit": "kg"
        },
        "sku": product.product.slug
      })

    payload = {
      "async": False,
      "shipper_accounts": [
        {
          "id": "d77629be-c995-477b-964c-2fc1ea3c76e5"
        }
      ],
      "is_document": False,
      "shipment": {
        "parcels": [
          {
            "box_type": "custom",
            "weight": {
              "value": float(cart_obj.get_total_weight()),
              "unit": "kg"
            },
            "dimension": {
              "width": 20,
              "height": 30,
              "depth": 40,
              "unit": "cm"
            },
            "items": products
          }
        ],
        "ship_from": {
          "contact_name": "Mister Jones",
          "phone": "4144369430",
          "email": "bijoytech71@gmail.com",
          "company_name": "Bijoy Tech",
          "street1": "5160 Wiley Post Way",
          "street2": "Building 2",
          "street3": "Reserved for international addresses",
          "city": "Salt Lake City",
          "state": "NY",
          "postal_code": "11372",
          "country": "USA",
          "type": "business"
        },
        "ship_to": ship_to
      }
    }



    headers = {
        'postmen-api-key': '00f1f31f-b3a6-4fdb-8988-28adcba53af4',
        'content-type': 'application/json'
    }

    response = requests.request('POST', url, data=json.dumps(payload), headers=headers)
    return response.json()
