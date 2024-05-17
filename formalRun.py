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

def interpolate_arc(center, radius, start_angle, end_angle, num_points, altitude):
    angles = np.linspace(start_angle, end_angle, num_points)
    lats = center[0] + radius * np.sin(np.radians(angles))
    lons = center[1] + radius * np.cos(np.radians(angles))
    alts = np.full(num_points, altitude)
    return list(zip(lats, lons, alts))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 地球半径，单位为米
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# 四个顶点
points = [
    (39.084861, 121.808194, 98.0), # 下顶点
    (39.085528, 121.807667, 96.0), # 左中点
    (39.086250, 121.808194, 99.0), # 上顶点
    (39.085556, 121.808667, 97.0), # 右中点
]

# 半径计算
radius_bottom_left = haversine(points[0][0], points[0][1], points[1][0], points[1][1])
radius_top_left = haversine(points[2][0], points[2][1], points[1][0], points[1][1])
radius_bottom_right = haversine(points[0][0], points[0][1], points[3][0], points[3][1])
radius_top_right = haversine(points[2][0], points[2][1], points[3][0], points[3][1])

# 中心点计算
center_bottom = (39.084861, (points[1][1] + points[3][1]) / 2)
center_top = (39.086250, (points[1][1] + points[3][1]) / 2)

# 为每圈生成100个点
num_points = 100
left_to_bottom = interpolate_line(points[1], points[0], num_points // 4)
bottom_arc = interpolate_arc(center_bottom, radius_bottom_left, 270, 360, num_points // 4, points[0][2])
bottom_to_right = interpolate_line(points[0], points[3], num_points // 4)
right_arc = interpolate_arc(center_top, radius_top_right, 0, 90, num_points // 4, points[3][2])
right_to_top = interpolate_line(points[3], points[2], num_points // 4)
top_arc = interpolate_arc(center_top, radius_top_left, 180, 270, num_points // 4, points[2][2])
top_to_left = interpolate_line(points[2], points[1], num_points // 4)
left_arc = interpolate_arc(center_bottom, radius_bottom_right, 90, 180, num_points // 4, points[1][2])

trackpoints = left_to_bottom + bottom_arc + bottom_to_right + right_arc + right_to_top + top_arc + top_to_left + left_arc

# 生成多个圈的点
total_points = []
for i in range(8):
    for point in trackpoints:
        lat, lon, alt = point
        alt = 96.0 + (i % 4)
        total_points.append((lat, lon, alt))

# 只取到总时间允许的点数
total_points = total_points[:int(1579 / 2.056)]

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
    
    total_distance = 0.0
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
            total_distance += haversine(total_points[i-1][0], total_points[i-1][1], lat, lon)
        distance.text = str(total_distance)
    
    # Pretty print
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open("/Users/Herython/Desktop/Test/running/5_1.tcx", "w") as f:
        f.write(xmlstr)

create_tcx()
