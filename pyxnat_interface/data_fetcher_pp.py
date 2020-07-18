from pyxnat import Interface
import pyxnat.core.errors as pyxnat_errors
import socket
import json
import warnings
warnings.filterwarnings("ignore")


class Fetcher:

    SELECTOR = None

    # Initializing the central interface object in the constructor
    def __init__(self, name, password, server, ssl):

        SELECTOR = Interface(server=server,
                             user=name,
                             password=password,
                             verify=(not ssl))
        self.name = name
        self.SELECTOR = SELECTOR

    # Disconnect with the instance
    def __del__(self):
        print("Disconnected")
        self.SELECTOR.disconnect()

    def get_subjects_details(self, project_id):

        try:
            self.subjects = self.SELECTOR.get(
                '/data/projects/' + project_id + '/subjects',
                params={'columns': 'ID,'
                        'project,handedness,'
                        'age,gender'})
            subjects_data = self.subjects.json()['ResultSet']['Result']

        except json.JSONDecodeError:
            if str(self.subjects).find('500') != -1:
                # 500 represent error in url or uri
                return 500
            elif str(self.subjects).find('401') != -1:
                # 401 represent error in login details
                return 401
        except socket.error as se:
            if str(se).find('SSL') != -1:
                # If verification enable and host unable to verify
                return 191912
            else:
                # Wrong URL Connection can't be established
                return 1

        return subjects_data

    def get_experiments_details(self, project_id):

        '''
        Using array method to get the experiment information present on XNAT.

        This will add a get_experiment_details key in stats dictionary
        which will have details of number of experiments, experiment per
        project, type of experiment, experiment per subjects.
        '''
        try:
            experiments = self.SELECTOR.array.experiments(
                project_id=project_id,
                experiment_type='',
                columns=['subject_ID']).data

        except pyxnat_errors.DatabaseError as dbe:
            if str(dbe).find('500') != -1:
                # 500 represent error in url or uri
                return 500
            elif str(dbe).find('401') != -1:
                # 401 represent error in login details
                return 401
        except socket.error as se:
            if str(se).find('SSL') != -1:
                # If verification enable and host unable to verify
                return 191912
            else:
                # Wrong URL Connection can't be established
                return 1

        return experiments

    def get_scans_details(self, project_id):

        '''
        Using array method to get the scans information present on XNAT.

        This will add a get_scans_details key in stats dictionary
        which will have details of number of scans, scans per subject,
        scans per project, scans per experimetn, type of experiment,
        scan quality (usable or unusable), xsi type of scan.
        '''
        try:
            scans = self.SELECTOR.array.scans(
                project_id=project_id,
                columns=['xnat:imageScanData/quality',
                         'xnat:imageScanData/type']).data

        except pyxnat_errors.DatabaseError as dbe:
            if str(dbe).find('500') != -1:
                # 500 represent error in url or uri
                return 500
            elif str(dbe).find('401') != -1:
                # 401 represent error in login details
                return 401
        except socket.error as se:
            if str(se).find('SSL') != -1:
                # If verification enable and host unable to verify
                return 191912
            else:
                # Wrong URL Connection can't be established
                return 1

        return scans

    def get_project_details(self, project_id):

        try:
            project = self.SELECTOR.select('xnat:projectData').where(
                [('xnat:projectData/id', '=', project_id)]).data
        except pyxnat_errors.DatabaseError as dbe:
            if str(dbe).find('500') != -1:
                # 500 represent error in url or uri
                return 500
            elif str(dbe).find('401') != -1:
                # 401 represent error in login details
                return 401
        except socket.error as se:
            if str(se).find('SSL') != -1:
                # If verification enable and host unable to verify
                return 191912
            else:
                # Wrong URL Connection can't be established
                return 1

        return project