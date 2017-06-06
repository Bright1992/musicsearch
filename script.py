from musicsearch.import_data import do_import_data
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

path = os.path.join(BASE_DIR, "..", "..", "data")

do_import_data(path)
