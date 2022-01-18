import mcl_micro_lib

#%%
Micro1 = mcl_micro_lib.MadMicroDrive()

#%%
info = Micro1.get_information()
print(info)

#%%
axis_info = Micro1.get_axis_info()
print(axis_info)

#%%
Micro1.get_serial()

#%%
Micro1.get_firmware()

#%%
encoder_info = Micro1.encoder_present()
print(encoder_info)

#%%
position = Micro1.read_encoders()
print(position)

#%%
#read position from step

position_x = Micro1.read_position(axis=1)
print(position_x)

#%%
position_y = Micro1.read_position(axis=2)
print(position_y)

#%%
status = Micro1.get_status()
print(status)

#%%
#only works if there are encoders
Micro1.set_origin()
print(status)

#%%
rel_coordinates = [0.1,0,0] # in mm
Micro1.move_R(rel_coordinates = rel_coordinates, velocity = 0.01, rounding = 1)

#%%
Micro1.mcl_close()

#%%
