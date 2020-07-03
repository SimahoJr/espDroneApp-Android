from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from math import sin
import random
import pyModbusTCP
from pyModbusTCP.client import ModbusClient
from kivy_garden.graph import Graph, MeshLinePlot, SmoothLinePlot
INTERVAL = 0.000001    # in seconds
scanned = False

Builder.load_file("kv_main.kv")
"""
When everything fails remember the Global Variables
"""
our_value = [[], []]
pid_values = []
m = []
pid_parameters = False

class Popups(FloatLayout):
    pass


"""THE ESP WORKS ON TWO MODES
1: STATION; IP = 192.168.43.54 (Remote control, needs port number)
2: ACCESS POINT; IP = 192.168.4.1 (Just a WiFi connection that involves SSID and Password)
"""
ip_, port_, ssid_, password_ = "192.168.4.1", "502", "Crazy Engineer's", "Alita:Battle Angel"
"""
This is unpleasant code (Soon to be BUG)
one way to run away and save time
TODO: This part letter
"""


class SetupScreen(Screen):
    # setupScreen attributes
    ip = StringProperty("192.168.43.243")
    ssid = StringProperty("Crazy Engineer's")
    password = StringProperty("Alita:Battle Angel")
    port = StringProperty("502")
    time_out = NumericProperty(50)

    connection_status = StringProperty()
    modbus_object = ObjectProperty()

    def __init__(self, **kwargs):
        super(SetupScreen, self).__init__(**kwargs)
        #  Connection initialization

    def update_values(self):
        global ip_, port_, ssid_, password_

        ip_ = str(self.ids.ip.text)
        port_ = str(self.ids.port.text)
        ssid_ = str(self.ids.ssid.text)
        password_ = str(self.ids.password.text)
        if port_ == "":
            port_ = 0

        # if self.ip == "0":
        #     # show_popup()
        # else:
        #     print(self.port)
    # connectionScreen methods

    def check_connection(self, *args):
        global c
        c = ModbusClient(host=ip_, port=int(port_), timeout=1, auto_open=True)

        """There is the bug here, as if it is false (c.is_open() = False)
        it doesnt show an update on the GUI

        debug: The c object above is constant"""

        if not c.is_open():
            if not c.open():
                self.connection_status = "Disconnected"
                # print("Unable to connect to " + ip_ + ":" + str(port_))
            else:
                self.connection_status = "Connected"

        return self.connection_status

    def custom_values(self):
        c.host("192.168.43.243")
        c.port(502)

# setupScreen methods

class DebugScreen(Screen):
    roll_Ki = NumericProperty()
    roll_Kp = NumericProperty()
    roll_Kd = NumericProperty()

    yaw_Ki = NumericProperty()
    yaw_Kp = NumericProperty()
    yaw_Kd = NumericProperty()

    pitch_Ki = NumericProperty()
    pitch_Kp = NumericProperty()
    pitch_Kd = NumericProperty()

    pressed = StringProperty("Continua")
    pressed_up = NumericProperty()
    pressed_down = NumericProperty()

    x_max0 = NumericProperty(100)
    x_max1 = NumericProperty(100)
    x_max2 = NumericProperty(100)
    x_max3 = NumericProperty(100)

    x_min0 = NumericProperty(0)
    x_min1 = NumericProperty(0)
    x_min2 = NumericProperty(0)
    x_min3 = NumericProperty(0)

    zoom_index = NumericProperty()
    size_snap = ListProperty()
    size_of_snap = StringProperty()

    reg = ListProperty()

    # connectionScreen attributes

    def __init__(self, **kwargs):
        super(DebugScreen, self).__init__(**kwargs)
        self.reg = MainScreen().read_registers()
        Clock.schedule_interval(self.motors_plot, INTERVAL)     # one millisecond

        self.counter = 0
        self.motor0_id_from = None
        self.motor0_id_to = None
        self.motor1_id_from = None
        self.motor1_id_to = None
        self.motor2_id_from = None
        self.motor2_id_to = None
        self.motor3_id_from = None
        self.motor3_id_to = None

        self.pop_counter = 0
        self.recv_reg = []
        self.dazzle = 0
        self.n = 1
        self.p = 1

    def update_check(self):
        pass

    def clear_issues(self):
        self.recv_reg.clear()
        self.x_min0 = 0
        self.x_max0 = 2000

    def slider_value(self):
        """
        This updates the PID parameters, we need this to be interactive
        :return:
        The graph should start from 0 when this is pressed
        """

        a = self.dazzle % 100

        print("reminder is ", a)
        self.x_max0 = self.x_max0 + a
        self.x_min0 = self.x_min0 + a
        self.x_max1 = self.x_max1 + a
        self.x_min1 = self.x_min1 + a
        self.x_max2 = self.x_max2 + a
        self.x_min2 = self.x_min2 + a
        self.x_max3 = self.x_max3 + a
        self.x_min3 = self.x_min3 + a
        self.dazzle = 0

        self.yaw_Ki = round(self.ids.yaw_slider_Ki.value, 3)
        self.yaw_Kp = round(self.ids.yaw_slider_Kp.value, 3)
        self.yaw_Kd = round(self.ids.yaw_slider_Kd.value, 3)

        self.pitch_Ki = round(self.ids.pitch_slider_Ki.value, 3)
        self.pitch_Kp = round(self.ids.pitch_slider_Kp.value, 3)
        self.pitch_Kd = round(self.ids.pitch_slider_Kd.value, 3)

        self.roll_Ki = round(self.ids.roll_slider_Ki.value, 3)
        self.roll_Kp = round(self.ids.roll_slider_Kp.value, 3)
        self.roll_Kd = round(self.ids.roll_slider_Kd.value, 3)

        # self.dazzle = self.dazzle + a
        # if self.dazzle == 3:
        #     self.dazzle = 2
        # print(round(float(self.ids.yaw_slider_Ki.value), 2))

        return [[self.yaw_Ki, self.yaw_Kp, self.yaw_Kd], [self.pitch_Ki, self.pitch_Kp, self.pitch_Kd], [
                self.roll_Ki, self.roll_Kp, self.roll_Kd]]

    def snaps(self, *args):
        pass

    def motor_id_clear(self):
        self.ids.motor0_from.text = ""
        self.ids.motor0_to.text = ""
        self.ids.motor1_from.text = ""
        self.ids.motor1_to.text = ""
        self.ids.motor2_from.text = ""
        self.ids.motor2_to.text = ""
        self.ids.motor3_from.text = ""
        self.ids.motor3_to.text = ""

    def motor_id_submit(self):
        if self.ids.motor0_from.text == "":
            self.ids.motor0_from.text = "0"
        if self.ids.motor0_to.text == "":
            self.ids.motor0_to.text = "0"

        if self.ids.motor1_from.text == "":
            self.ids.motor1_from.text = "0"
        if self.ids.motor1_to.text == "":
            self.ids.motor1_to.text = "0"

        if self.ids.motor2_from.text == "":
            self.ids.motor2_from.text = "0"
        if self.ids.motor2_to.text == "":
            self.ids.motor2_to.text = "0"

        if self.ids.motor3_from.text == "":
            self.ids.motor3_from.text = "0"
        if self.ids.motor3_to.text == "":
            self.ids.motor3_to.text = "0"

        self.motor0_id_from = int(self.ids.motor0_from.text)
        self.motor0_id_to = int(self.ids.motor0_to.text)

        self.motor1_id_from = int(self.ids.motor1_from.text)
        self.motor1_id_to = int(self.ids.motor1_to.text)

        self.motor2_id_from = int(self.ids.motor2_from.text)
        self.motor2_id_to = int(self.ids.motor2_to.text)

        self.motor3_id_from = int(self.ids.motor3_from.text)
        self.motor3_id_to = int(self.ids.motor3_to.text)

        if self.motor0_id_to == 0:
            self.motor0_id_to = None
        if self.motor1_id_to == 0:
            self.motor1_id_to = None
        if self.motor2_id_to == 0:
            self.motor2_id_to = None
        if self.motor3_id_to == 0:
            self.motor3_id_to = None

        return [[self.motor0_id_from, self.motor0_id_to], [self.motor1_id_from, self.motor1_id_to],
                [self.motor2_id_from, self.motor2_id_to], [self.motor3_id_from, self.motor3_id_to]]

    def motors_plot(self, *args):
        """
        The method takes the variable from Mainscreen class
        that returns: return [self.m, self.snap_shot]
        reg = MainScreen().show_snapshot()[0]
        which must be initialized in the init
        :param args: None
        :return: None
        """

        # Graph Constants
        motor_0 = self.ids.motor0_graph
        motor_1 = self.ids.motor1_graph
        motor_2 = self.ids.motor2_graph
        motor_3 = self.ids.motor3_graph

        # Color Yellow
        plot_set_val_0 = MeshLinePlot(color=[1, 1, 0, 1])
        plot_set_val_1 = MeshLinePlot(color=[1, 1, 0, 1])
        plot_set_val_2 = MeshLinePlot(color=[1, 1, 0, 1])
        plot_set_val_3 = MeshLinePlot(color=[1, 1, 0, 1])

        # Color Blue
        plot_pid_val_0 = MeshLinePlot(color=[0, 0, 1, 1])
        plot_pid_val_1 = MeshLinePlot(color=[0, 0, 1, 1])
        plot_pid_val_2 = MeshLinePlot(color=[0, 0, 1, 1])
        plot_pid_val_3 = MeshLinePlot(color=[0, 0, 1, 1])

        # Color violet
        plot_input_val_0 = MeshLinePlot(color=[0, 1, 1, 1])
        plot_input_val_1 = MeshLinePlot(color=[0, 1, 1, 1])
        plot_input_val_2 = MeshLinePlot(color=[0, 1, 1, 1])
        plot_input_val_3 = MeshLinePlot(color=[0, 1, 1, 1])

        motor_0.add_plot(plot_set_val_0)
        motor_0.add_plot(plot_pid_val_0)
        motor_0.add_plot(plot_input_val_0)

        motor_1.add_plot(plot_set_val_1)
        motor_1.add_plot(plot_pid_val_1)
        motor_1.add_plot(plot_input_val_1)

        motor_2.add_plot(plot_set_val_2)
        motor_2.add_plot(plot_pid_val_2)
        motor_2.add_plot(plot_input_val_2)

        motor_3.add_plot(plot_set_val_3)
        motor_3.add_plot(plot_pid_val_3)
        motor_3.add_plot(plot_input_val_3)

        # Graph Variables
        # the Reg value must be initialized in order to get the right values
        # print(len(self.reg[0]))
        # Sampled only 100 values

        reg_stream = our_value[0]
        # reg_stream = [self.rollSet_list, self.pitchSet_list, self.yawSet_list, self.rollPID_list, self.pitchPID_list,
        #           self.yawPID_list, self.rollInput, self.pitchInput, self.yawInput]
        reg_snap = our_value[1]
        # print(reg_snap)
        set_point = reg_stream[0:3]
        pid_point = reg_stream[3:6]
        output_point = reg_stream[6:9]

        # reg_snap consists of 100 values of snaps each time
        set_point_snap = reg_snap[0:3]
        pid_point_snap = reg_snap[3:6]
        output_point_snap = reg_snap[6:9]
        # print(yaw)

        reg_0 = set_point[0]        # Set_point
        reg_1 = pid_point[0]        # Input
        reg_2 = output_point[0]     # Output

        reg_3 = set_point[1]        # Set_point
        reg_4 = pid_point[1]        # Input
        reg_5 = output_point[1]     # Output
        # print("Hwll  ", reg_4)

        reg_6 = set_point[2]        # Set_point
        reg_7 = pid_point[2]        # Input
        reg_8 = output_point[2]     # Output

#   TODO The speed gets smaller as values increases, should i pop some out? delete?
        #    do i need the data?

        if self.pressed == "Continua":
            print("x min is ", self.x_min0)

            # print(self.pop_counter)

            # self.x_min0 = self.x_min0 + 1
            # self.x_max0 = len(reg_0) + self.x_min0 + 1

            # self.x_max0 = len(reg_0)
            # self.x_max1 = len(reg_1)
            # self.x_max2 = len(reg_2)
            # self.x_max3 = len(reg_3)
            # if self.x_max0 % 100 == 0:
            #     self.n = self.n + 1
            d = self.x_max0 - self.x_min0

            if self.x_max0 <= self.dazzle:
                a = self.dazzle // d * d

                # self.x_max0 = self.x_max0 + a + 1
                self.x_min0 = a
                self.x_max0 = d + a
                self.x_min1 = a
                self.x_max1 = d + a
                self.x_min2 = a
                self.x_max2 = d + a
                self.x_min3 = a
                self.x_max3 = d + a

                # self.dazzle = 2 * self.x_max0

            self.dazzle = self.dazzle + 1
            if self.dazzle == 100:
                self.dazzle = self.x_max0

            # if (self.dazzle - self.x_min0) < 5:
            #     self.x_min0 = self.dazzle

            print("the dazzle value is ", self.dazzle)
            print("x max is ", self.x_max0)

            # for i in range(0, len(self.recv_reg)):
            #     if len(self.recv_reg[i]) % 100 == 0:
            #         reg_100.append(self.recv_reg[i][-100:-1])
            #
            # if self.zoom_index != 0:
            #     if len(reg_100) % 3 == 0:
            #         reg_0 = reg_100[0 + 3 * self.zoom_index]
            #         reg_1 = reg_100[1 + 3 * self.zoom_index]
            #         reg_2 = reg_100[2 + 3 * self.zoom_index]
            #
            #         print(reg_0)

        else:
            if self.pressed == "Continua":
                self.pressed = "0"

                """ALERT ALERT ALERT
                        bug here
            Press Slowly as you Can, We(reg_snap) are gathering data
            and we can not predict the future yet
            
                I SMELL A BIG BUG, AND I'M LEAVING IT :)
                
                TODO: Access the axises from here ??
                
                SOLN:
                Binding is the cure: I leave this one as a battle scare 
                                (reminder next time)
                                self.x_max0 = self.x_max0
                                self.x_min0 = self.x_min0
            """
            if len(reg_snap) != 0:
                reg_0_snap = set_point_snap[0]      # Set_point
                reg_1_snap = pid_point_snap[0]      # Input
                reg_2_snap = output_point_snap[0]   # Output

                reg_3_snap = set_point_snap[1]      # Set_point
                reg_4_snap = pid_point_snap[1]      # Input
                reg_5_snap = output_point_snap[1]   # Output
                # print("Hwll  ", reg_4)

                reg_6_snap = set_point_snap[2]      # Set_point
                reg_7_snap = pid_point_snap[2]      # Input
                reg_8_snap = output_point_snap[2]   # Output

                recv_reg = reg_snap[int(self.pressed)]
                a = int(self.pressed)
                if a > 2:
                    a = 2
                print(reg_0_snap)

                reg_0 = reg_0_snap[0 + 3 * a][self.motor0_id_from:self.motor0_id_to]
                reg_1 = reg_1_snap[0 + 3 * a][self.motor1_id_from:self.motor1_id_to]
                reg_2 = reg_2_snap[0 + 3 * a][self.motor2_id_from:self.motor2_id_to]

                reg_3 = reg_3_snap[1 + 3 * a][self.motor0_id_from:self.motor0_id_to]
                reg_4 = reg_4_snap[1 + 3 * a][self.motor1_id_from:self.motor1_id_to]
                reg_5 = reg_5_snap[1 + 3 * a][self.motor2_id_from:self.motor2_id_to]

                reg_6 = reg_6_snap[2 + 3 * a][self.motor0_id_from:self.motor0_id_to]
                reg_7 = reg_7_snap[2 + 3 * a][self.motor1_id_from:self.motor1_id_to]
                reg_8 = reg_8_snap[2 + 3 * a][self.motor2_id_from:self.motor2_id_to]

                self.x_max0 = len(reg_0)
                self.x_min0 = 0
                self.x_max1 = len(reg_3)
                self.x_min1 = 0
                self.x_max2 = len(reg_6)
                self.x_min2 = 0
                self.x_max3 = len(reg_6)
                self.x_min3 = 0

                self.size_snap = [len(reg_0), len(reg_1), len(reg_2), len(reg_3), len(reg_4), len(reg_5), len(reg_6),
                                  len(reg_7), len(reg_8)]

                print("Got here")

        #         print("reached here")
        #
        # print(self.pressed)

        # self.x_min0 = self.x_min0 + 1
        # self.x_max0 = len(reg_0) + self.x_min0 + 1

        # if self.counter >= 10:
        #     self.x_max0 = self.x_max0 + 1
        #     self.x_min0 = self.x_min0 + 1
        #
        #     self.x_max1 = self.x_max2 + 1
        #     self.x_min1 = self.x_min1 + 1
        #
        #     self.x_max2 = self.x_max2 + 1
        #     self.x_min2 = self.x_min2 + 1
        #
        #     self.x_max3 = self.x_max3 + 1
        #     self.x_min3 = self.x_min3 + 1
        #
        # self.counter = self.counter + 1
        # print(self.counter)

        plot_set_val_0.points = [(x, int(reg_0[x])) for x in range(0, len(reg_0))]
        plot_pid_val_0.points = [(x, int(reg_1[x])) for x in range(0, len(reg_1))]
        plot_input_val_0.points = [(x, int(reg_2[x])) for x in range(0, len(reg_2))]

        # if len(recv_reg[1]) > 100:
        #     recv_reg[1].clear()
        # self.x_max1 = len(recv_reg[1])
        plot_set_val_1.points = [(x, int(reg_3[x])) for x in range(0, len(reg_3))]
        plot_pid_val_1.points = [(x, int(reg_4[x])) for x in range(0, len(reg_4))]
        plot_input_val_1.points = [(x, int(reg_5[x])) for x in range(0, len(reg_5))]

        # if len(recv_reg[2]) > 100:
        #     recv_reg[2].clear()
        # self.x_max2 = len(recv_reg[2])
        plot_set_val_2.points = [(x, int(reg_6[x])) for x in range(0, len(reg_6))]
        plot_pid_val_2.points = [(x, int(reg_7[x])) for x in range(0, len(reg_7))]
        plot_input_val_2.points = [(x, int(reg_8[x])) for x in range(0, len(reg_8))]
        #
        # if len(recv_reg[3]) > 100:
        #     recv_reg[3].clear()
        # self.x_max3 = len(recv_reg[3])
        plot_set_val_3.points = [(x, x) for x in range(0, len(reg_3))]
        plot_pid_val_3.points = [(x, x * x) for x in range(0, len(reg_3))]
        plot_pid_val_3.points = [(x, 10 * x) for x in range(0, len(reg_3))]

        # send PID values
        global pid_values
        pid_values = [self.yaw_Ki, self.yaw_Kd, self.yaw_Kp, self.pitch_Ki, self.pitch_Kd, self.pitch_Kp,
                      self.roll_Ki, self.roll_Kd, self.roll_Kp]

    def pressed_forward(self):
        if self.pressed == "Continua":
            self.pressed = "0"
        self.pressed = str(int(self.pressed) + 1)
        self.size_of_snap = str(self.pressed)

        # Only 100 snap shots available
        # Any changes has to go also to the main screen

        # if int(self.pressed) > 100:
        #     self.pressed = "100"

        if self.pressed == "0":
            self.pressed = "Continua"

    def pressed_back(self):
        if self.pressed == "Continua":
            self.pressed = "0"
        self.pressed = str(int(self.pressed) - 1)
        if int(self.pressed) < 0:
            self.size_of_snap = str(self.pressed)
            self.pressed = "Continua"

    def pressed_continue(self):
        self.pressed = "Continua"
        self.zoom_index = 0
        self.size_of_snap = str(self.pressed)

    def zoom_submit(self):
        self.zoom_index = self.zoom_index + 1

    def zoom_clear(self):
        self.zoom_index = self.zoom_index - 1
        if self.zoom_index < 0:
            self.zoom_index = 0

    def pid_values_to_send(self):
        global pid_values

        return [self.yaw_Ki, self.yaw_Kd, self.yaw_Kp, self.pitch_Ki, self.pitch_Kd, self.pitch_Kp,
                self.roll_Ki, self.roll_Kd, self.roll_Kp]


class MainScreen(Screen):
    # mainScreen attributes
    back = StringProperty("0")
    left = StringProperty("0")
    right_ = StringProperty("0")
    forward = StringProperty("0")
    on_off = StringProperty("False")
    throttle = NumericProperty(0)
    value = NumericProperty(0.0)
    connection_variable = StringProperty("Waiting...")
    sum_ = NumericProperty(0)
    sum1_ = NumericProperty(0)
    rollSet = StringProperty("0")
    pitchSet = StringProperty("0")
    yawSet = StringProperty("0")
    rollPID = StringProperty("0")
    pitchPID = StringProperty("0")
    yawPID = StringProperty("0")
    rollInput = StringProperty("0")
    pitchInput = StringProperty("0")
    yawInput = StringProperty("0")

    Speed_1 = StringProperty()
    Altitude_1 = StringProperty()
    Angle_1 = StringProperty()
    Angle_2 = StringProperty()
    Angle_0 = StringProperty()
    Motor_0 = StringProperty()
    Motor_1 = StringProperty()
    Motor_2 = StringProperty()
    Motor_3 = StringProperty()

    # the sample size corresponds to the x-max value of the plot
    sample_size = NumericProperty(100)
    snap_no = NumericProperty(100)

    # For debug
    auto_ = StringProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        #  Main initialization
        Clock.schedule_interval(self.read_registers, INTERVAL)
        Clock.schedule_interval(self.write_registers, INTERVAL)

        self.slider_ = 0
        self.on_off_ = 0
        self.left_or_right = 0
        self.forward_or_back = 0

        self.rollSet_list = []
        self.pitchSet_list = []
        self.yawSet_list = []

        self.rollPID_list = []
        self.pitchPID_list = []
        self.yawPID_list = []

        self.rollInput_list = []
        self.pitchInput_list = []
        self.yawInput_list = []

        self.snap_shot = []
        self.snap = []
        self.snap_send = []
        # the sample counter must begin at zero that way wen it increments
        #  it checks for the sample size
        self.counter = 100

    # mainScreen methods
    def read_registers(self, *args):
        """The speed from Arduino has to be full speed"""
        self.connection_variable = SetupScreen().check_connection()

        reg = []
        size = 100
        # Reg is the 32 bit register read from the ESP
        # the 16 bits are divided to get 6 signals from the ESP
        #  4*6bit + 2*4bit, RPM=6bit, Angle&Speed 4bit
        # if open() is ok, read register (modbus function 0x03)
        if self.connection_variable == "Connected":
            global m
                # read 6 registers from the address 101-106, registers of 16 bit each

            # mb.Hreg(108, yawInput);
            # mb.Hreg(107, pitchInput);
            # mb.Hreg(106, rollInput);
            # mb.Hreg(105, pid_yaw);
            # mb.Hreg(104, pid_pitch);
            # mb.Hreg(103, pid_roll);
            # mb.Hreg(102, yawSetpoint);
            # mb.Hreg(101, pitchSetpoint);
            # mb.Hreg(100, rollSetpoint);

            reg.append(str(c.read_holding_registers(100, 1)))
            reg.append(str(c.read_holding_registers(101, 1)))
            reg.append(str(c.read_holding_registers(102, 1)))
            reg.append(str(c.read_holding_registers(103, 1)))
            reg.append(str(c.read_holding_registers(104, 1)))
            reg.append(str(c.read_holding_registers(105, 1)))
            reg.append(str(c.read_holding_registers(106, 1)))
            reg.append(str(c.read_holding_registers(107, 1)))
            reg.append(str(c.read_holding_registers(108, 1)))
            # reg.append(str(c.read_holding_registers(109, 1)))

            # if success display registers
            if reg:
                a = []
                a.clear()

                for i in range(0, len(reg)):
                    # """
                    # LIMIT MEMORY
                    # """
                    # if len(reg[i]) <= 500:
                    if reg[i] == "None":
                        reg[i] = "0"

                    if reg[i] == "":
                        reg[i] = "0"

                    a.append(int(reg[i].strip("[,],',")))

                for i in range(0, len(a)):
                    if a[i] >= 9900:
                        a[i] = 9900 - a[i]

                # Print to the MainScreen
                self.rollSet = str(a[0]) + " RPM"
                self.pitchSet = str(a[1]) + " RPM"
                self.yawSet = str(a[2]) + " RPM"
                self.rollPID = str(a[3]) + " RPM"
                self.pitchPID = str(a[4]) + " Degrees"
                self.yawPID = str(a[5]) + " Degrees"
                self.rollInput = str(a[6]) + " Degrees"
                self.pitchInput = str(a[7]) + " m"
                self.yawInput = str(a[8]) + " m/s"

                # Sometimes it might read faster than the
                # operation on the Arduino

                # Bug fix here???
                for i in range(0, len(a)):
                    if (a[i] >= 9855) and (a[i] < 9900):
                        a[i] = -9900 + a[i]

                self.rollSet_list.append(int(a[0]))
                self.pitchSet_list.append(int(a[1]))
                self.yawSet_list.append(int(a[2]))

                self.rollPID_list.append(int(a[3]))
                self.pitchPID_list.append(int(a[4]))
                self.yawPID_list.append(int(a[5]))

                self.rollInput_list.append(int(a[6]))
                self.pitchInput_list.append(int(a[7]))
                self.yawInput_list.append(int(a[8]))

                # # Keep the lists on 100 length to create realtime graph
                # if len(self.rollPID_list) > size:
                #     self.rollPID_list.pop(0)
                # if len(self.pitchPID_list) > size:
                #     self.pitchPID_list.pop(0)
                # if len(self.yawPID_list) > size:
                #     self.yawPID_list.pop(0)
                #
                # if len(self.rollInput_list) > size:
                #     self.rollInput_list.pop(0)
                # if len(self.pitchInput_list) > size:
                #     self.pitchInput_list.pop(0)
                # if len(self.yawInput_list) > size:
                #     self.yawInput_list.pop(0)

                # print("Read reg: {0}".format(a))
                a.clear()

        if self.connection_variable == "Disconnected":
            # if len(self.rollSet_list) < size:
            self.rollSet_list.append(0)
            self.pitchSet_list.append(0)
            self.yawSet_list.append(0)

            self.rollPID_list.append(0)
            self.pitchPID_list.append(0)
            self.yawPID_list.append(0)

            self.rollInput_list.append(0)
            self.pitchInput_list.append(0)
            self.yawInput_list.append(0)

        # this is a bug, possibly the solution is too simple
        # when the code breaks, come back here
        # if self.m == []:
        #     self.m = [[0]]

        # Taking snapshots of the codes per sample sizes
        # MUST be done before pop()
        m = [self.rollSet_list, self.pitchSet_list, self.yawSet_list, self.rollPID_list, self.pitchPID_list,
             self.yawPID_list, self.rollInput_list, self.pitchInput_list, self.yawInput_list]

        # if there is anything in the sample_snip then add to the snapshot
        global pid_parameters
        print(pid_parameters)
        if pid_parameters is True:
            self.rollSet_list.clear()
            self.pitchSet_list.clear()
            self.yawSet_list.clear()
            self.rollPID_list.clear()
            self.pitchPID_list.clear()
            self.yawPID_list.clear()
            self.rollInput_list.clear()
            self.pitchInput_list.clear()
            self.yawInput_list.clear()
            pid_parameters = False

        """
        I SMELL A BUG HERE
        """
        #   Again: Assuming all all nothing approach
        # for i in range(0, len(sample_snip)):
        # Check how many snapshots are set
        # Remember the length snapshot is always equal to self.snap_no +1
        # The self.snap_no begins from 1 while self.snapshot begins from 0

        #  Check for if empty on sample snip first

        # Check if it is within the number of snips to be recorded

        # len() starts with 1 but list starts at 0
        # We slice the list and append equal to the sample size
        # every time and save a snapshot

        # for i in range(0, len(self.m)):
        # print("This is the length of {} , {} " .format(i, str(len(self.m[i]))))
        # print(self.snap_shot[0][0])
        # print(len(self.snap_shot))
        # print(self.m)

        # slicing a list
        for i in range(0, len(m)):
            if len(m[i]) % self.sample_size == 0:
                self.snap = m[i][-self.sample_size-1:-1]
                self.snap_shot.append(self.snap)
        #         need to clear
        self.snap_send.append(self.snap_shot)

        # print(self.snap_shot)
        global our_value
        our_value = [m, self.snap_send]

        return [m, self.snap_send]

    def show_snapshot(self):
        # print(self.snap_shot)
        return self.snap_shot

    def get_connection_variable(self):
        self.connection_variable = str(c.is_open())
        # print(self.connection_variable)
        return self.connection_variable

    def right_on_press(self):
        self.right_ = str(1)

    def right_on_release(self):
        self.right_ = str(0)

    def left_on_press(self):
        self.left = str(1)

    def left_on_release(self):
        self.left = str(0)

    def back_on_press(self):
        self.back = str(1)

    def back_on_release(self):
        self.back = str(0)

    def forward_on_press(self):
        self.forward = str(1)

    def forward_on_release(self):
        self.forward = str(0)

    def movement_right_or_left(self):
        """THis is the maximum angle that can be sent
        If the sent angle starts with 99, then it is a negative angle
        in order to find the right angle
        x= 9900-x"""
        a = 45
        # print("Left " + self.left)
        # print("Right " + self.right)
        # print("Forward " + self.forward)
        # print("Back " + self.back)

        if self.right_ == "1":
            # 1 to remove the negative and be aware
            self.sum_ = self.sum_ + 1
            if self.sum_ >= a:
                self.sum_ = a
            # print(self.sum_)
        elif self.left == "1":

            self.sum_ = self.sum_ - 1
            if self.sum_ <= -a:
                self.sum_ = -a
            # print(self.sum_)
        else:
            self.sum_ = 0
            # print(self.sum_)

        # 100 to remove the negative and be aware
        if self.sum_ < 0:
            self.left_or_right = int("99" + str(-1*self.sum_))
        else:
            self.left_or_right = self.sum_

        return self.left_or_right

    def movement_forward_or_back(self):
        """the bug is: It minus 2 at first number
        and it doesnt go to zero"""

        a = 45
        #  For back and forward, copied above
        if self.forward == "1":
            # 1 to remove the negative and be aware
            self.sum1_ = self.sum1_ + 1
            if self.sum1_ >= a:
                self.sum1_ = a
            # print(self.sum_)
        elif self.back == "1":
            self.sum1_ = self.sum1_ - 1
            if self.sum1_ <= -a:
                self.sum1_ = -a
            # print(self.sum_)
        else:
            self.sum1_ = 0
            # print(self.sum_)

        # 100 to remove the negative and be aware
        if self.sum1_ < 0:
            self.forward_or_back = int("99" + str(-1*self.sum1_))
        else:
            self.forward_or_back = self.sum1_

        return self.forward_or_back

    def on_off_parameter(self):
        if self.on_off == "True":
                self.on_off = "False"
        else:
            self.on_off = "True"
        # print(self.on_off)
        self.on_off_ = 1 if self.on_off == "True" else 0
        return self.on_off_

    def slider_value(self, *args):
        slider_value = 0
        for arg in args:
            slider_value = arg

        self.throttle = float(str(slider_value)[:5])
        self.slider_ = self.throttle
        return self.slider_

    def get_slider_value(self):

        # print(self.value)
        return self.value

    def control_parameters(self):
        # These are parameters sent out from the MainScreen window
        print([self.back, self.forward, self.left, self.right_, self.on_off, float(self.throttle), self.left])
        return [int(self.back), int(self.forward), int(self.left), int(self.right_), bool(self.on_off),
                float(self.throttle)]

    def get_control_parameters(self):

        return [self.back_parameter(), self.forward_parameter(), self.left_parameter(),
                self.right_parameter(), self.on_off_parameter(), self.throttle]

    def write_registers(self, *args):
        """
        forward_or_back/left_or_right:
        The values 1---->9 are positive while 11----->19 and 0 is Neutral
        slider_: is an float/int? variable of values 0 -----> 255
        on_off_: contains integer 1 ----> ON and 0----> OFF
        :param dt:
        :return: None
        """

        # From DEBUG SCREEN
        # def pid_values_to_send(self):
        #     return [[self.yaw_Ki, self.yaw_Kd, self.yaw_Kp], [self.pitch_Ki, self.pitch_Kd, self.pitch_Kp],
        #             [self.pitch_Ki, self.pitch_Kd, self.pitch_Kp]]

        # The PID values are float which presents the problems with the
        # Arduino Modbus Library

        sent_list = []
        for i in range(0, len(pid_values)):
            if len(pid_values) == 0:
                # pid_values[i] = [0, 0, 0]
                # luckly the values are limited to only two/or three digits????
                # If the length is not zero then
                sent_list = [0]
            else:
                # for j in range(0, len(pid_values)):
                #     # Too big for 16 bit?? NO
                #     # Correct the ranges of PID's say 0--->10!
                #     for k in range(0, len(pid_values[j])):
                #         # pid_values[j][k] = pid_values[j][k]
                #     # The PID has 9 values

                sent_list = [int(pid_values[i] * 100) for i in range(0, len(pid_values))]
                sent_list.extend([self.left_or_right, self.forward_or_back, int(self.throttle), self.on_off_])
                # print(sent_list)
                # print("Throttle", sent_list)

        # if self.connection_variable == "Connected":
        #     #  write 1 (16bit) register at address 100
        #     # if c.write_multiple_registers(200, sent_list):
        #     #     print("write ok")
        #     for m in range(0, len(sent_list)):
        #         if c.write_single_register(110+m, sent_list[m]):
        #             print("write ok")
        #         else:
        #             print("write error")


"""The Main Function Starts Here

# Check Connection to ESP
#     Global variable to send toGUI
#   If connected
#       Send control values to ESP
#       Receive status values from ESP
#       Global variable to send toGUI
#   If not Connected
#       Global variable to send toGUI
# Repeat

"""
# TCP auto connect on first modbus request
#  TCP always OPEN
# con_par = return [self.ids.ip.text, self.ids.port.text, self.ids.ssid.text, self.ids.password.text]


def callback(instance, value):
    print('My callback is call from', instance)
    print('and the a value changed to', value)


screen_manager = ScreenManager()

# Add the screens to the manager and then supply a name
# that is used to switch screens
screen_manager.add_widget(MainScreen(name="main"))
screen_manager.add_widget(SetupScreen(name="setup"))
screen_manager.add_widget(DebugScreen(name="debug"))


# The read bit are simple string_integers
def bit_to_str_decimal(_reg):
    num_dec = int(_reg, 2)
    # print(num_dec)
    return str(num_dec)

"""
righ_left_reg: Right Left Register
0 ----> No Right Left Movement
right_left_reg:value-----> Degree of left_ness or right_ness
"""

class DroneApp(App):
    def __init__(self):
        super(DroneApp, self).__init__()

    def build(self):
        return screen_manager


def show_popup():
    show = Popups()

    popupWindow = Popup(title="Popup Window", content=show,
                        size_hint=(None, None), size=(200, 200))

    # open popup window
    popupWindow.open()

    # Attach close button press with popup.dismiss action
    # content.bind(on_press = popup.dismiss)


if __name__ == "__main__":
    DroneApp().run()
