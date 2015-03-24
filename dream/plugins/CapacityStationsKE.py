from copy import copy, deepcopy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class CapacityStationsKE(plugin.InputPreparationPlugin):
    """ Input preparation 
        creates the CapacityStationBuffer and CapacityStationExit for each CapacityStation
    """

    def preprocess(self, data):
        from dream.KnowledgeExtraction.PilotCases.CapacityStations.DataExtraction import DataExtraction
        DBFilePath=data['general']['ke_url']
        extractedData=DataExtraction(DBFilePath)
        return data

    