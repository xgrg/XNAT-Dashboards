from pyxnat import Interface
from collections import Counter, OrderedDict
import numpy as np


class Fetcher:

    SELECTOR = None
    projects = None
    subjects = None
    experiments = None
    name = None
    scans = None

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

    def get_projects_details(self):

        try:
            self.projects = self.SELECTOR.select('xnat:projectData').all().data
            projects = self.projects
        except Exception as e:
            # Exception raised is Database error which is not a exception in
            # python thus using whole exception class
            # 500 represent error in url
            if str(e).find('500') != -1:
                return 500
            # 400 represent error in login details
            elif str(e).find('401') != -1:
                return 401
            # 1 represent Error in whole url
            elif str(e).find('SSL') != -1:
                return 191912
            else:
                return 1

        # Projects_details is a dictionary which will add details of all
        # projects to the global stats dictionary

        projects_details = {}
        projects_ims = {}
        project_acccess = {}
        mr_sessions_per_project = {}
        ct_sessions_per_project = {}
        pet_sessions_per_project = {}
        ut_sessions_per_project = {}

        project_acccess_list = [item['project_access']
                                if item['project_access'] != ''
                                else
                                "No Data"
                                for item in projects]
        project_acccess = dict(Counter(project_acccess_list))

        projects_ims['CT Sessions'] = sum([int(project['proj_ct_count'])
                                           for project in projects
                                           if project['proj_ct_count'] != ''])
        projects_ims['PET Sessions'] = sum([int(project['proj_pet_count'])
                                            for project in projects
                                            if project['proj_pet_count']
                                            != ''])
        projects_ims['MR Sessions'] = sum([int(project['proj_mr_count'])
                                           for project in projects
                                           if project['proj_mr_count'] != ''])
        projects_ims['UT Sessions'] = sum([int(project['proj_ut_count'])
                                           for project in projects
                                           if project['proj_ut_count'] != ''])

        for item in projects:

            if item['proj_mr_count'] != '':
                mr_sessions_per_project[item['id']] =\
                                                    int(item['proj_mr_count'])
            else:
                mr_sessions_per_project[item['id']] = 0

            if item['proj_pet_count'] != '':
                pet_sessions_per_project[item['id']] =\
                                                    int(item['proj_pet_count'])
            else:
                pet_sessions_per_project[item['id']] = 0

            if item['proj_ct_count'] != '':
                ct_sessions_per_project[item['id']] =\
                                                    int(item['proj_ct_count'])
            else:
                ct_sessions_per_project[item['id']] = 0

            if item['proj_ut_count'] != '':
                ut_sessions_per_project[item['id']] =\
                                                    int(item['proj_ut_count'])
            else:
                ut_sessions_per_project[item['id']] = 0

        projects_details['Number of Projects'] = len(projects)
        projects_details['Imaging Sessions'] = projects_ims
        projects_details['Projects Visibility'] = project_acccess
        projects_details['MR Sessions/Project'] = mr_sessions_per_project
        projects_details['PET Sessions/Project'] = pet_sessions_per_project
        projects_details['CT Sessions/Project'] = ct_sessions_per_project
        projects_details['UT Sessions/Project'] = ut_sessions_per_project
        projects_details['Total Sessions'] = projects_ims['PET Sessions']\
            + projects_ims['MR Sessions'] + projects_ims['UT Sessions']\
            + projects_ims['CT Sessions']

        return projects_details

    def get_subjects_details(self):

        try:
            self.subjects = self.SELECTOR.get('/data/subjects',
                                              params={'columns': 'ID,\
                                              project,handedness,age,gender'})\
                                              .json()['ResultSet']['Result']
            subjects_data = self.subjects
        except Exception:
            return 1

        # Subject_details is a dictionary which will add details of
        # all subjects to the global stats dictionary

        subjects_details = {}

        # Subject age information
        no_age_data_counter = 0
        age = []
        for item in subjects_data:
            if item['age'] != '':
                age.append(int(item['age']))
            else:
                no_age_data_counter = no_age_data_counter + 1

        # Create bins and their labels
        bins = np.arange(11)*10+10
        age_range_bins = dict(Counter(np.digitize(age, bins)))

        age_range_od = OrderedDict()
        for key, value in sorted(age_range_bins.items()):
            if key != 11:
                age_range_od[str(key*10)+'-'+str(key*10+10)] = int(value)
            else:
                age_range_od['100+'] = int(value)

        age_range = dict(age_range_od)
        age_range.update({"No Age Data": no_age_data_counter})

        # Subject handedness information

        handedness = dict(Counter([item['handedness']
                          if item['handedness'] != ''
                          else
                          "No Data"
                          for item in subjects_data]))

        # Subject gender information

        gender = dict(Counter([item['gender'][0].upper()
                      if item['gender'] != ''
                      else
                      "No Data"
                      for item in subjects_data]))

        # Subjects per project information

        subjects_per_project = dict(Counter([item['project']
                                    for item in subjects_data]))

        # Number of subjects information
        subjects_details['Number of Subjects'] = len(subjects_data)

        subjects_details['Subjects/Project'] = subjects_per_project
        subjects_details['Age Range'] = age_range
        subjects_details['Gender'] = gender
        subjects_details['Handedness'] = handedness

        return subjects_details

    def get_experiments_details(self):

        '''
        Using array method to get the experiment information present on XNAT.

        This will add a get_experiment_details key in stats dictionary
        which will have details of number of experiments, experiment per
        project, type of experiment, experiment per subjects.
        '''
        try:
            self.experiments = self.SELECTOR.array.experiments(
                                            experiment_type='',
                                            columns=['subject_ID']).data
            experiments = self.experiments
        except Exception:
            return 1

        experiments_details = {}

        experiments_details['Number of Experiments'] = len(experiments)

        # Experiments per project information

        experiments_per_project = dict(Counter([item['project']
                                       if item['project'] != ''
                                       else
                                       "No Data"
                                       for item in experiments]))

        # Experiments type information

        experiment_type = dict(Counter([item['xsiType']
                               if item['xsiType'] != ''
                               else
                               "No Data"
                               for item in experiments]))

        # Experiments per subject information

        experiments_per_subject = dict(Counter([item['subject_ID']
                                       if item['subject_ID'] != ''
                                       else
                                       "No Data"
                                       for item in experiments]))

        experiments_details['Experiments/Subject'] = experiments_per_subject
        experiments_details['Experiment Types'] = experiment_type
        experiments_details['Experiments/Project'] = experiments_per_project

        return experiments_details

    def get_scans_details(self):

        '''
        Using array method to get the scans information present on XNAT.

        This will add a get_scans_details key in stats dictionary
        which will have details of number of scans, scans per subject,
        scans per project, scans per experimetn, type of experiment,
        scan quality (usable or unusable), xsi type of scan.
        '''
        try:
            self.scans = self.SELECTOR.array.scans(
                columns=['xnat:imageScanData/quality',
                         'xnat:imageScanData/type'])
            scans = self.scans
        except Exception:
            return 1

        scans_details = {}

        scan_quality = dict(Counter([item['xnat:imagescandata/quality']
                            if item['xnat:imagescandata/quality'] != ''
                            else
                            "No Data"
                            for item in scans]))
        # Scans type information

        type_dict = dict(Counter([item['xnat:imagescandata/type']
                         if item['xnat:imagescandata/type'] != ''
                         else
                         "No Data"
                         for item in scans]))

        # Scans xsi type information

        xsi_type_dict = dict(Counter([item['xsiType']
                             if item['xsiType'] != ''
                             else
                             "No Data"
                             for item in scans]))

        # Scans per project information

        scans_per_project = dict(Counter([item['project']
                                 if item['project'] != ''
                                 else
                                 "No Data"
                                 for item in scans]))

        # Scans per subject information

        scans_per_subject = dict(Counter(
                            [item['xnat:imagesessiondata/subject_id']
                             if item['xnat:imagesessiondata/subject_id']
                             != ''
                             else
                             "No Data"
                             for item in scans]))

        scans_details['Scans Quality'] = scan_quality
        scans_details['Scan Types'] = type_dict
        scans_details['XSI Scan Types'] = xsi_type_dict
        scans_details['Scans/Project'] = scans_per_project
        scans_details['Scans/Subject'] = scans_per_subject
        scans_details['Number of Scans'] = len(scans)

        return scans_details

    def get_projects_details_specific(self):

        try:
            projects = self.projects
            if projects is None:
                raise Exception('No Information found')
        except Exception as e:
            # 500 represent error in url
            if str(e).find('500') != -1:
                return 500
            # 400 represent error in login details
            elif str(e).find('401') != -1:
                return 401
            # 1 represent Error in whole url
            else:
                return 1

        project_list_owned_collab_member = []

        for project in projects:
            project_owner = project['project_owners']
            project_collabs = project['project_collabs']
            project_member = project['project_members']
            user = self.name

            if project_owner.find(user) != -1\
               or project_collabs.find(user) != -1\
               or project_member.find(user) != -1:
                project_list_owned_collab_member.append(project['id'])

        project_list_all = [project['id'] for project in projects]

        list_data = {}
        list_data['project_list'] = project_list_all
        list_data['project_list_ow_co_me'] = project_list_owned_collab_member

        return list_data
