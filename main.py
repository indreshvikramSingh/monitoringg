

import requests
import datetime
import time
import random
import pandas as pd
import numpy as np


CHANNEL_ID = "2878752"
WRITE_API_KEY = "VH7OOX3ZRUM0V1D4"


FILE_PATH = r"C:\Users\Deckmount\Downloads\DATA0637.TXT"


def clean_data(data, min_val, max_val):
    data = data.astype(float) 
    data[~((data >= min_val) & (data <= max_val))] = np.nan  
    return data.interpolate()  


def smooth_data(data, min_val, max_val, window_size=15):
    data = data.astype(float)
    data[~((data >= min_val) & (data <= max_val))] = np.nan 
    return data.rolling(window=window_size, min_periods=1).mean() 


def send_data():
    try:
        
        df = pd.read_csv(FILE_PATH, header=None)

        
        breath_rate = df.iloc[:, 2]
        spo2 = df.iloc[:, 3]
        pulse = df.iloc[:, 4]
        body_position = df.iloc[:, 5]
        spo2_2 = df.iloc[:, 6]

        
        breath_rate_filtered = smooth_data(breath_rate, 80, 100)
        spo2_filtered = clean_data(spo2, 80, 100)
        pulse_filtered = clean_data(pulse, 0, 150)
        body_position_filtered = clean_data(body_position, 0, 4)
        spo2_2_filtered = clean_data(spo2_2, 0, 200)

        
        updates = []
        current_time = datetime.datetime.now()


        
        valid_indices = breath_rate_filtered.dropna().index[-5:]

        for i in valid_indices:
            timestamp = (current_time - datetime.timedelta(seconds=15 * i)).isoformat()

            updates.append({
                "created_at": timestamp,
                "field1": float(breath_rate_filtered.iloc[i]) + random.uniform(-0.2, 0.2),
                "field2": float(spo2_filtered.iloc[i]) + random.uniform(-0.2, 0.2),
                "field3": float(spo2_2_filtered.iloc[i]) + random.uniform(-0.2, 0.2),
                "field4": float(body_position_filtered.iloc[i]) + random.uniform(-0.2, 0.2),
                "field5": float(pulse_filtered.iloc[i]) + random.uniform(-0.2, 0.2)
            })

        if updates:
            url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/bulk_update.json"
            payload = {
                "write_api_key": WRITE_API_KEY,
                "updates": updates
            }
            headers = {"Content-Type": "application/json"}

            
            response = requests.post(url, json=payload, headers=headers)

            
            if response.status_code in [200, 202]:  
                print(" Data successfully sent to ThingSpeak!")
            else:
                print(f" Error: {response.status_code}, Response: {response.text}")
        else:
            print(" No valid data to send!")

    except Exception as e:
        print(f" Error: {e}")


while True:
    send_data()
    time.sleep(16)
