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

version 0.0.7 12032019 by Ammar
-back to using template matching for feature detection
-more GUI functions ( Reset )
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
import shutil
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.dropdown import DropDown
from kivy.uix.slider import Slider
import json
from kivy.uix.popup import Popup

class KivyCamera(Image):
    isDetecting =  True # KivyCamera attribute for start/stop cam feed
    feature = open("feature_list.txt", "r").read().split("\n") # Current feature list
    feature_detect = feature[0] # For detection on camera
    feature_write = feature[0] # For writing new images to feature dir
    
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
        # Select external cam and get fps
        try:
            self.capture = cv2.VideoCapture(0)
            fps = self.capture.get(cv2.CAP_PROP_FPS)
        except:
            raise ValueError("No camera found!")
        
        # Set refresh rate
        Clock.schedule_interval(self.update, 1/fps)

    def snap(self):
        ret, frame = self.capture.read()
        return ret, frame

    def update(self, dt):
        ret, frame = self.snap()
        
        if ret:
            # Do feature detection
            if self.isDetecting == True:
                frame = self.feature_detection(frame)
            
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
            
    def cv2_select_roi(self):
        # Get untouched frame for ROI selection
        ret, im = self.snap()
        
        # Get feature name and template image listing
        feature = KivyCamera.feature_write
        dir = f"template/{feature}/"

        # Check if feature directory exist, Create new if doesn't
        try:
            template_list = os.listdir(dir)
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
        unsuccessful = "Image captured unsuccessful! Cannot capture whole image!"
        
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
    
    def feature_detection(self, frame): # Using template matching
        good = 0
        # Get frame and change to gray
        img_bgr = frame
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Get feature name and template image listing
        feature = KivyCamera.feature_detect
        dir = f"template/{feature}/"
        template_list = os.listdir(dir)
        
        # If listing is empty return back frame
        if not template_list:
            return img_bgr
        
        # Foreach image in feature dir do template matching with frame
        for img in template_list:
            template = cv2.imread(str(dir+img), 0)
            h,w = template.shape[0:2]
            
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            # Threshold for template matching can be control within GUI (default:0.8)
            threshold = self.app.root.ids.settings_page.ids.threshold.value
            loc = np.where(res>=threshold)
            if loc[0].any():
                good+=1
            
            # Draw on frame the matching region
            for pt in zip(*loc[::-1]):
                cv2.rectangle(img_bgr, pt, (pt[0]+w, pt[1]+h), (0,255,255), 1)
        
        # Kivy GUI manipulation for if there is a match
        if good > 0:
            self.app.root.ids.main_page.ids.sidebar.ids.test_label.test_go()
        else:
            self.app.root.ids.main_page.ids.sidebar.ids.test_label.test_ng()
                
        return img_bgr
    
    def auto_image_rot(self, img):
        pass
            
class HoverBehavior(object):
    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)

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
    pass
        
class SettingsPage(Screen):
    pass

class AddFPopup(Popup):
    def __init__(self, **kwargs):
        super(AddFPopup, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def add_feature(self):
        self.dismiss()
        feature = open("feature_list.txt", "a+")
        text = self.ids.feature_name.text
        for each in KivyCamera.feature:
            if text == "":
                self.app.root.ids.settings_page.ids.console.console_write(f"Invalid name!")
                return
            elif text == each:
                self.app.root.ids.settings_page.ids.console.console_write(f"{text} already exist!")
                return
        feature.write(text+"\n")
        self.app.root.ids.settings_page.ids.console.console_write(f"{text} has been added!")
        
class DelFPopup(Popup):
    def __init__(self, **kwargs):
        super(DelFPopup, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def del_feature(self):
        pass

class Console(ScrollView):
    console = ObjectProperty()
    def __init__(self, **kwargs):
        super(Console, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
        # Boot up sequence
        Clock.schedule_once(self.start_up, 0)
        
    def start_up(self, dt):
        try:
            self.import_settings()
            self.console_write("Settings loaded!")
        except:
            raise ValueError("Settings file doesnt exist")
    
    def console_write(self, text):
        self.console.text += "[   System   ]  " + text + "\n"
        self.scroll_to(self.ids.console) # For autoscrolling
        
    def import_settings(self):
        settings = open("settings.json", "r").read()
        settings = json.loads(settings)
        self.app.root.ids.settings_page.ids.threshold.value = settings["Settings"]["Threshold"]
        
class MainSidebar(BoxLayout):
    def __init__(self, **kwargs):
        super(MainSidebar, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def reset(self):
        feature = open("feature_list.txt", "w")
        feature.write("feature1\nfeature2\n")
        feature.close()
        feature = open("feature_list.txt", "r").read().split("\n")
        KivyCamera.feature_detect = feature[0]
        KivyCamera.feature_write = feature[0]
        
        for each in feature:
            shutil.rmtree(f"template/{each}")
        self.copytree("data","template")
        
        self.app.root.ids.main_page.ids.console.console_write("DATA RESET!!!")
        
    def copytree(self, src, dst, symlinks = False, ignore = None):
        if not os.path.exists(dst):
            os.makedirs(dst)
            shutil.copystat(src, dst)
        lst = os.listdir(src)
        if ignore:
            excl = ignore(src, lst)
            lst = [x for x in lst if x not in excl]
        for item in lst:
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if symlinks and os.path.islink(s):
                if os.path.lexists(d):
                    os.remove(d)
                os.symlink(os.readlink(s), d)
                try:
                    st = os.lstat(s)
                    mode = stat.S_IMODE(st.st_mode)
                    os.lchmod(d, mode)
                except:
                    pass # lchmod not available
            elif os.path.isdir(s):
                self.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        
    def change_page(self):
        KivyCamera.isDetecting = False
        self.app.root.ids.main_page.manager.current = "settings_page"
        self.app.root.ids.main_page.ids.console.console_write("Entered SETTINGS Page!")
        self.app.root.ids.settings_page.ids.console.console_write("Entered SETTINGS Page!")

class SettingsSidebar(BoxLayout):
    def __init__(self, **kwargs):
        super(SettingsSidebar, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def change_page(self):
        KivyCamera.isDetecting = True
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
        if KivyCamera.isDetecting == True:
            KivyCamera.isDetecting = False
            self.app.root.ids.main_page.ids.console.console_write("Feature Detection has been turned OFF!")
        else:
            KivyCamera.isDetecting = True
            self.app.root.ids.main_page.ids.console.console_write("Feature Detection has turned ON!")
            
    def on_enter(self):
        self.background_color=(1.0, 0.3, 0.3, 1)
    def on_leave(self):
        self.background_color=(1.0, 0.1, 0.1, 1)
        
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
        
class ThresholdSlider(Slider):
    def __init__(self, **kwargs):
        super(ThresholdSlider, self).__init__(**kwargs)
        self.app = App.get_running_app()
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.app.root.ids.settings_page.ids.console.console_write(f"Threshold value has been changed to {self.value}")
    
class GermanyApp(App):
    def build(self):
        self.title = "KIVY TEST GUI"
        Factory.register("HoverBehavior", HoverBehavior)
        return SM()

if __name__ == "__main__":
    GermanyApp().run()