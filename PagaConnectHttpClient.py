import requests
from base64 import b64encode


def post_request(headers, url):
    response = requests.request(method="POST", url=url, headers=headers)
    return response


def get_basic_authorization(client_id, password):
    base64_string = b64encode(str.encode(client_id + ":" + password)).decode("ascii")
    return base64_string


test_server = "https://qa1.mypaga.com"
live_Server = "https://www.mypaga.com"


class PagaConnectClient(object):
    """
    This class provides an easy way to implement PagaConnect

    Parameters
    ----------
    client_id : string
        your public ID gotten from Paga
    password : string
        your account password
    test_server : string
        test server prefix
    live_server: string
        live server prefix
    test: string
        indicates whether application is in test or live mode
    """

    def __init__(self, client_id, password, test):
        """
        instantiates the class variables

        Parameters
        ----------
        client_id : string
            your public ID gotten from Paga
        password : string
            your account password
        test : boolean
            indicates whether application is in test or live mode
        """
        self.client_id = client_id
        self.password = password
        self.test = test

    def get_access_token(self, authorization_code, redirect_uri, scope,
                         user_data):
        """
        Gets the access token

        Parameters
        ----------
        authorization_code : string
            authorization code received from user's approval of
            Merchant's access to their Paga account
        redirect_uri : string
            Where Merchant would like the user to the redirected to after
            receiving the access token
        scope : string
            List of activities to be performed with the access token
        user_data : string
            List of user data data to be collected

        Returns
        -------
        JSON Object
            JSON Object with access token inside
        """
        server_url = self.url(self.test)
        print server_url
        access_token_url = server_url + "/paga-webservices/oauth2/token?"

        base64_string = get_basic_authorization(self.client_id, self.password)

        url = "{0}grant_type=authorization_code&redirect_uri={1}&code={2}&scope={3}&user_data={4}".format(
            access_token_url, redirect_uri, authorization_code, scope, user_data)

        print url

        headers = {
            'Authorization': "Basic " + base64_string
        }

        response = post_request(headers, url)
        return response.text

    def make_payment(self, access_token, reference_number, amount, user_id, product_code, currency):

        """ Make payment

        Parameters
        ----------
        access_token : string
            User's access token
        reference_number : string
            A unique reference number provided by the client to uniquely
            identify the transaction
        amount : float
            Amount to charge the user
        user_id : string
            A unique identifier for merchant's customer
        product_code : string
            Optional identifier for the product/service to be bought
        currency : string
            he currency code of the transaction, NGN is the only supported
            currency as of now (February 2016)

        Returns
        -------
        JSON Object
            JSON Object with access token inside
        """
        server_url = self.url(self.test)
        print server_url
        merchant_payment_url = server_url + "/paga-webservices/oauth2/secure/merchantPayment"
        print merchant_payment_url

        if currency is None:
            payment_link = merchant_payment_url + "/referenceNumber" + \
                           str(reference_number) + "/amount/" + str(amount) + \
                           "/merchantCustomerReference/" + str(user_id) + "/merchantProductCode/" + \
                           str(product_code)
        elif currency is None and product_code is None:
            payment_link = merchant_payment_url + "/referenceNumber/" + \
                           str(reference_number) + "/amount/" + str(amount) + \
                           "/merchantCustomerReference/" + str(user_id)
        else:
            payment_link = merchant_payment_url + "/referenceNumber/" + \
                           str(reference_number) + "/amount/" + str(amount) + \
                           "/merchantCustomerReference/" + str(user_id) + "/merchantProductCode" + \
                           "/" + str(product_code) + "/currency/" + str(currency)

        print payment_link

        headers = {
            'Authorization': "Bearer " + access_token,
            'Accept': 'application/json'
        }

        response = requests.request(method="POST", url=payment_link,
                                    headers=headers)
        print response
        return response.text

    def money_transfer(self, access_token, reference_number, amount, skip_messaging, recipient_credential):

        server_url = self.url(self.test)

        money_transfer_url = server_url + "/paga-webservices/oauth2/secure/moneyTransfer/v2?" + "amount=" + str(amount) \
                             + "&referenceNumber=" + reference_number + "&skipMessaging=" \
                             + str(skip_messaging) + "&recipientCredential=" + recipient_credential
        print money_transfer_url

        headers = {
            'Authorization': "Bearer " + access_token,
            'Accept': 'application/json'
        }

        response = post_request(headers, money_transfer_url)

        return response.text

    def get_user_details(self, access_token):

        server_url = self.url(self.test)

        user_detail_url = server_url + "/paga-webservices/oauth2/secure/getUserDetails"

        headers = {
            'Authorization': "Bearer " + access_token,
            'Accept': 'application/json'
        }

        response = post_request(headers,user_detail_url)

        return response.text

    @staticmethod
    def url(test):
        if test:
            return test_server
        else:
            return live_Server
