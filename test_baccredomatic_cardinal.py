import pycurl
import datetime
import urllib.parse
import hashlib
from io import BytesIO

class GWAPI:

    def __init__(self):
        self.login = {}
        self.order = {}
        self.billing = {}
        self.shipping = {}
        self.responses = {}

    def set_login(self, security_key):
        self.login['security_key'] = security_key

    def generate_hash(self, orderid, amount, time, security_key):
        hash_string = f"{orderid}|{amount}|{time}|{security_key}"
        print(f"Hash string: {hash_string}")
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()

    def do_sale(self, orderid, amount, ccnumber, ccexp, cvv, avs):
        query_params = {
            'key_id': '14357732',
            'processor_id': 'bolsha01',
            'orderid': orderid,
            'ccnumber': ccnumber,
            'ccexp': ccexp,
            'amount': f'{float(amount):.2f}',
            'cvv': cvv,
            'avs': avs,
            'redirect': '',
            'type': 'sale'
        }

        # Generate hash and timestamp
        time_var = str(int(datetime.datetime.now().timestamp()))
        query_params['hash'] = self.generate_hash(orderid, query_params['amount'], time_var, self.login['security_key'])
        query_params['time'] = time_var

        # Encode query parameters
        query = urllib.parse.urlencode(query_params)
        print(f"Query: {query}")
        return self.do_post(query)

    def do_post(self, query):
        response_io = BytesIO()
        curl_obj = pycurl.Curl()
        curl_obj.setopt(pycurl.POST, 1)
        curl_obj.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl_obj.setopt(pycurl.TIMEOUT, 30)
        curl_obj.setopt(pycurl.HEADER, 0)
        curl_obj.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl_obj.setopt(pycurl.WRITEFUNCTION, response_io.write)
        curl_obj.setopt(pycurl.URL, "https://credomatic.compassmerchantsolutions.com/api/transact.php")
        curl_obj.setopt(pycurl.POSTFIELDS, query)
        curl_obj.perform()
        curl_obj.close()

        data = response_io.getvalue().decode('utf-8')
        print(f"Response from API: {data}")
        self.responses = {k: v[0] for k, v in urllib.parse.parse_qs(data).items()}
        return self.responses.get('response', 'No response key found')

# Replace with your actual security key
gw = GWAPI()
gw.set_login("6j4rk2H3rh83pNdG68C6d9vaBY65Qpa9")
response = gw.do_sale("order1888", "55.00", "4111111111111111", "1024", '889', "Street 1")

print(f"Response: {response}")
if response == '1':
    print("Approved")
elif response == '2':
    print("Declined")
elif response == '3':
    print("Error")
else:
    print("Unknown response")