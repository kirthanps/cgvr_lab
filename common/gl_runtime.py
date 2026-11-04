"""Real OpenGL rendering: GLFW desktop windows or Linux EGL pbuffer contexts.

No plotting/image library renders the lab geometry. Pillow handles text glyphs
and encodes pixels read back from OpenGL. Requires compatibility OpenGL >= 2.1.
"""
from pathlib import Path
import ctypes
from io import BytesIO
import json
import os
import sys
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TEAL=(.07,.47,.57)
GRAY=(.65,.67,.70)
RED=(.85,.22,.17)


def output_dir(module_file):
    out=Path(module_file).resolve().parent/'outputs';out.mkdir(exist_ok=True)
    return out


def arguments(parser):
    parser.add_argument('--headless',action='store_true',help='Render with Linux EGL; no window server required')
    parser.add_argument('--show',action='store_true',help='Kept for compatibility; desktop mode opens a live OpenGL window by default')
    return parser


class Context:
    def __init__(self,width=1080,height=720,title='Computer Graphics — PyOpenGL',headless=None):
        self.width,self.height=width,height
        self.headless=('--headless' in sys.argv or os.environ.get('CG_HEADLESS')=='1') if headless is None else headless
        self.window=None;self.display=None;self.closed=False
        if self.headless:
            if 'OpenGL.GL' in sys.modules and os.environ.get('PYOPENGL_PLATFORM')!='egl':
                raise RuntimeError('EGL must be selected before importing OpenGL; start a new process with --headless')
            os.environ['PYOPENGL_PLATFORM']='egl';os.environ.setdefault('EGL_PLATFORM','surfaceless')
            from OpenGL import EGL
            self.egl=EGL
            self.display=EGL.eglGetDisplay(EGL.EGL_DEFAULT_DISPLAY)
            major,minor=ctypes.c_int(),ctypes.c_int()
            EGL.eglInitialize(self.display,ctypes.byref(major),ctypes.byref(minor))
            EGL.eglBindAPI(EGL.EGL_OPENGL_API)
            attrs=(ctypes.c_int*15)(EGL.EGL_SURFACE_TYPE,EGL.EGL_PBUFFER_BIT,EGL.EGL_RENDERABLE_TYPE,EGL.EGL_OPENGL_BIT,
                EGL.EGL_RED_SIZE,8,EGL.EGL_GREEN_SIZE,8,EGL.EGL_BLUE_SIZE,8,EGL.EGL_DEPTH_SIZE,24,EGL.EGL_NONE)
            configs=(EGL.EGLConfig*1)();count=ctypes.c_int()
            EGL.eglChooseConfig(self.display,attrs,configs,1,ctypes.byref(count))
            if not count.value:raise RuntimeError('No EGL desktop OpenGL pbuffer configuration with 24-bit depth')
            self.surface=EGL.eglCreatePbufferSurface(self.display,configs[0],(ctypes.c_int*5)(EGL.EGL_WIDTH,width,EGL.EGL_HEIGHT,height,EGL.EGL_NONE))
            self.context=EGL.eglCreateContext(self.display,configs[0],EGL.EGL_NO_CONTEXT,(ctypes.c_int*1)(EGL.EGL_NONE))
            EGL.eglMakeCurrent(self.display,self.surface,self.surface,self.context)
        else:
            import glfw
            self.glfw=glfw
            if not glfw.init():raise RuntimeError('GLFW could not open the display. On headless Linux, use --headless; on desktops install/update OpenGL drivers.')
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,2);glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
            glfw.window_hint(glfw.DEPTH_BITS,24);glfw.window_hint(glfw.RESIZABLE,False)
            self.window=glfw.create_window(width,height,title,None,None)
            if not self.window:glfw.terminate();raise RuntimeError('Could not create an OpenGL 2.1 compatibility window')
            glfw.make_context_current(self.window);glfw.swap_interval(1)
            # Framebuffer resolution can differ from logical window size on HiDPI desktops.
            self.width,self.height=glfw.get_framebuffer_size(self.window)
        from OpenGL import GL
        self.gl=GL
        GL.glDisable(GL.GL_DITHER);GL.glPixelStorei(GL.GL_PACK_ALIGNMENT,1);GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
        self.info={key:GL.glGetString(value).decode() for key,value in [('vendor',GL.GL_VENDOR),('renderer',GL.GL_RENDERER),('version',GL.GL_VERSION),('glsl',GL.GL_SHADING_LANGUAGE_VERSION)]}
        self.info.update(backend='EGL pbuffer' if self.headless else 'GLFW window',depth_bits=int(GL.glGetIntegerv(GL.GL_DEPTH_BITS)),framebuffer=[self.width,self.height])
        self.clear()

    def clear(self):
        g=self.gl;g.glUseProgram(0);g.glViewport(0,0,self.width,self.height)
        g.glDisable(g.GL_DEPTH_TEST);g.glDisable(g.GL_BLEND);g.glClearColor(.98,.98,.98,1)
        g.glClearDepth(1);g.glClear(g.GL_COLOR_BUFFER_BIT|g.GL_DEPTH_BUFFER_BIT)

    def panel(self,index,cols,rows,bounds,title='',depth=False):
        g=self.gl;w,h=self.width//cols,self.height//rows
        col,row=index%cols,index//cols
        vx,vy=col*w+12,self.height-(row+1)*h+12
        vw,vh=w-24,h-52
        self.viewport=(vx,vy,vw,vh)
        g.glViewport(vx,vy,vw,vh);g.glMatrixMode(g.GL_PROJECTION);g.glLoadIdentity()
        xmin,ymin,xmax,ymax=bounds
        if not depth:
            # Preserve geometry aspect ratio inside each panel.
            cx,cy=(xmin+xmax)/2,(ymin+ymax)/2;span=max((xmax-xmin)/vw,(ymax-ymin)/vh)
            xmin,xmax=cx-span*vw/2,cx+span*vw/2;ymin,ymax=cy-span*vh/2,cy+span*vh/2
        g.glOrtho(xmin,xmax,ymin,ymax,0 if depth else -1,1)
        g.glMatrixMode(g.GL_MODELVIEW);g.glLoadIdentity();g.glDisable(g.GL_DEPTH_TEST)
        if title:self.text(col*w+14,self.height-row*h-28,title,max_width=w-28)

    def text(self,x,y,text,max_width=None):
        """Glyphs are uploaded through OpenGL; they appear in the live framebuffer too."""
        g=self.gl;font=ImageFont.load_default(size=16)
        if max_width is not None:
            while font.getlength(text)>max_width and len(text)>4:text=text[:-4]+'...'
        box=font.getbbox(text);im=Image.new('RGBA',(max(1,box[2]+4),24),(0,0,0,0))
        ImageDraw.Draw(im).text((1,0),text,font=font,fill=(32,37,43,255))
        g.glUseProgram(0);g.glEnable(g.GL_BLEND);g.glBlendFunc(g.GL_SRC_ALPHA,g.GL_ONE_MINUS_SRC_ALPHA)
        g.glWindowPos2i(int(x),int(y));g.glDrawPixels(im.width,im.height,g.GL_RGBA,g.GL_UNSIGNED_BYTE,np.ascontiguousarray(np.flipud(np.asarray(im))))
        g.glDisable(g.GL_BLEND)

    def points(self,points,color=TEAL,size=2):
        g=self.gl;g.glColor3f(*color);g.glPointSize(size);g.glBegin(g.GL_POINTS)
        for x,y in points:g.glVertex2f(float(x),float(y))
        g.glEnd()

    def line(self,points,color=TEAL,width=2,closed=False):
        g=self.gl;g.glColor3f(*color);g.glLineWidth(width);g.glBegin(g.GL_LINE_LOOP if closed else g.GL_LINE_STRIP)
        for x,y in points:g.glVertex2f(float(x),float(y))
        g.glEnd();g.glLineWidth(1)

    def axes(self,bounds):
        x0,y0,x1,y1=bounds
        self.line([(x0,0),(x1,0)],(.84,.85,.86),1)
        self.line([(0,y0),(0,y1)],(.84,.85,.86),1)

    def image(self):
        g=self.gl;g.glFinish()
        raw=g.glReadPixels(0,0,self.width,self.height,g.GL_RGB,g.GL_UNSIGNED_BYTE)
        im=Image.frombytes('RGB',(self.width,self.height),bytes(raw)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.check();return im

    def save(self,path):
        im=self.image();buffer=BytesIO();im.save(buffer,format='PNG');Path(path).write_bytes(buffer.getvalue())

    def check(self):
        error=self.gl.glGetError()
        if error!=self.gl.GL_NO_ERROR:raise RuntimeError(f'OpenGL error 0x{error:04x}')

    def metadata(self,out):
        self.check();(Path(out)/'opengl.json').write_text(json.dumps(self.info,indent=2))

    def present(self):
        if not self.headless:
            self.glfw.swap_buffers(self.window);self.glfw.poll_events()

    def hold(self,redraw=None):
        if self.headless:return
        glfw=self.glfw
        if redraw is None:
            self.present()
            while not glfw.window_should_close(self.window):
                if glfw.get_key(self.window,glfw.KEY_ESCAPE)==glfw.PRESS:break
                glfw.wait_events_timeout(.05)
        else:
            start=time.monotonic()
            while not glfw.window_should_close(self.window):
                if glfw.get_key(self.window,glfw.KEY_ESCAPE)==glfw.PRESS:break
                redraw(time.monotonic()-start);self.present()

    def close(self):
        if self.closed:return
        if self.headless:
            e=self.egl;e.eglMakeCurrent(self.display,e.EGL_NO_SURFACE,e.EGL_NO_SURFACE,e.EGL_NO_CONTEXT)
            e.eglDestroyContext(self.display,self.context);e.eglDestroySurface(self.display,self.surface);e.eglTerminate(self.display)
        else:self.glfw.destroy_window(self.window);self.glfw.terminate()
        self.closed=True

    def __enter__(self):return self
    def __exit__(self,*exc):self.close()


def save_gif(frames,path,duration=80):
    buffer=BytesIO()
    frames[0].save(buffer,format='GIF',save_all=True,append_images=frames[1:],duration=duration,loop=0)
    Path(path).write_bytes(buffer.getvalue())
