from OpenGL import GL, GLU, GLUT

from PyQt5 import QtCore, QtWidgets, uic

import qdarkstyle

import traceback, sys, os, shutil, math

import numpy as np

class openGLDisplay(QtWidgets.QOpenGLWidget):

    def __init__(self, *args):

        super(openGLDisplay, self).__init__(*args)
        self.zoom = 1
        self.prev_x = 0.0
        self.prev_y = 0.0
        self.updateflag = 0
        self.coordinateflag = 0
        self.displayflag = 1
        self.framecount = 0
        self.pauseflag = False
        self.vectorflag = False

        self.center = np.array([0.0, 0.0, 0.0])
        self.resetup = np.array([-0.35355339, 0.8660254, -0.35355339])
        self.resetfront = np.array([0.61237244, 0.5, 0.61237244])
        self.front = self.resetfront
        self.up = self.resetup

        self.matrix = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        self.vector1 = np.array([[0.0], [0.0], [0.0]])
        self.vector2 = np.array([[0.0], [0.0], [0.0]])

        self.umatrix = np.identity(3)
        self.vmatrix = np.identity(3)
        self.smatrix = np.identity(3)

        self.u1vector = np.array([[0.0],[0.0],[0.0]])
        self.u2vector = np.array([[0.0],[0.0],[0.0]])
        self.u3vector = np.array([[0.0],[0.0],[0.0]])
        self.v1vector = np.array([[0.0],[0.0],[0.0]])
        self.v2vector = np.array([[0.0],[0.0],[0.0]])
        self.v3vector = np.array([[0.0],[0.0],[0.0]])

    def paint_axis(self):
        origin = self.center

        GL.glColor4f(1.0, 0.0, 0.0, 1)   

        GL.glBegin(GL.GL_LINES)
        GL.glVertex3f(origin[0], origin[1], origin[2])
        GL.glVertex3f(origin[0] + 0.5, origin[1], origin[2])
        GL.glEnd()        

        GL.glColor4f(0.0, 1.0, 0.0, 1)   

        GL.glBegin(GL.GL_LINES)
        GL.glVertex3f(origin[0], origin[1], origin[2])
        GL.glVertex3f(origin[0], origin[1] + 0.5, origin[2])
        GL.glEnd()  

        GL.glColor4f(0.0, 0.0, 1.0, 1)

        GL.glBegin(GL.GL_LINES)
        GL.glVertex3f(origin[0], origin[1], origin[2])
        GL.glVertex3f(origin[0], origin[1], origin[2] + 0.5)
        GL.glEnd()  

    def paint_vector(self, vector, r = 0.0, g = 0.0, b = 0.0):
        if(np.linalg.norm(vector) == 0):
            return

        GL.glColor4f(r, g, b, 1)   
        GL.glLineWidth(6)

        GL.glBegin(GL.GL_LINES)
        GL.glVertex3f(0.0 , 0.0, 0.0)
        GL.glVertex3fv(vector)
        GL.glEnd()

        GL.glLineWidth(2)

    def paint_plane(self, p1, p2, p3, p4):
        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex3fv(p1)
        GL.glVertex3fv(p2)
        GL.glVertex3fv(p3)
        GL.glVertex3fv(p4)
        GL.glEnd()

    def paint_plane_border(self, p1, p2, p3, p4):
        GL.glBegin(GL.GL_LINES)
        GL.glVertex3fv(p1)
        GL.glVertex3fv(p2)
        GL.glVertex3fv(p2)
        GL.glVertex3fv(p3)
        GL.glVertex3fv(p3)
        GL.glVertex3fv(p4)
        GL.glVertex3fv(p4)
        GL.glVertex3fv(p1)
        GL.glEnd()

    def paint_matrix_lines(self, matrix, s = 10):
        x = matrix.dot(np.array([[1.0], [0.0], [0.0]]))
        y = matrix.dot(np.array([[0.0], [1.0], [0.0]]))
        z = matrix.dot(np.array([[0.0], [0.0], [1.0]]))

        GL.glColor4f(0.75, 0.0, 0.0, 1)  
        GL.glBegin(GL.GL_LINES)
        for i in range(-s, s + 1):
            GL.glVertex3fv(i * y - x * s)
            GL.glVertex3fv(i * y + x * s)
            GL.glVertex3fv(i * x - y * s)
            GL.glVertex3fv(i * x + y * s)
        GL.glEnd()

        GL.glColor4f(0.0, 0.75, 0.0, 1)   
        GL.glBegin(GL.GL_LINES)
        for i in range(-s, s + 1):
            GL.glVertex3fv(i * z - y * s)
            GL.glVertex3fv(i * z + y * s)
            GL.glVertex3fv(i * y - z * s)
            GL.glVertex3fv(i * y + z * s)
        GL.glEnd()        

        GL.glColor4f(0.0, 0.0, 0.75, 1)   
        GL.glBegin(GL.GL_LINES)
        for i in range(-s, s + 1):
            GL.glVertex3fv(i * x - z * s)
            GL.glVertex3fv(i * x + z * s)
            GL.glVertex3fv(i * z - x * s)
            GL.glVertex3fv(i * z + x * s)
        GL.glEnd()

    def paint_matrix_planes(self, matrix, s = 5.0, d = 0.5):
        x = matrix.dot(np.array([[1.0], [0.0], [0.0]])) * s
        y = matrix.dot(np.array([[0.0], [1.0], [0.0]])) * s
        z = matrix.dot(np.array([[0.0], [0.0], [1.0]])) * s
        zero = np.array([[0.0], [0.0], [0.0]])
        camera = self.center + self.front * 20 * self.zoom

        planes = []
        planes.append([np.linalg.norm(camera - (x + y).T), x, y, 0.75, 0.0, 0.0])
        planes.append([np.linalg.norm(camera - (x - y).T), x, -y, 0.75, 0.0, 0.0])
        planes.append([np.linalg.norm(camera - (-x - y).T), -x, -y, 0.75, 0.0, 0.0])
        planes.append([np.linalg.norm(camera - (-x + y).T), -x, y, 0.75, 0.0, 0.0])

        planes.append([np.linalg.norm(camera - (x + z).T), x, z, 0.0, 0.0, 0.75])
        planes.append([np.linalg.norm(camera - (x - z).T), x, -z, 0.0, 0.0, 0.75])
        planes.append([np.linalg.norm(camera - (-x - z).T), -x, -z, 0.0, 0.0, 0.75])
        planes.append([np.linalg.norm(camera - (-x + z).T), -x, z, 0.0, 0.0, 0.75])

        planes.append([np.linalg.norm(camera - (z + y).T), z, y, 0.0, 0.75, 0.0])
        planes.append([np.linalg.norm(camera - (z - y).T), z, -y, 0.0, 0.75, 0.0])
        planes.append([np.linalg.norm(camera - (-z - y).T), -z, -y, 0.0, 0.75, 0.0])
        planes.append([np.linalg.norm(camera - (-z + y).T), -z, y, 0.0, 0.75, 0.0])
        planes.sort(key = lambda x: x[0], reverse = True)
        
        for plane in planes:
            GL.glColor4f(plane[3], plane[4], plane[5], d)
            self.paint_plane(plane[1], plane[1] + plane[2], plane[2], zero)

        GL.glColor4f(0, 0, 0, 1)

        self.paint_plane_border((x + y), (x - y), (-x - y), (-x + y))
        self.paint_plane_border((x + z), (x - z), (-x - z), (-x + z))
        self.paint_plane_border((y + z), (y - z), (-y - z), (-y + z))

    def paint_matrix(self, matrix, r = 0.15, g = 0.15, b = 0.15, d = 0.5):
        x = matrix.dot(np.array([[1.0], [0.0], [0.0]]))
        y = matrix.dot(np.array([[0.0], [1.0], [0.0]]))
        z = matrix.dot(np.array([[0.0], [0.0], [1.0]]))
        zero = np.array([0, 0, 0])

        GL.glColor4f(r, g, b, d)   

        self.paint_plane(zero, x, x + y, y)
        self.paint_plane(zero, y, y + z, z)
        self.paint_plane(zero, z, x + z, x)

        self.paint_plane(z, x + z, x + y + z, y + z)
        self.paint_plane(x, y + x, x + y + z, x + z)
        self.paint_plane(y, y + z, x + y + z, y + x)

        GL.glColor4f(0, 0, 0, 1)

        self.paint_plane_border(zero, x, x + y, y)
        self.paint_plane_border(z, x + z, x + y + z, y + z)

        self.paint_plane_border(zero, y, y + z, z)
        self.paint_plane_border(x, y + x, x + y + z, x + z)

        self.paint_plane_border(zero, z, x + z, x)
        self.paint_plane_border(y, y + z, x + y + z, y + x)

    def paint_coordinates(self, x, y, z):
        GL.glColor4f(0, 0, 0, 1)
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex3f(x, y, z)
        GL.glEnd()

        string = '(' + str(x) + ',' + str(y) + ',' + str(z) + ')'
        length = len(string) - 3

        GL.glRasterPos3f(x - (0.25 + length * 0.07), y - 0.15, z)
        for i in range(0, len(string)):
            GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_HELVETICA_12, ord(string[i]))

    def paintGL(self):
        self.loadScene()

        GLUT.glutInit()
        GL.glClearColor(0.7, 0.7, 0.7, 0)		
        GL.glClearDepth(1)

        if(self.coordinateflag):
            self.paint_axis()

        GL.glDisable(GL.GL_LINE_STIPPLE)
        self.paint_matrix_lines(np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]))
        self.paint_coordinates(0,0,0)

        if(self.displayflag == 1):  
            GL.glEnable(GL.GL_LINE_STIPPLE)    
            self.paint_vector(self.vector1)     
            GL.glDisable(GL.GL_LINE_STIPPLE)
            self.paint_vector(self.vector2)
            if(not self.vectorflag):
                self.paint_matrix(self.matrix)     
                self.paint_matrix_planes(self.matrix)  

        elif(self.displayflag == 2):
            self.paint_matrix(self.matrix)     
            self.paint_matrix_planes(self.matrix)  

        elif(self.displayflag == 3):
            x1 = self.vmatrix[:, 0]
            y1 = self.vmatrix[:, 1]
            z1 = self.vmatrix[:, 2]
            x = np.array([1.0, 0.0, 0.0])
            y = np.array([0.0, 1.0, 0.0])
            z = np.array([0.0, 0.0, 1.0])
            x2 = self.umatrix[:, 0]
            y2 = self.umatrix[:, 1]
            z2 = self.umatrix[:, 2]

            if(self.framecount < 120):
                self.paint_vector(x1)
                self.paint_vector(y1)
                self.paint_vector(z1)

            elif(self.framecount < 240):
                alpha = (self.framecount - 120) / 120
                self.paint_vector(x * alpha + x1 * (1 - alpha))
                self.paint_vector(y * alpha + y1 * (1 - alpha))
                self.paint_vector(z * alpha + z1 * (1 - alpha))

            elif(self.framecount < 360):
                alpha = (self.framecount - 240) / 120
                self.paint_vector(x * (1 - alpha) + x * self.smatrix[0, 0] * alpha)
                self.paint_vector(y * (1 - alpha) + y * self.smatrix[1, 1] * alpha)
                self.paint_vector(z * (1 - alpha) + z * self.smatrix[2, 2] * alpha)

            elif(self.framecount < 480):
                alpha = (self.framecount - 360) / 120
                self.paint_vector((x2 * alpha + x * (1 - alpha)) * self.smatrix[0, 0])
                self.paint_vector((y2 * alpha + y * (1 - alpha)) * self.smatrix[1, 1])
                self.paint_vector((z2 * alpha + z * (1 - alpha)) * self.smatrix[2, 2])

            elif(self.framecount < 550):
                self.paint_vector(x2 * self.smatrix[0, 0])
                self.paint_vector(y2 * self.smatrix[1, 1])
                self.paint_vector(z2 * self.smatrix[2, 2])

            else:
                self.framecount = -1
                self.displayflag = 2

            if(not self.pauseflag):
                self.framecount += 1
                self.updateflag = 1

        elif(self.displayflag == 4):
            u1 = self.u1vector
            u2 = self.u2vector
            u3 = self.u3vector
            v1 = self.v1vector
            v2 = self.v2vector
            v3 = self.v3vector
                
            if(self.framecount < 120):
                self.paint_vector(u1)
                self.paint_vector(u2)
                self.paint_vector(u3)

            elif(self.framecount < 180):
                self.paint_vector(v1)

            elif(self.framecount < 300):
                t = (self.framecount - 180) / 120.0

                GL.glLineWidth(3)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex3fv(-v1 * 100)
                GL.glVertex3fv(v1 * 100)
                GL.glEnd()
                GL.glLineWidth(2)

                v21 = (u2.T.dot(v1) / v1.T.dot(v1)) * v1

                self.paint_vector(u2 * (1 - t) + v2 * t)
                self.paint_vector(v21 * (1 - t))

            elif(self.framecount < 360):
                self.paint_vector(v1)
                self.paint_vector(v2)

            elif(self.framecount < 420):
                self.paint_vector(u3)
                self.paint_vector(v1)
                self.paint_vector(v2)

            elif(self.framecount < 540):
                t = (self.framecount - 420) / 120.0

                GL.glLineWidth(3)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex3fv(-v1 * 100)
                GL.glVertex3fv(v1 * 100)
                GL.glEnd()
                GL.glLineWidth(2)

                v31 = (u3.T.dot(v1) / v1.T.dot(v1)) * v1

                self.paint_vector(u3 * (1 - t) + (u3 - v31) * t)
                self.paint_vector(v31 * (1 - t))

            elif(self.framecount < 600):
                v31 = (u3.T.dot(v1) / v1.T.dot(v1)) * v1
                self.paint_vector(u3 - v31)
                self.paint_vector(v1)

            elif(self.framecount < 720):
                t = (self.framecount - 600) / 120.0

                GL.glLineWidth(3)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex3fv(-v2 * 100)
                GL.glVertex3fv(v2 * 100)
                GL.glEnd()
                GL.glLineWidth(2)

                v31 = (u3.T.dot(v1) / v1.T.dot(v1)) * v1
                v312 = (u3.T.dot(v2) / v2.T.dot(v2)) * v2

                self.paint_vector((u3 - v31) * (1 - t) + v3 * t)
                self.paint_vector(v312 * (1 - t))

            else:
                self.framecount = -1
                self.displayflag = 5

            if(not self.pauseflag):
                self.framecount += 1
                self.updateflag = 1

        elif(self.displayflag == 5):
            self.paint_vector(self.v1vector)
            self.paint_vector(self.v2vector)
            self.paint_vector(self.v3vector)

    def initializeGL(self):
        print("\033[4;30;102m INITIALIZE GL\033[0m")
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
        GL.glLineWidth(2)
        GL.glPointSize(4)
        GL.glLineStipple(1, 0xAA00)

    def loadScene(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        _, _, width, height = GL.glGetDoublev(GL.GL_VIEWPORT)
        GLU.gluPerspective(
            45,
            width / float(height or 1), 
            0.25, 
            200, 
        )

        cam_pos = self.center + self.front * 20 * self.zoom
        GLU.gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2], self.center[0], self.center[1], self.center[2], self.up[0], self.up[1], self.up[2])

    def rotatecamera(self, x , y):
        if(abs(x) + abs(y) == 0):
            return

        right = np.cross(self.up, self.front)
        rotatevector = (self.up * x + right * y) / (abs(x) + abs(y))
        angle = math.sqrt(math.pow(x, 2) + math.pow(y, 2))

        frontparallel = rotatevector.dot(self.front) * rotatevector
        frontperp1 = self.front - frontparallel
        if(np.linalg.norm(frontperp1) > 0):
            frontperp2 = np.cross(frontperp1 / np.linalg.norm(frontperp1), rotatevector)
            self.front = frontperp1 * math.cos(angle) + frontperp2 * math.sin(angle) * np.linalg.norm(frontperp1) + frontparallel
            self.front /= np.linalg.norm(self.front)

        upparallel = rotatevector.dot(self.up) * rotatevector
        upperp1 = self.up - upparallel
        if(np.linalg.norm(upperp1) > 0):
            upperp2 = np.cross(upperp1 / np.linalg.norm(upperp1), rotatevector)
            self.up = upperp1 * math.cos(angle) + upperp2 * math.sin(angle) * np.linalg.norm(upperp1) + upparallel
            self.up /= np.linalg.norm(self.up)

    def rotatecenter(self, x , y):
        if(abs(x) + abs(y) == 0):
            return

        right = np.cross(self.up, self.front)
        rotatevector = (self.up * x + right * y) / (abs(x) + abs(y))
        angle = math.sqrt(math.pow(x, 2) + math.pow(y, 2))

        frontparallel = rotatevector.dot(self.front) * rotatevector
        frontperp1 = self.front - frontparallel
        if(np.linalg.norm(frontperp1) > 0):
            frontperp2 = np.cross(frontperp1 / np.linalg.norm(frontperp1), rotatevector)
            front = frontperp1 * math.cos(angle) + frontperp2 * math.sin(angle) * np.linalg.norm(frontperp1) + frontparallel
            front /= np.linalg.norm(self.front)
            camera = self.center + self.front * 20 * self.zoom
            self.center = camera - front * 20 * self.zoom
            self.front = front

        upparallel = rotatevector.dot(self.up) * rotatevector
        upperp1 = self.up - upparallel
        if(np.linalg.norm(upperp1) > 0):
            upperp2 = np.cross(upperp1 / np.linalg.norm(upperp1), rotatevector)
            self.up = upperp1 * math.cos(angle) + upperp2 * math.sin(angle) * np.linalg.norm(upperp1) + upparallel
            self.up /= np.linalg.norm(self.up)

    def mousePressEvent(self, event):
        self.prev_x = event.x()
        self.prev_y = event.y()
        self.coordinateflag = 1
        self.updateflag = 1
        self.setFocus()

    def mouseReleaseEvent(self, event):
        self.coordinateflag = 0
        self.updateflag = 1

    def mouseMoveEvent(self, event):
        x = (event.x() - self.prev_x) * math.pi / 950.0
        y = (event.y() - self.prev_y) * math.pi / 950.0

        self.rotatecamera(x, y)
        self.prev_x = event.x()
        self.prev_y = event.y()
        self.updateflag = 1

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 400.0
        self.center += delta * self.front
        self.updateflag = 1

    def keyPressEvent(self, event):
        super(openGLDisplay, self).keyPressEvent(event)

        x = 0
        if(event.key() == QtCore.Qt.Key_Left):
            x = -0.2
        elif(event.key() == QtCore.Qt.Key_Right):
            x = 0.2

        self.center += x * self.zoom * np.cross(self.up, self.front)

        y = 0
        if(event.key() == QtCore.Qt.Key_Up):
            y = 0.2
        elif(event.key() == QtCore.Qt.Key_Down):
            y = -0.2

        self.center += y * self.zoom * self.up

        if(event.key() == QtCore.Qt.Key_P):
            self.pauseflag = not self.pauseflag

        if(event.key() == QtCore.Qt.Key_V):
            self.vectorflag = not self.vectorflag

        if(event.key() == QtCore.Qt.Key_X):
            self.front = self.resetfront
            self.up = self.resetup
        
        if(event.key() == QtCore.Qt.Key_F):
            self.front = np.array([0.0, 0.0, 1.0])
            self.up = np.array([0.0, 1.0, 0.0])

        if(event.key() == QtCore.Qt.Key_U):
            self.front = np.array([0.0, 1.0, 0.0])
            self.up = np.array([0.0, 0.0, -1.0])
        
        if(event.key() == QtCore.Qt.Key_R):
            self.front = np.array([1.0, 0.0, 0.0])
            self.up = np.array([0.0, 1.0, 0.0])

        if(event.key() == QtCore.Qt.Key_T):
            self.center = np.array([0.0, 0.0, 0.0])

        self.updateflag = 1
