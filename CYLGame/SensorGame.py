from CYLGame.Game import NonGridGame
from CYLGame.Player import Player
from CYLGame.Frame import GameFrame
from CYLGame import GameLanguage
import math
import random

TAU = 2.0 * math.pi;
SEP = "---------------------------------------"

DEBUG = False
def dprint(string):
    if DEBUG:
        print(string)
    

def deg2rad(deg):
    return float(deg) * TAU / 360.0
def rad2deg(rad):
    return float(rad) * 360.0 / TAU

def rotate_point(angle, point):
    cos_ = math.cos(angle)
    sin_ = math.sin(angle)

    newp = [0, 0]
    newp[0] = float(point[0])*cos_ - float(point[1])*sin_
    newp[1] = float(point[0])*sin_ + float(point[1])*cos_

    return newp

def compute_vector(start, end, screen_width, screen_height):
    """
    Computes the vector and distance between two objects, start and end.
    start and end must have a position attribute which is a list/tuple
    of the x and y coord.
    """
    vector = []
    half_width = float(screen_width) / 2.0
    vector.append(end.position[0] - start.position[0])
    if vector[0] > half_width:
        vector[0] -= screen_width
    elif vector[0] < -half_width:
        vector[0] += screen_width

    half_height = float(screen_height) / 2.0
    vector.append(end.position[1] - start.position[1])
    if vector[1] > half_height:
        vector[1] -= screen_height
    elif vector[1] < -half_height:
        vector[1] += screen_height

    return vector[0]**2 + vector[1]**2, vector

class SensorSanitizers(object):
    # sensor sanitize/validate functions
    @staticmethod
    def san_range(r):
        if not r:
            return 0.0

        new_r = float(r)
        if new_r < 0.0:
            new_r = 0.0
        elif new_r > 100.0:
            new_r = 100.0
        return new_r

    @staticmethod
    def san_angle(a):
        if not a:
            return 0.0

        return float(a)

    @staticmethod
    def san_width(w):
        if not w:
            return 0.0

        new_w = float(w)
        if new_w < 0.0:
            new_w = 0.0
        elif new_w > 360.0:
            new_w = 360.0
        return new_w

    @staticmethod
    def san_turret(t):
        if not t:
            return False

        return bool(t)

    import re
    color_re = re.compile(r'#[0-9A-Fa-f]{6}')
    @staticmethod
    def san_color(c):
        if not c:
            return None
        elif SensorSanitizers.color_re.match(c):
            return c
        else:
            return None

class SensorPlayer(Player):

    def add_sensor(self, _range, angle, width, turret):
        """
        Adds a sensor to this player.
        _range: integer [0, 100], the distance that the sensor travels
        angle: integer [0, 360], the direction in degrees the sensor points
        width: integer [0, 360], the width in degrees of the sensor
        turret: bool, if True, the angle is relative to the turret's angle,
        otherwise angle is relative to the tank's angle
        """
        sensor = {}
        sensor["range"] = float(_range)
        sensor["angle"] = deg2rad(angle)
        sensor["width"] = deg2rad(width)
        sensor["turret"] = turret
        sensor["triggered"] = 0
        self.sensors.append(sensor)

    def sensor_calc(self, other, dist_sq, vector, tank_sensor_range):
        """
        See if other is in any of our sensors.
        """
        if self.killer or other.killer:
            return

        # check if they are in our max sensor range
        if dist_sq > (tank_sensor_range + other.radius)**2:
            return
        #print("sensor_calc")
        #print(dist_sq, vector, self.angle)
        # Now calculate sensors
        for i, sensor in enumerate(self.sensors):
            if sensor["range"] <= 0:
                continue

            if sensor["triggered"] & other.obj_type:
                # sensor already firing
                continue

            if dist_sq > (sensor["range"] + other.radius)**2:
                # out of range
                continue

            theta = self.angle + sensor["angle"]
            #print(sensor["angle"])
            if sensor["turret"]:
                theta += self.turret_current

            # do some funky math
            # rotate other's position by theta
            rotated_point = rotate_point(-theta, vector)
            # Sensor is symmetrical, so we only need to consider top
            # quadrants
            rotated_point[1] = abs(rotated_point[1])
            # compute inverse slope of our sensor
            m_s = 1.0 / math.tan(sensor["width"] / 2.0)
            # compute slope to other
            m_r = rotated_point[0] / rotated_point[1] 
            
            # if our inverse slope is less than other, they're inside
            # the arc
            if m_r >= m_s:
                #print("triggered", i)
                sensor["triggered"] |= other.obj_type
                continue

            # Now check if the edge of the arc intersects the tank. Do
            # this just like with firing
            rotated_point = rotate_point(sensor["width"] / -2.0, rotated_point)
            if rotated_point[0] > 0 and abs(rotated_point[1]) < other.radius:
                #print("triggered", i)
                sensor["triggered"] |= other.obj_type



class SensorGame(NonGridGame):
    WEBONLY = True
    NONGRID = True
    OPTIONS = "sensors"

    def do_sensors(self):
        players = self.players
        for player in players:
            for sensor in player.sensors:
                sensor["triggered"] = 0

        for i in range(len(players)):
            if players[i].killer:
                continue

            for j in range(i + 1, len(players)):
                if players[j].killer:
                    continue
                dist_sq, vector = compute_vector(players[i], players[j], self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                players[i].sensor_calc(players[j], dist_sq, vector, self.MAX_SENSOR_RANGE)
                vector[0] = -vector[0];
                vector[1] = -vector[1];
                players[j].sensor_calc(players[i], dist_sq, vector, self.MAX_SENSOR_RANGE)


