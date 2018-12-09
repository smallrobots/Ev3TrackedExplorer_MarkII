#################################################################################################
# ev3te package                                                                                 #
# Version 1.0                                                                                   #
#                                                                                               #
# Happily shared under the MIT License (MIT)                                                    #
#                                                                                               #
# Copyright(c) 2017 SmallRobots.it                                                              #
#                                                                                               #
# Permission is hereby granted, free of charge, to any person obtaining                         #
# a copy of this software and associated documentation files (the "Software"),                  #
# to deal in the Software without restriction, including without limitation the rights          #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies              #
# of the Software, and to permit persons to whom the Software is furnished to do so,            #
# subject to the following conditions:                                                          #
#                                                                                               #
# The above copyright notice and this permission notice shall be included in all                #
# copies or substantial portions of the Software.                                               #
#                                                                                               #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,           #
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR      #
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE            #
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,           #
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE         #
# OR OTHER DEALINGS IN THE SOFTWARE.                                                            #
#                                                                                               #
# Visit http://www.smallrobots.it for tutorials and videos                                      #
#                                                                                               #
# Credits                                                                                       #
# The Ev3TrackedExlpor3r is built with Lego Mindstorms Ev3 and Lego Technic Parts               #
#                                                                                               #
# Note.                                                                                         #
# This version uses Version N.2 of ev3dev, the so called ev3dev2                                #
#################################################################################################

# Example mjpg streamer ativation
# mjpg_streamer -i "input_uvc.so -r 800x600 -y -n -f 15" -o "output_http.so -w /usr/local/www"

import ev3_remoted
import ev3te
from ev3te.ev3_tracked_explor3r_message import *
from ev3_remoted.ev3_robot_model import *
import time
# from ev3dev import ev3 as ev3
from ev3dev2 import motor
from ev3dev2.sensor.lego import InfraredSensor, GyroSensor

class Ev3TrackedExplor3r (Ev3RobotModel):
    """Main class for the Ev3 Tracked Explor3r"""

    # Default main constructor
    def __init__(self):
        """Default main constructor for the Ev3TrackedExplor3r class"""
        # Call parent constructor
        super(Ev3TrackedExplor3r, self).__init__()

        # Init robot sensors and actuators
        try:
            # Init robot actuators
            self.left_motor = motor.LargeMotor('outB')    # Address is important for motors
            self.right_motor = motor.LargeMotor('outC')
            self.head_motor = motor.MediumMotor('outA')
            self.head_motor.position_i = 1000
        except Exception as theException:
            # Most probably one of  the actuators is not connected
            ev3te.ev3te_logger.critical("Ev3TrackedExplor3r: Exception in routine __init__() + "
                                        + "in the actuators initialization section: "
                                        + str(theException))
        # Init robot sensors
        try:
            self.ir_sensor = InfraredSensor()       
            self.ir_sensor.mode = 'IR-PROX'
        except Exception as theException:
            # Most probably one of the sensors is not connected
            ev3te.ev3te_logger.critical("Ev3TrackedExplor3r: Exception in routine __init__() + "
                                        + "Infrared sensor initialization failed: "
                                        + str(theException))
        try:          
            self.gyro_sensor = GyroSensor()
            self.gyro_sensor.mode = 'GYRO-ANG'
            self.gyro_following = False                     # This is True when gyro reference following is enabled
            self.gyro_reference = 0
        except Exception as theException:
            # Most probably one of the sensors is not connected
            ev3te.ev3te_logger.critical("Ev3TrackedExplor3r: Exception in routine __init__() + "
                                        + "Gyro sensor initialization failed: "
                                        + str(theException))

        # Rover selected
        self.rover_selected = 0

        # Single Scan
        self.ir_reading_update_counter = 0
        self.ir_samples_to_skip = 5
        self.ir_last_reading = 0

        # Continuous scan (default setting is for Ev3 Tracked Explor3r)
        self.ircs_activated = False
        # Values for Mark I
        # self.ircs_leftmost = -150
        # self.ircs_rightmost = 150
        # self.ircs_step = 10

        # Values for Mark II
        self.ircs_leftmost = -1300
        self.ircs_rightmost = 1300
        self.ircs_step = 87
        self.ircs_number_of_scans = int((self.ircs_rightmost - self.ircs_leftmost) / self.ircs_step)
        self.ircs_scan_counter = 0
        self.ircs_scan_list = [0] * self.ircs_number_of_scans

        # Roaming states
        self.current_state = "start"
        self.actuate_current_state = {"start" : self.roaming_state_start,
                                      "roam" : self.roaming_state_roam,
                                      "scan" : self.roaming_state_scan,
                                      "backtrace" : self.roaming_state_backtrace,
                                      "turn" : self.roaming_state_turn}

    # Process the incoming message
    def process_incoming_message(self, message):
        """Process the incoming message"""
        # Call the parent method
        ev3te.ev3te_logger.debug("Ev3TrackedExplor3r.process_incoming_message() - Processing a received message")
        super().process_incoming_message(message)

        # Decode the message
        message_str = str(message, 'utf-8')
        decoded_message = json.loads(message_str, object_hook = Ev3TrackedExplor3rMessage.object_decoder)

        # Rover selected
        if self.rover_selected != decoded_message.rover_selected:
            self.rover_selected = decoded_message.rover_selected
            if self.rover_selected == 0:
                self.ircs_leftmost = -150
                self.ircs_rightmost = 150
                self.ircs_step = 10
            elif self.rover_selected == 1:
                self.ircs_leftmost = -1200
                self.ircs_rightmost = 1200
                self.ircs_step = 80
            self.ircs_number_of_scans = int((self.ircs_rightmost - self.ircs_leftmost) / self.ircs_step)
            self.ircs_scan_counter = 0
            self.ircs_scan_list = [0] * self.ircs_number_of_scans

        # Use the message fields here
        if not decoded_message.roaming_mode_activated:
            # The roaming mode is not activated
            # Process the remote manual commands
            # Actuate the main motors
            ev3te.ev3te_logger.debug("Ev3TrackedExplor3r.process_incoming_message() - Actuating main motors")
            try:
                ev3te.ev3te_logger.debug("Ev3TrackedExplor3r.process_incoming_message() - Forward Command: " +
                                        str(decoded_message.forward_command))
                ev3te.ev3te_logger.debug("Ev3TrackedExplor3r.process_incoming_message() - Turn Command: " +
                                        str(decoded_message.turn_command))

                if self.rover_selected == 0:
                    # Main motors
                    self.actuate_main_motors(decoded_message)

                # Head motor
                # Must be moved only if continuous scan is not activated
                if not self.ircs_activated:
                    self.actuate_head_motor(decoded_message)

                # Continuous scan
                self.actuate_continuous_scan(decoded_message)

            except Exception as theException:
                ev3_remoted.ev3_logger.critical("Ev3TrackedExplor3r: Exception in routine process_incoming_message() + "
                                                + str(theException))
        else:
            # Roaming mode is activated
            self.actuate_roaming(decoded_message)
        return decoded_message

    # Actuate the head medium motor with the remote commands
    def actuate_head_motor(self, decoded_message):
        """Actuate the head medium motor"""
        if not self.ircs_activated:
            # The remote command is executed only if the
            # infrared continuous scan is not activated
            # i.e. IR Scan is either automatic or manual
            try:
                if abs(decoded_message.turn_head_command) > 5:
                    head_motor_speed = decoded_message.turn_head_command
                    ev3te.ev3te_logger.debug("Ev3TrackedExplor3r.process_incoming_message() - delta: " +
                                            str(head_motor_speed))
                    self.head_motor.run_forever(speed_sp = head_motor_speed)
                else:
                    self.head_motor.stop(stop_action = "coast")
            except Exception as theException:
                ev3_remoted.ev3_logger.critical("Ev3TrackedExplor3r: Exception in routine actuate_head_motor() + "
                                                + str(theException))

    # Actuate the main motors
    def actuate_main_motors(self, decoded_message):
        try:
            # Init left and right motor speed
            left_speed = 0
            right_speed = 0

            if abs(decoded_message.forward_command) > 5:
                # The remote command is to move forward
                left_speed = decoded_message.forward_command
                right_speed = decoded_message.forward_command
        
            if decoded_message.gyro_reference_driving_activated:
                if not self.gyro_following:
                    # First scan with this mode
                    self.gyro_reference = self.get_rover_measured_heading()
                    self.gyro_following = True

                # Compute the correction as a simple proportional controller with unitary constant
                kp = 100
                if decoded_message.forward_command > 0:
                    # Correction if moving forward
                    route_correction = kp * (self.gyro_reference - self.get_rover_measured_heading())
                else:
                    # The correction must be opposite sign if moving bakcward
                    route_correction = kp * (self.gyro_reference - self.get_rover_measured_heading())
                left_speed -= route_correction
                right_speed += route_correction
            else:
                # Gyro reference following not requested
                self.gyro_following = False
                left_speed -= decoded_message.turn_command
                right_speed += decoded_message.turn_command

            # Clamp the values
            left_speed = self.clamp(left_speed, -1000, 1000)
            right_speed = self.clamp(right_speed, -1000, 1000)
            
            if left_speed != 0 and right_speed != 0:
                # Actuate the motors
                self.left_motor.run_forever(speed_sp = -left_speed)
                self.right_motor.run_forever(speed_sp = -right_speed)
            else:
                # Coast the motors to complete stop
                self.left_motor.stop(stop_action = "coast")
                self.right_motor.stop(stop_action = "coast")

        except Exception as theException:
            ev3_remoted.ev3_logger.critical("Ev3TrackedExplor3r: Exception in routine actuate_main_motors() + "
                                            + str(theException))
            # Stop the motors
            self.left_motor.stop(stop_action = "coast")
            self.right_motor.stop(stop_action = "coast")

    # Actuate the continuous IR Scan
    def actuate_continuous_scan(self, decoded_message):
        """Actuate the continuous IR Scan"""
        self.ircs_activated = decoded_message.is_continuous_scan_activated

    # Start roaming
    def roaming_state_start(self):
        # Coast the motors to complete stop
        self.left_motor.stop(stop_action = "coast")
        self.right_motor.stop(stop_action = "coast")
        # Next state
        self.current_state = "roam"
        return
    
    # Roam until an obstacle is detected
    def roaming_state_roam(self):
        roam_speed = 500
        proximity_warning = 30
        obstacle_detected = False

        proximity_reading = self.ir_sensor.proximity
        ev3te.ev3te_logger.info("Proximity Readying: " + str(proximity_reading))
        obstacle_detected = proximity_reading < proximity_warning or proximity_reading == 100

        if obstacle_detected:
            self.left_motor.stop(stop_action = "coast")
            self.right_motor.stop(stop_action = "coast")
        else:
            self.left_motor.run_forever(speed_sp = -roam_speed)
            self.right_motor.run_forever(speed_sp = -roam_speed)
        return

    def roaming_state_scan(self):
        return

    def roaming_state_backtrace(self):
        return

    def roaming_state_turn(self):
        return

    # Actuate the roaming mode (automatic roaming mode)
    def actuate_roaming(self, decoded_message):
        if decoded_message.roaming_mode_activated:
           # Roaming mode is activated 
           self.actuate_current_state[self.current_state]()
           return

    # Create an outbound status message
    def create_outbound_message(self):
        # Call parent method
        message = super().create_outbound_message()

        # Get specific status
        if self.rover_selected == 0:
            message.left_motor_speed = self.get_left_motor_speed()
            message.right_motor_speed = self.get_right_motor_speed()
        
        if self.ircs_activated:
            # Get the reading only for the selected moe
            # This is continuous ir scan
            message.ircs_scan_list = self.get_continuous_scan()
            message.single_ir_reading = 0
            message.head_motor_position = 0
        else:
            # This is single ir reading
            message.single_ir_reading = self.get_single_ir_reading()
            message.head_motor_position = self.get_head_motor_position()
            self.ircs_scan_list = [0] * self.ircs_number_of_scans
        
        message.rover_measured_heading = self.get_rover_measured_heading()
        return message

    # Get the continuous IR Scan
    def get_continuous_scan(self):
        if self.ircs_activated:
            try:
                # Compute the next position set-point
                if self.ircs_scan_counter >= self.ircs_number_of_scans:
                    self.ircs_scan_counter = 0
                position_to_scan = self.ircs_leftmost + self.ircs_scan_counter * self.ircs_step

                # Move the motor
                self.head_motor.run_to_abs_pos(speed_sp = 900, position_sp = position_to_scan, stop_action = 'hold')

                # Wait motion to complete
                while 'running' in self.head_motor.state:
                    sleep(0.1)

                # Scan current position
                self.ircs_scan_list[self.ircs_scan_counter] = self.ir_sensor.proximity

                # Advance to next step
                self.ircs_scan_counter = self.ircs_scan_counter + 1
                while 'running' in self.head_motor.state:
                    sleep(0.1)

            except Exception as theException:
                ev3te.ev3te_logger.critical("Ev3TrackedExplor3r.actuate_continuous_scan() - " + str(theException))
            return self.ircs_scan_list
        else:
            self.ircs_scan_list = [0] * self.ircs_number_of_scans
        return self.ircs_scan_list

    # Get the left motor speed
    def get_left_motor_speed(self):
        try:
            ret_value = self.left_motor.duty_cycle
        except Exception as theException:
            ev3te.ev3te_logger.critical("Ev3TrackedExplor3r.get_left_motor_speed() - " + str(theException))
            ret_value = 0
        return ret_value

    # Get the left motor speed
    def get_right_motor_speed(self):
        try:
            ret_value = self.right_motor.duty_cycle
        except Exception as theException:
            ev3te.ev3te_logger.critical("Ev3TrackedExplor3r.get_right_motor_speed() - " + str(theException))
            ret_value = 0
        return ret_value

    # Get a single reading from the IR Sensor
    def get_single_ir_reading(self):
        if self.ir_reading_update_counter > self.ir_samples_to_skip:
            try:
                self.ir_last_reading = self.ir_sensor.proximity
            except Exception as theException:
                ev3te.ev3te_logger.critical("Ev3TrackedExplor3r.get_single_ir_reading() - " + str(theException))
            finally:
                self.ir_reading_update_counter = 0
        else:
            self.ir_reading_update_counter += 1
        ret_value = self.ir_last_reading
        return ret_value

    # Get head motor position
    def get_head_motor_position(self):
        try:
            ret_value = self.head_motor.position
        except Exception as theException:
            ev3te.ev3te_logger.critical("Ev3TrackedExplor3r.get_head_motor_position() - " + str(theException))
            ret_value = 0
        return ret_value

    # Get the rover measured heading
    def get_rover_measured_heading(self):
        try:
            ret_value = self.gyro_sensor.angle
        except Exception as theException:
            ev3te.ev3te_logger.critical("Ev3TrackedExplor3r.get_rover_measured_heading() - " + str(theException))
            ret_value = 0
        return ret_value    

    # Helper function to clab a value to a specific range
    def clamp(self, x, minimum, maximum):
        return max(minimum, min(x, maximum))   

