import sys
import Pyro4.util
import re


def contains_number(string):
    return any(char.isdigit() for char in string)


def is_valid_email(emailArg):
    # Regular expression pattern for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    # Check if the email matches the pattern
    match = re.match(pattern, emailArg)
    return match

def is_valid_mobile(mobile):
    # Regular expression pattern for mobile number validation
    pattern = r"^\d+$"
    # Check if the mobile number matches the pattern
    match = re.match(pattern, mobile)
    return match


# exception traceback if any
sys.excepthook = Pyro4.util.excepthook

# Obtain a proxy object representing the remote server
uri = "PYRO:example.pitre@localhost:9092"
tre_server = Pyro4.Proxy(uri)

is_Continue = True

while is_Continue:
    password = ""
    userName = ""
    isCredentialsCorrect = True

    while isCredentialsCorrect:
        # prompt for username
        userName = input("Enter your User Name: ").strip()

        # Prompt for other authentication information (e.g., first name, last name, email)
        password = input("Enter your password: ").strip()

        if not contains_number(userName):
            isCredentialsCorrect = False
        else:
            print("User Name can't have numbers")

    # check if the user is authenticated

    authenticated = tre_server.authenticate(userName, password)

    if authenticated:
        print("Authentication successful!\n")
        print("\t\t\t============================")
        print("\t\t\t| Welcome to PITRE system! |")
        print("\t\t\t============================\n")

        is_TFN_Have = False
        isTFN_Out_Correct = True
        while isTFN_Out_Correct:
            is_TFN_Have = input("Do you have TFN number (y/n):").lower().strip()
            if is_TFN_Have == "y":
                is_TFN_Have = True
                isTFN_Out_Correct = False
            elif is_TFN_Have == "n":
                is_TFN_Have = False
                isTFN_Out_Correct = False
            else:
                print("Please enter correct input (y/n)")
                isTFN_Out_Correct = True

        if is_TFN_Have:
            tfn, person_id, mobileNumber, email = 0, 0, "", ""

            isTFN_Filed = False
            while not isTFN_Filed:
                try:
                    # prompt for TFN
                    tfn = int(input("Enter your TFN value: ").strip())
                    if not len(str(tfn)) == 9:
                        print("TFN value's length should be equal to 9")
                    else:
                        isTFN_Filed = True
                    
                except ValueError:
                    print("TFN only contain numbers")

            isPersonID_Filed = False
            while not isPersonID_Filed:
                try:
                    # prompt for Person id
                    person_id = int(input("Enter your Person id value: ").strip())
                    isPersonID_Filed = True
                except ValueError:
                    print("Person id only contain numbers")

            isMobileNum_Filed = False
            while not isMobileNum_Filed:
                
                # prompt for mobile number
                mobileNumber = input("Enter your mobile number: ").strip()
                if not len(str(mobileNumber)) == 10:
                    print("mobile number length should be equal to 10")
                elif(not is_valid_mobile(mobileNumber)):
                    print("mobileNumber only contain numbers")
                else:
                    mobileNumber = str(mobileNumber)
                    isMobileNum_Filed = True
                

            isEmail_Filed = False
            while not isEmail_Filed:
                email = input("Enter your Email address: ").strip()
                if not is_valid_email(email):
                    print("Email is not correct. please enter again")
                else:
                    isEmail_Filed = True

            user_data = [{'TFN': int(tfn), 'personId': int(person_id), 'mobile': mobileNumber, 'email': email}]

            # Calculate annual taxable income
            print("Waiting for the output...")
            #---------------------------------------------------------------------------------------------------------------
            userExists = tre_server.tfn_verify(user_data)
            if userExists:
            #---------------------------------------------------------------------------------------------------------------
                estimate_result = tre_server.calculate_tax_return_estimate_for_TFN(tfn)

                # Display the estimate result to the user
                print("Person ID: ",estimate_result[0])
                print("TFN :", estimate_result[1])
                print("Annual Taxable income :", estimate_result[2])
                print("Total tax withheld :", estimate_result[3])
                print("Total net income :", estimate_result[4])
                print("Estimate tax refund :", estimate_result[5])

            else:
                print("User not found")


        else:

            num_periods = 0
            isNumPeriodCorrect = True

            while isNumPeriodCorrect:
                try:
                    person_id = int(input('Enter the Person id: '))
                    num_periods = int(input('Enter the number of periods: '))

                    if num_periods < 1 or num_periods > 26:
                        print('Number of periods should be between 1 and 26')
                    else:
                        break
                except ValueError:
                    print("Only numbers are allowed. Please enter again")

            user_data = []

            for i in range(num_periods):
                isContainsOnlyNumbers = True
                while isContainsOnlyNumbers:
                    # Read input from the user in the format: net_wage, Tax_withheld

                    user_input = ""
                    isCommaNotMissing = True
                    while isCommaNotMissing:
                        try:
                            user_input = input("Enter net_wage and Tax_withheld (separated by a comma): ")

                            if not len(user_input.split(",")) == 2:
                                print("please enter net_wage and Tax_withheld, separated by a one comma")
                            else:
                                isCommaNotMissing = False
                        except:
                            print("please enter net_wage and Tax_withheld, separated by a comma")

                    # Split the input into two values
                    net_wage_v, tax_withheld_v = user_input.strip().split(',')
                    try:
                        user_data.append({"net_wage": float(net_wage_v), "Tax_withheld": float(tax_withheld_v)})
                        isContainsOnlyNumbers = False
                    except ValueError:
                        print("Only numbers are allowed. Please enter again")

            is_PHIC_Have = False
            isPHICNotCorrect = True

            while isPHICNotCorrect:
                phic = input("Do you have private health insurance cover? (y/n): ").lower().strip()
                if phic == "y":
                    is_PHIC_Have = True
                    isPHICNotCorrect = False
                elif phic == "n":
                    is_PHIC_Have = False
                    isPHICNotCorrect = False
                else:
                    print("Please enter correct input (y/n)")
                    isPHICNotCorrect = True

            # Calculate annual taxable income
            print("Waiting for the output...")
            estimate_result = tre_server.calculate_tax_return_estimate(user_data, is_PHIC_Have, person_id)

            # Display the estimate result to the user
            print("Person ID: ",estimate_result[0])
            print("TFN :", estimate_result[1])
            print("Annual Taxable income :", estimate_result[2])
            print("Total tax withheld :", estimate_result[3])
            print("Total net income :", estimate_result[4])
            print("Estimate tax refund :", estimate_result[5])

            print(
                '\nGiven results calculated assuming that entered values are the only incomes received for the entire year')

            is_Continue_Correct = True

            while is_Continue_Correct:
                do_Continue = input("\nDo you need to check Estimated Tax Refund Amount again? (y/n): ").lower()

                if do_Continue == "y":
                    is_Continue = True
                    is_Continue_Correct = False
                elif do_Continue == "n":
                    is_Continue = False
                    is_Continue_Correct = False
                else:
                    print("Please enter correct input (y/n)")
    else:
        print("Authentication failed. Please check your credentials.")
        print("Enter your credentials again!")
