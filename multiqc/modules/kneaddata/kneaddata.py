#!/usr/bin/env python

""" MultiQC module to parse output from Kneaddata """

from __future__ import print_function
from collections import OrderedDict
import json
import logging
import re
from distutils.version import StrictVersion

from multiqc import config
from multiqc.plots import bargraph
from multiqc.modules.base_module import BaseMultiqcModule

# Initialise the logger
log = logging.getLogger(__name__)
log.info('KneadData - Hello world!!')

class MultiqcModule(BaseMultiqcModule):
    """
    Kneaddata module class, parses stderr logs.
    Also understands logs saved by Trim Galore!
    (which contain cutadapt logs)
    """

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='KneadData', anchor='kneaddata',
        href='https://bitbucket.org/biobakery/kneaddata/wiki/Home',
        info="is a tool designed to perform quality control on metagenomic and"
        " metatranscriptomic sequencing data, especially data from microbiome"
        " experiments")

        # Find and load any KneadData reports
        self.kneaddata_data = dict()
        for f in self.find_log_files(config.sp['kneaddata'], filehandles=True):
            self.parse_kneaddata_log(f)
            self.add_data_source(f)

        # Err if no reports
        if len(self.kneaddata_data) == 0:
            log.debug("Could not find any reports in {}".format(config.analysis_dir))
            raise UserWarning

        # Err if duplicate filenames
        if f['s_name'] in self.kneaddata_data:
            log.debug("Duplicate sample name found! Overwriting: {}".format(f['s_name']))


    def parse_kneaddata_log(self, f):

        for line in f['f']:
            s_name = f['s_name']
            self.kneaddata_data[s_name] = dict()

            # Get total number of reads
            if "Input Reads:" in line:
                initial_reads = line.split()[2]
                trim_reads = line.split()[4]
                print("Initial # of reads: " + str( initial_reads ))
                print("Reads post trimming: " + str( trim_reads ))

            # Get filtered data
            if "Total reads after merging results from multiple databases" in line:
                post_aligned = (line.split()[-1::])
                print("Reads post alignment: " + str(post_aligned))
