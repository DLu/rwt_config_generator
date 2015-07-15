BASIC_FRAME = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />

%(headers)s

<script>
%(main_script)s
</script>
</head>

<body onload="init()">
  <div id="%(div_id)s"></div>
</body>
</html>
"""

INCLUDE_TEMPLATE = '<script src="http://cdn.robotwebtools.org/%s"></script>'

REQUIRED_HEADERS = ['threejs/current/three.min.js', 'EventEmitter2/current/eventemitter2.min.js', 
                    'roslibjs/current/roslib.min.js', 'ros3djs/current/ros3d.min.js']

COLLADA_HEADERS = ['threejs/current/ColladaLoader.min.js', 'ColladaAnimationCompress/current/ColladaLoader2.min.js']

class RWTConfig:
    def __init__(self, div_id='robotdisplay'):
        self.params = {'div_id': div_id}
        self.headers = REQUIRED_HEADERS
        
    def get_headers(self):
        return '\n'.join([INCLUDE_TEMPLATE%s for s in self.headers])
        
    def __repr__(self):
        d = {}
        d.update(self.params)
        d['headers'] = self.get_headers()
        d['main_script'] = ''
        return BASIC_FRAME % d    
