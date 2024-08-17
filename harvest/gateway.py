import hashlib
import urllib.parse

class PayfastPayment:
    def __init__(self, data, passPhrase='', sandbox_mode=False):
        self.data = data
        self.passPhrase = passPhrase
        self.sandbox_mode = sandbox_mode

    def generate_signature(self):
        payload = ""
        for key in self.data:
            payload += key + "=" + urllib.parse.quote_plus(self.data[key].replace("+", " ")) + "&"
        payload = payload[:-1]
        if self.passPhrase != '':
            payload += f"&passphrase={self.passPhrase}"
        return hashlib.md5(payload.encode()).hexdigest()

    def generate_html_form(self):
        signature = self.generate_signature()
        self.data['signature'] = signature

        pf_host = 'sandbox.payfast.co.za' if self.sandbox_mode else 'www.payfast.co.za'

        html_form = f'<form action="https://{pf_host}/eng/process" method="post">'
        for key in self.data:
            html_form += f'<input name="{key}" type="hidden" value="{self.data[key]}" />'
        html_form += '<input type="submit" value="Pay Now" /></form>'
        return html_form

# Example usage:
if __name__ == '__main__':
    data = {
    # Merchant details
    'merchant_id': '10000100',
    'merchant_key': '46f0cd694581a',
    'return_url': 'http://www.yourdomain.co.za/return.php',
    'cancel_url': 'http://www.yourdomain.co.za/cancel.php',
    'notify_url': 'http://www.yourdomain.co.za/notify.php',
    # Buyer details
    'name_first': 'First Name',
    'name_last': 'Last Name',
    'email_address': 'test@test.com',
    # Transaction details
    'm_payment_id': '1234', #Unique payment ID to pass through to notify_url
    'amount': "200",
    'item_name': 'Order#123'
}

    passphrase = 'jt7NOE43FZPn'
    payfast_payment = PayfastPayment(data, passphrase, sandbox_mode=True)
    html_form = payfast_payment.generate_html_form()
    print()
