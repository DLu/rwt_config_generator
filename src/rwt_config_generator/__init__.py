from collections import OrderedDict

BASIC_FRAME = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />

%(headers)s

<script type="text/javascript">
%(main_script)s
</script>
</head>

<body onload="init()">
  <div id="%(div_id)s"></div>
</body>
</html>
"""

INCLUDE_TEMPLATE = '<script type="text/javascript" src="http://cdn.robotwebtools.org/%s"></script>'

REQUIRED_HEADERS = ['threejs/current/three.min.js', 'EventEmitter2/current/eventemitter2.min.js', 
                    'roslibjs/current/roslib.min.js', 'ros3djs/current/ros3d.min.js']

COLLADA_HEADERS = ['threejs/current/ColladaLoader.min.js', 'ColladaAnimationCompress/current/ColladaLoader2.min.js']
BSON_HEADER = 'js-bson/current/bson.min.js'

SCRIPT = """
  /**
   * Setup all visualization elements when the page is loaded.
   */
  function init() {
    // Connect to ROS.
    var ros = new ROSLIB.Ros({
      url : 'ws://%(host)s:9090'
    });

    // Create the main viewer.
    var viewer = new ROS3D.Viewer({
      divID : '%(div_id)s',
      width : %(width)d,
      height : %(height)d,
      antialias : true
    });

%(objects)s
  }
"""

OBJECT_TEMPLATE = """%(comment)s    var %(name)s = new %(type)s(%(dict)s);\n\n"""

def quote(s):
    if s is None:
        return None
    elif len(s)>0 and (s[0]=='"' or s[0]=="'"):
        return s
    else:
        return "'%s'"%s

def double(d):
    if d is None:
        return None
    else:
        return d*2                

class RWTConfig:
    def __init__(self, host=None, div_id='robotdisplay', size=(800,600), fixed_frame=None):
        if host is None:
            host = 'localhost'
        self.div_id = div_id
        self.fixed_frame = fixed_frame
        self.params = {'host': host, 'width': size[0], 'height': size[1], 'div_id': div_id}
        self.headers = REQUIRED_HEADERS
        self.names = set()
        self.tf = None
        self.objects = []
        
    def add_object(self, d):
        self.objects.append(d) 
        

    def add_tf_client(self, name='tfClient', angularThres=0.01, transThres=0.01, rate=10.0, comment='Setup a client to listen to TFs'):
        if self.tf:
            return self.tf
        self.tf = name    
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROSLIB.TFClient'
        d['comment'] = 'Setup a client to listen to TFs.'
        d['ros'] = 'ros'
        d['angularThres'] = angularThres
        d['transThres'] = transThres
        d['rate'] = rate
        if self.fixed_frame:
            d['fixedFrame'] = quote(self.fixed_frame)
        
        self.add_object(d)
        
        return self.tf
        
    def add_grid(self, comment='Add a grid.'):
        s = ''
        if comment:
            s += ' '*4 + '// ' + comment + '\n'
        s += ' '*4 + 'viewer.addObject(new ROS3D.Grid());'
        self.add_object(s)
        
    def add_model(self, param=None, path='http://resources.robotwebtools.org/', tfPrefix=None, comment='Setup the URDF client.'):
        d = OrderedDict()
        
        self.headers += COLLADA_HEADERS
        
        d['type'] = 'ROS3D.UrdfClient'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['param'] = quote(param)
        d['tfClient'] = self.add_tf_client()
        d['tfPrefix'] = quote(tfPrefix)
        d['path'] = quote(path)
        d['rootObject'] = 'viewer.scene'
        d['loader'] = 'ROS3D.COLLADA_LOADER_2'
        
        self.add_object(d)
        
    def add_map(self, name='gridClient', topic=None, tf=False, comment='Setup the map client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.OccupancyGridClient'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['topic'] = topic
        if tf:
            d['tfClient'] = self.add_tf_client()
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_markers(self, name=None, topic='/visualization_marker', comment='Setup the marker client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.MarkerClient'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_marker_array(self, name=None, topic='/visualization_marker_array', comment='Setup the marker client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.MarkerArrayClient'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)

    def add_imarkers(self, name='imClient', topic='/interactive_markers', comment='Setup the marker client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.InteractiveMarkerClient'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['camera'] = 'viewer.camera'
        d['rootObject'] = 'viewer.selectableObjects'
        
        self.add_object(d)
        
    def add_pointcloud(self, name=None, topic='/points', size=None, max_pts=None, comment='Setup the Point Cloud client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.PointCloud2'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['size'] = size
        d['max_pts'] = max_pts
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_laserscan(self, name=None, topic='/scan', color=None, size=None, max_pts=None, comment='Setup the LaserScan client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.LaserScan'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['size'] = size
        d['max_pts'] = max_pts
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_path(self, name=None, topic='/path', color=None, comment='Setup the Path client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.Path'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['color'] = color
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_polygon(self, name=None, topic='/polygon', color=None, comment='Setup the Path client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.Polygon'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['color'] = color
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_pose(self, name=None, topic='/pose', color=None, shaft_radius=None, head_radius=None, 
        shaft_length=None, head_length=None, comment=''):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.Pose'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['color'] = color
        d['length'] = shaft_length
        d['headLength'] = head_length
        d['shaftDiameter'] = double(shaft_radius)
        d['headDiameter'] = double(head_radius)
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_odometry(self, name=None, topic='/pose', color=None, keep=None, shaft_radius=None, head_radius=None, 
        shaft_length=None, head_length=None, comment=''):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.Odometry'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['color'] = color
        d['keep'] = keep
        d['length'] = shaft_length
        d['headLength'] = head_length
        d['shaftDiameter'] = double(shaft_radius)
        d['headDiameter'] = double(head_radius)
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_posearray(self, name=None, topic='/particlecloud', color=None, length=None, comment='Setup the PoseArray client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.PoseArray'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['color'] = color
        d['length'] = length
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def add_point(self, name=None, topic='/point', color=None, radius=None, comment='Setup the Point client.'):
        d = OrderedDict()
        d['name'] = name
        d['type'] = 'ROS3D.Point'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['tfClient'] = self.add_tf_client()
        d['topic'] = quote(topic)
        d['color'] = color
        d['radius'] = radius
        d['rootObject'] = 'viewer.scene'
        
        self.add_object(d)
        
    def get_main_script(self):
        d = {}
        d.update(self.params)
        object_strings = []
        for o in self.objects:
            if type(o)==str:
                object_strings.append(o)
            else:
                object_strings.append( self.get_object(o) )
        d['objects'] = '\n'.join( object_strings )
        return SCRIPT % d    
        
    def get_object(self, params):
        p2 = params.copy()
        d = {}
        d['type'] = p2['type']
        del p2['type']
        
        if 'name' in p2 and p2['name'] is not None:
            d['name'] = p2['name']
            del p2['name']
        else:
            name = d['type']
            if '.' in name:
                _, name = name.split('.', 1)
            name = name[0].lower() + name[1:]
            base = name
            c = 0
            while name in self.names:
                c+=1
                name = '%s_%d'%(name, c)
            self.names.add(name)    
                
            d['name'] = name
        
        if 'comment' in p2:
            d['comment'] = '    // %s\n'%p2['comment']
            del p2['comment']
        else:
            d['comment'] = ''
            
        if len(p2)>0:
            ps = []    
            for k,v in p2.iteritems():
                if v is None:
                    continue
                ps.append('      %s : %s'%(k, str(v)))
            d['dict'] = '{\n%s\n    }'%',\n'.join(ps)
        else:
            d['dict'] = '{}'
            
        return OBJECT_TEMPLATE % d
        
    def get_headers(self):
        return '\n'.join([INCLUDE_TEMPLATE%s for s in self.headers])
        
    def add_bson_header(self):
        self.headers.append(BSON_HEADER)    
        
    def __repr__(self):
        d = {}
        d['div_id'] = self.div_id
        d['headers'] = self.get_headers()
        d['main_script'] = self.get_main_script()
        return BASIC_FRAME % d    
