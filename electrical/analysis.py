import pandas as pd
import numpy as np
import easygui
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from scipy import stats


def get_live_devices(df, cutoff=5e-6):
    device_list = df.device.unique()
    live_list = []
    for device in device_list:
        df1 = df[df['device'] == device]
        if df1['G'].max() > cutoff:
            live_list.append(device)
    return(live_list)


def get_dead_devices(df, cutoff=5e-6):
    device_list = df.device.unique()
    dead_list = []
    for device in device_list:
        df1 = df[df['device'] == device]
        if df1['G'].max() < cutoff:
            dead_list.append(device)
    return dead_list

def plot_all(df,
             title='title',
             cutoff=1E-5,
             plot_repeat=False,
             save=False,
             basepath='G:/Shared drives/Nanoelectronics Team Drive/Data/2021/Marta/test_folder'):

    device_list = df.device.unique()
    dfa = get_G_average(df)

    liveDevices = get_live_devices(df, cutoff=cutoff)
    deadDevices = get_dead_devices(df, cutoff=cutoff)

    line_styles = ['-', '--', '-.', ':']
    plt.style.use('seaborn')
    centimetre = 1 / 2.54
    color = iter(cm.tab20(np.linspace(0, 1, len(liveDevices)))) #change 46 to i

    fig, ax1 = plt.subplots(figsize=(30*centimetre, 20*centimetre))
    plt.subplots_adjust(left=None, bottom=None, right=0.8, top=None, wspace=None, hspace=None)

    G_mean = dfa.G[dfa.device.isin(liveDevices)].mean()
    G_std = dfa.G_std[dfa.device.isin(liveDevices)].mean()
    add_text = 'G_mean_live = ' + '{:.2E}'.format(G_mean) + '\n' + 'G_mean_std_live = ' + '{:.2E}'.format(G_std)
    ax1.text(1.03, 0.0, add_text, transform=ax1.transAxes)

    if plot_repeat == True:
        xlabel = 'repeat'
        xtype = 'repeat'
    else:
        xlabel = 'time (s)'
        xtype = 'time'

    ax1.set_title(title)
    ax1.set(xlabel = xlabel, ylabel='G (S)')
    for i, device in enumerate(liveDevices):
        df1 = df[df['device'] == device]
        ax1.plot(df1[xtype], df1['G'], color=next(color), label=device, linestyle=line_styles[i % 4 - 1])
        ax1.legend(ncol=2, loc=9, bbox_to_anchor=(1.13, 1.0))

    for device in deadDevices:
        df1 = df[df['device'] == device]
        ax1.plot(df1[xtype], df1['G'], color= 'gray', label=device, linestyle='-')
        ax1.legend(ncol=2, loc=9, bbox_to_anchor=(1.13, 1.0))

    if save:
        save_at = basepath + '/summary.png'
        fig.savefig(save_at)
    return


def get_G_average(df):
    device_list = df.device.unique()
    ResultsDF = pd.DataFrame()
    for device in device_list:
        df1 = df[df['device'] == device]
        #print(df1)
        ResultsDF = ResultsDF.append({'device': device, 'G': df1.G.mean(), 'G_std': df1.G.std(),
                                      'G_sterr': df1.G.sem()}, ignore_index=True)
    return ResultsDF

def plot_IV(df, device=None, ID=None, repeat=None):
    '''Supply either an ID or a device number with the repeat number'''
    fig, ax1 = plt.subplots()

    if repeat is None and ID is None:
        print('specify device and repeat OR ID.')
    if ID is not None:
        df1 = df[df['ID'] == ID]
        x = list(map(float, df1['V_SD'].tolist()[0].replace('[', '').replace(']', '').split(',')))
        y = list(map(float, df1['I_SD'].tolist()[0].replace('[', '').replace(']', '').split(',')))
        ax1.plot(x, y)
    if repeat is not None and device is not None:
        df1 = df.loc[(df['device'] == device) & (df['repeat'] == repeat)]
        x = list(map(float, df1['V_SD'].tolist()[0].replace('[', '').replace(']', '').split(',')))
        y = list(map(float, df1['I_SD'].tolist()[0].replace('[', '').replace(']', '').split(',')))
        ax1.plot(x, y)

def check_values(df,
                 R_ev=1e3,
                 device_type='top',
                 tol=0.1,
                 rel_std=0.005,
                 R_zero_tol=1e6,
                 zero_std_tol=1e6,
                 save=False,
                 basePath='G:/Shared drives/Nanoelectronics Team Drive/Data/2021/Marta/test'):

    completeReport = ('R expected: ' + str(R_ev) + 'Ohm \n' +
                      'type: ' + str(device_type) + '\n' +
                      'tol = ' + str(tol) + '\n' +
                      'rel std = ' + str(rel_std) + '\n' +
                      'R_zero_tol = ' + str(R_zero_tol) + '\n' +
                      'base path = ' + basePath + '\n \n')

    ev = 1/(R_ev+100) #100 ohm internal resistance of multiplexer
    zero_tol = 1/R_zero_tol

    topDevices = [i for i in range(1, 12 + 1)] + [i for i in range(24, 34 + 1)]
    bottomDevices = [i for i in range(13, 23 + 1)] + [i for i in range(35, 46 + 1)]
    allDevices = topDevices + bottomDevices

    dfa = get_G_average(df)

    G_OK = []
    noise_OK = []
    G_bad = []
    noise_bad = []

    if device_type == 'top':
        liveDevices = topDevices
        deadDevices = bottomDevices
    elif device_type == 'bottom':
        liveDevices = bottomDevices
        deadDevices = topDevices
    elif device_type == 'all':
        liveDevices = allDevices
        deadDevices = []

    # check live devices
    for device in liveDevices:
        G = float(dfa.G.loc[dfa.device == device])
        std = float(dfa.G_std.loc[dfa.device == device])
        if (G*(1+tol) > ev) & (G*(1-tol) < ev):
            G_OK.append(device)
        else:
            G_bad.append(device)
        if (std/G < rel_std):
            noise_OK.append(device)
        else:
            noise_bad.append(device)

    G_a_live = dfa.G[dfa.device.isin(G_OK)].mean()
    STD_a_live = dfa.G_std[dfa.device.isin(G_OK)].mean()

    report_c = ('G average of devices within range =  ' + str(G_a_live) + ' S \n' +
              'STD average of devices within range =  ' + str(STD_a_live) + ' S \n \n' +
              'Report for connected devices = ' + str(liveDevices) + '\n' 
              'G within range for devices: ' + str(G_OK) + '\n' 
              'G out of range for devices: ' + str(G_bad) + '\n'
              'noise within range for devices: ' + str(noise_OK) + '\n'
              'noise out of range range for devices: ' + str(noise_bad) + '\n \n'
          )
    #print(report_c)
    #check disconnected devices
    completeReport = completeReport + report_c

    G_OK = []
    noise_OK = []
    G_bad = []
    noise_bad = []
    for device in deadDevices:
        G = float(dfa.G.loc[dfa.device == device])
        std = float(dfa.G_std.loc[dfa.device == device])
        if (G < zero_tol) & (G*tol < zero_tol):
            G_OK.append(device)
        else:
            G_bad.append(device)
        if (std/G < zero_std_tol):
            noise_OK.append(device)
        else:
            noise_bad.append(device)

    if device_type != 'all':
        G_a_live = dfa.G[dfa.device.isin(G_OK)].mean()
        STD_a_live = dfa.G_std[dfa.device.isin(G_OK)].mean()
        #print('G average of disconnected devices within range =  ' + str(G_a_live) + ' S')
        #print('STD average of disconnected devices within range =  ' + str(STD_a_live) + ' S')

        report_d = ('G average of disconnected devices within range =  ' + str(G_a_live) + ' S \n'+
                    'STD average of disconnected devices within range =  ' + str(STD_a_live) + ' S \n \n' +
                    'Report for disconnected devices = ' + str(deadDevices) + '\n' 
                    'G within range for devices: ' + str(G_OK) + '\n'
                    'G out of range for devices: ' + str(G_bad) + '\n'
                    'noise within range for devices: ' + str(noise_OK) + '\n'
                    'noise out of range range for devices: ' + str(noise_bad) + '\n'
              )
        completeReport = completeReport + report_d

    print(completeReport)

    if save == True:
        dfa.to_csv(basePath + '/dfa.csv')
        print('saved dfa')

        with open(basePath + '/testchip_summary.txt', 'w') as f:
            f.write(completeReport)

    return dfa

def check_noise(df, basePath = 'G:/Shared drives/Nanoelectronics Team Drive/Data/2021/Marta/test'):
    dfa = get_G_average(df)
    print(dfa.G_std.mean())
    #return (dfa.G_std)

def plot_all_live_add_legend(ax1):
    ax1.legend(ncol=2, loc=9, bbox_to_anchor=(1.13, 1.0))
    print('added legend')

def plot_all_live(df, deviceList, fig, ax1, title='sample name', cutoff=-10, label=False):

        #legend = False
        #first_legend = True
        #if deviceList == list(df.device) and first_legend == True:
            #legend = True

        #dfa = get_G_average(df)

        liveDevices = get_live_devices(df, cutoff=cutoff)
        deadDevices = get_dead_devices(df, cutoff=cutoff)

        linestyles = ['-', '--', '-.', ':']
        color = iter(cm.tab20(np.linspace(0, 1, len(liveDevices))))  # change 46 to i

        #G_mean = dfa.G[dfa.device.isin(liveDevices)].mean()
        #G_std = dfa.G_std[dfa.device.isin(liveDevices)].mean()
        #add_text = 'G_mean_live = ' + '{:.2E}'.format(G_mean) + '\n' + 'G_mean_std_live = ' + '{:.2E}'.format(G_std)
        #t1 = ax1.text(1.03, 0.0, add_text, transform=ax1.transAxes)
        #t1.set_text(str(add_text))

        ax1.set_title(title)
        ax1.set(xlabel='time (s)', ylabel='G (S)')

        for i, device in enumerate(liveDevices):
            df1 = df[df['device'] == device]
            if label == True:
                ax1.plot(df1['time'], df1['G'], color=next(color), label=device, linestyle=linestyles[i % 4 - 1])
            if label == False:
                ax1.plot(df1['time'], df1['G'], color=next(color), linestyle=linestyles[i % 4 - 1])


        for device in deadDevices:
            df1 = df[df['device'] == device]
            if label == True:
                ax1.plot(df1['time'], df1['G'], color='gray', label=device, linestyle='-')
            if label == False:
                ax1.plot(df1['time'], df1['G'], color='gray', linestyle='-')

        legend = False

        plt.pause(0.01)  # needed for live plotting to work
        return legend


def save_for_manual_plot(df, path, save=True):
    device_list = df.device.unique()
    df_plot = pd.DataFrame()
    df_plot['repeat'] = list(df.repeat[df['device'] == device_list[0]])
    for device in device_list:
        S_time = df.time[df['device'] == device]
        S_G = df.G[df['device'] == device]
        df_plot['time_device' + str(device)] = list(S_time)
        df_plot['G_device' + str(device)] = list(S_G)
    if save == True:
        df_plot.to_csv(path + '/for_manual_plotting.csv')
    return df_plot


def basic_stat_2seg(df, event_repeat, plot_all_bool = False, cutoff = 0):

    plt.style.use('seaborn')
    centimeter = 1/2.54
    fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(ncols=2, nrows=2, figsize=(20*centimeter, 20*centimeter))
    plt.subplots_adjust(left=None, bottom=0.2, right=None, top=None, wspace=None, hspace=None)
    ax1.set_title('individual devices')
    ax2.set_title('all devices box plot')
    ax3.set_title('relative change distribution')
    ax4.set_title('absolute change distribution')

    #plot all
    if plot_all_bool == True:
        plot_all(df)

    #drop dead devices
    dead_list = get_dead_devices(df, cutoff=cutoff)
    live_list = get_live_devices(df, cutoff=cutoff)
    print('dead devices are: ' + str(dead_list))
    print('live devices are: ' + str(live_list))

    df = df.loc[(df.device.isin(live_list))]

    #split at event repead
    df_before = df[df.repeat < event_repeat]
    df_after = df[df.repeat > event_repeat]

    #get averages
    df_G_before_av = get_G_average(df_before)
    df_G_after_av = get_G_average(df_after)
    df_for_box1 = pd.DataFrame({'before': list(df_G_before_av.G), 'after': list(df_G_after_av.G)})

    #paired ttest for G
    tt = stats.ttest_rel(df_G_before_av.G, df_G_after_av.G)
    print(tt)

    #error bar plot all
    for device in live_list:
        x = ['before', 'after']
        y = [float(df_G_before_av.G[df_G_before_av.device == device]), float(df_G_after_av.G[df_G_after_av.device == device])]
        yerr = [float(df_G_before_av.G_sterr[df_G_before_av.device == device]), float(df_G_after_av.G_sterr[df_G_after_av.device == device])]
        ax1.errorbar(x, y, yerr=yerr)

    ax1.set_ylabel('G (S)')

    #boxplot
    x = ['before', 'after']
    ax2.boxplot(df_for_box1, showmeans=True)
    ax2.set_xticklabels(labels=x)
    ax2.set_ylabel('G (S)')

    #relative hist
    rel_diff = (df_G_after_av.G - df_G_before_av.G)/df_G_before_av.G
    ax3.hist(rel_diff, fc='lightcoral', ec='black')
    ax3.set_xlabel(r'$(G_{after}-G_{after})/G_{before}$')
    ax3.set_ylabel('number of devices')
    ax3.axvline(rel_diff.mean(), color='k', linestyle='dashed', linewidth=1)

    #absolute hist
    abs_diff = (df_G_after_av.G - df_G_before_av.G)
    ax4.hist(abs_diff, fc='cornflowerblue', ec='black')
    ax4.set_xlabel(r'$G_{after}-G_{after}$')
    ax4.set_ylabel('number of devices')
    ax4.axvline(abs_diff.mean(), color='k', linestyle='dashed', linewidth=1)

    add_text = ('Dead devices were removed. Dead device list: ' + str(dead_list) + '\n' +
                'Total live devices: ' + str(len(live_list)) + '\n' +
                'Paired T-test for live devices: test statistic = ' + '{:.2f}'.format(tt[0]) +
                ' p-value =' + '{:.7f}'.format(tt[1]))
    ax1.text(-0.2, -1.8, add_text, transform=ax1.transAxes)



if __name__ == "__main__":
    df = pd.read_csv('G:/Shared drives/Nanoelectronics Team Drive/Data/2021/Marta/simulation/simulation.csv')
    plot_all(df, cutoff=0.01)
    basic_stat_2seg(df, event_repeat=20,cutoff=0.01)
    plot_IV(df,device=1, repeat=5)
    get_dead_devices(df, cutoff=0.01)
    print('done')


