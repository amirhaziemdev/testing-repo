"""
version 0.0.1.04032019 by Ammar
-GUI Placeholder

version 0.0.2 05032019 by Ammar
-added version 2 of feature detection (in seperate func for now)

"""
from kivy.config import Config
# Config.set('graphics', 'resizable', '0') # 0 being off 1 being on as in true/false
# Min width and height should be change according to screen spec.
# Changes should also be made within kv file
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '580')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
import cv2
import numpy as np
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class KivyCamera(Image):
    isRecording =  True #KivyCamera attribute for start/stop cam feed
    
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
        # Select external cam and get fps
        self.capture = cv2.VideoCapture(1)
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        
        # Check for camera
        if fps == 0:
            raise ValueError("No camera found!")
        
        # Set refresh rate
        Clock.schedule_interval(self.update, 1.0 / fps)
        
    def snap(self):
        ret, frame = self.capture.read()
        return ret, frame

    def update(self, dt):
        # Don't update if set to not recording
        if self.isRecording == True:
            ret, xframe = self.snap()
            
            if ret:
                # Do feature detection
                frame = self.feature_detection_v2(xframe)
                
                # Convert it to texture for display in Kivy GUI
                frame = cv2.flip(frame, 0) # Flip v
                w, h = int(self.width), int(self.height)
                buf = cv2.resize(frame, (w,h))
                buf = buf.tostring()
                image_texture = Texture.create(
                    size=(w, h), colorfmt="bgr")
                image_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                # display image from the texture
                self.texture = image_texture
    
    def feature_detection(self, frame):
        img_bgr = frame
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        temp = cv2.imread('1.jpg',1)
        template = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
        w,h = template.shape[::-1]
        
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        # Starting threshold value can be changes in kv file under Slider
        threshold = self.app.root.ids.settings_page.ids.threshold.value
        loc = np.where(res>=threshold)
        
        if loc[0].any():
            self.app.root.ids.main_page.ids.sidebar.ids.test_label.test_go()
        else: self.app.root.ids.main_page.ids.sidebar.ids.test_label.test_ng()
        
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_bgr, pt, (pt[0]+w, pt[1]+h), (0,255,255), 1)

        cv2.imshow("Current Detection Template", temp)
        return img_bgr
            
    def cv2_select_roi(self):
        self.isRecording = False
        ret, im = self.snap()
        r = cv2.selectROI("Image", im, False)
        if r[1]:
            imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
            cv2.imwrite("1" + ".jpg", imCrop)
            self.app.root.ids.main_page.ids.console.console_write("New image has been saved as 1.jpg")
        else:
            self.app.root.ids.main_page.ids.console.console_write("No ROI was selected!")
        cv2.destroyAllWindows()
        self.isRecording = True
        
    def feature_detection_v2(self, frame):
        src = cv2.imread('1.jpg')
        src2 = frame
        # Convert image to grayscale
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
        
        # Convert image to binary
        _, bw = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
        _2, bw2 = cv2.threshold(gray2, 160, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours2, _2 = cv2.findContours(bw2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        list1, list2, i_list, i2_list = [], [], [], []
        
        for i, c in enumerate(contours):
            # Calculate the area of each contour
            area = cv2.contourArea(c);
            # Ignore contours that are too small or too large
            if area < 1e2 or 1e5 < area:
                continue
            list1.append(i)
        for i2, c2 in enumerate(contours2):
            # Calculate the area of each contour
            area2 = cv2.contourArea(c2);
            # Ignore contours that are too small or too large
            if area2 < 1e2 or 1e5 < area2:
                continue
            list2.append(i2)
        
        for i in list1:
            for i2 in list2:
                ret = cv2.matchShapes(contours[i],contours2[i2],1,0.0)
                ret1 = cv2.matchShapes(contours[i],contours2[i2],2,0.0)
                ret2 = cv2.matchShapes(contours[i],contours2[i2],3,0.0)
                if (ret <= 1 and ret1 <= 1.5 and ret2 <= 0.5):
#                     print(f"ret: {ret}, ret1: {ret1}, ret2: {ret2}")
                    i_list.append({'index': i, 'ret': ret})
                    i2_list.append({'index': i2, 'ret': ret})
        
        comp = []
        x, x2 = False, False
        if len(i_list) > 1:
            for x in i_list:
                comp.append(x['ret'])
            x = comp.index(min(comp))
            x = i_list[x]['index']
        elif i_list:
            x = i_list[0]['index']
        if len(i2_list) > 1:
            comp.clear()
            for x2 in i2_list:
                comp.append(x2['ret'])
            x2 = comp.index(min(comp))
            x2 = i2_list[x2]['index']
        elif i2_list:
            x2 = i2_list[0]['index']
        if x and x2:
            cv2.drawContours(src, contours, x, (0, 0, 255), 2);
            cv2.drawContours(src2, contours2, x2, (0, 0, 255), 2);
            self.app.root.ids.main_page.ids.sidebar.ids.test_label.test_go()
        else: self.app.root.ids.main_page.ids.sidebar.ids.test_label.test_ng()
            
        return src2
            
class HoverBehavior(object):
    """Hover behavior.
    :Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget 
    """

    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)
    """Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    """

    def __init__(self, **kwargs):
        self.register_event_type("on_enter")
        self.register_event_type("on_leave")
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I"m not displayed <=> If have no parent
        pos = args[1]
        #Next line to_widget allow to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            #We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch("on_enter")
        else:
            self.dispatch("on_leave")

    def on_enter(self):
        pass

    def on_leave(self):
        pass
        
class SM(ScreenManager):
    pass

class MainPage(Screen):
    def __init__(self, **kwargs):
        super(MainPage, self).__init__(**kwargs)
        
class SettingsPage(Screen):
    def __init__(self, **kwargs):
        super(SettingsPage, self).__init__(**kwargs)
        
class Console(ScrollView):
    console = ObjectProperty()
    def __init__(self, **kwargs):
        super(Console, self).__init__(**kwargs)
    
    def console_write(self, text):
        self.console.text += "[ console ]  " + text + "\n"
        self.scroll_to(self.ids.console) # For autoscrolling
        
class Sidebar(BoxLayout):
    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def change_page(self):
        if self.app.root.ids.main_page.manager.current == "main_page":
            self.app.root.ids.main_page.manager.current = "settings_page"
            self.app.root.ids.settings_page.ids.sidebar.ids.settings_button.text = "BACK"
            self.app.root.ids.main_page.ids.console.console_write("Entered SETTINGS Page!")
            self.app.root.ids.settings_page.ids.console.console_write("Entered SETTINGS Page!")
        else:
            self.app.root.ids.main_page.manager.current = "main_page"
            self.app.root.ids.main_page.ids.console.console_write("Exited SETTINGS Page!")
            self.app.root.ids.settings_page.ids.console.console_write("Exited SETTINGS Page!")
        
class GenericButton(Button, HoverBehavior):
    def __init__(self, **kwargs):
        super(GenericButton, self).__init__(**kwargs)
        self.app = App.get_running_app()            
        
    def on_enter(self):
        self.background_color=(0.5, 0.5, 0.5, 1)
    def on_leave(self):
        self.background_color=(0.3, 0.3, 0.3, 1)
        
class RedButton(Button, HoverBehavior):
    def __init__(self, **kwargs):
        super(RedButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def cam_toggle(self):
        if KivyCamera.isRecording == True:
            KivyCamera.isRecording = False
            self.app.root.ids.main_page.ids.console.console_write("CAMERA has stopped!")
        else:
            KivyCamera.isRecording = True
            self.app.root.ids.main_page.ids.console.console_write("CAMERA is running!")
            
    def on_enter(self):
        self.background_color=(1.0, 0.1, 0.1, 1)
    def on_leave(self):
        self.background_color=(1.0, 0.3, 0.3, 1)
        
class TestLabel(Button):
    def __init__(self, **kwargs):
        super(TestLabel, self).__init__(**kwargs)
        self.app = App.get_running_app()
    
    def test_go(self):
        self.background_color=(0.0, 0.5, 0.0, 1)
        self.text = "GO!"
    
    def test_ng(self):
        self.background_color=(0.5, 0.0, 0.0, 1)
        self.text = "NG!"
    
class GermanyApp(App):
    def build(self):
        self.title = "KIVY TEST GUI"
        Factory.register("HoverBehavior", HoverBehavior)
        return SM()

if __name__ == "__main__":
    GermanyApp().run()