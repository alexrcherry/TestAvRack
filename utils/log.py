import logging
import csv

def init_logger(log_name, log_file_path, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file_path)
    handler.setFormatter(formatter)

    logger = logging.getLogger(log_name)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger

def init_csv_write(csv_headers, csv_file_path):
    with open(csv_file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)

def csv_write(csv_data, csv_file_path):
    with open(csv_file_path, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(csv_data)


