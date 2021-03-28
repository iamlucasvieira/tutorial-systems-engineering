import matplotlib.pyplot as plt
import numpy as np
from helpers import load_data

class Stabcont:
    def __init__(self):
        self.data=load_data()

        T=288.15-0.3048*self.data['h_cruise']*6.5/1000
        a=np.sqrt(1.4*T*287)
        m=self.data['v_max']*0.514444/a
        self.data['mach_cr']=m

        self.data['mach_l']=self.data['v_app']*0.514444/np.sqrt(1.4*288.15*287)

        c_r=4*self.data['S']/self.data['b']/(1+self.data['taper'])
        self.data['c_r']=c_r

    @staticmethod
    def transformsweep(qsweep,taper,AR):
        thsweep=np.tan(np.deg2rad(qsweep))-4/AR*(1/4*(1-taper)/(1+taper))
        hsweep=np.rad2deg(np.arctan(thsweep))
        return hsweep

    def getCLaw(self,fc):
        A=self.data['A']
        L_quart=self.data['quart_sweep']
        taper=self.data['taper']
        L_half=self.transformsweep(L_quart,taper,A)

        m_cr=self.data['mach_cr']
        beta_cr=np.sqrt(1-m_cr**2)
        m_l=self.data['mach_l']
        beta_l = np.sqrt(1 - m_l ** 2)

        if fc=='cruise':
            Claw=(2*np.pi*A)/(2+np.sqrt(4+(A*beta_cr/0.95)**2*(1+np.tan(np.deg2rad(L_half))**2/beta_cr**2)))
        if fc=='land':
            Claw = (2 * np.pi * A) / (2 + np.sqrt(
                4 + (A * beta_l / 0.95) ** 2 * (1 + np.tan(np.deg2rad(L_half)) ** 2 / beta_l ** 2)))
        return Claw
    def getCLah(self,fc):
        A_h=self.data['A_h']
        L_h_quart=self.data['quart_sweep_h']
        taper_h=self.data['taper_h']
        L_h_half=self.transformsweep(L_h_quart,taper_h,A_h)
        m_cr=self.data['mach_cr']
        beta_cr=np.sqrt(1-m_cr**2)
        m_l=self.data['mach_l']
        beta_l = np.sqrt(1 - m_l ** 2)

        if fc=='cruise':
            Clah=(2*np.pi*A_h)/(2+np.sqrt(4+(A_h*beta_cr/0.95)**2*(1+np.tan(np.deg2rad(L_h_half))**2/beta_cr**2)))
        if fc=='land':
            Clah = (2 * np.pi * A_h) / (2 + np.sqrt(
                4 + (A_h * beta_l / 0.95) ** 2 * (1 + np.tan(np.deg2rad(L_h_half)) ** 2 / beta_l ** 2)))
        return Clah
    def getCLaminh(self,fc):
        b_f=self.data['b_f']
        b=self.data['b']
        S=self.data['S']
        c_r=self.data['c_r']
        CL_aw= self.getCLaw(fc)
        taper=self.data['taper']

        S_net=S-2* b_f/2*(c_r+c_r*taper*b/b_f)/2

        CLaminh=CL_aw*(1+2.15*b_f/b)*S_net/S+np.pi/2*b_f**2/S

        return CLaminh


    def getx_ac(self,fc):
        m_cr=self.data['mach_cr']
        m_land=self.data['mach_l']
        A=self.data['A']
        L_quart=self.data['quart_sweep']
        taper=self.data['taper']
        mac=self.data['mac']
        b=self.data['b']
        b_f= self.data['b_f']
        h_f=self.data['h_f']
        l_fn=self.data['l_fn']
        S= self.data['S']
        l_n=self.data['l_n']
        b_n=self.data['b_n']
        if fc=='cruise':
            CLaminh=self.getCLaminh('cruise')
        if fc=='land':
            CLaminh=self.getCLaminh('land')
        c_g=S/b


        #xac_wingfuselage
        if fc=='cruise':
            beta=np.sqrt(1-m_cr**2)
            lb=np.rad2deg(np.arctan(np.tan(np.deg2rad(L_quart))/beta))
            print(beta*A,lb,taper)
            xac_w = 0.265  # visually determined from graph
        if fc=='land':
            beta=np.sqrt(1-m_land**2)
            lb=np.rad2deg(np.arctan(np.tan(np.deg2rad(L_quart))/beta))
            print(beta*A,lb,taper)
            xac_w = 0.26  # visually determined from graph


        xacf_1=1.8/CLaminh*b_f*h_f*l_fn/S/mac
        xacf_2=0.273/(1+taper)*b_f*c_g*(b-b_f)/mac**2/(b+2.15*b_f)*np.tan(np.deg2rad(L_quart))

        #x_ac nacelles
        xac_n=4*-4*b_n**2*l_n/(S*mac*CLaminh)

        x_ac=xac_w-xacf_1+xacf_2+xac_n

        return x_ac
    def getdownwash(self):
        b=self.data['b']
        A=self.data['A']
        l_h=self.data['l_h']
        z_h=self.data['z_h']
        CL_aw=self.getCLaw('cruise')
        L_quart=np.deg2rad(self.data['quart_sweep'])

        r=l_h/b*2
        mtv=z_h/b*2
        KeL=(0.1124+0.1265*L_quart+0.1766*L_quart**2)/r**2+0.1024/r+2
        Ke0=0.1124/r**2+0.1024/r+2

        term1=0.4876*r/(r**2+mtv**2)/np.sqrt(r**2+0.6319+mtv**2)
        term2=1+(r**2/(r**2+0.7915+5.0734*mtv**2))**0.3113
        term3=1-np.sqrt(mtv**2/(1+mtv**2))

        deda=KeL/Ke0*(term1+term2*term3)*CL_aw/np.pi/A
        return deda
    def stabline(self,xcg):
        CL_ah=self.getCLah('cruise')
        CL_aminh=self.getCLaminh('cruise')
        x_ac=self.getx_ac('cruise')
        deda=self.getdownwash()
        l_h=self.data['l_h']
        mac=self.data['mac']

        sratio = 1 / (CL_ah / CL_aminh * (1 - deda) * l_h / mac * 1) * xcg - (x_ac) / (
                    CL_ah / CL_aminh * (1 - deda) * l_h / mac * 1)

        sratio_sm=1/(CL_ah/CL_aminh*(1-deda)*l_h/mac*1)*xcg - (x_ac-0.05)/(CL_ah/CL_aminh*(1-deda)*l_h/mac*1)

        return sratio, sratio_sm


    def getcmac(self):
        A=self.data['A']
        L_quart=self.data['quart_sweep']
        b_f=self.data['b_f']
        l_f=self.data['l_f']
        h_f=self.data['h_f']
        S=self.data['S']
        S_hld=self.data['S_hld']
        mac=self.data['mac']
        CLaminh=self.getCLaminh('land')


        cm0=-0.0078 #From Boeing 737 midwing airfoil
        CLa=CLaminh*(S+S_hld)/S
        alpha_0L= -12.65*np.pi/180
        CL0=-CLa*alpha_0L

        cmac_w=cm0*(A*np.cos(np.deg2rad(L_quart))**2/(A+2*np.cos(np.deg2rad(L_quart))))
        cmacf=-0.55 #Taken from graph, Boeing 737, comparable flap area ratio
        cmacfus=-1.8*(1-2.5*b_f/l_f)*np.pi*b_f*h_f*l_f/(4*S*mac)*CL0/CLaminh

        cmac=cmac_w+cmacf+cmacfus
        return cmac
    def contline(self,xcg):
        CL_max=self.data['CL_max']
        l_h=self.data['l_h']
        mac=self.data['mac']
        xac=self.getx_ac('land')
        Cm_ac=self.getcmac()
        CL_h=-0.8

        sratio=1/(CL_h/CL_max*l_h/mac*1)*xcg+(Cm_ac/CL_max-xac)/(CL_h/CL_max*l_h/mac*1)

        return sratio

    def scissorplot(self):
        S=self.data['S']
        S_h=self.data['S_h']

        sratio=S_h/S
        print("Here:", sratio)

        xcgrange=np.arange(0,1,0.05)
        stabrange=self.stabline(xcgrange)
        contrange=self.contline(xcgrange)

        plt.plot(xcgrange,stabrange[0])
        plt.plot(xcgrange,stabrange[1],label='S.M.')
        plt.plot(xcgrange, contrange)
        plt.xlabel(r'$\frac{x_{cg}}{mac}$')
        plt.ylabel(r'$\frac{S_h}{S}$')
        plt.ylim((0))
        plt.legend()
        plt.grid()
        plt.show()





if __name__=="__main__":
    ac=Stabcont()
    ac.scissorplot()





