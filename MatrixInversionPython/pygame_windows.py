import pygame
import numpy as np
import threading

white200 = (200,)*3
white = (255,)*3
graysmoke = (50,)*3
whitesmoke = (100,)*3
vsgray = (31,)*3
yellow = (254,205,116)
bluenavy = (18,60,143)
redpink = (252,4,116)
gray62 = (62,)*3
gray24 = (24,)*3
blueturq = (81, 187, 254)
bluealpha = (81, 187, 254, 70)

cycler = [redpink, yellow, blueturq, white]

def map_value(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

class AxesPG:
    """" Create an axes for plot in a pygame window """
    def __init__(self, surface, xlims, ylims, pos, 
                 background = vsgray, border = white, title: str = "",
                 border_width = 3, callback = lambda x1,y1,x2,y2,t,dat: None,
                 dtx_grid=1, dty_grid=0.5):
        """
            background: tuple (r, g, b) color
            border: tuple (r, g, b) color
            xlims: tuple (lower, upper) bounds for x axis
            ylims: tuple (lower, upper) bounds for y axis
            pos: tuple (x, y, width, height) position of the axis in the pygame window
            callback: function with five parameters e.g f(x1,y1,x2,y2,title)
        """
        self.surface = surface
        self.bg = background
        self.bd = border
        self.bw = border_width
        self.xl = xlims
        self.yl = ylims
        self.p = pos
        self.title = title
        self.fontSmall = pygame.font.SysFont(None, 14)
        self.fontBig = pygame.font.SysFont(None, 32)
        self.pad = self.fontBig.get_linesize()
        self.innerPos = (pos[0]+self.pad, pos[1]+self.pad, pos[2] - 3*self.pad, pos[3] - 2*self.pad)
        self.gridx, self.gridy = dtx_grid, dty_grid
        self.linsX = np.arange(*xlims, self.gridx, dtype=np.float32)
        self.linsY = np.arange(*ylims, self.gridy, dtype=np.float32)
        self.flag_mdown = False
        self.selection_box_tl = (0,0)
        self.selection_box_br = (0,0)
        self.callback = callback
        self.data = None

    def __drawgrid(self):
        for v in self.linsX:
            dx = self.innerPos[0]+map_value(v, self.xl[0], self.xl[1], 0, self.innerPos[2])
            start = (dx, self.innerPos[1])
            stop = (dx, self.innerPos[1] + self.innerPos[3])
            text_surface = self.fontSmall.render(f"{v:.1f}", True, whitesmoke)
            pygame.draw.line(self.surface, graysmoke, start, stop)
            self.surface.blit(text_surface, (stop[0]-text_surface.get_width()/2, stop[1]+5))
        for v in self.linsY:
            dy = self.innerPos[1]+map_value(v, self.yl[1], self.yl[0], 0, self.innerPos[3])
            start = (self.innerPos[0], dy)
            stop = (self.innerPos[0] + self.innerPos[2], dy)
            text_surface = self.fontSmall.render(f"{v:.1f}", True, whitesmoke)
            pygame.draw.line(self.surface, graysmoke, start, stop)
            self.surface.blit(text_surface, (stop[0]+5, stop[1]-text_surface.get_height()/2))

    def __drawline(self, xdata, ydata, color=yellow, wd=1):
        pts = [(int(x), int(y)) for x, y in zip(xdata, ydata)]
        if wd==1:
            pygame.draw.aalines(self.surface, color, False, pts)
        else:
            pygame.draw.lines(self.surface, color, False, pts, width=wd)

    def __ishover(self, mouse) -> bool:
        return (self.innerPos[0] < mouse[0] < self.innerPos[0] + self.innerPos[2]) \
            and (self.innerPos[1] < mouse[1] < self.innerPos[1] + self.innerPos[3])
    
    def draw(self, data: np.ndarray = None, mouse=None):
        pygame.draw.rect(self.surface, self.bg, self.p, border_radius=10)
        self.__drawgrid()
        pygame.draw.rect(self.surface, self.bd, self.p, width=self.bw,border_radius=10)
        if data.shape[0] > 1 and data.shape[1] > 1:
            self.data = data
            t = map_value(data[:,0], self.xl[0], self.xl[1], self.innerPos[0], self.innerPos[0]+self.innerPos[2])
            for i in range(data.shape[1]-1):
                li = map_value(data[:,i+1], self.yl[1], self.yl[0], self.innerPos[1], self.innerPos[1]+self.innerPos[3])
                self.__drawline(t, li, cycler[i], wd=[3,1][i])
        if mouse and self.flag_mdown:
            try:
                self.selection_box_br = (mouse[0]-self.selection_box_tl[0], mouse[1]-self.selection_box_tl[1])
                myrect = [self.selection_box_tl[0], self.selection_box_tl[1], 
                          self.selection_box_br[0], self.selection_box_br[1]]
                # pygame.draw.rect(self.surface, bluealpha, myrect)
                s = pygame.Surface((myrect[2], myrect[3]), pygame.SRCALPHA)   # per-pixel alpha
                s.fill(bluealpha)                         # notice the alpha value in the color
                self.surface.blit(s, (myrect[0],myrect[1]))
            except:
                pass

    def clicked(self, mouse):
        if not self.__ishover(mouse):
            return
        self.flag_mdown = True
        self.selection_box_tl = mouse
    
    def released(self, mouse):
        # if not self.__ishover(mouse):
        #     return
        if self.flag_mdown:
            self.flag_mdown = False
            if self.data is not None:
                vals_l = [self.selection_box_tl[0]-self.innerPos[0], self.selection_box_tl[1]-self.innerPos[1]]
                vals_u = [vals_l[0]+self.selection_box_br[0], vals_l[1]+self.selection_box_br[1]]
                vals = [map_value(vals_l[0], 0, self.innerPos[2], *self.xl), 
                        map_value(vals_l[1], self.innerPos[3], 0, *self.yl),
                        map_value(vals_u[0], 0, self.innerPos[2], *self.xl),
                        map_value(vals_u[1], self.innerPos[3], 0, *self.yl)]
                self.callback(*vals, self.title, self.data)

class Button:
    def __init__(self, surface, pos, text, cllFcn, endf = lambda: None, background = whitesmoke, border = white, border_width=2):
        self.p = pos
        self.bg = background
        self.bd = border
        self.bw = border_width
        self.surface = surface
        self.text = text
        font = pygame.font.SysFont(None, 26)
        self.text_surface = font.render(self.text, True, white)
        self.enabled = True
        self.flag = False
        self.highlight = True
        self.callback = cllFcn
        self.callThread = threading.Thread(target=self.callback)
        self.endedFlag = endf
    
    def __ishover(self, mouse) -> bool:
        return (self.p[0] < mouse[0] < self.p[0] + self.p[2]) and (self.p[1] < mouse[1] < self.p[1] + self.p[3])

    def __update(self, mouse):
        if self.flag and not self.callThread.is_alive():
            self.enabled, self.flag = True, False
            self.endedFlag()
        # self.enabled = not self.callThread.is_alive()
        if self.enabled:
            self.highlight = False
            if self.__ishover(mouse):
                self.highlight = True
        

    def draw(self, mousePos=None):
        if mousePos:
            self.__update(mousePos)
        bg = self.bg
        if self.highlight:
            bg = [f*1.5 for f in self.bg]
        if not self.enabled:
            bg = [f*0.5 for f in self.bg]
        pygame.draw.rect(self.surface, bg, self.p, border_radius=5)
        pygame.draw.rect(self.surface, self.bd, self.p, width=self.bw, border_radius=5)
        self.surface.blit(self.text_surface, (self.p[0] + self.p[2]/2 - self.text_surface.get_width()/2, 
                                              self.p[1] + self.p[3]/2 - self.text_surface.get_height()/2))

    def clicked(self, mouse):
        if not self.enabled:
            return
        if not self.__ishover(mouse):
            return
        if self.callThread.is_alive():
            return
        self.enabled = False
        self.highlight = False
        self.flag = True
        self.callThread = threading.Thread(target=self.callback)
        self.callThread.start()