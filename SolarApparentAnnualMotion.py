import os, sys
import numpy as np
import matplotlib.pyplot as plt


# SI units used.
Second = 1.
Minute = 60 * Second
Hour = 60 * Minute
Day = 24 * Hour # Assume a mean solar day as 24 hours.
Degree = np.pi / 180.


G = 6.67408e-11
M = 1.989e30
m = 5.972e24 # Assume M >> m.
e = 0.0167 # Eccentricity of earth orbit
T = 365.25636 * Day

periapsisLongitude = 103. * Degree
earthTilt = 23.5 * Degree


def rotate_x(th, vec):
    matrix = np.array([
        [1.,         0.,          0.],
        [0., np.cos(th), -np.sin(th)],
        [0., np.sin(th),  np.cos(th)]])
    return matrix.dot(vec)

def rotate_y(th, vec):
    matrix = np.array([
        [ np.cos(th), 0., np.sin(th)],
        [         0., 1.,         0.],
        [-np.sin(th), 0., np.cos(th)]])
    return matrix.dot(vec)

def rotate_z(th, vec):
    matrix = np.array([
        [np.cos(th), -np.sin(th), 0.],
        [np.sin(th),  np.cos(th), 0.],
        [        0.,          0., 1.]])
    return matrix.dot(vec)

def angle_between(v1, v2):
    cs = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return np.arccos(cs)


a = np.cbrt(G * M * T**2 / 4. / np.pi**2)
c = a * e
b = np.sqrt(a**2 - c**2)
J = m * np.sqrt(G * M * a * (1.-e**2))
perihelion = a * (1.-e)
aphelion = a * (1.+e)
vPerihelion = np.sqrt(G * M * (1.+e) / perihelion)
vAphelion = np.sqrt(G * M * (1.-e) / aphelion)
omegaEarth = 2*np.pi * (T/Day+1) / T

print("earth orbit semimajor axis: a={}".format(a))
print("earth rotation angular speed: omegaEarth={}".format(omegaEarth))


# Axis configuration:
#   Set theta(th) coordinate of perihelion to 0.
#   Set theta(th) axis direction the same as earth's orbital direction.

# Set theta(th) coordinate of earth at zero time to 0.
# Set the upward meridian as prime meridian
#   which at zero time is orthogonal to the intersection line
#   of ecliptic plane and equatorial plane.

latitude = 0. * Degree # North latitude as positive.
longitude = 0. * Degree # East longitude as positive.
shotClock = 0.*Hour + 0.*Minute + 0.*Second

print("Arguments: [lat [lon [hour]]]")
if len(sys.argv) >= 2:
    latitude = float(sys.argv[1]) * Degree
if len(sys.argv) >= 3:
    longitude = float(sys.argv[2]) * Degree
if len(sys.argv) >= 4:
    shotClock = float(sys.argv[3]) * Hour

# Four axes:
#
# For earth's orbital revolution:
#   Polar axis: Sun as the origin. zero theta direction points to earth's perihelion.
#
# For trigonometric calculation:
#   Use 3 axes, all using earth as origin.
#   Axis 1: x1's direction points from sun to earth's perihelion.
#           z1's direction points to celestial north pole.
#   Axis 2: tilt axis 1 an angle of (-periapsisLongitude + np.pi/2.) around z1.
#           So that x2 is parallel with the intersection line of ecliptic plane and equitorial plane.
#   Axis 3: tilt axis 2 an angle of (-earthTilt) around x2.
#           So that z3 points to the earth axis.

zenithPoint3_lat0_lon0_t0 = np.array([0., -1., 0.]) # 0-lat 0-lon direction at 0 time
northPoint3_lat0_lon0_t0 = np.array([0., 0., 1.]) # North direction at (lat 0., lon 0.) point at 0 time
zenithPoint3_t0 = rotate_z(longitude,
        rotate_x(-latitude, zenithPoint3_lat0_lon0_t0) # Use rotate_x because of the choice of prime meridian.
        )
northPoint3_t0 = rotate_z(longitude,
        rotate_x(-latitude, northPoint3_lat0_lon0_t0) # Use rotate_x because of the choice of prime meridian.
        )

iday = 0
solarAngle = []


# Use leap frog scheme.
# Calculation Starts from Perhelion (t = 0.).

stepPerCircle = 100 * T/Day
nCircles = 1
nStep = int(stepPerCircle * nCircles)
dt = T / stepPerCircle

t = np.zeros(nStep+1)

r = np.zeros(nStep+1)
th_t = np.zeros(nStep+1)
r_t_t = np.zeros(nStep+1)

th_h = np.zeros(nStep+1)
r_t_h = np.zeros(nStep+1)

th = np.zeros(nStep+1)
r_t = np.zeros(nStep+1)

t[0] = 0.

r[0] = perihelion
th_t[0] = J / m / r[0]**2
r_t_t[0] = r[0] * th_t[0]**2 - G * M / r[0]**2

th[0] = 0.
r_t[0] = 0.

# Push the first half step.
th_h[0] = th[0] + th_t[0] * dt/2.
r_t_h[0] = r_t[0] + r_t_t[0] * dt/2.

for i in range(nStep):
    t[i+1] = t[i] + dt

    r[i+1] = r[i] + r_t_h[i] * dt
    th_t[i+1] = J / m / r[i+1]**2
    r_t_t[i+1] = r[i+1] * th_t[i+1]**2 - G * M / r[i+1]**2

    th_h[i+1] = th_h[i] + th_t[i+1] * dt
    r_t_h[i+1] = r_t_h[i] + r_t_t[i+1] * dt

    th[i+1] = th_h[i+1] - th_t[i+1] * dt/2.
    r_t[i+1] = r_t_h[i+1] - r_t_t[i+1] * dt/2.

    if (t[i+1] // Day >= iday and t[i+1] % Day >= shotClock):
        iday = t[i+1] // Day + 1

        backtime = t[i+1] % Day - shotClock
        theta = th[i+1] - th_t[i+1] * backtime
        rotation = omegaEarth * (t[i+1] - backtime)

        zenithPoint3 = rotate_z(rotation, zenithPoint3_t0)
        zenithPoint2 = rotate_x(-earthTilt, zenithPoint3)
        zenithPoint1 = rotate_z(-periapsisLongitude + np.pi/2., zenithPoint2)

        northPoint3 = rotate_z(rotation, northPoint3_t0)
        northPoint2 = rotate_x(-earthTilt, northPoint3)
        northPoint1 = rotate_z(-periapsisLongitude + np.pi/2., northPoint2)

        # Start to calculate solar angle.
        # eastPoint1-northPoint1-zenithPoint1 forms another x-y-z point whose origin is the observer.
        eastPoint1 = np.cross(northPoint1, zenithPoint1)
        sunPoint1 = np.array([np.sin(theta), -np.cos(theta), 0.])
        zenithAngle = angle_between(sunPoint1, zenithPoint1)
        azimuth = np.arctan2(np.dot(sunPoint1, eastPoint1), np.dot(sunPoint1, northPoint1))

        # Assume a new latitude-longitude coordinates.
        # The north pole is on the direction of northPoint1, and 0-lat coincide with zenithPoint1.
        # Under this coordinates, the sun occupy the point (elat, elon).
        elat = -angle_between(sunPoint1, northPoint1) + np.pi/2.
        elon = np.arctan2(np.dot(sunPoint1, eastPoint1), np.dot(sunPoint1, zenithPoint1))

        solarAngle.append((azimuth, zenithAngle, elat, elon))


solarAngle = np.array(solarAngle)

ax = plt.subplot(231, projection='polar')
ax.plot(th, r)
ax.plot((np.pi,), (c,), 'go', markersize=3.0)
ax.plot((0.,), (0.,), 'ro')
ax.set_xticks(np.linspace(0, 1.5*np.pi, 4))
ax.set_rticks([1.0e11, 2.0e11])
ax.set_rlabel_position(135)  # Move radial labels away from plotted line
ax.grid(True)

arcToDegree = 180. / np.pi
ax = plt.subplot(233, projection='polar')
ax.plot(solarAngle[:,0], solarAngle[:,1]*arcToDegree)
ax.plot((solarAngle[0,0],), (solarAngle[0,1]*arcToDegree,), 'ko')
ax.set_theta_zero_location("N")
ax.set_xticks(np.linspace(0, 1.5*np.pi, 4))
ax.set_xticklabels(['N', 'E', 'S', 'W'])
# ax.set_rmax(180.)
# ax.set_yticks([90.])
# ax.set_yticklabels(['horizon'])
ax.set_rlabel_position(45)
ax.grid(True)

ax = plt.subplot(235)
ax.invert_xaxis()
ax.scatter(solarAngle[:,3]*arcToDegree, solarAngle[:,2]*arcToDegree, s=0.3)
ax.plot((solarAngle[0,3]*arcToDegree,), (solarAngle[0,2]*arcToDegree,), 'ko')
ax.grid(True)

plt.show()


