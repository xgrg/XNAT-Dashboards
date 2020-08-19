from xnat_dashboards.pyxnat_interface import pickle_saver
from xnat_dashboards import path_creator
import pickle


def test_save_data_and_user(mocker):

    path = 'xnat_dashboards/config/central.cfg'

    resource_return_value = {
        'date': '28', 'resources': [], 'resources_bbrc': []}
    data_return_value = {
        'info': 'data',
        'projects': [], 'subjects': [],
        'experiments': [], 'scans': []}

    mocker.patch(
        'xnat_dashboards.pyxnat_interface.data_fetcher.Fetcher.get_resources',
        return_value=resource_return_value)

    mocker.patch(
        'xnat_dashboards.pyxnat_interface.data_fetcher.Fetcher'
        '.get_bbrc_resource',
        return_value=resource_return_value)

    mocker.patch(
        'xnat_dashboards.pyxnat_interface.data_fetcher.Fetcher'
        '.get_instance_details',
        return_value=data_return_value)

    pickle_saver.PickleSaver(path).save()

    with open(path_creator.get_pickle_path(), 'rb') as handle:
        data = pickle.load(handle)

    assert type(data) == dict
    assert type(data['info']) == dict
    assert type(data['resources']) == dict
    assert type(data['resources_bbrc']) == dict