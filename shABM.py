# -*- coding: utf-8 -*-
#! Python 3.6.6 
"""
Created on Fri Aug 31 21:56:31 2018
Reorganized on Fri Jan 1 2021 by shoffens

@author: amino

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ important lists (arrays) and variables ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Three hashtag symbol (###) at the beginning of a line means that the line was created for debugging purposes and is not a comment explaining the line below it
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""

import random
import math
# import scipy
import csv
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
# bimport matplotlib.pyplot as plt         this is equivalent to "from matplotlib import pyplot as plt"
# from matplotlib.font_manager import FontProperties 
# import matplotlib.backends.backend_pdf
# from matplotlib.backends.backend_pdf import PdfPages
from statistics import mean
import time
start_time = time.time() # track execution time

#################### Define agent types ####################
class Consumer:
    def __init__(self, amean, astd, amin, amax, PWU = None, Ut = None):
        self.Ut = Ut
        self.PWU = Attr[random.randint(0,len(Attr)-1)]  # Pick random row from survey utility data  
        self.Ageconstant = agecons(amean,astd,amin,amax)    # Generate a random age constant
        self.Ut = [0, 0, 0, 0, 0, 0]  #Each consumer has a utility array with values for each producer
        self.CurrUt = 0           # Initial utility
        self.currcarage = 0      # current age of owned vehicle
        self.currcarageset = []  # store temporary current car age values
        self.CurrUtset = []      # store current utility
        self.currmodelyr = 0
        self.FEPWU = 0      # part worth utility of current owned vehicle's fuel economy
        self.AccPWU = 0     # part worth utility of current owned vehicle's performance
        self.PrPWU = 0      # part worth utility of current owned vehicle's price
        self.color = (0,0,0)
        self.currAcc = 0
        self.currFE = 0
        self.currPr = 0
        self.maxcarut = []
        self.holdl = []
        self.repch = []

class Producer:
    def __init__(self, Specs = [0,0,0,0,0,0,0,0,0,0,0]):
        self.Specs = Specs     # Fuel economy, acceleration, price, cf, ca, then 6 zeros
        self.sumcar = 0         # Sale per year of producer
        self.sumcarset = []     # Sales per year tracked across all years
        self.purchdcar = 0      # Cumulative sale of producer
        self.purchdcarset = []  # Cumulative sales of producer tracking all years
        self.temprofit = 0      # NOT USED: temporary storage of profits
        self.profit = 0         # NOT USED: Cumulative profit of the producer
        self.profitset = []     # NOT USED: Cumulative profits tracked across years
        self.FEset = []     # Stores the fuel economy of this producer in every tick
        self.Accset = []    # Stores the acceleration of this producer in every tick
        self.Prset = []     # Stores the price of this producer in every tick
        
############################################ All the functions ###########################################
#%%
#Read the csv file containing the part worth utilities of 184 consumers
def readCSVPWU():
    global headers
    global Attr
    Attr = []
    with open('PWUfromCBCdata.csv') as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',')
        headers = next(csvreader)  # skip the first row of the CSV file.
        #CSV header cells are string and should be turned to a float number.
        for i in range(len(headers)):   
            if headers[i].isnumeric():
                headers[i] = float(headers[i])
        for row in csvreader:
            AttrS = row
            Attr.append(AttrS)
    #convert strings to float numbers
    Attr = [[float(float(j)) for j in i] for i in Attr]
    #Return the CSV as a matrix with 17 columns and 184 rows 
    return Attr
#%%
######################################################################################################
    #Read producer specifications
def readProdSpecs():
    global Prodcr
    Prodcr = []
    with open('SixProdinitspecs.csv') as csvfile:
        csvreaderP = csv.reader(csvfile,delimiter=',')
        next(csvreaderP)
        for rowP in csvreaderP:
            ProdcrS = rowP
            Prodcr.append(ProdcrS)
    #float numbers
    Prodcr = [[float(float(jj)) for jj in ii] for ii in Prodcr]
    #Return the CSV as a matrix with 11 columns and 3 rows 
    return Prodcr

#%%
###########################################################################################################################
#Create a negative age constant from a random distribution
def agecons(amean,astd,amin,amax):
    # Inputs are mean and standard deviation of random number, and min/max bounds for filter
    agecon = float(np.random.normal(amean,astd, 1)) # Generate random number
    while agecon <= amin or agecon >= amax:         # Filter if outside min/max range
        agecon = float(np.random.normal(amean,astd, 1))
    return agecon

#%%
#########################################################################################################
# Evaluate the part-worth utility (PWU) for fuel economy (FE) using linear interpolation
def EvalFE(FE, cons_agent, cons_id):
    if FE in headers:   
        ndx = headers.index(FE)     ##Find first position of values in list
        return cons_agent[cons_id].PWU[ndx]
    else: 
        #interpolate extrapolate
        ndx12 = headers.index(12)
        ndx18 = headers.index(18)
        ndx24 = headers.index(24)
        ndx30 = headers.index(30)
        ndx36 = headers.index(36)
        if FE < 12:
            return cons_agent[cons_id].PWU[ndx12]
        if FE > 36:
            return cons_agent[cons_id].PWU[ndx36]
        #interpolate y = ya + (yb - ya) ((x - xa)/(xb - xa))
        if 12 < FE < 18:
            return cons_agent[cons_id].PWU[ndx12] + ((FE - 12) * (cons_agent[cons_id].PWU[ndx18] - cons_agent[cons_id].PWU[ndx12])) / (18 - 12)
        if 18 < FE < 24:
            return cons_agent[cons_id].PWU[ndx18] + ((FE - 18) * (cons_agent[cons_id].PWU[ndx24] - cons_agent[cons_id].PWU[ndx18])) / (24 - 18)
        if 24 < FE < 30:
            return cons_agent[cons_id].PWU[ndx24] + ((FE - 24) * (cons_agent[cons_id].PWU[ndx30] - cons_agent[cons_id].PWU[ndx24])) / (30 - 24)
        if 30 < FE < 36:
            return cons_agent[cons_id].PWU[ndx30] + ((FE - 30) * (cons_agent[cons_id].PWU[ndx36] - cons_agent[cons_id].PWU[ndx30])) / (36 - 30)

#%%
################################################################################################################################
def EvalAcc(Acc, cons_agent, cons_id):
    if Acc in headers[7:]:   
        ndxx = headers[7:].index(Acc) + 7     ##Find first position of values in list
        return cons_agent[cons_id].PWU[ndxx]
    else: 
        indx4 = headers[7:].index(4) + 7
        indx6 = headers[7:].index(6) + 7
        indx8 = headers[7:].index(8) + 7
        indx10 = headers[7:].index(10) + 7
        indx12 = headers[7:].index(12) + 7
        if Acc < 4:
            return cons_agent[cons_id].PWU[indx4]
        if Acc > 12:
            return cons_agent[cons_id].PWU[indx12]
        #interpolate y = ya + (yb - ya) ((x - xa)/(xb - xa))
        if 4 < Acc < 6:
            return cons_agent[cons_id].PWU[indx4] + ((Acc - 4) * (cons_agent[cons_id].PWU[indx6] - cons_agent[cons_id].PWU[indx4])) / (6 - 4)
        if 6 < Acc < 8:
            return cons_agent[cons_id].PWU[indx6] + ((Acc - 6) * (cons_agent[cons_id].PWU[indx8] - cons_agent[cons_id].PWU[indx6])) / (8 - 6)
        if 8 < Acc < 10:
            return cons_agent[cons_id].PWU[indx8] + ((Acc - 8) * (cons_agent[cons_id].PWU[indx10] - cons_agent[cons_id].PWU[indx8])) / (10 - 8)
        if 10 < Acc < 12:
            return cons_agent[cons_id].PWU[indx10] + ((Acc - 10) * (cons_agent[cons_id].PWU[indx12] - cons_agent[cons_id].PWU[indx10])) / (12 - 10)

#%%
########################################################################################################################################3
def EvalPr(Pr, cons_agent, cons_id):
    if Pr in headers:   
        ndxxx = headers.index(Pr)     ##Find first position of values in list
        return cons_agent[cons_id].PWU[ndxxx]
    else:                            
        ndx10000 = headers.index(10000)
        ndx15000 = headers.index(15000)
        ndx20000 = headers.index(20000)
        ndx25000 = headers.index(25000)
        ndx30000 = headers.index(30000)
        if Pr < 10000:
            return cons_agent[cons_id].PWU[ndx10000]
        if Pr > 30000:
            return cons_agent[cons_id].PWU[ndx30000]
        #interpolate y = ya + (yb - ya) ((x - xa)/(xb - xa))
        if 10000 < Pr < 15000:
            return cons_agent[cons_id].PWU[ndx10000] + ((Pr - 10000) * (cons_agent[cons_id].PWU[ndx15000] - cons_agent[cons_id].PWU[ndx10000])) / (15000 - 10000)
        if 15000 < Pr < 20000:
            return cons_agent[cons_id].PWU[ndx15000] + ((Pr - 15000) * (cons_agent[cons_id].PWU[ndx20000] - cons_agent[cons_id].PWU[ndx15000])) / (20000 - 15000)
        if 20000 < Pr < 25000:
            return cons_agent[cons_id].PWU[ndx20000] + ((Pr - 20000) * (cons_agent[cons_id].PWU[ndx25000] - cons_agent[cons_id].PWU[ndx20000])) / (25000 - 20000)
        if 25000 < Pr < 30000:
            return cons_agent[cons_id].PWU[ndx25000] + ((Pr - 25000) * (cons_agent[cons_id].PWU[ndx30000] - cons_agent[cons_id].PWU[ndx25000])) / (30000 - 25000)

#%%
#########################################################################################################
def prod_out(prod_agent):
      for idp in range(len(Prodcr)):
          prod_agent[idp].FEset.append(prod_agent[idp].Specs[0])
          prod_agent[idp].Accset.append(prod_agent[idp].Specs[1]) 
          prod_agent[idp].Prset.append(prod_agent[idp].Specs[2]) 
          prod_agent[idp].sumcarset.append(10 * prod_agent[idp].sumcar)  # Sales units are in thousands (each consumer agent represents 10,000 people)
          prod_agent[idp].purchdcarset.append(prod_agent[idp].purchdcar)

#%%            
########################################################################################################
#Next year's designs/strategy
def realinput(prod_agent, yr, mpg, acc, prc):
#    import pdb; pdb.set_trace()
    for idp in range(len(Prodcr)):
        idp_index = idp + idp*16 + yr
        prod_agent[idp].Specs[0] = mpg[idp_index]
        prod_agent[idp].Specs[1] = acc[idp_index]
        prod_agent[idp].Specs[2] = prc[idp_index]
    
#%%
#########################################################
# Decide whether and which new vehicle to purchase
def shopping(idc, cons_agent, prod_agent, randutstd, currutconst):
    # First, find utilities for all vehicles and store in Ut agent variable:
    for idp in range(len(Prodcr)):
        FEtemp = EvalFE(prod_agent[idp].Specs[0], cons_agent, idc)
        Acctemp = EvalAcc(prod_agent[idp].Specs[1], cons_agent, idc)
        Prtemp = EvalPr(prod_agent[idp].Specs[2], cons_agent, idc)
        cons_agent[idc].Ut[idp] = FEtemp + Acctemp + Prtemp + float(np.random.normal(0,randutstd, 1))
    #Find the maximum utility among the three values for three vehicles
    cons_agent[idc].maxcarut = max(cons_agent[idc].Ut)
    # Set colors 0 = blue, 1 = orange, 2 = green, 3 = red, 4 = purple, 5 = maroon
    colors = [(0,0,255),(255,165,0),(0,255,0),(255,0,0),(128,0,128),(128,0,0)]
    #if the max of the utility array is bigger than the current utility (for first-time shoppers, 0): Replace your car
    if cons_agent[idc].maxcarut > cons_agent[idc].CurrUt:   #Purchase a new vehicle which gives you the highest utility
        indexp = cons_agent[idc].Ut.index(cons_agent[idc].maxcarut)
        cons_agent[idc].color = colors[indexp] # Agent's color associated with producer (see colors variable)
        cons_agent[idc].currFE = prod_agent[indexp].Specs[0]  #Current owned vehicle's fuel economy
        cons_agent[idc].currAcc = prod_agent[indexp].Specs[1]  #Current owned vehicle's performance
        cons_agent[idc].currPr = prod_agent[indexp].Specs[2]#Current owned vehicle's price
        cons_agent[idc].FEPWU = EvalFE(cons_agent[idc].currFE, cons_agent, idc)  #The part worth utility of current owned vehicle's fuel economy
        cons_agent[idc].AccPWU = EvalAcc(cons_agent[idc].currAcc, cons_agent, idc)  #The part worth utility of current owned vehicle's performance
        cons_agent[idc].PrPWU = EvalPr(cons_agent[idc].currPr, cons_agent, idc)    #The part worth utility of current owned vehicle's price
        cons_agent[idc].currmodelyr = yearlist[-1]    #Current model year
        cons_agent[idc].holdl.append(yearlist[-1])
        # Track the sales for the producer:
        prod_agent[indexp].sumcar += 1 #By this purchase, sale increases
        prod_agent[indexp].purchdcar += 1   #By one purchase, cumulative sale increases

    cons_agent[idc].currcarage = yearlist[-1] - cons_agent[idc].currmodelyr
    cons_agent[idc].currcarageset.append(cons_agent[idc].currcarage)
    cons_agent[idc].CurrUt = cons_agent[idc].FEPWU + cons_agent[idc].AccPWU + cons_agent[idc].currcarage * cons_agent[idc].Ageconstant + currutconst
    cons_agent[idc].CurrUtset.append(cons_agent[idc].CurrUt)
    
#%%
########################################################################################################
def draw_plots(producer_agent) :    
    ax = plt.figure(6)
    plt.plot(yearlist, producer_agent[0].sumcarset,label = 'Taurus-Fusion' )
    plt.plot(yearlist, producer_agent[1].sumcarset,label = 'Malibu')
    plt.plot(yearlist, producer_agent[2].sumcarset,label = 'Accord')
    plt.plot(yearlist, producer_agent[3].sumcarset,label = 'Sonata')
    plt.plot(yearlist, producer_agent[4].sumcarset,label = 'Altima')
    plt.plot(yearlist, producer_agent[5].sumcarset,label = 'Camry')
#    plt.axis([0, 30, 0, 100])
    plt.xlabel('Years')
    plt.ylabel('Sale Per Year in Thousands')
#    plt.title('Producers sale per year')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
#    plt.grid(b=True, which='major')
    # plt.savefig('saleee.png')
#    plt.grid(b=True, which='major')

    plt.show()
#    pdf = matplotlib.backends.backend_pdf.PdfPages("rrww.pdf")
#    for figure in range(1, 6): ## will open an empty extra figure :(
#        pdf.savefig(figure)
#    pdf.close()
#%%
###############################################  Main   #####################################################
###def main():
def main(params):
    amean = params[0]
    astd = params[1]
    amin = params[2]
    amax = params[3]
    randutstd = params[4]
    currutconst = params[5]
    global yearlist, consumer_agent, producer_agent, rmse
    ticks = 0  
    yearlist = []
    #Read csv
    readCSVPWU()
    readProdSpecs()
    #Read real data
    df = pd.read_csv("SixAutoVisumanual.csv")  
    # modelyr = list(df.ModelYear)
    # model = list(df.Model)
    prc = list(df.Price)
    mpg = list(df.MPG)
    acc = list(df.AccTime)
    # sals = list(df.Sales)
    #create consumer agents (randomly drawn from the 184 population) and assign id's starting from 0
    ncons = 1050
    consumer_agent = dict(enumerate([Consumer(amean, astd, amin, amax, PWU = [], Ut = []) for ij in range(ncons)])) # Ut=[]
    #create producer  agents and assign id's starting from 0
    producer_agent = dict(enumerate([Producer(Specs = Prodcr[ik]) for ik in range(len(Prodcr))]))     

    while ticks <= 16:
        yearlist.append(ticks + 2000)
        # Producer sales per year and consumer utility arrays reset to zero:
        for idp in range(len(Prodcr)): 
            #sale per year of producer idp 
            producer_agent[idp].sumcar = 0       # Reset this value every year
            for idc in range(ncons):      
                consumer_agent[idc].Ut[idp] = 0
        # Now each consumer can go shopping:
        for i in range(len(consumer_agent)):
            # Only allow 1/7th to enter the market in each of the first 7 years:
            if ticks >= math.floor(i/(ncons/7)):
                shopping(i, consumer_agent, producer_agent, randutstd, currutconst)
        #Store sales per year and current specifications
        prod_out(producer_agent) 
        # Use next year (ticks + 1)'s real specifications as an input
        if ticks < 16:
            realinput(producer_agent, ticks + 1, mpg, acc, prc) # was "ticks + 1 + 2000)"
        ticks += 1
#        import pdb; pdb.set_trace()
    # draw_plots(producer_agent)
    
    # # Save sales in a csv file:
    # savesales(producer_agent[0].sumcarset)
    # savesales(producer_agent[1].sumcarset)
    # savesales(producer_agent[2].sumcarset)
    # savesales(producer_agent[3].sumcarset)
    # savesales(producer_agent[4].sumcarset)
    # savesales(producer_agent[5].sumcarset)

    hol = []
    for idc in range(ncons):
        hol.append(consumer_agent[idc].holdl)
    buyfreq = []
    #For each consumer, keep track of the year they make a (re)purchase in the list a:consumer_agent[i].holdl   
    #find the difference between consequtive elements in the repurchase year list (consumer.holdl)
    #using [x - a[i - 1] for i, x in enumerate(a)][1:], where a is the original list
    for idc in range(ncons):
        a = consumer_agent[idc].holdl
        if len (consumer_agent[idc].holdl) > 1 :
            # repch stores the gaps between different purchases of a consumer, meaning purchase years in the list [0,2,14] turns to [2,12]
            consumer_agent[idc].repch = [x - a[i - 1] for i, x in enumerate(a)][1:] = [x - a[i - 1] for i, x in enumerate(a)][1:]
            #find the mean between diff repch gaps
            buyfreq.append(mean(consumer_agent[idc].repch))
    print("Average repurchase time: %.2f years" % (mean(buyfreq)))
    
    sala = []
    for i in range(6):
        sala.append(producer_agent[i].sumcarset)
    
    # Import actual sales:
    df1 = pd.read_csv('Realsales.csv', header=None)
    realsales = df1.values.tolist()
    
    # Calculate rmse
    sqerror = []
    for idp in range(6):
        # Only calculate for years after 2006:
        for idy in range(7,17):
            sqerror.append((producer_agent[idp].sumcarset[idy] - realsales[idp][idy]/1000)**2)
    mse = sum(sqerror)/len(sqerror)
    rmse = math.sqrt(mse)
    print("The RMSE is %.2f thousand vehicles" % rmse)
        
    print("Simulation time: %.3f seconds" % (time.time() - start_time))
    
    objfun = rmse + 50*(7-mean(buyfreq))**2
    print("Objective function value: %.2f \n" % objfun)
    return objfun

###############################################  Set parameters and run #####################################################
# Now, actually run the program
amean = -1.55      # Was -1.5
astd = 0.508        # Was 0.5
amin = -2      # Was -2
amax = 0        # Was 0
randutstd = 9   # Was 7
currutconst = 24.7    # Was 30
params = [amean,astd,amin,amax,randutstd,currutconst]
if __name__ == "__main__":
    obj = main(params)

############################################### Run 100 times ############################################
# def run100(params):
#     global iter,fevals
#     objfuns = []
#     for i in range(100):
#         # Evaluate main function and add result to objfuns list
#         objfuns.append(main(params))
#     avg100 = sum(objfuns)/len(objfuns)
#     fevals += 1
#     print("(Iter %i; Feval %i) Average over 100 sims: %.2f \n" % (iter,fevals,avg100))
#     return avg100
# ############################################### Optimize parameters ######################################
# from scipy.optimize import minimize
# # This starting point is the result of a 300-run, 100-MC NM optimization:[-1.61216494e+00  4.90594572e-01 -2.08432385e+00  9.76773190e-05 8.74987757e+00  2.44480477e+01]
# x0 = [-1.61,0.491,-2.08,0,8.75,24.4]

# b1 = (-9,-0.5) 
# b2= (0.1, 6)
# b3 = (-15,-0.5)
# b4 = (-4,0)
# b5 = (2,20)
# b6 = (10,50)
# bnds = (b1,b2,b3,b4,b5,b6)

# history = []
# iter = 1
# fevals = 0
# def callback(x):
#     global iter
#     # fobj = run100(x)
#     # history.append(fobj)
#     iter += 1
#     print(iter)
# optparams = minimize(run100, x0, method='Nelder-Mead',bounds=bnds,callback=callback, options={'maxiter': 300,'disp': True}) 
# print(optparams.x)