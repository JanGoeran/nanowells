import cv2
import pandas as pd
import numpy as np
from zaber_motion import Library
from zaber_motion.ascii import Connection
from zaber_motion import Units
import time
import alignment

def drive2uv(u,v, params):
    """Takes the u and v coordinate of a location and drives the stage to that coordinate.
    Takes params dictionary that is generated using the get_alignment function.
    """

    tran = params['t']
    angle = params['r']
    zoom = params['zoom']
    base = params['base']
    slope = params['slope_uv']

    puv = np.array([u, v])
    x = alignment.uv2xy(puv, tran, angle, zoom)[0]
    y = alignment.uv2xy(puv, tran, angle, zoom)[1]
    z = alignment.uv2z(v, base, slope)

    Library.enable_device_db_store()

    with Connection.open_serial_port("COM4") as connection:
        device_list = connection.detect_devices()
        device_x = device_list[2]
        axis_x = device_x.get_axis(1)
        device_y = device_list[1]
        axis_y = device_y.get_axis(1)
        device_r = device_list[3]
        axis_r = device_r.get_axis(1)
        device_z = device_list[4]
        axis_z = device_z.get_axis(1)

        axis_x.move_absolute(x, Units.LENGTH_MILLIMETRES)
        axis_y.move_absolute(y, Units.LENGTH_MILLIMETRES)
        axis_z.move_absolute(z, Units.LENGTH_MILLIMETRES)

        print('uv position = ' + str((u,v)))


def read_all():
    """Reads current x,y,z,r position from zaber stage."""
    Library.enable_device_db_store()

    with Connection.open_serial_port("COM4") as connection:
        device_list = connection.detect_devices()
        print("Found {} devices".format(len(device_list)))

        device_x = device_list[2]
        axis_x = device_x.get_axis(1)
        device_y = device_list[1]
        axis_y = device_y.get_axis(1)
        device_r = device_list[3]
        axis_r = device_r.get_axis(1)
        device_z = device_list[4]
        axis_z = device_z.get_axis(1)

        x = axis_x.get_position(unit=Units.LENGTH_MILLIMETRES)
        y = axis_y.get_position(unit=Units.LENGTH_MILLIMETRES)
        r = axis_r.get_position(unit=Units.ANGLE_DEGREES)
        z = axis_z.get_position(unit=Units.LENGTH_MILLIMETRES)

    return x, y, r, z


def zaber_position(path='C:/Users/Jakob Seidl/Desktop/capture/alignment.csv'):
    """Function used to define two alignment points on the sample.
    1. Wait until video feed to the microscope camera is started.
    2. Drive to position P1, focus, and press 'z'.
    3. Drive to position P2, focus, and press 'x'.
    4. press 'q' to quit and save the stage coordinates into a local file.
    """
    w = 1920
    h = 1080
    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    df = pd.DataFrame(columns=['rows', 'P1', 'P2'])
    df['rows'] = ['x', 'y', 'r', 'z']

    while (True):
        ret, frame = vid.read()
        frame = cv2.resize(frame, (w // 2, h // 2))
        k = cv2.waitKey(30)
        h, w, _ = frame.shape

        cv2.line(frame, (w//4,0), (w//4,h), (0, 255, 0), thickness=2, lineType=8)
        cv2.line(frame, (0, h//4), (w, h//4), (0, 255, 0), thickness=2, lineType=8)

        cv2.imshow('frame', frame)

        #press q to quit
        if k & 0xFF == ord('q'):
            df.to_csv(path)
            break

        #if k % 256 == 32:
        #    print('space')

        #press z on keyboard
        if k % 256 == 122:
            x, y, r, z = read_all()
            df['P1'] = [x, y, r, z]
            print('updated P1')
            print(' x = ' + str(x) + '\n y = ' + str(y) + '\n', 'r = ' + str(r) + '\n', 'z = ' + str(z) + '\n')

        #press x on keyboard
        if k % 256 == 120:
            x, y, r, z = read_all()
            df['P2'] = [x, y, r, z]
            print('updated P2')
            print(' x = ' + str(x) + '\n y = ' + str(y) + '\n', 'r = ' + str(r) + '\n', 'z = ' + str(z) + '\n')

    vid.release()
    cv2.destroyAllWindows()


def get_linear_focus_correction(path='C:/Users/Jakob Seidl/Desktop/capture/alignment.csv'):
    """Calculates parameters for linear focus correction from alignment file."""
    df = pd.read_csv(path)
    x1, y1, r1, z1 = df['P1']
    x2, y2, r2, z2 = df['P2']

    z0 = z1
    slope = (z2-z1)/(y2-y1)

    return z0, slope

def look_and_image(file_name='snap', path='C:/Users/Jakob Seidl/Desktop/capture'):
    """Snap images by pressing space button.
    :param path: path to where you want the image saved.
    :return:
    """

    w = 1920
    h = 1080
    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    image_count = 0

    while True:
        ret, frame = vid.read()
        cv2.imshow('frame', frame)
        frame = cv2.resize(frame, (w // 2, h // 2))
        k = cv2.waitKey(30)

        # press q to quit
        if k & 0xFF == ord('q'):
            break

        # press space to take a picture
        if k % 256 == 32:
            save_as = path + '/' + file_name + '_' + str(image_count) + '.jpg'
            cv2.imwrite(save_as, frame)
            print(f'took image, saved at {save_as}.')
            image_count += 1

    vid.release()
    cv2.destroyAllWindows()

def image_fields(params, target_list=[[0,v] for v in range(24)]):
    """Images all locations in target list.
    :param params: dictionary generated by get_alignment function.
    :param target_list: uv coordinates in mm of locations that should be imaged.
    :return: 0
    """
    Library.enable_device_db_store()
    w = 1920
    h = 1080
    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    ret, frame = vid.read()
    frame = cv2.resize(frame, (w // 2, h // 2))
    time.sleep(1)

    with Connection.open_serial_port("COM4") as connection:
        device_list = connection.detect_devices()
        print("Found {} devices".format(len(device_list)))

        device_x = device_list[2]
        axis_x = device_x.get_axis(1)
        device_y = device_list[1]
        axis_y = device_y.get_axis(1)
        device_r = device_list[3]
        axis_r = device_r.get_axis(1)
        device_z = device_list[4]
        axis_z = device_z.get_axis(1)

        for i, target in enumerate(target_list):
            u = target[0]
            v = target[1]

            tran = params['t']
            angle = params['r']
            zoom = params['zoom']
            base = params['base']
            slope = params['slope_uv']

            puv = np.array([u, v])
            x = alignment.uv2xy(puv, tran, angle, zoom)[0]
            y = alignment.uv2xy(puv, tran, angle, zoom)[1]
            z = alignment.uv2z(v, base, slope)

            axis_x.move_absolute(x, Units.LENGTH_MILLIMETRES)
            axis_y.move_absolute(y, Units.LENGTH_MILLIMETRES)
            axis_z.move_absolute(z, Units.LENGTH_MILLIMETRES)
            time.sleep(0.5)

            ret, frame = vid.read()
            frame = cv2.resize(frame, (w // 2, h // 2))
            time.sleep(1)
            cv2.imshow('frame', frame)
            cv2.imwrite('C:/Users/Jakob Seidl/Desktop/capture/devices/device_' + str(24-i) + '.jpg', frame)
            k = cv2.waitKey(1000)

    return 0

if __name__ == '__main__':
    #position()
    #print(read_all())
    #params = alignment.get_alignment(v2 = 2.3, getslope=True)
    #print(get_linear_focus_correction())
    #drive2uv(0, 2.3, params)
    #look_and_image()
    #image_fields(params)
    print('done')