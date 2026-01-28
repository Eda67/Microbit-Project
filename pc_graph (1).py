import serial                  
import time                    
import matplotlib.pyplot as plt  

# USB serial connection
#PORT = "/dev/ttyACM0" for linux  or Windows = "COM3"             
ser = serial.Serial("/dev/ttyACM0" , 115200, timeout=0.1)

start_time = time.time()

# Lists to store graph data
temp_t = []    
temp_v = []    
hum_t = []     
hum_v = []     

print("Listening...")          # Just to show the program is running

# Runs forever
while True:
    line = ser.readline().decode("utf-8").strip()
    if not line:
        continue
    else:
        print(line)
    sensor, value = line.split(",")
    t = time.time() - start_time   #time since the data received
    value = float(value)

    if sensor == "Temp": # Store the data depending on sensor type        
        temp_t.append(t)
        temp_v.append(value)
    elif sensor == "humidity":
        hum_t.append(t)
        hum_v.append(value)

    

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.set_title('Temperature distribution on campus')
    ax1.set_xlabel('Time (Seconds)')
    ax1.set_ylabel('Temperature (°C)')

    ax2.set_title('Humidity distribution on campus')
    ax2.set_xlabel('Time (Seconds)')
    ax2.set_ylabel('Humidity (%)')

    ax1.scatter(temp_t, temp_v)
    ax2.scatter(hum_t, hum_v)

    plt.tight_layout()
    plt.show()