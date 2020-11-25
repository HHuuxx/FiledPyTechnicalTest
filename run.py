from flask import *
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)

@app.route("/", methods=["POST"])
def ProcessPayment():
    CreditCardNumber = request.form.get("CreditCardNumber", None)
    CardHolder = request.form.get("CardHolder", None)
    ExpirationDate = request.form.get("ExpirationDate", None)
    SecurityCode = request.form.get("SecurityCode", "")
    Amount = request.form.get("Amount", None)

    if not CardHolder:  
        return "", 400
        
    if not CreditCardNumber:  
        return "", 400



    CreditCardNumberValidity = False
    # Validate Credit Card
    card_number = list(CreditCardNumber.strip())
    
    # Remove the last digit from the card number
    check_digit = card_number.pop()

    # Reverse the order of the remaining numbers
    card_number.reverse()

    processed_digits = []

    for index, digit in enumerate(card_number):
        if index % 2 == 0:
            doubled_digit = int(digit) * 2

            # Subtract 9 from any results that are greater than 9		
            if doubled_digit > 9:
                doubled_digit = doubled_digit - 9

            processed_digits.append(doubled_digit)
        else:
            processed_digits.append(int(digit))

    total = int(check_digit) + sum(processed_digits)

    # Verify that the sum of the digits is divisible by 10
    if total % 10 == 0:
        CreditCardNumberValidity = True
    else:
        CreditCardNumberValidity = False
        return "", 400
        
    Logs = {
        "IsCreditCardValid?": CreditCardNumberValidity,
        
    }



    if not ExpirationDate:  
        return "", 400
    #Check if Date is Valid
    year,month = ExpirationDate.split('/')
    day = 1
    HasDatePassed = False
    isValidDate = True

    try: 
        datetime(int(year),int(month),int(day))
    except ValueError:
        isValidDate = False


    if isValidDate:
        #Check if the date has passedd
        present = datetime.now()

        HasDatePassed = datetime(int(year),int(month),day) < present
        
        Logs["HasDatePassed?"] = HasDatePassed
        if HasDatePassed: 
            return "", 400

    else:
        return "", 400
    
    PaymentProvider = [
        {"Name": "PremiumPaymentGateway", "IsAvailable": True, "Retries": 3},
        {"Name": "ExpensivePaymentGateway", "IsAvailable": True, "Retries": 1},
        {"Name": "CheapPaymentGateway", "IsAvailable": True, "Retries": 1}, 
    ]
    


    if not Amount:  
        return "", 400
    #Check Amount
    Amount = Decimal(Amount.replace(',','.'))

    # Check if Amount Is Negative Or Not
    if Amount < 0:
        Logs["IsAmountNotNegative"] = False
        return "", 400
    else:
        Logs["IsAmountNotNegative"] = True

        
    PrefferedGateway = ""
    IsProcessed = False
    # Assign a Preffered Gateway
    if Amount <= 20:
        PrefferedGateway = PaymentProvider[2]["Name"]
        IsProcessed = True
    elif Amount > 20 and Amount <= 500:

        #Check if Preffered Gateway is Available
        if PaymentProvider[1]["IsAvailable"] == True:
            PrefferedGateway = PaymentProvider[1]["Name"]
            IsProcessed = True
        else:
            PrefferedGateway = PaymentProvider[2]["Name"]

    elif Amount > 500:  
        Retries = 0
        #Check if Preffered Gateway is Available
        while(Retries <= PaymentProvider[0]["Retries"]):
            Retries = Retries + 1
            if PaymentProvider[0]["IsAvailable"] == True:
                PrefferedGateway= PaymentProvider[0]["Name"]
                IsProcessed = True
            else:
                IsProcessed = False
      
    response = {
        "Card Details": {
            "Credit Card Number": CreditCardNumber,
            "Card Holder": CardHolder,
            "Expiration": ExpirationDate,
            "SecurityCode": SecurityCode
        },
        "Transaction Details":{
            "Amount": str(Amount),
            "PaymentGateway": PrefferedGateway
        },
        "Logs": Logs
    }

    if IsProcessed: 
        return response
    else: 
        return "",400






        

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8000, debug=True)
