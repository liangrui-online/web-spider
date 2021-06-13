from spider import get_hospital_list
from dump_and_load import save2excel

hospitals = get_hospital_list()
save2excel(hospitals)
