import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from pyopengltk import OpenGLFrame

class OBJViewer(OpenGLFrame):
    def __init__(self, master):
        super().__init__(master, width=230, height=230)
        self.pack()
        self.vertices = []
        self.faces = []
        self.normals = []
        self.center = [0, 0, 0]
        self.angle_x, self.angle_y = 0, 0
        self.trans_x, self.trans_y = 0, 0
        self.zoom_factor = -5
        self.wireframe_mode = 0  # 0: solid, 1: wireframe, 2: wireframe+solid
        self.bind("<Button-1>", self.start_rotate)
        self.bind("<B1-Motion>", self.rotate)
        self.bind("<Button-3>", self.start_pan)
        self.bind("<B3-Motion>", self.pan)
        self.bind("<Shift-Button-1>", self.start_pan)  # Shift + 左鍵 = 右鍵平移
        self.bind("<Shift-B1-Motion>", self.pan)
        self.bind("<MouseWheel>", self.zoom)
        self.master.bind_all("<Control-w>", self.toggle_wireframe)
    
    def initgl(self):
        print("初始化")
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.33, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        self.redraw()  # **確保 OpenGL 環境準備好後才開始繪製**
    
    def load_obj_data(self, obj_text):
        """解析 .obj 格式文本，並載入頂點與面資訊"""
        print("load")
        self.vertices = []
        self.faces = []
        try:
            for line in obj_text.split("\n"):
                if line.startswith("v "):
                    self.vertices.append(list(map(float, line.strip().split()[1:])))
                elif line.startswith("f "):
                    self.faces.append([int(i.split("/")[0]) - 1 for i in line.strip().split()[1:]])
            
            self.vertices = np.array(self.vertices)
            self.center = self.vertices.mean(axis=0)
            self.compute_normals()
        except Exception as e:
            print("Error loading OBJ:", e)

    def compute_normals(self):
        print("compute_normals")
        self.normals = np.zeros_like(self.vertices)
        for face in self.faces:
            v1, v2, v3 = [self.vertices[i] for i in face]
            normal = np.cross(v2 - v1, v3 - v1)
            normal = normal / np.linalg.norm(normal)
            for i in face:
                self.normals[i] += normal
        self.normals = np.array([n / np.linalg.norm(n) for n in self.normals])
    
    def redraw(self):
        print("redraw")
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.trans_x / 100, -self.trans_y / 100, self.zoom_factor)
        glRotatef(self.angle_x, 1, 0, 0)
        glRotatef(self.angle_y, 0, 1, 0)
        glTranslatef(-self.center[0], -self.center[1], -self.center[2])
        
        if self.wireframe_mode != 1:  # 當不是「純框線模式」時，繪製實體
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(1.0, 1.0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glColor3f(0.8, 0.8, 0.8)  # 灰色模型
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex in face:
                    glNormal3fv(self.normals[vertex])
                    glVertex3fv(self.vertices[vertex])
            glEnd()
    
        if self.wireframe_mode in [1, 2]:  # 框線模式 或 實體+框線模式
            glDisable(GL_POLYGON_OFFSET_FILL)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glColor3f(0.0, 0.0, 0.0)  # 細黑線
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex in face:
                    glVertex3fv(self.vertices[vertex])
            glEnd()
    
        self.tkSwapBuffers()
    
    def toggle_wireframe(self, event):
        self.wireframe_mode = (self.wireframe_mode + 1) % 3
        self.redraw()
    
    def start_rotate(self, event):
        self.last_x, self.last_y = event.x, event.y
    
    def rotate(self, event):
        dx, dy = event.x - self.last_x, event.y - self.last_y
        self.angle_x += dy * 0.5
        self.angle_y += dx * 0.5
        self.last_x, self.last_y = event.x, event.y
        self.redraw()
    
    def start_pan(self, event):
        self.last_x, self.last_y = event.x, event.y
    
    def pan(self, event):
        dx, dy = event.x - self.last_x, event.y - self.last_y
        self.trans_x += dx
        self.trans_y += dy
        self.last_x, self.last_y = event.x, event.y
        self.redraw()
    
    def zoom(self, event):
        self.zoom_factor += event.delta / 120
        self.redraw()