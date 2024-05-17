import numpy as np
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
import random

def interpolate_line(start, end, num_points):
    lats = np.linspace(start[0], end[0], num_points)
    lons = np.linspace(start[1], end[1], num_points)
    alts = np.linspace(start[2], end[2], num_points)
    return list(zip(lats, lons, alts))

def interpolate_arc(center, radius, start_angle, end_angle, num_points):
    angles = np.linspace(start_angle, end_angle, num_points)
    lats = center[0] + radius * np.sin(np.radians(angles))
    lons = center[1] + radius * np.cos(np.radians(angles))
    alts = np.linspace(center[2], center[2] + 1, num_points)  # 高度变化
    return list(zip(lats, lons, alts))

def haversine(coord1, coord2):
    R = 6371000  # 地球半径，单位为米
    lat1, lon1 = np.radians(coord1[:2])  # 只传递纬度和经度
    lat2, lon2 = np.radians(coord2[:2])  # 只传递纬度和经度
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def add_random_offset(lat, lon, alt, max_offset=0.00001):
    lat += random.uniform(-max_offset, max_offset)
    lon += random.uniform(-max_offset, max_offset)
    alt += random.uniform(-0.5, 0.5)
    return lat, lon, alt

def generate_trackpoints(num_points):
    points = {
        'left': (39.085528, 121.807667, 96.0),
        'right': (39.085556, 121.808667, 97.0),
        'bottom': (39.084861, 121.808194, 98.0),
        'top': (39.086250, 121.808194, 99.0)
    }
    
    left_to_bottom = interpolate_line(points['left'], points['bottom'], num_points // 4)
    bottom_to_right = interpolate_arc((points['bottom'][0], (points['bottom'][1] + points['right'][1]) / 2, points['bottom'][2]), 
                                      haversine(points['bottom'], points['right']) / 2, 270, 360, num_points // 4)
    right_to_top = interpolate_line(points['right'], points['top'], num_points // 4)
    top_to_left = interpolate_arc((points['top'][0], (points['top'][1] + points['left'][1]) / 2, points['top'][2]), 
                                  haversine(points['top'], points['left']) / 2, 90, 180, num_points // 4)
    
    trackpoints = left_to_bottom + bottom_to_right + right_to_top + top_to_left
    trackpoints = [add_random_offset(lat, lon, alt) for lat, lon, alt in trackpoints]
    return trackpoints

def create_tcx():
    root = ET.Element("TrainingCenterDatabase", 
                      {"xmlns": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2", 
                       "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", 
                       "xsi:schemaLocation": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"})
    
    activities = ET.SubElement(root, "Activities")
    activity = ET.SubElement(activities, "Activity", {"Sport": "Running"})
    
    id = ET.SubElement(activity, "Id")
    id.text = "2024-05-01T10:03:32Z"
    
    lap = ET.SubElement(activity, "Lap", {"StartTime": "2024-05-01T10:03:32Z"})
    
    total_time = ET.SubElement(lap, "TotalTimeSeconds")
    total_time.text = "1579"
    
    distance = ET.SubElement(lap, "DistanceMeters")
    distance.text = "3020"
    
    calories = ET.SubElement(lap, "Calories")
    calories.text = "288"
    
    avg_pace = ET.SubElement(lap, "Extensions")
    tpx = ET.SubElement(avg_pace, "TPX", {"xmlns": "http://www.garmin.com/xmlschemas/ActivityExtension/v2"})
    speed = ET.SubElement(tpx, "Speed")
    speed.text = str(3020 / 1579)
    
    intensity = ET.SubElement(lap, "Intensity")
    intensity.text = "Active"
    
    trigger_method = ET.SubElement(lap, "TriggerMethod")
    trigger_method.text = "Manual"
    
    track = ET.SubElement(lap, "Track")
    
    start_time = datetime.strptime("2024-05-01T10:03:32Z", "%Y-%m-%dT%H:%M:%SZ")
    
    num_points_per_circle = int((1579 / 7.55) / 2.056)
    trackpoints = generate_trackpoints(num_points_per_circle)
    
    for i, (lat, lon, alt) in enumerate(trackpoints[:int(1579 / 2.056)]):
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
        distance.text = str(i * 3.02 / len(trackpoints) * 400)  # 简单线性插值距离
    
    # Pretty print
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open("/Users/Herython/Desktop/Test/running/5_1.tcx", "w") as f:
        f.write(xmlstr)

create_tcx()
