import os
import subprocess
import argparse
import logging
import tempfile




class Metsample():
    """A class for metagenomics sample dataself.

    This class provides a container and methods to perform opperations on
    metagenomics sample data where MLST analysis is needed

    Attributes:


    """


    def __init__(self, name, infile, tempdir, ref_loci, bbtoolsdir):
        """initialization of the metsample class

        """
        logging.info("Initializing metsample object")
        self.name = name
        self.infile = infile
        if tempdir:
            self.tempdir = tempdir
        else:
            self.tempdir = tempfile.mkdtemp()
        self.refloci = ref_loci
        self.loci_reads = os.path.join(self.tempdir, 'loci_reads.fq.gz')
        self.clean = os.path.join(self.tempdir, 'clean_reads.fq.gz')
        self.trimmed =  os.path.join(self.tempdir, 'trimmed_reads.fq.gz')
        self.ecorr = os.path.join(self.tempdir, 'ec_reads.fq.gz')



    def _get_loci(self):
        """ Identify the target loci by kmer matching

        """
        try:
            parameters = ['bbduk.sh',
                          'in=' + self.infile,
                          'outm=' + self.loci_reads,
                          'stats=' + os.path.join(self.tempdir, 'locistats.txt'),
                          'ref=' + self.ref_loci
                        ]
            p1 = subprocess.run(parameters, stderr=subprocess.PIPE)
            return p1.stderr.decode('utf-8')
        except RuntimeError:
            logging.error("could identify reads with , target loci using bbduk")
            logging.error(p1.stderr.decode('utf-8'))




    def _filter_contaminants(self):
        """Calls bbduk to perform adapter removal and create quality data

        """
        try:
            bbtoolsdict = self.parse_params()
            parameters = ['bbduk.sh',
                          'in=' + self.loci_reads,
                          'out=' + self.clean,
                          'stats=' + os.path.join(self.tempdir, 'filterstats.txt'),
                          'ref=' + os.path.join(bbtoolsdir, "resources", "sequencing_artifacts.fq.gz"),
                          ]
            p1 = subprocess.run(parameters, stderr=subprocess.PIPE)
            return p1.stderr.decode('utf-8')
        except RuntimeError:
            logging.error("could not perform contaminant filtering with bbduk")
            logging.error(p1.stderr.decode('utf-8'))

    def _trim_adaptors(self):
        """Calls bbduk to remove contaminant sequences

        """
        try:
            bbtoolsdict = self.parse_params()
            parameters = ['bbduk.sh', 'in=' + self.clean,
                          'out=' + self.trimmed,
                          'ref=' + os.path.join(bbtoolsdir, "resources", "adaptors.fq")]
            p2 = subprocess.run(parameters, stderr=subprocess.PIPE)
            return p2.stderr.decode('utf-8')
        except RuntimeError:
            logging.error("could not perform adaptor removal with bbduk")

    def _merge_reads(self):
        """Merge reads for error correction returns unmerged reads.

        """
        try:
            bbtoolsdict = self.parse_params()
            parameters = ['bbmerge.sh',
                          'in=' + self.trimmed,
                          'out=' + self.eforr,
                          'eeco',
                          'mix'
                          ]
            p3 = subprocess.run(parameters, stderr=subprocess.PIPE)
            return p3.stderr.decode('utf-8')
        except RuntimeError:
            logging.error("could not perform read merging with bbmerge")

    def preprocess(self):
        """Preprocess a fastq library identifying target loci and performing
        quality control.

        """
        try:
            self._get_loci()
            self._filter_contaminants()
            self._trim_adaptors()
            self._merge_reads()
        except RuntimeError:
            logging.error("could not preprocess data")


    def _map_to_loci(self):
        pass

    def call_snps(self):
        pass

    def predict_st(self):
        pass

    def predict_serovar(self):
        pass

    def closest_genome(self):
        pass
