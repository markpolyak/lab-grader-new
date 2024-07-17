import logging

Log = logging.getLogger()
Log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:[%(levelname)s] - %(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

file_handler = logging.FileHandler('grader.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

Log.addHandler(handler)
Log.addHandler(file_handler)
