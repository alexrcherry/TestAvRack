from contextlib import contextmanager
import numpy as np
import nidaqmx as ni
import queue
from .log import csv_write
from datetime import datetime

# for analog input thread
def ai_read(run, queue, reader, output, task, logger, csv_file_path, queue_cont, logger_cont, csv_file_path_cont):
	global pressure_output 
	#global cont
	while True:
		reader.read_many_sample(output, number_of_samples_per_channel=100)
		output = np.around(output, 6)
		print('.....................................')
		print(np.shape(output))
		print('.....................................')
		#cont = output[4]
		#lox = output[5]
		
		out_psi = pressure_output = np.around(voltz_to_psi(output),6)
		queue.put((out_psi))
		to_log(out_psi, logger)
		to_csv(out_psi, csv_file_path)
		# check_cont(queue_cont, task, logger_cont, csv_file_path_cont)

		if not (run()):  # to kill the thread
			print('AI input thread closed!')
			break


def voltz_to_psi(output):

	#split up analog voltage output data for each pressure transducer, based on hardware setup
	he_post_out_raw = output[0]	 # ai0: helium pressure, 0-5000psi
	he_pre_out_raw = output[1] 	# ai1: helium supply pressure, 0-7500psi
	pnu_post_out_raw = output[2]  # ai2: pneumatics pressure, 0-200psi
	pnu_pre_out_raw = output[3]	 # ai3: pneumatics supply pressure, 0-3000psi
	cont_voltage = output[4]
	lox_voltage = output[5]

	he_post_out_psi = 37.5*he_post_out_raw-75
	he_pre_out_psi = 36.2*he_pre_out_raw-68.6
	pnu_post_out_psi = 36.2*pnu_post_out_raw-68.6
	pnu_pre_out_psi = 36.2*pnu_pre_out_raw-68.6

	out_psi = np.vstack((he_post_out_psi, he_pre_out_psi, pnu_post_out_psi, pnu_pre_out_psi, cont_voltage, lox_voltage))
	return out_psi

def check_cont(queue, task, logger, csv_fp):
	cont = task.in_stream.open_current_loop_chans_exist()
	if cont == False:
		out = 'GOOD CONTINUITY'
	else:
		out = 'NO CONTINUITY'
	queue.put(out)
	logger.info(out)
	csv_write(out, csv_fp)

def to_log(output, logger):
	data = output
	he_post_msg = 'ERROR: Helium Pressure[psi]: '
	he_pre_msg = 'ERROR: Helium Supply Pressure[psi]: '
	pnu_post_msg = 'ERROR: Pneumatics Pressure[psi]: ]'
	pnu_pre_msg = 'ERROR: Pneumatics Supply Pressure[psi]: '

	if(0.0 >= data[0].any() >= 5000.0):
		logger.error(he_post_msg + str(data[0]))
	if(0.0 >= data[1].any() >= 7500.0):
		logger.error(he_pre_msg + str(data[1]))
	if(0.0 >= data[2].any() >= 200.0):
		logger.error(pnu_post_msg + str(data[2]))
	if(0.0 >= data[3].any() >= 3000.0):
		logger.error(pnu_pre_msg + str(data[3]))

def to_csv(output, csv_file_path):
	data = output
	timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	out_he = [timestamp,' -- HE PRESS -- ', data[0,1], ' -- HE SUPPLY -- ', data[1,1]]
	out_pnu = [timestamp,' -- PNU PRESS -- ', data[2,1], ' -- PNU SUPPLY -- ', data[3,1]]
	csv_write(out_he, csv_file_path)
	csv_write(out_pnu, csv_file_path)


