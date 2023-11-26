import pymysql


def conn():
    return pymysql.connect(host='localhost',
                           user='mdbaki',
                           password='TalhaZubayer789*',
                           database='car_sales_au',
                           charset='utf8mb4',
                           autocommit=True,
                           cursorclass=pymysql.cursors.DictCursor)


def insert_autotrader(title, year, price, kilometers, vehicle_type, gearbox, fuel_type, seller_type, condition, suburb,
                      state, transmission, body_type, drive_type, engine, fuel_consumption, colour_ext, colour_int,
                      registration, vin, stock_no, dealer, make, model, variant, series, is_sold, sold_date):
    try:
        with conn().cursor() as cursor:
            insert_sql = ('INSERT INTO `autotrader` (`title`, `year`, `price`, `kilometers`, `vehicle_type`, `gearbox`,'
                          ' `fuel_type`, `seller_type`, `condition`, `suburb`, `state`, `transmission`, `body_type`,'
                          ' `drive_type`, `engine`, `fuel_consumption`, `colour_ext`, `colour_int`, `registration`,'
                          ' `vin`, `stock_no`, `dealer`, `make`, `model`, `variant`, `series`, `is_sold`, `sold_date`) VALUES (%s, %s, %s, %s,'
                          ' %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);')
            cursor.execute(insert_sql, (title, year, price, kilometers, vehicle_type, gearbox, fuel_type, seller_type,
                                        condition, suburb, state, transmission, body_type, drive_type, engine, fuel_consumption,
                                        colour_ext, colour_int, registration, vin, stock_no, dealer, make, model, variant, series, is_sold, sold_date))
    except Exception as e:
         print(e)


def get_all_carsdata():
    try:
        with conn().cursor() as cursor:
            sql = "SELECT * FROM car_sales_au.autotrader;"
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
    except Exception as e:
         print(e)

