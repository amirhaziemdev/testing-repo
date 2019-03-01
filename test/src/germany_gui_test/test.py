from kivy.config import Config
# Config.set('graphics', 'resizable', '0') #0 being off 1 being on as in true/false
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '580')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
import cv2
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button

isRecording = True

class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        Clock.schedule_interval(self.update, 1.0 / fps)
        self.x, self.y, self.x1, self.x2, self.y1, self.y2 = 0,0,0,0,0,0
        self.app = App.get_running_app()
        self.first_pos, self.second_pos = [None,None], [None, None]

    def update(self, dt):
        if isRecording == True:
            ret, frame = self.capture.read()
            if ret:
                # convert it to texture
                frame = cv2.flip(frame, 0)
                frame = cv2.flip(frame, 1)
                w, h = int(self.width), int(self.height)
                buf = cv2.resize(frame, (w,h))
                self.temp = buf
                buf = buf.tostring()
                image_texture = Texture.create(
                    size=(w, h), colorfmt="bgr")
                image_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                # display image from the texture
                self.texture = image_texture
                
                # variables for ROI
                self.x, self.y = self.pos
                self.x1 = self.x + w
                self.y1 = self.y + h
        else:
            pass
            
    def on_touch_down(self, touch):
        self.first_pos = touch.pos
        self.app.root.ids.main_page.console_write(f"First position: x: {self.first_pos[0]}, y: {self.first_pos[1]}")
    
    def on_touch_up(self, touch):
        self.x2, self.y2 = touch.pos
        self.x2 = self.x2
        self.y2 = self.y2
        if self.x2 <= self.x1 and self.y2 <= self.y1 and self.x2 >= self.x and self.y2 >= self.y:
            self.second_pos = touch.pos
            self.app.root.ids.main_page.console_write(f"Second position: x: {self.second_pos[0]}, y: {self.second_pos[1]}")
            
    def cv2_select_roi(self):
        global isRecording
        isRecording = False
        im = cv2.flip(self.temp, 0)
        r = cv2.selectROI("Image", im, False)
        imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        print(r)
        cv2.imshow("Image", imCrop)
        cv2.imwrite("1" + ".jpg", imCrop)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        isRecording = True
            
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
        
    def console_write(self, text):
        global isRecording
        self.ids.console.text += "[ console ]  " + text + "\n"
        
class SettingsPage(Screen):
    def __init__(self, **kwargs):
        super(SettingsPage, self).__init__(**kwargs)
        
class Sidebar(BoxLayout):
    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
        self.app = App.get_running_app()
        
    def change_page(self):
        if self.app.root.ids.main_page.manager.current == "main_page":
            self.app.root.ids.main_page.manager.current = "settings_page"
        else:
            self.app.root.ids.main_page.manager.current = "main_page"
            
        
class GenericButton(Button, HoverBehavior):
    def __init__(self, **kwargs):
        super(GenericButton, self).__init__(**kwargs)
    def on_enter(self):
        self.background_color=(0.5, 0.5, 0.5, 1)
    def on_leave(self):
        self.background_color=(0.3, 0.3, 0.3, 1)

class GoButton(Button, HoverBehavior):
    def __init__(self, **kwargs):
        super(GoButton, self).__init__(**kwargs)
    def on_enter(self):
        self.background_color=(0.5, 1.0, 0.5, 1)
    def on_leave(self):
        self.background_color=(0.3, 1.0, 0.3, 1)
        
class NGButton(Button, HoverBehavior):
    def __init__(self, **kwargs):
        super(NGButton, self).__init__(**kwargs)
    def on_enter(self):
        self.background_color=(1.0, 0.5, 0.5, 1)
    def on_leave(self):
        self.background_color=(1.0, 0.3, 0.3, 1)
    
class TestApp(App):
    def build(self):
        self.title = "KIVY TEST GUI"
        Factory.register("HoverBehavior", HoverBehavior)
        return SM()

if __name__ == "__main__":
    TestApp().run()