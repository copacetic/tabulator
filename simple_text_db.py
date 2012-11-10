# Two types of entries: user and product
# User entry: <user id> <id type (rfid or barcode)>
# Product entry: <product id> <product desc.> <product size> <product price>

DB_NAME = "./tabulator_db.txt"
PRODUCT_RECORD=0
USER_RECORD=1
DELIM="%%%"
def add_product(prod_id, desc, size, price):
    f = open(DB_NAME, 'a')
    f.write(str(PRODUCT_RECORD) + DELIM + prod_id + DELIM + desc + DELIM + size + DELIM + str(price) + '\n')
    f.close()

def add_user(user_id, id_type, user_name):
    f = open(DB_NAME, 'a')
    f.write(str(USER_RECORD) + user_id + DELIM + str(id_type) + DELIM + user_name + '\n')
    f.close()

def get_record(record_type, record_id):
    try:
        f = open(DB_NAME, 'r')
    except IOError:
        return None
    lines = list(f.readlines())
    print(lines)
    users = {}
    products = {}
    for line in lines:
        rec = line.split(DELIM)
        print(rec)
        without_rec_type = rec[1:]
        if rec[0] == str(PRODUCT_RECORD):
            products[without_rec_type[0]] = without_rec_type[1:]
        else:
            users[without_rec_type[0]] = without_rec_type[1:]
    print(products) 
    f.close()
    if record_type == PRODUCT_RECORD:
        if record_id in products:
            return products[record_id]
        else:
            return None
    else:
        if record_id in users:
            return users[record_id]
        else:
            return None
        


