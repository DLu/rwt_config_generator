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

frame = get('Global Options/Fixed Frame')
displays = get('Displays')

c = RWTConfig(host=args.host, fixed_frame=frame)
if args.bson:
    c.add_bson_header()

for display in displays:
    cls = display['Class']
    if cls == 'rviz/Grid':
        c.add_grid()
    elif cls == 'rviz/RobotModel':
        c.add_model(param=display.get('Robot Description', None), tfPrefix=display.get('TF Prefix', None))        
    elif cls == 'rviz/Marker':
        c.add_markers(topic=display.get('Marker Topic', None))
    elif cls == 'rviz/MarkerArray':
        c.add_marker_array(topic=display.get('Marker Topic', None))    
    elif cls == 'rviz/InteractiveMarkers':
        topic = display.get('Update Topic')
        topic = topic.replace('/update', '')
        c.add_imarkers(topic=topic)
    elif cls == 'rviz/PointCloud2':
        c.add_pointcloud(topic=display.get('Topic', None), size=display.get('Size (m)', None))
    elif cls == 'rviz/LaserScan':
        c.add_laserscan(topic=display.get('Topic', None), color=to_hex(display.get('Color', None)), size=display.get('Size (m)', None))
    elif cls == 'rviz/Path':
        c.add_path(topic=display.get('Topic', None), color=to_hex(display.get('Color', None)))
    elif cls == 'rviz/Polygon':
        c.add_polygon(topic=display.get('Topic', None), color=to_hex(display.get('Color', None)))
    elif cls == 'rviz/Pose':
        c.add_pose(topic=display.get('Topic', None), color=to_hex(display.get('Color', None)),
            shaft_radius=display.get('Shaft Radius', None),
            head_radius=display.get('Head Radius', None),
            shaft_length=display.get('Shaft Length', None),
            head_length=display.get('Head Length', None))
    elif cls == 'rviz/Odometry':
        c.add_odometry(topic=display.get('Topic', None), color=to_hex(display.get('Color', None)),
            shaft_length=display.get('Length', None), keep=display.get('Keep', None))

    elif cls == 'rviz/PoseArray':
        c.add_posearray(topic=display.get('Topic', None), color=to_hex(display.get('Color', None)), length=display.get('Arrow Length', None))
    elif cls == 'rviz/PointStamped':
        c.add_point(topic=display.get('Topic', None), color=to_hex(display.get('Color', None)), radius=display.get('Radius', None))
    else:
        warning("Class %s not supported yet!"%cls)    
        
if args.output_html_file:
    with open(args.output_html_file, 'w') as f:
        f.write(str(c))
else:
    print(c)
