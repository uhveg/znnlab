import numpy as np
import time
import pickle
import zmq
from noise import pnoise1
from collections import deque

class Sim_RANDOM2by2:
    def __init__(self, max_time = 10):
        self.time, self.dt = 0, 0.05
        self.A = np.array([
            [np.cos(self.time), -np.sin(self.time)],
            [np.sin(self.time), np.cos(self.time)]
        ])
        self.X = self.A + np.random.randn(*self.A.shape)*0.2
        self.max_time = max_time
        max_points = int((max_time - self.time) / self.dt)+1
        self.index = 0
        self.__logtime = np.empty((max_points,), dtype=np.float32)
        self.__logA = np.empty((max_points, self.A.size), dtype=np.float32)
        self.__logX = np.empty((max_points, self.X.size), dtype=np.float32)
        self.__append()

    def __append(self):
        self.__logtime[self.index] = self.time
        self.__logA[self.index, :] = self.A.flatten()
        self.__logX[self.index, :] = self.X.flatten()
        self.index += 1

    def __update(self):
        if self.index < self.__logtime.size:
            self.time += self.dt
            self.A = np.array([
                [np.cos(self.time), -np.sin(self.time)],
                [np.sin(self.time), np.cos(self.time)]
            ])
            self.X = self.A + np.random.randn(*self.A.shape)*0.3
            self.__append()
            # time.sleep(self.dt)

    def loop(self):
        self.index, self.time = 0, 0
        while self.time < self.max_time:
            self.__update()
            

    def getData(self):
        return [np.vstack((self.__logtime[:self.index], 
                           self.__logA[:self.index,i], 
                           self.__logX[:self.index,i])).T for i in range(self.X.size)]

class Sim_invA2by2_EDZNN:
    # Inverse of a 2 by 2 rotation matrix where we obtain
    # the values of the matrix via ZMQ in communication 
    # with the script simRot.py
    def __init__(self, max_time = 10, tau=0.01, h=0.4, ZMQ=False):
        self.time, self.dt = 0, tau
        self.max_time = max_time

        self.N = 4
        self.ZMQ = ZMQ
        # init communication via zmq
        if self.ZMQ:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            self.socket.connect("tcp://localhost:12345")
            self.socket.setsockopt(zmq.SUBSCRIBE, b"")

        self.A = deque(maxlen=3)
        self.X = None
        
        self.tau, self.gamma = self.dt, 1.0
        self.h = h
        
        max_points = int((max_time - self.time) / self.dt)+1
        self.index = 0
        self.__logtime = np.empty((max_points,), dtype=np.float32)
        self.__logA = np.empty((max_points, self.N), dtype=np.float32)
        self.__logX = np.empty((max_points, self.N), dtype=np.float32)

        self.flag = True

    def __append(self):
        self.__logtime[self.index] = self.time
        self.__logA[self.index, :] = self.A[2].T.flatten()
        self.__logX[self.index, :] = self.X.flatten()
        self.index += 1

    def __update(self):
        if self.index < self.__logtime.size:
            self.time += self.dt
            if self.ZMQ:
                data = self.socket.recv()
                A:np.ndarray = pickle.loads(data)
            else:
                angle = pnoise1(self.time*0.08) * 2 * np.pi
                # angle = self.time
                A = np.array([
                    [np.cos(angle), -np.sin(angle)],
                    [np.sin(angle), np.cos(angle)]
                ])
            self.A.append(A)
            if(len(self.A) == 3):
                if self.flag:
                    self.X = 2*self.A[2].T/np.trace(self.A[2] @ self.A[2].T)
                    # print(np.linalg.eigvals(self.A[2]))
                    # self.X = 0.1*np.eye(2)
                    self.flag = False
                else:
                    A_k, A_k_1, A_k_2 = self.A[2], self.A[1], self.A[0]
                    dA = (3*A_k - 4*A_k_1 + A_k_2) / (2*self.tau)
                    self.X += self.X @ (-self.h*(A_k @ self.X - np.eye(2)) - self.tau*(dA @ self.X))
                self.__append()

    def loop(self):
        self.index, self.time = 0, 0
        self.A.clear()
        self.flag = True
        while self.time < self.max_time:
            self.__update()

    def getData(self):
        return [np.vstack((self.__logtime[:self.index], 
                           self.__logA[:self.index,i], 
                           self.__logX[:self.index,i])).T for i in range(self.N)]


class Sim_invA2by2_5STEPZNN:
    # FIVE STEP DISCRETIZATION
    # Inverse of a 2 by 2 rotation matrix where we obtain
    # the values of the matrix via ZMQ in communication 
    # with the script simRot.py
    def __init__(self, max_time = 10, tau=0.01, h=0.4, ZMQ=False):
        self.time, self.dt = 0, tau
        self.max_time = max_time

        self.N = 4
        self.ZMQ = ZMQ
        # init communication via zmq
        if self.ZMQ:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            self.socket.connect("tcp://localhost:12345")
            self.socket.setsockopt(zmq.SUBSCRIBE, b"")

        self.A = deque(maxlen=5)
        self.X = deque(maxlen=5)
        
        self.tau, self.gamma = self.dt, 1.0
        self.h = h
        
        max_points = int((max_time - self.time) / self.dt)+1
        self.index = 0
        self.__logtime = np.empty((max_points,), dtype=np.float32)
        self.__logA = np.empty((max_points, self.N), dtype=np.float32)
        self.__logX = np.empty((max_points, self.N), dtype=np.float32)

        self.flag_ZERO = True
        self.flag_INIT = False

    def __append(self):
        self.__logtime[self.index] = self.time
        self.__logA[self.index, :] = self.A[-1].T.flatten()
        self.__logX[self.index, :] = self.X[-1].flatten()
        self.index += 1

    def __update(self):
        if self.index < self.__logtime.size:
            self.time += self.dt

            if not self.ZMQ:
                angle = pnoise1(self.time*0.08) * 2 * np.pi
                # angle = self.time
                A = np.array([
                    [np.cos(angle), -np.sin(angle)],
                    [np.sin(angle), np.cos(angle)]
                ])
            else:
                data = self.socket.recv()
                A:np.ndarray = pickle.loads(data)
            
            self.A.append(A)
            if(len(self.A) == 5):
                if self.flag_ZERO:
                    X = 2*self.A[2].T/np.trace(self.A[2] @ self.A[2].T)
                    self.X.append(X)
                    self.flag_ZERO = False
                    self.flag_INIT = True
                elif self.flag_INIT:
                    A_k, A_k_1, A_k_2, A_k_3, A_k_4 = self.A[-1], self.A[-2], self.A[-3], self.A[-4], self.A[-5]
                    dA = (25*A_k - 48*A_k_1 + 36*A_k_2 - 16*A_k_3 + 3*A_k_4) / (12*self.tau)
                    X = self.X[-1] + self.X[-1] @ (-self.h*(A_k @ self.X[-1] - np.eye(2)) - self.tau*(dA @ self.X[-1]))
                    self.X.append(X)
                    if len(self.X) == 5:
                        self.flag_INIT = False
                else:
                    X_k, X_k_1, X_k_2, X_k_3, X_k_4 = self.X[-1], self.X[-2], self.X[-3], self.X[-4], self.X[-5]
                    A_k, A_k_1, A_k_2, A_k_3, A_k_4 = self.A[-1], self.A[-2], self.A[-3], self.A[-4], self.A[-5]
                    dA = (25*A_k - 48*A_k_1 + 36*A_k_2 - 16*A_k_3 + 3*A_k_4) / (12*self.tau)
                    X = (5/24)*X_k + (1/2)*X_k_1 + (1/4)*X_k_2 + (1/6)*X_k_3 - (1/8)*X_k_4 \
                        + X_k @ (-self.h*(A_k @ X_k - np.eye(2)) - 2*self.tau*(dA @ X_k))
                    self.X.append(X)
                self.__append()

    def loop(self):
        self.index, self.time = 0, 0
        self.A.clear()
        self.X.clear()
        self.flag_ZERO = True
        self.flag_INIT = False
        while self.time < self.max_time:
            self.__update()

    def getData(self):
        return [np.vstack((self.__logtime[:self.index], 
                           self.__logA[:self.index,i], 
                           self.__logX[:self.index,i])).T for i in range(self.N)]