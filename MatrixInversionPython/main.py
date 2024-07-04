import matplotlib.axes
import pygame
import matplotlib
import argparse
import matplotlib.pyplot as plt
from pygame_windows import *
from simulations import *

# matplotlib.rcParams['toolbar'] = 'None'
plt.style.use("assets/vstyle.mplstyle")

width_s, height_s = 1920, 1080
w, h = 920, 570
sbig, ssmall = 1.2, 0.4
wbig, hbig, wsmall, hsmall = int(w*sbig), int(h*sbig), int(w*ssmall), int(h*ssmall)
pbig = (int((width_s-wbig)/2), 50)
psmall = (int((width_s-wsmall)/2), int(height_s-hsmall-50))

px = 1/plt.rcParams['figure.dpi']  # pixel in inches

def run_simulation():
    btns[1].enabled = False
    sim.loop()
def toogle_btn2():
    btns[1].enabled = True
def zoomed_plt(x1, y2, x2, y1, title:str, data:np.ndarray):
    fig, ax = plt.subplots(figsize=(wbig*px,hbig*px))
    ax:matplotlib.axes.Axes
    fig.canvas.manager.window.move(*pbig)
    for i in range(data.shape[1]-1):
        ax.plot(data[:,0], data[:,i+1], linewidth=[2,1][i])
    ax.set_title(f"{title} : Zoomed Area")
    ax.set_xlabel("time(s)")
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)
    plt.legend(["$A_{0,0}^{-1}$", "$X_{0,0}$"])
    plt.show()
def view_plots():
    def on_close_f1(handle):
        fig2.set_size_inches(wbig*px,hbig*px)
        fig2.canvas.manager.window.move(*pbig)
    # define data
    timeline = data[0][:,0]
    Dat = np.array(data)
    A = Dat[:,:,1].reshape((2,2,-1)).transpose(2,0,1)
    X = Dat[:,:,2].reshape((2,2,-1)).transpose(2,0,1)
    error = Dat[:,:,1] - Dat[:,:,2]
    froNorm = np.array([np.linalg.norm(a.T @ x - np.eye(2), ord='fro') for a, x in zip(A, X)])
    # mse:np.ndarray = np.mean(error**2, axis=0)
    # Create a figure MAIN
    fig, ax = plt.subplots(figsize=(wbig*px,hbig*px))
    ax:matplotlib.axes.Axes
    fig.canvas.manager.window.move(*pbig)
    fig.canvas.mpl_connect('close_event', on_close_f1)


    ax.plot(timeline, froNorm)
    ax.set_title(f"$\| A_k X_k - I \|_F$")
    ax.set_xlabel("time(s)")
    # Create a figure secundary
    idx = np.random.randint(0,4)
    fig2, ax2 = plt.subplots(figsize=(wsmall*px,hsmall*px))
    ax2:matplotlib.axes.Axes
    fig2.canvas.manager.window.move(*psmall)
    # fig2.canvas.mpl_connect('close_event', on_close_f2)
    ax2.plot(timeline, Dat[idx,:,1], linewidth=2)
    ax2.plot(timeline, Dat[idx,:,2], linewidth=1)
    ax2.set_title(r"Approximation")
    ax2.set_xlabel("time(s)")
    end = timeline.size
    dt = timeline[1] - timeline[0]
    npoints = int(2 / dt)
    dmin = np.min(Dat[idx,end-npoints:,1:])
    dmax = np.max(Dat[idx,end-npoints:,1:]) 
    diff = dmax - dmin
    x1, x2, y1, y2 = timeline[end-npoints], timeline[-1], dmin-0.5*diff, dmax+0.5*diff  # subregion of the original image
    axins = ax2.inset_axes(
                [0.07, 0.07, 0.4, 0.4],
                xlim=(x1, x2), ylim=(y1, y2))
    axins.plot(timeline, Dat[idx,:,1])
    axins.plot(timeline, Dat[idx,:,2])
    ax2.indicate_inset_zoom(axins, edgecolor="white", linewidth=2)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Zeroing Neural Network for matrix inversion")
    parser.add_argument('--stop', type=float, default=30, help="The time at which the simulation will stop")
    parser.add_argument('--znn', type=str, default='euler', help="Dscretization technique (Euler difference: 'euler' / Five step: otherwise)")
    parser.add_argument('--zmq', type=bool, default=False, help="Use real-time communication with ZMQ and the script simRot.py")

    args = parser.parse_args()
    assert args.stop > 0
    assert args.znn in ['euler', 'fivestep'] 

    stoptime = args.stop
    if args.znn == 'euler':
        sim = Sim_invA2by2_EDZNN(max_time=stoptime, ZMQ=args.zmq)
    else:
        sim = Sim_invA2by2_5STEPZNN(max_time=stoptime, ZMQ=args.zmq)
    data: list[np.ndarray] = None

    pygame.init()
    pygame.display.set_caption("Graphs")
    screen = pygame.display.set_mode((w, h))


    axes = [AxesPG(screen, (0,stoptime), (-2,2), (50,100,400,200), callback=zoomed_plt, dtx_grid=stoptime/10),
        AxesPG(screen, (0,stoptime), (-2,2), (50,320,400,200), callback=zoomed_plt, dtx_grid=stoptime/10),
        AxesPG(screen, (0,stoptime), (-2,2), (470,100,400,200), callback=zoomed_plt, dtx_grid=stoptime/10),
        AxesPG(screen, (0,stoptime), (-2,2), (470,320,400,200), callback=zoomed_plt, dtx_grid=stoptime/10)]
    btns = [Button(screen, (300,25,150,50), "RUN", run_simulation, endf=toogle_btn2),
            Button(screen, (470,25,150,50), "VIEW", lambda:None, endf=view_plots)]

    btns[1].enabled = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in btns:
                    btn.clicked(mouse)
                for ax in axes:
                    ax.clicked(mouse)
            if event.type == pygame.MOUSEBUTTONUP:
                for ax in axes:
                    ax.released(mouse)
        
        mouse = pygame.mouse.get_pos()

        data = sim.getData()

        screen.fill(gray24)
        for ax, dat in zip(axes, data):
            ax.draw(dat, mouse)
        for btn in btns:
            btn.draw(mouse)
        # Update the display
        pygame.display.flip()
    pygame.quit()
