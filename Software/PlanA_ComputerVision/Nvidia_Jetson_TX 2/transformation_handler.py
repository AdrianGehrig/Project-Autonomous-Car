import numpy as np
import cv2
import matplotlib
import matplotlib.image 
import matplotlib.pyplot as plt

img = cv2.imread('frame.jpg')

def measure_warp(img):
    top = 0
    bottom = img.shape[0]
    def handler(e):
        if len(src)<4:
            plt.axhline(int(e.ydata), linewidth=2, color = 'r')
            plt.axvline(int(e.xdata), linewidth=2, color = 'r')
            src.append((int(e.xdata), int(e.ydata)))
        if len(src)==4:
            dst.extend([(200,bottom), (200,top), (500,top),(500,bottom)])
    was_interactive = matplotlib.is_interactive()
    if not matplotlib.is_interactive():
        plt.ion()
    fig = plt.figure()
    plt.imshow(img)
    global src
    global dst
    src = []
    dst = []
    cid1 = fig.canvas.mpl_connect('button_press_event', handler)
    cid2 = fig.canvas.mpl_connect('close_event', lambda e: e.canvas.stop_event_loop())
    fig.canvas.start_event_loop(timeout=-1)
    M = cv2.getPerspectiveTransform(np.asfarray(src, np.float32), np.asfarray(dst, np.float32))
    Minv = cv2.getPerspectiveTransform(np.asfarray(dst, np.float32), np.asfarray(src, np.float32))
    matplotlib.interactive(was_interactive)
    return M, Minv

M, Minv = measure_warp(img)
M.dump("trans_M.dat")
Minv.dump("trans_inv_M.dat")

