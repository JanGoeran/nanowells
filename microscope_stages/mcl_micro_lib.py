import atexit
import numpy as np
import ctypes

#Code is set up to work with one Microdrive only.

# The linear actuators have a step resolution of 1.524 microns and are operated in a divide by 16 microstep mode.
# The minimum step of the MicroStage is 95.25 nm. MicroStage stages enabled with the encoder option have a
# measurement resolution of 50 nm.

# Error Codes
#
# MCL_SUCCESS 0	Task has been completed successfully.
# MCL_GENERAL_ERROR	-1 These errors generally occur due to an internal sanity check failing.
# MCL_DEV_ERROR	-2 A problem occurred when transferring data to the Micro-Drive.
# It is likely that the Micro-Drive will have to be power cycled to correct these errors.
# MCL_DEV_NOT_ATTACHED -3 The Micro-Drive cannot complete the task because it is not attached.
# MCL_USAGE_ERROR -4 Using a function from the library which the Micro-Drive does not support causes these errors.
# MCL_DEV_NOT_READY -5 The Micro-Drive is currently completing or waiting to complete another task.
# MCL_ARGUMENT_ERROR -6 An argument is out of range or a required pointer is equal to NULL.
# MCL_INVALID_AXIS -7 Attempting an operation on an axis that does not exist in the Micro-Drive.
# MCL_INVALID_HANDLE -8 The handle is not valid. Or at least is not valid in this instance of the DLL.

class MadMicroDrive:

    def __init__(self):
        # provide valid path to Madlib.dll. Madlib.h and Madlib.lib should also be in the same folder
        path_to_dll = 'C:/Program Files/Mad City Labs/MicroDrive/MicroDrive.dll'
        self.madlib = ctypes.cdll.LoadLibrary(path_to_dll)
        self.handler = self.mcl_start()
        atexit.register(self.mcl_close)

        #position
        self.currentPositionByMove = np.array([0,0,0])
        self.currentPositionByRead = np.array([0,0,0])

        #pointers
        self.encoderRes = ctypes.c_double()
        self.encoderRes_pointer = ctypes.pointer(self.encoderRes)
        self.stepSize = ctypes.c_double()
        self.stepSize_pointer = ctypes.pointer(self.stepSize)
        self.maxVelocity = ctypes.c_double()
        self.maxVelocity_pointer = ctypes.pointer(self.maxVelocity)
        self.maxVelocityTwoAxis = ctypes.c_double()
        self.maxVelocityTwoAxis_pointer = ctypes.pointer(self.maxVelocityTwoAxis)
        self.maxVelocityThreeAxis = ctypes.c_double()
        self.maxVelocityThreeAxis_pointer = ctypes.pointer(self.maxVelocityThreeAxis)
        self.minVelocity = ctypes.c_double()
        self.minVelocity_pointer = ctypes.pointer(self.minVelocity)

        self.firmwareVersion = ctypes.c_short()
        self.firmwareVersion_pointer = ctypes.pointer(self.firmwareVersion)
        self.firmwareProfile = ctypes.c_short()
        self.firmwareProfile_pointer = ctypes.pointer(self.firmwareProfile)

        self.encoderBM = ctypes.c_ubyte()
        self.encoderBM_pointer = ctypes.pointer(self.encoderBM)

        self.axisBM = ctypes.c_ubyte()
        self.axisBM_pointer = ctypes.pointer(self.axisBM)

        self.status = ctypes.c_ushort()
        self.status_pointer = ctypes.pointer(self.status)
        self.isMoving = ctypes.c_int()
        self.isMoving_pointer = ctypes.pointer(self.isMoving)
        self.xSteps = ctypes.c_int()
        self.xSteps_pointer = ctypes.pointer(self.xSteps)
        self.ySteps = ctypes.c_int()
        self.ySteps_pointer = ctypes.pointer(self.ySteps)

        #for encoder
        self.e1 = ctypes.c_double()
        self.e1_pointer = ctypes.pointer(self.e1)
        self.e2 = ctypes.c_double()
        self.e2_pointer = ctypes.pointer(self.e2)
        self.e3 = ctypes.c_double()
        self.e3_pointer = ctypes.pointer(self.e3)
        self.e4 = ctypes.c_double()
        self.e4_pointer = ctypes.pointer(self.e4)

    # int MCL_InitHandle()
    def mcl_start(self):
        """
        Requests control of a single Mad City Labs Micro-Drive. Is called in initialize
        """
        mcl_init_handle = self.madlib['MCL_InitHandle']

        mcl_init_handle.restype = ctypes.c_int
        handler = mcl_init_handle()
        if (handler == 0):
            print("MCL init error")
            return -1
        return handler

    # int MCL_MDInformation(
    #     double * encoderResolution,
    #     double * stepSize,
    #     double * maxVelocity,
    #     double * maxVelocityTwoAxis,
    #     double * maxVelocityThreeAxis,
    #     double * minVelocity,
    #     int handle)
    def get_information(self):
        """Gather Information about the resolution and speed of the Micro-Drive."""

        mcl_get_info = self.madlib['MCL_MDInformation']
        mcl_get_info.restype = ctypes.c_int
        mcl_get_info(self.encoderRes_pointer, self.stepSize_pointer, self.maxVelocity_pointer,
                     self.maxVelocityTwoAxis_pointer, self.maxVelocityThreeAxis_pointer,
                     self.minVelocity_pointer, ctypes.c_int(self.handler))
        info = [self.encoderRes.value, self.stepSize.value, self.maxVelocity.value,
                     self.maxVelocityTwoAxis.value, self.maxVelocityThreeAxis.value,
                     self.minVelocity.value]
        forprint = ['Encoder res (um): ', 'step: ', 'max velocity M1: ', 'max velocity M2: ', 'max velocity M3: ',
                    'min velocity: ']

        for i in range(len(info)):
            print(forprint[i] + str(info[i]))

        return info

    #int MCL_MDEncodersPresent(unsigned char* encoderBitmap, int handle)
    def encoder_present(self):
        """Determine which encoders are present in the Micro-Drive."""

        mcl_encoder_present = self.madlib['MCL_MDEncodersPresent']
        mcl_encoder_present.restype = ctypes.c_int
        mcl_encoder_present(self.encoderBM_pointer, ctypes.c_int(self.handler))

        l = [d for d in str(self.encoderBM.value)]
        l.reverse()
        Encoders = ['Encoder 1: ', 'Encoder 2: ', 'Encoder 3: ', 'Encoder 4: ']
        for i in range(4):
            print(Encoders[i] + l[i])

        return self.encoderBM.value

    #int MCL_MDStatus(unsigned short* status, int handle)
    def get_status(self):
        """Reads the limit switches."""

        mcl_get_status = self.madlib['MCL_MDStatus']
        mcl_get_status.restype = ctypes.c_int
        mcl_get_status(self.status_pointer, ctypes.c_int(self.handler))

        l = [d for d in str(self.status.value)]
        l.reverse()

        status = ['M1 Reverse Limit Switch: ', 'M1 Forward Limit Switch: ', 'M2 Reverse Limit Switch: ',
                  'M2 Forward Limit Switch: ', 'M3 Reverse Limit Switch: ', 'M3 Forward Limit Switch: ',
                  'Success/Failure!: ']

        for i in range(7):
            print(status[i] + l[i])

        return self.status.value


    #int MCL_MDStop(unsigned short* status, int handle)
    def stop_move(self):
        """Stops the stage from moving."""

        mcl_get_status = self.madlib['MCL_MDStop']
        mcl_get_status.restype = ctypes.c_int
        mcl_get_status(self.status_pointer, ctypes.c_int(self.handler))
        return self.status.value

    #int MCL_MicroDriveMoveStatus(int * isMoving, int handle)
    def is_moving(self):
        """
        Queries the device to see if it is moving. This function should be called prior
        to reading the encoders as the encoders should not be read when the stage is in motion.
        """
        mcl_is_moving = self.madlib['MCL_MicroDriveMoveStatus']
        mcl_is_moving.restype = ctypes.c_int
        mcl_is_moving(self.isMoving_pointer, ctypes.c_int(self.handler))
        return self.isMoving.value

    #int MCL_MicroDriveWait(int handle)
    def wait(self):
        """Waits long enough for the previously commanded move to finish."""

        print('start wait')
        mcl_wait = self.madlib['MCL_MicroDriveWait']
        mcl_wait.restype = ctypes.c_int
        mcl_wait(ctypes.c_int(self.handler))
        print('finished wait')

    #int MCL_MDMoveThreeAxesR(int axis1, double velocity1, double distance1, int rounding1, int axis2, double
    # velocity2, double distance2, int rounding2, int axis3, double velocity3, double distance3, int rounding3,
    # int handle)
    def move_R(self, rel_coordinates, velocity = 0.01, rounding = 1):
        """Standard movement function. Acceleration and deceleration ramps are generated for the specified motion.
        In some cases when taking smaller steps the velocity parameter may be coerced to its maximum achievable value.
        The maximum and minimum velocities can be found using MCL_MDInformation.
        The maximum velocity differs depending on how many axes are commaned to move.
        :param rel_coordinates: list with three elements with relative movement in [mm]. Example [0.2,0.1,0]
        :param velocity: velocity of movement.
        :param rounding: 0 - Nearest microstep. 1 - Nearest full step. 2 - Nearest half step.
        """

        mcl_move_three_axesR = self.madlib['MCL_MDMoveThreeAxesR']
        mcl_move_three_axesR.restype = ctypes.c_int
        mcl_move_three_axesR(ctypes.c_int(1), ctypes.c_double(velocity), ctypes.c_double(rel_coordinates[0]), ctypes.c_int(rounding),
                             ctypes.c_int(2), ctypes.c_double(velocity), ctypes.c_double(rel_coordinates[1]), ctypes.c_int(rounding),
                             ctypes.c_int(3), ctypes.c_double(velocity), ctypes.c_double(rel_coordinates[2]), ctypes.c_int(rounding),
                             ctypes.c_int(self.handler))
        self.wait()
        self.currentPositionByMove = self.currentPositionByMove + rel_coordinates
        self.currentPositionByRead = self.currentPositionByRead + np.array(self.read_encoders()+[0])

    #int MCL_MDResetEncoders(unsigned short* status, int handle)
    def set_origin(self):
        """Resetting an encoder makes the current position of the microstage the zero position of the encoder.
        Use  MCL_MDResetEncoders to reset all encoders or  MCL_MDResetEncoder to reset a specifc encoder.
        """

        mcl_reset_encoders = self.madlib['MCL_MDResetEncoders']
        mcl_reset_encoders.restype = ctypes.c_int
        mcl_reset_encoders(self.status_pointer, ctypes.c_int(self.handler))
        self.currentPositionByRead = [0, 0, 0]
        self.currentPositionByMove = [0, 0, 0]

        print('set origin at current position')

    #int MCL_MDReadEncoders(double* e1, double* e2, double *e3, double *e4, int handle)
    def read_encoders(self):
        """Reads all encoders"""

        mcl_read_encoders = self.madlib['MCL_MDReadEncoders']
        mcl_read_encoders.restype = ctypes.c_int
        mcl_read_encoders(self.e1_pointer, self.e2_pointer, self.e3_pointer, self.e4_pointer, ctypes.c_int(self.handler))
        print('position: ' + str([self.e1.value, self.e2.value]))
        return [self.e1.value, self.e2.value]

    #int MCL_MDCurrentPositionM(unsigned int axis, int *microSteps, int handle)
    def read_position(self, axis):
        """Reads the number of microsteps taken since the beginning of the program."""

        mcl_current_position = self.madlib['MCL_MDCurrentPositionM']
        mcl_current_position.restype = ctypes.c_int
        if axis == 1:
            mcl_current_position(ctypes.c_uint(axis), self.xSteps_pointer, ctypes.c_int(self.handler))
            return self.xSteps.value
        if axis == 2:
            mcl_current_position(ctypes.c_uint(axis), self.ySteps_pointer, ctypes.c_int(self.handler))
            return self.ySteps.value
        else:
            print('axis needs to be 1 or 2')

    #void MCL_ReleaseAllHandles()
    def mcl_close(self):
        """Releases control of all Micro-Drives controlled by this instance of the DLL."""
        mcl_release_all = self.madlib['MCL_ReleaseAllHandles']
        mcl_release_all()

    #int  MCL_GetFirmwareVersion(short *version, short *profile, int handle)
    def get_firmware(self):
        """Gives access to the Firmware version and profile information."""
        mcl_get_firmware_version = self.madlib['MCL_GetFirmwareVersion']
        mcl_get_firmware_version.restype = ctypes.c_int
        mcl_get_firmware_version(self.firmwareVersion_pointer, self.firmwareProfile_pointer, ctypes.c_int(self.handler))
        print('version is: ' + str(self.firmwareVersion.value))
        print('profile is: ' + str(self.firmwareProfile.value))
        return [self.firmwareVersion.value, self.firmwareProfile.value]

    #int MCL_GetSerialNumber(int handle)
    def get_serial(self):
        """Returns the serial number of the Micro-Drive.
        This information can be useful if  you need support for your device
        or if you are attempting to tell the difference between two similar Micro-Drives.
        """
        mcl_get_serial = self.madlib['MCL_GetSerialNumber']
        mcl_get_serial.restype = ctypes.c_int
        serial = mcl_get_serial(ctypes.c_int(self.handler))
        print('serial is: ' + str(serial))
        return serial

    #int MCL_GetAxisInfo(unsigned char *axis_bitmap, int handle)
    def get_axis_info(self):
        """Allows the program to query which axes are available."""
        mcl_get_axis_info = self.madlib['MCL_GetAxisInfo']
        mcl_get_axis_info.restype = ctypes.c_int
        mcl_get_axis_info(self.axisBM_pointer, ctypes.c_int(self.handler))

        l = [d for d in str(self.axisBM.value)]
        l.reverse()

        status = ['M1 valid: ', 'M2 valid: ', 'M3 valid: ', 'M4 valid: ', 'M5 valid: ', 'M6 valid: ']

        for i in range(len(status)):
            print(status[i] + l[i])

        return self.status.value

if __name__ == "__main__":

    Micro1 = MadMicroDrive()
    Micro1.mcl_close()

