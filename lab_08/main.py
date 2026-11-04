"""Lab 8: vertex/fragment shaders with a VBO, attributes, varyings and uniforms."""
import argparse
import ctypes
import json
from pathlib import Path
import numpy as np
from common.gl_runtime import Context,arguments,output_dir,save_gif

TRIANGLE=np.array([[-.75,-.65,0,1,0,0],[.75,-.65,0,0,1,0],[0,.75,0,0,0,1]],dtype=np.float32)


def rotation_z(degrees):
    a=np.deg2rad(degrees);c,s=np.cos(a),np.sin(a)
    return np.array([[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]],dtype=np.float32)


class ShaderMesh:
    """A basic programmable OpenGL pipeline; also reused by the viewing lab."""
    def __init__(self,ctx,data,mode=None):
        from OpenGL.GL.shaders import compileProgram,compileShader
        self.ctx=ctx;g=ctx.gl;self.mode=g.GL_TRIANGLES if mode is None else mode
        data=np.ascontiguousarray(data,dtype=np.float32)
        if data.ndim!=2 or data.shape[1]!=6 or not np.isfinite(data).all():raise ValueError('Expected finite Nx6 position/color vertices')
        self.count=len(data);self.program=None;self.vbo=None
        root=Path(__file__).resolve().parent/'shaders'
        self.program=compileProgram(compileShader((root/'basic.vert').read_text(),g.GL_VERTEX_SHADER),compileShader((root/'basic.frag').read_text(),g.GL_FRAGMENT_SHADER))
        try:
            self.vbo=g.glGenBuffers(1);g.glBindBuffer(g.GL_ARRAY_BUFFER,self.vbo);g.glBufferData(g.GL_ARRAY_BUFFER,data.nbytes,data,g.GL_STATIC_DRAW);g.glBindBuffer(g.GL_ARRAY_BUFFER,0)
            self.position=g.glGetAttribLocation(self.program,'position');self.color=g.glGetAttribLocation(self.program,'vertexColor')
            self.mvp=g.glGetUniformLocation(self.program,'mvp');self.tint=g.glGetUniformLocation(self.program,'tint')
            if min(self.position,self.color,self.mvp,self.tint)<0:raise RuntimeError('Expected shader attributes/uniforms are missing')
            log=g.glGetProgramInfoLog(self.program)
            self.status={'linked':bool(g.glGetProgramiv(self.program,g.GL_LINK_STATUS)),
                         'program_log':log.decode() if isinstance(log,bytes) else str(log),'vertices':self.count,
                         'stride_bytes':24,'position_offset_bytes':0,'color_offset_bytes':12,'glsl_target':'1.20'}
            ctx.check()
        except Exception:self.close();raise

    def draw(self,matrix=None,tint=(1,1,1),mode=None):
        g=self.ctx.gl;matrix=np.eye(4,dtype=np.float32) if matrix is None else np.asarray(matrix,dtype=np.float32)
        tint=np.asarray(tint,dtype=float)
        if matrix.shape!=(4,4) or not np.isfinite(matrix).all() or tint.shape!=(3,) or not np.isfinite(tint).all():raise ValueError('Expected finite 4x4 MVP and three tint channels')
        g.glUseProgram(self.program)
        # OpenGL expects column-major storage with transpose=false.
        g.glUniformMatrix4fv(self.mvp,1,g.GL_FALSE,np.ascontiguousarray(matrix.T))
        g.glUniform3f(self.tint,*tint);g.glBindBuffer(g.GL_ARRAY_BUFFER,self.vbo)
        g.glEnableVertexAttribArray(self.position);g.glEnableVertexAttribArray(self.color)
        try:
            g.glVertexAttribPointer(self.position,3,g.GL_FLOAT,g.GL_FALSE,24,ctypes.c_void_p(0))
            g.glVertexAttribPointer(self.color,3,g.GL_FLOAT,g.GL_FALSE,24,ctypes.c_void_p(12))
            g.glDrawArrays(self.mode if mode is None else mode,0,self.count)
        finally:
            g.glDisableVertexAttribArray(self.position);g.glDisableVertexAttribArray(self.color)
            g.glBindBuffer(g.GL_ARRAY_BUFFER,0);g.glUseProgram(0)
        self.ctx.check()

    def close(self):
        g=self.ctx.gl
        if self.vbo is not None:g.glDeleteBuffers(1,[self.vbo]);self.vbo=None
        if self.program is not None:g.glDeleteProgram(self.program);self.program=None

    def __enter__(self):return self
    def __exit__(self,*exc):self.close()


def demo(angle=35,tint=(1,.55,.55)):
    out=output_dir(__file__)
    with Context(1200,430,title='Lab 8 — vertex and fragment shader pipeline') as ctx:
        with ShaderMesh(ctx,TRIANGLE) as mesh:
            settings=[('Vertex color interpolation',np.eye(4),(1,1,1)),('Vertex shader | rotated MVP',rotation_z(angle),(1,1,1)),('Fragment shader | tint uniform',np.eye(4),tint)]
            for i,(title,matrix,color) in enumerate(settings):
                ctx.panel(i,3,1,(-1,-1,1,1),title);mesh.draw(matrix,color)
            ctx.save(out/'shader_pipeline.png');ctx.metadata(out)
            (out/'shader_status.json').write_text(json.dumps(mesh.status,indent=2))
            ctx.hold()
    with Context(500,500,title='Lab 8 — animated shader uniform') as ctx:
        with ShaderMesh(ctx,TRIANGLE) as mesh:
            def frame(degrees):
                ctx.clear();ctx.panel(0,1,1,(-1,-1,1,1),f'GLSL MVP uniform | {degrees:.0f} degrees');mesh.draw(rotation_z(degrees))
            frames=[]
            for degrees in range(0,360,10):frame(degrees);frames.append(ctx.image())
            save_gif(frames,out/'shader_rotation.gif',70);ctx.hold(lambda t:frame((t*60)%360))
    (out/'results.json').write_text(json.dumps({'vertex_layout':'position.xyz, color.rgb','vertices':TRIANGLE.tolist(),
        'rotation_degrees':angle,'rotation_matrix':rotation_z(angle).tolist(),'tint':list(tint),
        'pipeline':'VBO -> vertex attributes -> GLSL vertex shader -> varying interpolation -> GLSL fragment shader -> framebuffer'},indent=2))
    print('Lab 8 OpenGL outputs:',out)


if __name__=='__main__':
    p=arguments(argparse.ArgumentParser(description=__doc__));p.add_argument('--angle',type=float,default=35);p.add_argument('--tint',nargs=3,type=float,default=[1,.55,.55]);a=p.parse_args()
    if not np.isfinite([a.angle,*a.tint]).all():p.error('Angle and tint must be finite')
    if min(a.tint)<0 or max(a.tint)>1:p.error('Tint channels must be in [0,1]')
    demo(a.angle,a.tint)
