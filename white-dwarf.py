import matplotlib.pyplot as plt
import numpy as np

MSun = 1.99e30
RSun = 6.96e8
rhoSun = 1.5e5
pi = np.pi
G = 6.67e-11
h = 6.63e-34
hbar = h / (2*pi)
me = 9.1e-31
NA = 6.02e23
He_H_Ratio = 1. / 10.
He_H_Ratio = 1000000. / 1.
c = 2.99792e8
Z_H = 1
Z_He = 2
Z = (Z_H + Z_He * He_H_Ratio) / (1 + He_H_Ratio)
mu_H = 1.0e-3
mu_He = 4.0e-3
mu = (mu_H + mu_He * He_H_Ratio) / (1 + He_H_Ratio)
# print(He_H_Ratio, 'Z=', Z, 'mu=', mu)
# raise SystemExit

# Non-relativistic electron gas.
fp = (3*pi**2)**(2./3.) * hbar**2 / (5*me) * (Z*NA/mu)**(5./3.)
def pressure(rho):
    return fp * rho**(5./3.)

# Relativistic electron degeneracy pressure is needed.
# But the following is the ultra-relativistic limit.
# So that all white dwarfs with different radius will have the same mass.
fp_r = (3*pi**2)**(1./3.) * hbar * (c/4) * (Z*NA/mu)**(4./3.)
def pressure_r(rho):
    return fp_r * rho**(4./3.)

# frho = mu / (Z*NA*(3*(pi**2))**0.4) * (5*me/hbar**2)**0.6
# def density(p):
#     return frho * p**0.6
# 
# def g(M, r):
#     return G * M / r**2

class _star:
    def __init__(self, nstep, src):
        self.nstep = nstep
        self.r = src[:,0]
        self.RSunRatio = src[:,1]
        self.M = src[:,2]
        self.MSunRatio = src[:,3]
        self.rplus = src[:,4]
        self.rho = src[:,5]
        self.pres = src[:,6]

Num = 50
rhostart = 1.e9
rhostep = 1.e10
# rCore = dr * 2

stars = []
for n in range(Num):
    star = []
    nstep = 0
    istep = 0
    dr = 1.0e3
    r = dr * 5
    rho = rhostart + rhostep * n
    M = (4./3.) * pi * r**3 * rho

    # rho23 += -(2./5.) * (G/fp) * (M/r**2) * (dr/2.)
    # rho = rho23**(3./2.)
    # star.append((nstep, r, M, r+dr/2., rho, pressure(rho)))
    # d_M = 4*pi * r**2. * rho * dr
    # d_rho23 = -(2./5.) * (G/fp) * (M/r**2) * dr

    # rho23 = rho**(2./3.)
    # rho53 = rho**(5./3.)
    # d_rho23 = -(2./5.) * (G/fp) * (M/r**2) * (dr/2.)
    # d_rho53 = -(G/fp) * (M/r**2) * (dr/2.)
    # while(rho53 > -10.*d_rho53):

    rho13 = rho**(1./3.)
    d_rho13 = -(1./4.) * (G/fp_r) * (M/r**2) * (dr/2.)
    # while(rho13 > -10.*d_rho13):
    while(rho13 > -10.*d_rho13 and rho > 1.*rhoSun):
        rho13 += d_rho13
        # rho23 += d_rho23
        # rho53 += d_rho53
        rho = rho13**3
        # rho = rho23**(3./2.)
        # rho = rho53**(3./5.)
        # pres = pressure(rho)
        pres = pressure_r(rho)

        if istep % 1 == 0:
            star.append((r, r/RSun, M, M/MSun, (r+dr/2)/RSun, rho/rhoSun, pres))
            nstep += 1

        istep += 1
        d_M = 4*pi * (r+dr/2.)**2. * rho * dr
        M += d_M
        r += dr
        d_rho13 = -(1./4.) * (G/fp_r) * (M/r**2) * dr
        # d_rho23 = -(2./5.) * (G/fp) * (M/r**2) * dr
        # d_rho53 = -(G/fp) * (M/r**2) * dr

        if r > RSun:
            print('Bigger than the Sun!')
            break

    if nstep > 50:
        print(n, r/RSun, M/MSun)
        starnd = np.zeros((nstep, 7))
        for i in range(nstep):
            starnd[i,:] = star[i][:]
        stars.append(_star(nstep, starnd))
    else:
        print('break at: {}/{}\n'.format(n+1,Num))
        break
    star = None
print('Calculated: {}/{}\n'.format(n+1,Num))

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

sample = range(0,len(stars),len(stars)//2)
sample = [0, len(stars)//2, len(stars)-1]
for i in sample:
    star = stars[i]
    fig, host = plt.subplots()
    # fig.subplots_adjust(right=0.75)
    par2 = host.twinx()
    par3 = host.twinx()
    par3.spines["right"].set_position(("axes", 1.2))
    make_patch_spines_invisible(par3)
    par3.spines["right"].set_visible(True)

    p1, = host.plot(star.rplus, star.rho, 'b', label='rho/rhoSun')
    host.set_ylabel('rho/rhoSun')
    host.set_xlabel('RSunRatio')
    p2, = par2.plot(star.RSunRatio, star.MSunRatio, 'r', label='MSunRatio')
    par2.set_ylabel('MSunRatio')
    p3, = par3.plot(star.RSunRatio, range(star.nstep), 'g', label='nstep')
    par3.set_ylabel('nstep')

    lines = (p1, p2, p3)
    host.legend(lines, [l.get_label() for l in lines])

    # plt.legend()
    # plt.title('nstep={}   MSunRatio={}   RSunRatio={}'.format(star.nstep, star.MSunRatio[-1], star.RSunRatio[-1]))
    plt.title('MSunRatio={:.5f}'.format(star.MSunRatio[-1]))
    plt.show()

    # plt.plot(star.rplus, star.rho, label='rho')
    # plt.title('{}   {}'.format(star.nstep, star.MSunRatio[-1]))
    # plt.legend()
    # plt.show()
    # plt.plot(star.rplus, star.pres, label='pres')
    # plt.title('{}   {}'.format(star.nstep, star.MSunRatio[-1]))
    # plt.legend()
    # plt.show()

