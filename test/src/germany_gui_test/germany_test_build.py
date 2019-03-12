"""
version 0.0.1.04032019 by Ammar
-GUI Placeholder

version 0.0.2 05032019 by Ammar
-added version 2 of feature detection (in seperate func for now)

version 0.0.3 07032019 by Ammar
-remove version 2 of feature detection
-improve feature detection for multiple images

version 0.0.4 08032019 by Ammar
-added lbp cascade classifier for object detection
    -very laggy

version 0.0.5 11032019 by Ammar
-moves top not to a seperate readme files

version 0.0.6 11032019 by Ammar
-added object detection with KAZE + flann method
-added choosing feature detection function
-minor GUI changes

version 0.0.7 11032019 by Ammar
-code rewrite for KivyCamera

version 0.0.8 12/3/2019 by Ammar
-object detection is now implemented
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
import os
from csv import reader
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class KivyCamera(Image):
    isRecording =  True # KivyCamera attribute for start/stop cam feed
    isType = 'object'
    object_ = open("object_list.txt", "r").read().split("\n")
    object_detect = object_[0]
    object_write = object_[0]
    object_img = ""
    object_kp = ""
    object_des = ""
    
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.app = App.get_running_app()


        # Settings for object detection
        self.kaze = cv2.KAZE_create()
        # FLANN parameters
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary
        self.flann = cv2.FlannBasedMatcher(index_params,search_params)
        # Ready first object image
        Clock.schedule_once(self.set_obj_img, 0)

        # Select external cam and get fps
        try:
            self.capture = cv2.VideoCapture(1)
            fps = self.capture.get(cv2.CAP_PROP_FPS)
        except:
            raise ValueError("No camera found!")
        # Set refresh schedule
        Clock.schedule_interval(self.update, 1/fps)

    def snap(self):
        ret, frame = self.capture.read()
        return ret, frame

    def update(self, dt):
        # Don't update if set to not recording
        if self.isRecording == True:
            ret, frame = self.snap()
            
            if ret:
                # Do feature detection
                # frame = self.feature_detection_lbp(xframe)
                frame = self.object_detection(frame)
                
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

    def set_obj_img(self, dt=0): # Ready object image for comparison
        # Get current object to detect
        object_ = KivyCamera.object_detect

        # Initialize var
        img = False
        _dir = f"template/{object_}/"

        # Check directory
        try:
            _get_list = os.listdir(_dir)
        except:
            raise ValueError(f"{object_} directory doesn't exist!")

        # Check if object already has image
        for each in _get_list:
            if each == "1.jpg":
                img = each
                break
            else:
                pass
        if not img:
            text = "No OBJECT found in template folder!"
            self.app.root.ids.main_page.ids.console.console_write(text)
            return

        # Feature detection on reference image
        img = cv2.imread(_dir+img, 0)
        KivyCamera.object_img = img
        KivyCamera.object_kp, KivyCamera.object_des = self.kaze.detectAndCompute(img,None)
        text = f"{object_} is ready for detection!"
        self.app.root.ids.main_page.ids.console.console_write(text)

    def object_detection(self, frame):
        # Threshold
        MIN_MATCH_COUNT = 10
        # Get frame and compute
        gray_f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp, des = self.kaze.detectAndCompute(gray_f, None)
        # Feature matching
        try:
            match = self.flann.knnMatch(KivyCamera.object_des, des, k=2)
            # Sort by their distance.
            match = sorted(match, key = lambda x:x[0].distance)
            # Ratio test, to get good matches.
            good = [m1 for (m1, m2) in match if m1.distance < 0.7 * m2.distance]
            # find homography matrix
            if len(good)>MIN_MATCH_COUNT:
                src_pts = np.float32([ KivyCamera.object_kp[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
                # find homography matrix in cv2.RANSAC using good match points
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                h,w = KivyCamera.object_img.shape[:2]
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                try:
                    # Draw box around object and put object name on top
                    dst = cv2.perspectiveTransform(pts,M)
                    dst2 = np.int32(dst[:1,:2])
                    dst2 = dst2.tolist()
                    w1,h1 = dst2[0][0]
                    cv2.polylines(frame,[np.int32(dst)],True,(0,200,0),3, cv2.LINE_AA)
                    cv2.putText(frame,KivyCamera.object_detect,(w1,h1-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,200,0), 3, cv2.LINE_AA)
                except:
                    pass
        except:
            pass
            
        return frame

    def feature_detection(self, frame):
        pass
            
    def cv2_select_roi(self):
        # Get untouched frame for ROI selection
        ret, im = self.snap()
        
        # Get feature name and template image listing
        object_ = KivyCamera.object_write
#         feature = KivyCamera.feature_write
        if KivyCamera.isType == "object":
            dir = f"template/{object_}/"
#         elif KivyCamera.isType == "feature":
#             dir = f"template/{object_}/{feature}/"
        else: # taking account into type error
            raise TypeError(f"{KivyCamera.isType} is not a valid type!")

        # Check if feature directory exist, Create new if doesnt
        try:
            template_list = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
        except:
            os.mkdir(dir)

        # Get latest filename. if empty start from 1
        if not template_list:
            template_list = [0]
        else:
            template_list = template_list[-1].split(".jpg")
        next = int(template_list[0])+1
        
        # Text for console
        success1 = f"Image captured successfully! Image saved in {dir} as {next}.jpg"
        unsuccessful = "Image captured unsuccessful"
        
        # Get user input on ROI
        r = cv2.selectROI("Image", im, False)
        
        # Write image if ROI is given, else return unsuccessful
        if r[1]:
            imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
            cv2.imwrite(dir+str(next)+'.jpg', imCrop)
            self.app.root.ids.main_page.ids.console.console_write(success1)
        else:
            self.app.root.ids.main_page.ids.console.console_write(unsuccessful)
        cv2.destroyAllWindows()
            
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
        
class MainSidebar(BoxLayout):
    def __init__(self, **kwargs):
        super(MainSidebar, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def change_page(self):
        KivyCamera.isRecording = False
        self.app.root.ids.main_page.manager.current = "settings_page"
        self.app.root.ids.main_page.ids.console.console_write("Entered SETTINGS Page!")
        self.app.root.ids.settings_page.ids.console.console_write("Entered SETTINGS Page!")

class SettingsSidebar(BoxLayout):
    def __init__(self, **kwargs):
        super(SettingsSidebar, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def change_page(self):
        KivyCamera.isRecording = True
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
        self.text = "GOOD!"
    
    def test_ng(self):
        self.background_color=(0.5, 0.0, 0.0, 1)
        self.text = "BAD!"
    
class GermanyApp(App):
    def build(self):
        self.title = "KIVY TEST GUI"
        Factory.register("HoverBehavior", HoverBehavior)
        return SM()

if __name__ == "__main__":
    GermanyApp().run()