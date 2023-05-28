import Pyro4

#implementing the server class
@Pyro4.expose
class Server:
    #authenticate user 
    def authenticate(self,username,password):
        if(username == "user" and password == "user123"):
            print("Client is login to the server...\n")
            return True
        else:
            return False

    #calculate the tax return estimate
    def calculate_tax_return_estimate(self, user_data, have_phic,personId):
        #user_data is a dictionary passed from the client containing taxable income,witholding tax and if the taxpayer has the private health insuarance cover

        display(user_data)

        taxable_income = 0
        withheld = 0
        tax_liability = 0
        # medicare levy surcharge
        mls = 0
        #medicare levy
        ml = 0

        # calculate annual taxable income
        size = len(user_data)
        for data in user_data:
            temp_income = data["net_wage"] * 26
            taxable_income += temp_income/26
            withheld += data["Tax_withheld"] 

            #calculate medicare levy
            #get 2% of annual income as medicare levy and calculate total medicare levy 
            # divide by size to get biweekly ml
            ml += temp_income * 0.02 /size
            
            #calculate tax_liability
            tax_liability = basic_tax_calculator(temp_income)/size
            #calculate medicare levy surcharge
            mls = MLS_calculator(temp_income,have_phic)/size
    
        print(f"Annual taxable income : {taxable_income}")

        #refund : if taxpayer able to get refund this value is a positive and otherwise negetive 
        refund = tax_liability - withheld - ml - mls

        estimate_result = [personId,"No TFN",round(taxable_income,2),round(withheld,2),round(taxable_income-tax_liability-ml-mls,2),round(refund,2)]

        print (estimate_result)

        return estimate_result

# display list of tax data
def display(list):
    for tax_data in list:
        print(f"Biweekly Income :{tax_data['net_wage']} , Withheld : {tax_data['Tax_withheld']}")

#calculate basic tax
def basic_tax_calculator(income):
    if (income>180000):
        tax = 51667 + (income-180000) * 0.45
    elif (income > 120000):
        tax = 29467 + (income-120000) * 0.37
    elif (income > 45000):
        tax = 5092 + (income-45000) * 0.325
    elif (income > 18200):
        tax = (income-18200) * 0.19
    
    return round(tax,2)

 #calculate the medicare levy surcharge
def MLS_calculator(income,have_phic):
    _mls = 0
    if (have_phic == False):
        if (income > 140000):
            _mls = income * 0.015
        elif (income > 105000):
            _mls = income * 0.0125
        elif (income > 90000):
            _mls = income * 0.01
    return _mls

#main method
def main():
    Pyro4.Daemon.serveSimple(
            {
                Server: "example.pitre"
            },
            #host ip address
            host= "192.168.8.152",
            #port
            port= 9092,
            ns = False)
    
if __name__=="__main__":
    main()
