# BrachioGraph bundle for MicroPython

### CONFIG ###

# The path to the file on the MicroPython device.
FILENAME = "drawing.json"

# Servo ports
SERVO1 = 28 # The servo that sits on the ground.
SERVO2 = 27 # The servo in the center.
SERVO3 = 26 # The servo used to push up and down the pen.

### END CONFIG ###

### CODE
from time import sleep,ticks_ms
try:import machine
except ImportError:print('ERROR: This device does not have MicroPython.');exit(1)
class Servo:
	def __init__(self):0
	def get(self)->int:raise NotImplementedError()
	def goto(self,pos:int):raise NotImplementedError()
	def goto_float(self,pos:float):self.goto(round(pos))
	def move(self,start:int,end:int):
		diff=end-start;angle=start;length_of_step=diff/abs(diff)
		for _ in range(abs(diff)):angle+=length_of_step;self.goto_float(angle);sleep(.001)
class PicoServo(Servo):
	def __init__(self,port:int):self.pwm=machine.PWM(machine.Pin(port));self.pwm.freq(50);machine.time_pulse_us(port,0)
	def get(self)->int:return self.pwm.duty_u16()
	def goto(self,pos:int):self.pwm.duty_u16(pos)
import json,math
try:from ulab import numpy
except ImportError:
	try:import numpy
	except ImportError:print('ERROR: ulab micropython is not installed.');exit(1)
def monotonic():return ticks_ms()/1000
class Plotter:
	has_turtle:bool;angle_2:float|None;angle_1:float|None
	def __init__(self,servo_1:Servo,servo_2:Servo,servo_3:Servo,virtual:bool=False,turtle:bool=False,turtle_coarseness=None,bounds:tuple=(-10,5,10,15),servo_1_parked_pw:int=1500,servo_2_parked_pw:int=1500,servo_1_degree_ms:float=-10,servo_2_degree_ms:float=10,servo_1_parked_angle:float=0,servo_2_parked_angle:float=0,hysteresis_correction_1:float=0,hysteresis_correction_2:float=0,servo_1_angle_pws:list=[],servo_2_angle_pws:list=[],servo_1_angle_pws_bidi:dict={},servo_2_angle_pws_bidi:dict={},pw_up:int|None=None,pw_down:int|None=None,angular_step:float|None=None,wait:float|None=None,resolution:float|None=None):
		self.servo_1=servo_1;self.servo_2=servo_2;self.servo_3=servo_3;self.last_moved=monotonic();self.virtual=virtual;self.angle_1=servo_1_parked_angle;self.angle_2=servo_2_parked_angle
		if turtle:
			try:from turtle import Turtle,Screen;self.setup_turtle(turtle_coarseness);self.turtle.showturtle();self.has_turtle=True
			except ModuleNotFoundError:self.has_turtle=False;print('Turtle mode unavailable')
		else:self.has_turtle=False
		self.bounds=bounds;self.servo_1_parked_pw=servo_1_parked_pw;self.servo_1_degree_ms=servo_1_degree_ms;self.servo_1_parked_angle=servo_1_parked_angle;self.hysteresis_correction_1=hysteresis_correction_1
		if servo_1_angle_pws_bidi:
			servo_1_angle_pws=[];differences=[]
			for(angle,pws)in servo_1_angle_pws_bidi.items():pw=(pws['acw']+pws['cw'])/2;servo_1_angle_pws.append([angle,pw]);differences.append((pws['acw']-pws['cw'])/2)
			self.hysteresis_correction_1=numpy.mean(differences)
		if servo_1_angle_pws:servo_1_array=numpy.array(servo_1_angle_pws);self.angles_to_pw_1=numpy.poly1d(numpy.polyfit(servo_1_array[:,0],servo_1_array[:,1],3))
		else:self.angles_to_pw_1=self.naive_angles_to_pulse_widths_1
		self.servo_2_parked_pw=servo_2_parked_pw;self.servo_2_degree_ms=servo_2_degree_ms;self.servo_2_parked_angle=servo_2_parked_angle;self.hysteresis_correction_2=hysteresis_correction_2
		if servo_2_angle_pws_bidi:
			servo_2_angle_pws=[];differences=[]
			for(angle,pws)in servo_2_angle_pws_bidi.items():pw=(pws['acw']+pws['cw'])/2;servo_2_angle_pws.append([angle,pw]);differences.append((pws['acw']-pws['cw'])/2)
			self.hysteresis_correction_2=numpy.mean(differences)
		if servo_2_angle_pws:servo_2_array=numpy.array(servo_2_angle_pws);self.angles_to_pw_2=numpy.poly1d(numpy.polyfit(servo_2_array[:,0],servo_2_array[:,1],3))
		else:self.angles_to_pw_2=self.naive_angles_to_pulse_widths_2
		self.previous_pw_1=self.previous_pw_2=0;self.active_hysteresis_correction_1=self.active_hysteresis_correction_2=0;self.reset_report()
		if self.virtual:self.wait=wait or 0;self.virtualise()
		else:
			try:self.virtual=False;self.wait=wait if wait is not None else .01
			except AttributeError:print('pigpio daemon is not available; running in virtual mode');self.virtualise();self.wait=wait if wait is not None else 0
		pw_up=pw_up or 1400;pw_down=pw_down or 1600;self.pen=Pen(servo_3,bg=self,pw_up=pw_up,pw_down=pw_down,virtual=self.virtual);self.angular_step=angular_step or .1;self.resolution=resolution or .1;self.set_angles(self.servo_1_parked_angle,self.servo_2_parked_angle);sleep(1);self.status()
	def virtualise(self):print('Initialising virtual BrachioGraph');self.virtual_pw_1=self.angles_to_pw_1(-90);self.virtual_pw_2=self.angles_to_pw_2(90);self.virtual=True
	def setup_turtle(self,coarseness):
		try:from turtle import BaseTurtle;self.turtle=BaseTurtle(window_size=850,speed=10,machine=self,coarseness=coarseness);self.turtle.draw_grid();self.t=self.turtle
		except:print('turtle plotter unavailable')
	def plot_file(self,filename='',bounds=None,angular_step=None,wait=None,resolution=None):
		bounds=bounds or self.bounds
		with open(filename,'r')as line_file:lines=json.load(line_file)
		self.plot_lines(lines,bounds,angular_step,wait,resolution,flip=True)
	def plot_lines(self,lines=[],bounds=None,angular_step=None,wait=None,resolution=None,flip=False,rotate=False):
		bounds=bounds or self.bounds;lines=self.rotate_and_scale_lines(lines=lines,bounds=bounds,flip=True)
		for line in lines:
			x,y=line[0]
			if(round(self.x,1),round(self.y,1))!=(round(x,1),round(y,1)):self.xy(x,y,angular_step,wait,resolution)
			for point in line[1:]:x,y=point;self.xy(x,y,angular_step,wait,resolution,draw=True)
		self.park()
	def box(self,bounds=None,angular_step=None,wait=None,resolution=None,repeat=1,reverse=False):
		bounds=bounds or self.bounds
		if not bounds:return'Box drawing is only possible when the bounds attribute is set.'
		self.xy(bounds[0],bounds[1],angular_step,wait,resolution)
		for r in range(repeat):
			if not reverse:self.xy(bounds[2],bounds[1],angular_step,wait,resolution,draw=True);self.xy(bounds[2],bounds[3],angular_step,wait,resolution,draw=True);self.xy(bounds[0],bounds[3],angular_step,wait,resolution,draw=True);self.xy(bounds[0],bounds[1],angular_step,wait,resolution,draw=True)
			else:self.xy(bounds[0],bounds[3],angular_step,wait,resolution,draw=True);self.xy(bounds[2],bounds[3],angular_step,wait,resolution,draw=True);self.xy(bounds[2],bounds[1],angular_step,wait,resolution,draw=True);self.xy(bounds[0],bounds[1],angular_step,wait,resolution,draw=True)
		self.park()
	def test_pattern(self,lines=4,bounds=None,angular_step=None,wait=None,resolution=None,repeat=1,reverse=False,both=False):self.vertical_lines(lines,bounds,angular_step,wait,resolution,repeat,reverse,both);self.horizontal_lines(lines,bounds,angular_step,wait,resolution,repeat,reverse,both)
	def vertical_lines(self,lines=4,bounds=None,angular_step=None,wait=None,resolution=None,repeat=1,reverse=False,both=False):
		bounds=bounds or self.bounds
		if not bounds:return'Plotting a test pattern is only possible when the bounds attribute is set.'
		if not reverse:top_y=self.top;bottom_y=self.bottom
		else:bottom_y=self.top;top_y=self.bottom
		for n in range(repeat):
			step=(self.right-self.left)/lines;x=self.left
			while x<=self.right:self.draw_line((x,top_y),(x,bottom_y),angular_step,wait,resolution,both);x=x+step
		self.park()
	def horizontal_lines(self,lines=4,bounds=None,angular_step=None,wait=None,resolution=None,repeat=1,reverse=False,both=False):
		bounds=bounds or self.bounds
		if not bounds:return'Plotting a test pattern is only possible when the bounds attribute is set.'
		if not reverse:min_x=self.left;max_x=self.right
		else:max_x=self.left;min_x=self.right
		for n in range(repeat):
			step=(self.bottom-self.top)/lines;y=self.top
			while y>=self.bottom:self.draw_line((min_x,y),(max_x,y),angular_step,wait,resolution,both);y=y+step
		self.park()
	def draw_line(self,start=(0,0),end=(0,0),angular_step=None,wait=None,resolution=None,both=False):
		start_x,start_y=start;end_x,end_y=end;self.xy(start_x,start_y,angular_step,wait,resolution);self.xy(end_x,end_y,angular_step,wait,resolution,draw=True)
		if both:self.xy(start_x,start_y,angular_step,wait,resolution,draw=True)
	def xy(self,x:None|float=None,y:None|float=None,angular_step=None,wait=None,resolution=None,draw=False):
		wait=wait if wait is not None else self.wait;resolution=resolution or self.resolution;x=x if x is not None else self.x;y=y if y is not None else self.y;angle_1,angle_2=self.xy_to_angles(x,y)
		if draw:
			if x!=None:x_length,y_length=x-self.x,y-self.y
			length=math.sqrt(x_length**2+y_length**2);no_of_steps=round(length/resolution)or 1;length_of_step_x,length_of_step_y=x_length/no_of_steps,y_length/no_of_steps
			for step in range(no_of_steps):self.x=self.x+length_of_step_x;self.y=self.y+length_of_step_y;angle_1,angle_2=self.xy_to_angles(self.x,self.y);self.move_angles(angle_1,angle_2,angular_step,wait,draw)
		else:self.move_angles(angle_1,angle_2,angular_step,wait,draw)
	def move_angles(self,angle_1=None,angle_2=None,angular_step=None,wait=None,draw=False):
		wait=wait if wait is not None else self.wait;angular_step=angular_step or self.angular_step
		if draw:self.pen.down()
		else:self.pen.up()
		diff_1=diff_2=0
		if angle_1 is not None:diff_1=angle_1-self.angle_1
		if angle_2 is not None:diff_2=angle_2-self.angle_2
		no_of_steps=int(max(map(abs,(diff_1/angular_step,diff_2/angular_step))))or 1;length_of_step_1,length_of_step_2=diff_1/no_of_steps,diff_2/no_of_steps
		for step in range(no_of_steps):
			if self.angle_1!=None and self.angle_2!=None:self.angle_1=self.angle_1+length_of_step_1;self.angle_2=self.angle_2+length_of_step_2
			time_since_last_moved=monotonic()-self.last_moved
			if time_since_last_moved<wait:sleep(wait-time_since_last_moved)
			self.set_angles(self.angle_1,self.angle_2);self.last_moved=monotonic()
	def set_angles(self,angle_1=None,angle_2=None):
		pw_1=pw_2=None
		if angle_1 is not None:
			pw_1=self.angles_to_pw_1(angle_1)
			if pw_1>self.previous_pw_1:self.active_hysteresis_correction_1=self.hysteresis_correction_1
			elif pw_1<self.previous_pw_1:self.active_hysteresis_correction_1=-self.hysteresis_correction_1
			self.previous_pw_1=pw_1;pw_1=pw_1+self.active_hysteresis_correction_1;self.angle_1=angle_1;self.angles_used_1.add(int(angle_1));self.pulse_widths_used_1.add(int(pw_1))
		if angle_2 is not None:
			pw_2=self.angles_to_pw_2(angle_2)
			if pw_2>self.previous_pw_2:self.active_hysteresis_correction_2=self.hysteresis_correction_2
			elif pw_2<self.previous_pw_2:self.active_hysteresis_correction_2=-self.hysteresis_correction_2
			self.previous_pw_2=pw_2;pw_2=pw_2+self.active_hysteresis_correction_2;self.angle_2=angle_2;self.angles_used_2.add(int(angle_2));self.pulse_widths_used_2.add(int(pw_2))
		self.x,self.y=self.angles_to_xy(self.angle_1,self.angle_2)
		if self.has_turtle:self.turtle.set_angles(self.angle_1,self.angle_2)
		self.set_pulse_widths(pw_1,pw_2)
	def park(self):
		if self.virtual:print('Parking')
		self.pen.up();self.move_angles(self.servo_1_parked_angle,self.servo_2_parked_angle)
	def naive_angles_to_pulse_widths_1(self,angle):return(angle-self.servo_1_parked_angle)*self.servo_1_degree_ms+self.servo_1_parked_pw
	def naive_angles_to_pulse_widths_2(self,angle):return(angle-self.servo_2_parked_angle)*self.servo_2_degree_ms+self.servo_2_parked_pw
	def rotate_and_scale_lines(self,lines=[],rotate=False,flip=False,bounds=None):
		rotate,x_mid_point,y_mid_point,box_x_mid_point,box_y_mid_point,divider=self.analyse_lines(lines,rotate,bounds)
		for line in lines:
			for point in line:
				if rotate:point[0],point[1]=point[1],point[0]
				x=point[0];x=x-x_mid_point;x=x/divider
				if flip^rotate:x=-x
				x=x+box_x_mid_point;y=point[1];y=y-y_mid_point;y=y/divider;y=y+box_y_mid_point;point[0],point[1]=x,y
		return lines
	def analyse_lines(self,lines=[],rotate=False,bounds=None):
		bounds=bounds or self.bounds;x_values_in_lines=set();y_values_in_lines=set()
		for line in lines:x_values_in_line,y_values_in_line=zip(*line);x_values_in_lines.update(x_values_in_line);y_values_in_lines.update(y_values_in_line)
		min_x,max_x=min(x_values_in_lines),max(x_values_in_lines);min_y,max_y=min(y_values_in_lines),max(y_values_in_lines);x_range,y_range=max_x-min_x,max_y-min_y;box_x_range,box_y_range=bounds[2]-bounds[0],bounds[3]-bounds[1];x_mid_point,y_mid_point=(max_x+min_x)/2,(max_y+min_y)/2;box_x_mid_point,box_y_mid_point=(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2
		if x_range>=y_range and box_x_range>=box_y_range or x_range<=y_range and box_x_range<=box_y_range:divider=max(x_range/box_x_range,y_range/box_y_range);rotate=False
		else:divider=max(x_range/box_y_range,y_range/box_x_range);rotate=True;x_mid_point,y_mid_point=y_mid_point,x_mid_point
		return rotate,x_mid_point,y_mid_point,box_x_mid_point,box_y_mid_point,divider
	def set_pulse_widths(self,pw_1=None,pw_2=None):
		if self.virtual:
			if pw_1:
				if 500<pw_1<2500:self.virtual_pw_1=int(pw_1)
				else:raise ValueError
			if pw_2:
				if 500<pw_2<2500:self.virtual_pw_2=int(pw_2)
				else:raise ValueError
		else:
			if pw_1:self.servo_1.goto(pw_1)
			if pw_2:self.servo_2.goto(pw_2)
	def get_pulse_widths(self):
		if self.virtual:actual_pulse_width_1=self.virtual_pw_1;actual_pulse_width_2=self.virtual_pw_2
		else:actual_pulse_width_1=self.servo_1.get();actual_pulse_width_2=self.servo_2.get()
		return actual_pulse_width_1,actual_pulse_width_2
	def quiet(self):
		if self.virtual:print('Going quiet')
		else:
			for servo in[self.servo_1,self.servo_2,self.servo_3]:servo.goto(0)
	def status(self):print('------------------------------------------');print('                      | Servo 1 | Servo 2 ');print('----------------------|---------|---------');pw_1,pw_2=self.get_pulse_widths();print(f"{'pulse-width |':>23}",f"{pw_1:>7.0f}",'|',f"{pw_2:>7.0f}");angle_1,angle_2=self.angle_1,self.angle_2;print(f"{'angle |':>23}",f"{angle_1:>7.0f}",'|',f"{angle_2:>7.0f}");h1,h2=self.hysteresis_correction_1,self.hysteresis_correction_2;print(f"{'hysteresis correction |':>23}",f"{h1:>7.1f}",'|',f"{h2:>7.1f}");print('------------------------------------------');print(f"{'x/y location |':>23}",f"{self.x:>7.1f}",'|',f"{self.y:>7.1f}");print();print('------------------------------------------');print('pen:',self.pen.position);print('------------------------------------------');print(f"left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom}");print('------------------------------------------');print(f"wait: {self.wait} seconds");print('------------------------------------------');print(f"resolution: {self.resolution} cm");print('------------------------------------------');print(f"angular step: {self.angular_step}'");print('------------------------------------------')
	@property
	def left(self):return self.bounds[0]
	@property
	def bottom(self):return self.bounds[1]
	@property
	def right(self):return self.bounds[2]
	@property
	def top(self):return self.bounds[3]
	def reset_report(self):self.angle_1=self.angle_2=None;self.angles_used_1=set();self.angles_used_2=set();self.pulse_widths_used_1=set();self.pulse_widths_used_2=set()
	def xy_to_angles(self,x:None|float=0,y:None|float=0):return 0,0
	def angles_to_xy(self,angle_1,angle_2):return 0,0
class Pen:
	def __init__(self,servo:Servo,bg:Plotter,pw_up=1700,pw_down=1300,transition_time=.25,virtual=False):
		self.servo=servo;self.bg=bg;self.pw_up=pw_up;self.pw_down=pw_down;self.transition_time=transition_time;self.position='down';self.virtual=virtual
		if self.virtual:print('Initialising virtual Pen')
		self.up()
	def down(self):
		if self.position=='up':
			if self.virtual:self.virtual_pw=self.pw_down
			else:self.ease_pen(self.pw_up,self.pw_down)
			if self.bg.has_turtle:self.bg.turtle.down();self.bg.turtle.color('blue');self.bg.turtle.width(1)
			self.position='down'
	def up(self):
		if self.position=='down':
			if self.virtual:self.virtual_pw=self.pw_up
			else:self.ease_pen(self.pw_down,self.pw_up)
			if self.bg.has_turtle:self.bg.turtle.up()
			self.position='up'
	def ease_pen(self,start,end):self.servo.move(start,end)
	def pw(self,pulse_width):
		if self.virtual:self.virtual_pw=pulse_width
		else:self.servo.goto(pulse_width)
	def get_pw(self):
		if self.virtual:return self.virtual_pw
		else:return self.servo.get()
import math
class BrachioGraph(Plotter):
	def __init__(self,servo_1:Servo,servo_2:Servo,servo_3:Servo,virtual:bool=False,turtle:bool=False,turtle_coarseness=None,bounds:tuple[int,int,int,int]=(-8,4,6,13),inner_arm:float=8,outer_arm:float=8,servo_1_parked_pw:int=1500,servo_2_parked_pw:int=1500,servo_1_degree_ms:int=-10,servo_2_degree_ms:int=10,servo_1_parked_angle:int=-90,servo_2_parked_angle:int=90,hysteresis_correction_1:int=0,hysteresis_correction_2:int=0,servo_1_angle_pws:list=[],servo_2_angle_pws:list=[],servo_1_angle_pws_bidi:dict={},servo_2_angle_pws_bidi:dict={},pw_up:int=1500,pw_down:int=1100,wait:float|None=None,angular_step:float|None=None,resolution:float|None=None):self.inner_arm=inner_arm;self.outer_arm=outer_arm;self.x=-self.inner_arm;self.y=self.outer_arm;super().__init__(servo_1,servo_2,servo_3,bounds=bounds,servo_1_parked_pw=servo_1_parked_pw,servo_2_parked_pw=servo_2_parked_pw,servo_1_degree_ms=servo_1_degree_ms,servo_2_degree_ms=servo_2_degree_ms,servo_1_parked_angle=servo_1_parked_angle,servo_2_parked_angle=servo_2_parked_angle,hysteresis_correction_1=hysteresis_correction_1,hysteresis_correction_2=hysteresis_correction_2,servo_1_angle_pws=servo_1_angle_pws,servo_2_angle_pws=servo_2_angle_pws,servo_1_angle_pws_bidi=servo_1_angle_pws_bidi,servo_2_angle_pws_bidi=servo_2_angle_pws_bidi,pw_up=pw_up,pw_down=pw_down,wait=wait,angular_step=angular_step,resolution=resolution,virtual=virtual,turtle=turtle,turtle_coarseness=turtle_coarseness)
	def test_arcs(self):
		self.park();elbow_angle=120;self.move_angles(angle_2=elbow_angle)
		for angle_1 in range(-135,15,15):
			self.move_angles(angle_1=angle_1,draw=True)
			for angle_2 in range(elbow_angle,elbow_angle+16):self.move_angles(angle_2=angle_2,draw=True)
			for angle_2 in range(elbow_angle+16,elbow_angle-16,-1):self.move_angles(angle_2=angle_2,draw=True)
			for angle_2 in range(elbow_angle-16,elbow_angle+1):self.move_angles(angle_2=angle_2,draw=True)
	def xy_to_angles(self,x:float=0,y:float=0):
		hypotenuse=math.sqrt(x**2+y**2)
		if hypotenuse>self.inner_arm+self.outer_arm:raise Exception(f"Cannot reach {hypotenuse}; total arm length is {self.inner_arm+self.outer_arm}")
		hypotenuse_angle=math.asin(x/hypotenuse);inner_angle=math.acos((hypotenuse**2+self.inner_arm**2-self.outer_arm**2)/(2*hypotenuse*self.inner_arm));outer_angle=math.acos((self.inner_arm**2+self.outer_arm**2-hypotenuse**2)/(2*self.inner_arm*self.outer_arm));shoulder_motor_angle=hypotenuse_angle-inner_angle;elbow_motor_angle=math.pi-outer_angle;return math.degrees(shoulder_motor_angle),math.degrees(elbow_motor_angle)
	def angles_to_xy(self,shoulder_motor_angle,elbow_motor_angle):elbow_motor_angle=math.radians(elbow_motor_angle);shoulder_motor_angle=math.radians(shoulder_motor_angle);hypotenuse=math.sqrt(self.inner_arm**2+self.outer_arm**2-2*self.inner_arm*self.outer_arm*math.cos(math.pi-elbow_motor_angle));base_angle=math.acos((hypotenuse**2+self.inner_arm**2-self.outer_arm**2)/(2*hypotenuse*self.inner_arm));inner_angle=base_angle+shoulder_motor_angle;x=math.sin(inner_angle)*hypotenuse;y=math.cos(inner_angle)*hypotenuse;return x,y
	def report(self):
		print(f"               -----------------|-----------------");print(f"               Servo 1          |  Servo 2        ");print(f"               -----------------|-----------------");h1,h2=self.hysteresis_correction_1,self.hysteresis_correction_2;print(f"hysteresis                 {h1:>2.1f}  |              {h2:>2.1f}");pw_1,pw_2=self.get_pulse_widths();print(f"pulse-width               {pw_1:<4.0f}  |             {pw_2:<4.0f}");angle_1,angle_2=self.angle_1,self.angle_2
		if angle_1 and angle_2:print(f"      angle               {angle_1:>4.0f}  |             {angle_2:>4.0f}")
		print(f"               -----------------|-----------------");print(f"               min   max   mid  |  min   max   mid");print(f"               -----------------|-----------------")
		if self.angles_used_1 and self.angles_used_2 and self.pulse_widths_used_1 and self.pulse_widths_used_2:min1=min(self.pulse_widths_used_1);max1=max(self.pulse_widths_used_1);mid1=(min1+max1)/2;min2=min(self.pulse_widths_used_2);max2=max(self.pulse_widths_used_2);mid2=(min2+max2)/2;print(f"pulse-widths  {min1:>4.0f}  {max1:>4.0f}  {mid1:>4.0f}  | {min2:>4.0f}  {max2:>4.0f}  {mid2:>4.0f}");min1=min(self.angles_used_1);max1=max(self.angles_used_1);mid1=(min1+max1)/2;min2=min(self.angles_used_2);max2=max(self.angles_used_2);mid2=(min2+max2)/2;print(f"      angles  {min1:>4.0f}  {max1:>4.0f}  {mid1:>4.0f}  | {min2:>4.0f}  {max2:>4.0f}  {mid2:>4.0f}")
		else:print('No data recorded yet. Try calling the BrachioGraph.box() method first.')
servo1=PicoServo(SERVO1)
servo2=PicoServo(SERVO2)
servo3=PicoServo(SERVO3)
bg=BrachioGraph(servo1,servo2,servo3)
bg.plot_file(FILENAME)
# END CODE