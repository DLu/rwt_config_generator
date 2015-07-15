from __future__ import print_function
import sys
import yaml
from rviz_to_rwt import *
import argparse
import rospy

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)
    
parser = argparse.ArgumentParser()
parser.add_argument('rviz_config')
parser.add_argument('output_html_file', nargs='?')
args = parser.parse_args(rospy.myargv()[1:])

rviz = yaml.load( open(args.rviz_config) )['Visualization Manager']

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

c = RWTConfig(fixed_frame=frame)
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
    elif cls == 'rviz/Path':
        c.add_path(topic=display.get('Topic', None), color=display.get('Color', None))
    else:
        warning("Class %s not supported yet!"%cls)    
        
if args.output_html_file:
    with open(args.output_html_file, 'w') as f:
        f.write(str(c))
else:
    print(c)
