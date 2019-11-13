import time
import sqlite3
conn = sqlite3.connect('sensordata.db')
 
c = conn.cursor()

def createDB(c):
    # Create Database
    c.execute('''CREATE TABLE sensors(id INTEGER PRIMARY KEY ASC, name varchar(250) NOT NULL, sensor_id varchar(250) NOT NULL)''')
    # Create smoke sensor
    c.execute('''INSERT INTO sensors VALUES(1, 'smoke', 60)''')
    # Create co2 sensor
    c.execute('''INSERT INTO sensors VALUES(3, 'c02', 61)''')
    # Create temp sensor
    c.execute('''INSERT INTO sensors VALUES(2, 'temp', 62)''')
    # Create sensor data table linked to sensors
    c.execute('''CREATE TABLE sensordata(id INTEGER PRIMARY KEY AUTOINCREMENT, result varchar(250), sensor_id INTEGER NOT NULL, datetime timestamp DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(sensor_id) REFERENCES sensors(id))''')
    # Enter values for smoke sensor
    for value in range(70, 100):
        if value > 90:
            # Set smoke detector to YES
            c.execute("INSERT INTO sensordata VALUES(null, '1', 60, current_timestamp)")
        else:
            # Set smoke detector to NO
            c.execute("INSERT INTO sensordata VALUES(null, '0', 60, current_timestamp)")
        if value > 80:
            # Set c02 detector to YES
            c.execute("INSERT INTO sensordata VALUES(null, '1', 61, current_timestamp)")
        else:
            # Set c02 detector to NO
            c.execute("INSERT INTO sensordata VALUES(null, '0', 61, current_timestamp)")
        # Set temperature detector to value from range
        c.execute("INSERT INTO sensordata VALUES(null, \'{0}\', 62, current_timestamp)".format(value))
        time.sleep(5)

    # Create table to store sensor configurations
    c.execute('''CREATE TABLE sensorconfig(id INTEGER PRIMARY KEY AUTOINCREMENT, min varchar(250), max varchar(250), sensor_id INTEGER NOT NULL, datetime timestamp DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(sensor_id) REFERENCES sensors(id))''')
    # Insert default smoke sensor range
    c.execute('''INSERT INTO sensorconfig VALUES(null, '-1', '1', 60, current_timestamp)''')
    # Insert default c02 sensor range
    c.execute('''INSERT INTO sensorconfig VALUES(null, '-1', '1', 61, current_timestamp)''')
    # Insert default temp sensor range
    c.execute('''INSERT INTO sensorconfig VALUES(null, '60', '100', 62, current_timestamp)''')

createDB(c)
conn.commit()

c.execute('SELECT * FROM sensors')
print c.fetchall()
c.execute('SELECT * FROM sensordata')
print c.fetchall()
c.execute('SELECT * FROM sensorconfig')
print c.fetchall()

conn.close()



# curl -i -H "Content-Type: application/json" -X PUT -d '{"id":"null", "min":"20", "max":"50", "sensor_id":60, "datetime":"current_timestamp"}' http://127.0.0.1/sensorconfig/60

# curl http://127.0.0.1/sensors

# http://127.0.0.1/sensorconfig/60