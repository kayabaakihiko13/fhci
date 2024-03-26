import csv
import requests
import time
import tqdm
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

class RekrutmenBersama(object):
    def __init__(self) -> None:
        self.url_base ='https://rekrutmenbersama2024.fhcibumn.id'
        self.url_job = f'{self.url_base}/job'
        self.url_load_record = f'{self.url_base}/job/loadRecord'
        self.url_get_detail = f'{self.url_base}/job/get_detail_vac'

    def requests_all_job(self, to_csv: bool = False, path_save: str = None):
        session = requests.Session()
        soupjob = BeautifulSoup(session.get(self.url_job).content, 'html.parser')
        csrftoken = soupjob.find('input', dict(name='csrf_fhci'))['value']
        print(csrftoken)
        jobs = session.post(
            self.url_load_record,
            data=dict(csrf_fhci=csrftoken, company='all'),
            verify=False
        )
        print(jobs.status_code)
        if to_csv and path_save:
            self.__parse_to_csv(jobs.json()['data']['result'], path_save)
        else:
            return jobs.json()

    def __parse_to_csv(self, data, path):
        keys = data[0].keys()
        with open(path, 'w', newline='',encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
            for row in data:
                clean_row = {}
                for key, value in row.items():
                    if value is not None:
                        clean_row[key] = BeautifulSoup(value, 'html.parser').get_text()
                    else:
                        clean_row[key] = None
                dict_writer.writerow(clean_row)

    def __get_detail_jobs(self, job_id):
        session = requests.Session()
        soupjob = BeautifulSoup(session.get(self.url_job).content, 'html.parser')
        csrftoken = soupjob.find('input', dict(name='csrf_fhci'))['value']
        detail = session.post(
            self.url_get_detail,
            data=dict(csrf_fhci=csrftoken, id=job_id),
            verify=False
        )
        print(detail.status_code)
        print(detail.text)
        if detail.status_code == 200:
            return detail.json()
        return None

    def get_all_details(self,path_job_csv, to_csv: bool = False, path_save: str = None):
        vacant_ids = []
        with open(path_job_csv, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                vacant_ids.append(row[0])
        print(len(vacant_ids))
        data = []
        for id in tqdm.tqdm(vacant_ids):
            try:
                datum = self.__get_detail_jobs(id)
                if datum:
                    data.append(datum)
                    time.sleep(0.1)
            except Exception as e:
                print("Error:", e)
                continue
        
        # Check if data is empty before parsing to CSV
        if data:
            if to_csv and path_save:
                self.__parse_to_csv(data, path_save)
            else:
                return data
        else:
            print("No data to parse.")


if __name__ == '__main__':
    api_bumn = RekrutmenBersama()
    
    api_bumn.get_all_details(to_csv=True,path_job_csv="data/all_jobs.csv", path_save="data/all_detail.csv")
