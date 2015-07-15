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
    if s[0]=='"' or s[0]=="'":
        return s
    else:
        return "'%s'"%s    

class RWTConfig:
    def __init__(self, host='localhost', div_id='robotdisplay', size=(800,600)):
        self.div_id = div_id
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
        
        self.add_object(d)
        
        return self.tf
        
    def add_grid(self, comment='Add a grid.'):
        s = ''
        if comment:
            s += ' '*4 + '// ' + comment + '\n'
        s += ' '*4 + 'viewer.addObject(new ROS3D.Grid());'
        self.add_object(s)
        
    def add_model(self, param=None, path='http://resources.robotwebtools.org/', comment='Setup the URDF client.'):
        d = OrderedDict()
        
        self.headers += COLLADA_HEADERS
        
        d['type'] = 'ROS3D.UrdfClient'
        d['comment'] = comment
        d['ros'] = 'ros'
        d['param'] = param
        d['tfClient'] = self.add_tf_client()
        d['path'] = quote(path)
        d['rootObject'] = 'viewer.scene'
        d['loader'] = 'ROS3D.COLLADA_LOADER_2'
        
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
        
        if 'name' in p2:
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
                name = '%s%d'%(name, c)
                
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
        
    def __repr__(self):
        d = {}
        d['div_id'] = self.div_id
        d['headers'] = self.get_headers()
        d['main_script'] = self.get_main_script()
        return BASIC_FRAME % d    
