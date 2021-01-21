from flask import Flask
import re
from flask_restful import Resource, Api, abort, reqparse
import datetime

app = Flask(__name__)

api = Api(app)

PremiumPaymentGateway = True
ExpensivePaymentGateway = True
CheapPaymentGateway = True


def toDate(dateString):  # https://stackoverflow.com/questions/53460391/                passing-a-date-as-a-url-parameter-to-a-flask-route
    return datetime.datetime.strptime(dateString, "%Y-%m-%d").date()


card_args = reqparse.RequestParser()
# CreditCardNumber(mandatory, string)
card_args.add_argument("CreditCardNumber", type=str,
                       help="Card number is required", required=True)
# CardHolder: (mandatory, string)
card_args.add_argument("CardHolder", type=str,
                       help="Card holder is required", required=True)
# ExpirationDate(mandatory, DateTime)
card_args.add_argument("ExpirationDate", type=toDate,
                       help="Expiration date is required", required=True)
# SecurityCode(optional, string, 3 digits)
card_args.add_argument("SecurityCode", type=str, )
# Amount(mandatoy decimal)
card_args.add_argument("Amount", type=float,
                       help="Amount is required", required=True)


class ProcessPayment(Resource):
    def get(self):
        args = card_args.parse_args()
        """https: // allhackerranksolutions.blogspot.com/2019/12/validating-credit-card-numbers-hacker.html
        Credit card validation
        """
        for i in range(int(args["CreditCardNumber"])):
            S = args["CreditCardNumber"].strip()
            # Check if credit card number size if exactly 16, all the characters are integers and - symbol may be present after every group of 4 digits
            pre_match = re.search(r'^[456]\d{3}(-?)\d{4}\1\d{4}\1\d{4}$', S)
            if pre_match:
                processed_string = "".join(pre_match.group(0).split('-'))
                # Check is credit card number has 4 or more repeating consecutive digits
                final_match = re.search(r'(\d)\1{3,}', processed_string)
                if final_match:
                    abort(400, message="bad request")
                else:
                    break
            else:
                abort(400, message="bad request")
        # CreditCardNumber, CardHolder, ExpirationDate, Amount are all mandatoy
        if args["CreditCardNumber"] == None or args["CardHolder"] == None or args["ExpirationDate"] == None or args["Amount"] == None:
            abort(400, message="bad request")
        # ExpirationDate(cannot be in the past)
        if args["ExpirationDate"] < datetime.datetime.now().date():
            abort(400, message="bad request")
        # Amount(positive amount)
        if args["Amount"] < 1:
            abort(400, message="bad request")
        # If the amount to be paid is less than £20
        if args["Amount"] < 20:
            # use CheapPaymentGateway.
            providr = CheapPaymentGateway
            return "OK", 200
        # If the amount to be paid is £21-500
        if args["Amount"] in range(21, 501):
            # use ExpensivePaymentGateway if available
            if ExpensivePaymentGateway:
                provider = ExpensivePaymentGateway
                return "OK", 200
            # Otherwise, retry only once with CheapPaymentGateway.
            elif not ExpensivePaymentGateway:
                provider = CheapPaymentGateway
                return "OK", 200
            else:
                abort(500, message="internal server error")
        # If the amount is > £500
        if args["Amount"] > 500:
            # try only PremiumPaymentGateway and retry up to 3 times in case payment does not get processed
            for i in range(0, 3):
                if PremiumPaymentGateway:
                    return "OK", 200
                    break
                else:
                    continue
            abort(500, message="internal server error")


api.add_resource(ProcessPayment, "/processpayment")

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
