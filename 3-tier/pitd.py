import Pyro4
import sqlite3
import os
import traceback

#Create the database and populate it with test data
def create_database():
    # Connect to the database
    conn = sqlite3.connect('pitd.db')
    cursor = conn.cursor()

    # Create the taxfile table
    cursor.execute('''
        CREATE TABLE taxfile (
            TFN INTEGER PRIMARY KEY,
            personId INTEGER,
            email TEXT,
            mobile TEXT,
            PHIC_status Integer
        )
    ''')

    # create the biweekly_records table
    cursor.execute('''
        CREATE TABLE biweekly_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            income REAL,
            withheld REAL,
            TFN INTEGER,
            FOREIGN KEY (TFN) REFERENCES taxfile (TFN)
        )
    ''')

     # Insert sample taxfile data into the table
    taxfile_data = [
        (111111111, 220136304556, 'joe@gmail.com', '0762342552', 1),
        (222222222, 220136304556, 'mary@gmail.com','0752122365', 0),
        (333333333, 220136304556, 'bob@gmail.com','0717879503', 1),
    ]
    cursor.executemany('INSERT INTO taxfile (TFN, personId, email, mobile,PHIC_status) VALUES (?, ?, ?, ?,?)', taxfile_data)

    # Insert sample payment details into the table
    payment_details = [
        (960.23 , 123.20, 111111111),
        (970.28 , 123.20, 111111111),
        (920.23 , 123.20, 111111111),
        (970.21 , 123.20, 111111111),
        (980.23 , 123.20, 111111111),
        (990.23 , 123.20, 111111111),
        (930.28 , 123.20, 111111111),
        (950.23 , 123.20, 111111111),
        (920.23 , 123.20, 111111111),
        (970.23 , 123.20, 111111111),
        (930.26 , 123.20, 111111111),
        (910.23 , 123.20, 111111111),
        (990.23 , 123.20, 111111111),
        (960.23 , 123.20, 111111111),
        (900.23 , 123.20, 111111111),
        (430.13 , 223.45, 222222222),
        (460.13 , 223.45, 222222222),
        (420.13 , 223.45, 222222222),
        (410.13 , 223.45, 222222222),
        (440.14 , 223.45, 222222222),
        (460.13 , 223.45, 222222222),
        (470.18 , 223.45, 222222222),
        (420.13 , 223.45, 222222222),
        (470.11 , 223.45, 222222222),
        (480.13 , 223.45, 222222222),
        (490.13 , 223.45, 222222222),
        (430.18 , 223.45, 222222222),
        (430.18 , 223.45, 222222222),
        (450.13 , 223.45, 222222222),
        (420.13 , 223.45, 222222222),
        (470.13 , 223.45, 222222222),
        (430.16 , 223.45, 222222222),
        (410.13 , 223.45, 222222222),
        (490.13 , 223.45, 222222222),
        (460.13 , 223.45, 222222222),
        (400.13 , 223.45, 222222222),
        (430.13 , 223.45, 222222222),
        (460.13 , 223.45, 222222222),
        (420.13 , 223.45, 222222222),
        (410.13 , 223.45, 222222222),
        (440.14 , 223.45, 222222222),
        (656.83 , 14.45, 333333333),
        (626.83 , 14.45, 333333333),
        (676.83 , 14.45, 333333333),
        (636.86 , 14.45, 333333333),
        (616.83 , 14.45, 333333333),
        (696.83 , 14.45, 333333333),
        (666.83 , 14.45, 333333333),
        (606.83 , 14.45, 333333333),
        (636.83 , 14.45, 333333333),
        (666.83 , 14.45, 333333333),
        (626.83 , 14.45, 333333333),
        (616.83 , 14.45, 333333333),
        (646.84 , 14.45, 333333333)
       
    ]
    cursor.executemany('INSERT INTO biweekly_records (income,withheld,TFN) VALUES (?, ?, ?)', payment_details)


    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Create the PITD server
@Pyro4.expose
class PITD:
    def __init__(self):
        self.db_file = 'pitd.db'

# verify tfn with provided user data
    def tfn_verification(self,tfn_details):
        try:
            #get tfn data from database
            tfn_data = tfn_details[0]
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            print("Recieved data: ",tfn_data)

            cursor.execute('SELECT * FROM taxfile WHERE TFN = ?',(tfn_data['TFN'],))
            taxfile = cursor.fetchone()

            print("Relevent Tax File: ",taxfile)
            cursor.close()

            # validate given data matches to the tfn data
            if(tfn_data['personId'] != taxfile[1]):
                print(f"PersonId Should be {taxfile[1]} not {tfn_data['personId']}")
                return False
            elif(tfn_data['email'] != taxfile[2]):
                print(len(taxfile[2]),len(tfn_data['email']))
                print(f"email Should be {taxfile[2]} not {tfn_data['email']}")
                return False
            elif(tfn_data['mobile'] != taxfile[3]):
                print(f"mobile Should be {taxfile[3]} not {tfn_data['mobile']}")
                return False
            else:
                print(f"{tfn_data['TFN']} is verified!")    
                return True
                
        except Exception as e:
            print("invalid TFN",e)
            traceback.print_exc()
            return False

#calculate estimate and send it to server1
    def get_estimate_result(self,tfn):
        payroll_data = []
        personId,phic_status = 0,0

        try:
            # get payroll data from database
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT income,withheld FROM biweekly_records WHERE TFN = ?',(tfn,))
            payroll_data  = cursor.fetchall()
            print("Payroll data: ",payroll_data)
            cursor.close()

            # get person id and private insuarance cover status
            cursor = conn.cursor()
            cursor.execute('SELECT personId,PHIC_status FROM taxfile WHERE TFN = ?',(tfn,))
            personId,phic_status = cursor.fetchone()
            print(personId,phic_status)
            cursor.close()

            taxable_income = 0
            withheld = 0
            tax_liability = 0
            # medicare levy surcharge
            mls = 0
            #medicare levy
            ml = 0

            # calculate annual taxable income
            size = len(payroll_data)
            for data in payroll_data:
                temp_income = data[0] * 26
                taxable_income += temp_income/26
                withheld += data[1] 

                #calculate medicare levy
                #get 2% of annual income as medicare levy and calculate total medicare levy 
                # divide by size to get biweekly ml
                ml += temp_income * 0.02 /size
                
                #calculate tax_liability
                tax_liability = basic_tax_calculator(temp_income)/size
                #calculate medicare levy surcharge
                mls = MLS_calculator(temp_income,phic_status==1)/size

            refund = tax_liability - withheld - ml - mls

            

            estimate_result = [personId,tfn,round(taxable_income,2),round(withheld,2),round(taxable_income-tax_liability-ml-mls,2),round(refund,2)]
            return estimate_result
        except Exception as e:
            traceback.print_exc()
            return [0,0,0,0,0,0]
   
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
    if(os.path.exists('pitd.db')):
        os.remove('pitd.db')

    create_database()
    Pyro4.Daemon.serveSimple(
            {
                PITD: "example.pitd"
            },
            #host ip address
            # host= "192.168.8.152",
            #port
            port= 9093,
            ns = False)
    
if __name__=="__main__":
    main()
# Start the Pyro4 server
# calculate basic tax