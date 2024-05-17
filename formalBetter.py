import numpy as np
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
import random

def interpolate_points(points, num_intervals):
    latitudes = [point[0] for point in points]
    longitudes = [point[1] for point in points]
    altitudes = [point[2] for point in points]

    latitudes = np.interp(np.linspace(0, len(points)-1, num_intervals), np.arange(len(points)), latitudes)
    longitudes = np.interp(np.linspace(0, len(points)-1, num_intervals), np.arange(len(points)), longitudes)
    altitudes = np.interp(np.linspace(0, len(points)-1, num_intervals), np.arange(len(points)), altitudes)

    return list(zip(latitudes, longitudes, altitudes))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 地球半径，单位为米
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def add_random_offset(lat, lon, alt, max_offset=0.00005):
    lat += random.uniform(-max_offset, max_offset)
    lon += random.uniform(-max_offset, max_offset)
    alt += random.uniform(-0.5, 0.5)
    return lat, lon, alt

def create_tcx(date, start_time, total_distance, total_time):
    points = [
        (39.084861, 121.808194, 96.0), # 下顶点
        (39.084997, 121.807718, 96.0), # 左下
        (39.085528, 121.807667, 96.0), # 左中点
        (39.086046, 121.807723, 96.0), # 左上
        (39.086250, 121.808194, 96.0), # 上顶点
        (39.086046, 121.808603, 96.0), # 右上
        (39.085556, 121.808667, 96.0), # 右中点
        (39.085005, 121.808587, 96.0), # 右下
        (39.084861, 121.808194, 96.0)  # 回到下顶点
    ]

    num_intervals = 100
    trackpoints = interpolate_points(points, num_intervals)

    total_points = []
    for i in range(8):
        for point in trackpoints:
            lat, lon, alt = add_random_offset(*point)
            alt = 96.0 + (i % 4)
            total_points.append((lat, lon, alt))

    total_points = total_points[:int(total_time / 2.056)]

    root = ET.Element("TrainingCenterDatabase", 
                      {"xmlns": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2", 
                       "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", 
                       "xsi:schemaLocation": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"})
    
    activities = ET.SubElement(root, "Activities")
    activity = ET.SubElement(activities, "Activity", {"Sport": "Running"})
    
    id = ET.SubElement(activity, "Id")
    id.text = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    lap = ET.SubElement(activity, "Lap", {"StartTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")})
    
    total_time_elem = ET.SubElement(lap, "TotalTimeSeconds")
    total_time_elem.text = str(total_time)
    
    distance_elem = ET.SubElement(lap, "DistanceMeters")
    distance_elem.text = str(total_distance)
    
    calories = ET.SubElement(lap, "Calories")
    calories.text = str(int(total_distance * 0.1))
    
    avg_pace = ET.SubElement(lap, "Extensions")
    tpx = ET.SubElement(avg_pace, "TPX", {"xmlns": "http://www.garmin.com/xmlschemas/ActivityExtension/v2"})
    speed = ET.SubElement(tpx, "Speed")
    speed.text = str(total_distance / total_time)
    
    intensity = ET.SubElement(lap, "Intensity")
    intensity.text = "Active"
    
    trigger_method = ET.SubElement(lap, "TriggerMethod")
    trigger_method.text = "Manual"
    
    track = ET.SubElement(lap, "Track")
    
    total_distance_calculated = 0.0
    for i, (lat, lon, alt) in enumerate(total_points):
        trackpoint = ET.SubElement(track, "Trackpoint")
        
        t = ET.SubElement(trackpoint, "Time")
        t.text = (start_time + timedelta(seconds=i * 2.056)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        position = ET.SubElement(trackpoint, "Position")
        
        latitude = ET.SubElement(position, "LatitudeDegrees")
        latitude.text = str(lat)
        
        longitude = ET.SubElement(position, "LongitudeDegrees")
        longitude.text = str(lon)
        
        altitude = ET.SubElement(trackpoint, "AltitudeMeters")
        altitude.text = str(alt)
        
        distance = ET.SubElement(trackpoint, "DistanceMeters")
        if i > 0:
            total_distance_calculated += haversine(total_points[i-1][0], total_points[i-1][1], lat, lon)
        distance.text = str(total_distance_calculated)
    
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    filename = f"/Users/Herython/Desktop/Test/running/te/{date.month}_{date.day}.tcx"
    with open(filename, "w") as f:
        f.write(xmlstr)

start_date = datetime(2024, 4, 17)
for i in range(30):
    date = start_date + timedelta(days=i)
    start_hour = random.randint(17, 20)
    start_minute = random.randint(0, 59) if start_hour != 20 else random.randint(0, 12)
    start_second = random.randint(0, 59)
    start_time = datetime(date.year, date.month, date.day, start_hour, start_minute, start_second)

    total_distance = random.uniform(3020, 3230)
    total_time = random.uniform(25*60, 30*60)
    
    create_tcx(date, start_time, total_distance, total_time)
