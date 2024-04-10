# https://qiita.com/dario_okazaki/items/7892b24fcfa787faface

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
# from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivymd.app import MDApp

import math
import pandas as pd
import json
from pathlib import Path
import os

base_window_size = (1000, 1000)

Config.set('graphics', 'resizable', False)
Config.write()
Window.size = base_window_size
Window.top = 65
Window.left = 15




class PressureVisualizer(BoxLayout, MDApp):

    ########################
    # load json setting file
    ########################
    this_file_path = os.path.dirname(__file__)
    print(this_file_path)
    f = open(this_file_path + '/setting.json')
    # f = open('./setting.json')
    json_dict = json.load(f)


    ##############################
    # measure point color property
    ##############################
    c_left = [[0, 0, 0, 0.8]]*99
    c_right = [[0, 0, 0, 0.8]]*99
    color_left = ListProperty(c_left)
    color_right = ListProperty(c_right)



    #############################
    # rectangle of measured point
    #############################
    # 長方形のサイズを定義
    # rectangle_width = 30
    # rectangle_height = 50
    # rectangle_size = ListProperty([rectangle_width, rectangle_height])

    # 左足の測定点の長方形の座標を定義
    # 方針:各列のx座標の終点と一列目(踵側)のy座標の始点を指定して後は自動で生成
    num_of_rectangle_in_each_row = [5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 4] # 各行の長方形の数を定義. 下から順
    rectangle_x_end = [300, 320, 330, 330, 330, 335, 340, 350, 360, 370, 375, 380, 385, 375, 350] # 各行の長方形のx座標の終点を定義(土踏まず側)
    rectangle_y_start = 100 # y座標の始点を定義(踵側)
    rectangle_height = 47 # 長方形の高さは固定
    rectangle_width = [18, 19, 22, 23, 23, 24, 25, 27, 30, 32, 34, 33, 32, 31, 30]    # 列ごとに長方形の幅を定義. 
    rectangle_points_left = []
    rectangle_size_list = []
    for row in range(15):
        for col in range(num_of_rectangle_in_each_row[row]):
            rectangle_points_left.append([rectangle_x_end[row]-(rectangle_width[row]*(col+1)), rectangle_y_start+(row*rectangle_height)])
            rectangle_size_list.append([rectangle_width[row], rectangle_height])

    # 左足の測定点の座標をミラーリングして右足の測定点の座標を定義
    mirroring_axis = 500
    rectangle_points_right = []
    for row in range(15):
        for col in range(num_of_rectangle_in_each_row[row]):
            # x = ((mirroring_axis-rectangle_x_end[row]) + mirroring_axis) + (rectangle_width[row]*col)
            # y = rectangle_y_start+(row*rectangle_height)
            rectangle_points_right.append([((mirroring_axis-rectangle_x_end[row]) + mirroring_axis) + (rectangle_width[row]*col),
                                           rectangle_y_start+(row*rectangle_height)])

    rectangles_left = ListProperty(rectangle_points_left)
    rectangles_right = ListProperty(rectangle_points_right)
    rectangle_size = ListProperty(rectangle_size_list)



    #######################
    # text widget property
    ######################
    play_path = StringProperty()
    default_path = StringProperty(json_dict['default_path'])
    
    ####################################
    # recording/playback button property
    ####################################
    playback_button_pos = [750, 50]
    playback_button_size = [80, 80]

    playback_button_state = BooleanProperty(False)


    # スケールの違うディスプレイでリサイズする時に必要
    window_size = ListProperty(base_window_size)


    # フィードバック用文字列
    responce = StringProperty()

    # スライダーのポジションに渡す
    counter = NumericProperty()
    step = NumericProperty()





    def __init__(self, **kwargs):
        
        super(PressureVisualizer, self).__init__(**kwargs)
        self.counter = 0
        self.step = 100
        


    def update_color(self, count_up=True):

        # if self.playback_button_state == True:

        #     for i in range(99):
        #         try:
        #             left_num = self.color_df.iloc[self.counter, i]
        #             right_num = self.color_df.iloc[self.counter, i+99]
        #         except IndexError:
        #             self.responce = 'Error: DataFrame IndexError'
        #             print('Error: {}'.format(self.counter))
        #         else: 
        #             self.color_left[i] = [0, left_num, 0, 1/left_num]
        #             self.color_right[i] = [0, right_num, 0, 1/right_num]

            # if self.counter >= self.step:
            #     self.counter = 0
            # else:
            #     self.counter += 1

        for i in range(99):
            left_num = self.color_df.iloc[self.counter, i]
            right_num = self.color_df.iloc[self.counter, i+99]
            self.color_left[i] = [0, left_num, 0, 1/left_num]
            self.color_right[i] = [0, right_num, 0, 1/right_num]


    
        if count_up:
            if self.counter >= self.step:
                self.counter = 0
            else:
                self.counter += 1
        
        


    def set_play_path(self, **kwargs):
        self.play_path = self.ids.play_path.text

        try:
            self.df = pd.read_csv(self.play_path)
            self.responce = 'Loading ...'
        except FileNotFoundError:
            print('Error:FileNotFound')
            self.responce = 'Error : FileNotFound'
        else:

            self.step = len(self.df) - 1
            self.df = self.df.iloc[:,1:]

            max_list = self.df.max()
            self.max = max(max_list)

            min_list = self.df.min()
            self.min = min(min_list)

            self.color_df = self.df.applymap( lambda x: ((((x-self.min)/self.max) + 1) ** 2) -1 )

            self.responce = 'Loaded successfully'


    def playback_start(self, **kwargs):
        if self.playback_button_state == False:
            self.playback_button_state = True
            Clock.schedule_interval(self.update_color, 1.0/1000.0)
            self.responce = 'Playing'
        elif self.playback_button_state == True:
            self.playback_button_state = False
            Clock.unschedule(self.update_color)
            self.responce = 'Stop'
        # print('playback button state : {}'.format(self.playback_button_state))

    def on_slider_move(self, instance, value):
        self.counter = int(instance.value)
        try:
            self.update_color(count_up=False)
        except AttributeError:
            self.responce = 'Please set the csv path first'
        else:
            pass




class PressureVisualizerApp(App):

    def build(self):
        self.title = 'Pressure Visualizer'
        pressure_viewer = PressureVisualizer()

        return pressure_viewer



if __name__ == '__main__':
    PressureVisualizerApp().run()