import cv2
import numpy as np
from matplotlib import pyplot as plt
# import win32api,win32con
from win32api import GetSystemMetrics
from win32con import SRCCOPY,SM_CXSCREEN,SM_CYSCREEN
from win32gui import FindWindow, GetWindowDC, DeleteObject, ReleaseDC,GetDesktopWindow
from win32ui import CreateDCFromHandle, CreateBitmap
import time
import pyautogui
import sys
import threading


#    左上和右上坐标

class GameStart():

    # 点击屏幕并且获取坐标
    def __init__(self):
        self.first_pointX=0
        self.first_pointY=0
        self.second_pointX=0
        self.second_pointY=0
        self.clock_number=0
        self.center_post_list=[]
    def on_EVENT_LBUTTONDOWN(self,event, x, y, flags, param):
        if (self.clock_number > 1):
            cv2.destroyWindow('image')
        # 左键按下
        if event == cv2.EVENT_LBUTTONDOWN:
            # 输出坐标信息

            xy = "%d,%d" % (x, y)
            print(xy)
            if(self.clock_number==0):
                self.first_pointX=x
                self.first_pointY=y
            elif(self.clock_number==1):
                self.second_pointX = x
                self.second_pointY = y
            self.clock_number+=1
    def windowshots(self,x1, y1, x2, y2):
        w, h = x2 - x1, y2 - y1
        # wDC = GetDC(hwnd)
        # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        # 获取桌面
        hdesktop = GetDesktopWindow()
        wDC = GetWindowDC(hdesktop)
        # 根据窗口的DC获取dcObj
        dcObj = CreateDCFromHandle(wDC)
        # dcObj创建可兼容的DC
        cDC = dcObj.CreateCompatibleDC()
        # 创建bigmap准备保存图片
        dataBitMap = CreateBitmap()
        # 为bitmap开辟空间
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        # 高度cDC，将截图保存到dataBitMap中
        cDC.SelectObject(dataBitMap)
        # 截取从左上角（0，0）长宽为（w，h）的图片
        cDC.BitBlt((0, 0), (w, h), dcObj, (x1, y1), SRCCOPY)
        # 保存图像
        # dataBitMap.SaveBitmapFile(cDC, 'test.jpg')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        # Free Resources
        # 释放资源
        DeleteObject(dataBitMap.GetHandle())
        cDC.DeleteDC()
        dcObj.DeleteDC()
        ReleaseDC(hdesktop, wDC)

        screen = np.frombuffer(signedIntsArray, dtype='uint8')
        screen.shape = (h, w, 4)
        screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        return screen

    def press(self,key):
        print(key.char)
        # if(key.char=="q"):
        #     return sys.exit(0)

    def plt_show0(self,img):
        b, g, r = cv2.split(img)
        img = cv2.merge([r, g, b])
        plt.imshow(img)
        plt.show()

    def plt_show(self,img):
        plt.imshow(img, cmap="gray")
        plt.show()


    def get_pos(self,contours):
        pos_list = []
        for contour in contours:
            rect = cv2.boundingRect(contour)
            x, y, weight, height = rect
            pos_list.append([x, y + height])
        return pos_list

    def speed_pos(self,contours, Min_Area=6500):
        chunk_contours = []
        for item in contours:
            if cv2.contourArea(item) > Min_Area:
                # 用最小巨型进行包裹
                rect = cv2.boundingRect(item)
                x, y, weight, height = rect
                if (height > 120):
                    for next_y in range(int(height / 120) + 1):
                        next_y += 1
                        chunk_contours.append([x + weight / 8, y + 120 * next_y])
                else:
                    chunk_contours.append([x + weight / 8, y + height])
        return chunk_contours
    def start(self):
        max_win_width=GetSystemMetrics(SM_CXSCREEN)
        max_win_height=GetSystemMetrics(SM_CYSCREEN)
        img=self.windowshots(0,0,max_win_width,max_win_height)
        cv2.namedWindow("image",cv2.WINDOW_KEEPRATIO)
        cv2.setMouseCallback("image", self.on_EVENT_LBUTTONDOWN)
        cv2.imshow("image",img)
        cv2.waitKey(0)
        time.sleep(0.5)
        # print(self.clock_number)
        while(1):
            # global center_post_list
            # hwnd = 0
            # st = time.time()
            img = self.windowshots(self.first_pointX,self.first_pointY,self.second_pointX,self.second_pointY)
            # cv2.imshow("test",img)
            # cv2.waitKey()
            # et = time.time() - st
            # FPS = 1//et
            img=np.asarray(img)
            cv2.imwrite("image.png", img)
            img_gray=img.copy()
            img_gray=cv2.cvtColor(img_gray,cv2.COLOR_BGR2GRAY)
            ret,img_threshold=cv2.threshold(img_gray,60,255,cv2.THRESH_BINARY_INV)
            kernelY=cv2.getStructuringElement(cv2.MORPH_RECT,(5,7))
            image = cv2.morphologyEx(img_threshold, cv2.MORPH_CLOSE, kernelY, iterations=1)
            kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            image = cv2.erode(image, kernelX)
            contours,hierarchy=cv2.findContours(image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            self.center_post_list=self.speed_pos(contours)
            self.center_post_list=sorted(self.center_post_list, key=lambda tup: tup[1],reverse=True)
            if (len(self.center_post_list)==0):
                break

    def work(self):
        while (1):
            for pos in self.center_post_list:
                print(self.center_post_list)
                pyautogui.moveTo(int(pos[0] + self.first_pointX), int(pos[1] +self.first_pointY), duration=0)
                pyautogui.click()
                break
if __name__ == '__main__':
    Start=GameStart()
    t1 = threading.Thread(target=Start.start)

    t2 = threading.Thread(target=Start.work)
    t1.start()
    t2.start()
    # t1.join()
    # t2.join()