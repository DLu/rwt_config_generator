#!/usr/bin/python
from __future__ import print_function
import sys
import yaml
from rwt_config_generator import *
import argparse
import rospy

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)
    
parser = argparse.ArgumentParser()
parser.add_argument('rviz_config')
parser.add_argument('output_html_file', nargs='?')
parser.add_argument('-b', '--bson', action='store_true')
parser.add_argument('-u', '--host', type=str, nargs='?')
args = parser.parse_args(rospy.myargv()[1:])

rviz = yaml.load( open(args.rviz_config) )['Visualization Manager']

def to_hex(s):
    if s is None:
        return None
    ns = tuple(map(int, s.split(';')))
    s = '0x%02x%02x%02x'%ns
    return s

def get(key, d=None):
    if d is None:
        d = rviz
    for s in key.split('/'):
        d = d.get(s, None)
        if d==None:
            return None
    return d        
    
def parse_displays(c, displays):
    for display in displays:
        cls = display['Class']
        if cls == 'rviz/Grid':
            c.add_grid()
        elif cls == 'rviz/RobotModel':
            c.add_model(param=display.get('Robot Description'), tfPrefix=display.get('TF Prefix'))        
        elif cls == 'rviz/Marker':
            c.add_markers(topic=display.get('Marker Topic'))
        elif cls == 'rviz/MarkerArray':
            c.add_marker_array(topic=display.get('Marker Topic'))    
        elif cls == 'rviz/InteractiveMarkers':
            topic = display.get('Update Topic')
            topic = topic.replace('/update', '')
            c.add_imarkers(topic=topic)
        elif cls == 'rviz/PointCloud2':
            c.add_pointcloud(topic=display.get('Topic'), size=display.get('Size (m)'))
        elif cls == 'rviz/LaserScan':
            c.add_laserscan(topic=display.get('Topic'), color=to_hex(display.get('Color')), size=display.get('Size (m)'))
        elif cls == 'rviz/Path':
            c.add_path(topic=display.get('Topic'), color=to_hex(display.get('Color')))
        elif cls == 'rviz/Polygon':
            c.add_polygon(topic=display.get('Topic'), color=to_hex(display.get('Color')))
        elif cls == 'rviz/Pose':
            c.add_pose(topic=display.get('Topic'), color=to_hex(display.get('Color')),
                shaft_radius=display.get('Shaft Radius'),
                head_radius=display.get('Head Radius'),
                shaft_length=display.get('Shaft Length'),
                head_length=display.get('Head Length'))
        elif cls == 'rviz/Odometry':
            c.add_odometry(topic=display.get('Topic'), color=to_hex(display.get('Color')),
                shaft_length=display.get('Length'), keep=display.get('Keep'))

        elif cls == 'rviz/PoseArray':
            c.add_posearray(topic=display.get('Topic'), color=to_hex(display.get('Color')), length=display.get('Arrow Length'))
        elif cls == 'rviz/PointStamped':
            c.add_point(topic=display.get('Topic'), color=to_hex(display.get('Color')), radius=display.get('Radius'))
        elif cls == 'rviz/Group':
            parse_displays( c, display['Displays'] )
        elif cls == 'rviz/Map':
            c.add_map(topic=display.get('Topic'), alpha=display.get('Alpha'), tf=True)
        else:
            warning("Class %s not supported yet!"%cls)    
   

frame = get('Global Options/Fixed Frame')

c = RWTConfig(host=args.host, fixed_frame=frame)
if args.bson:
    c.add_bson_header()
parse_displays(c, get('Displays'))
        
if args.output_html_file:
    with open(args.output_html_file, 'w') as f:
        f.write(str(c))
else:
    print(c)
