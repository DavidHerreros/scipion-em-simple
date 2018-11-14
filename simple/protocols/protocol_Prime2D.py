# **************************************************************************
# *
# * Authors:     David Herreros
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os, glob, shutil
#import pyworkflow.em as em
from pyworkflow import VERSION_1_1
#import pyworkflow.protocol.params as param
from pyworkflow.protocol.params import IntParam, PointerParam, EnumParam, FileParam
from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs
from pyworkflow.utils.path import cleanPath, makePath
from pyworkflow.em.convert import ImageHandler
from pyworkflow.protocol.constants import STEPS_PARALLEL
from pyworkflow.em.data import SetOfParticles

class ProtPrime2D(ProtMicrographs):
    """
    Simultaneous 2D alignment and clustering
    
    To find more information about Simple.Prime2D go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'Prime2D'
    
    def __init__(self,**kwargs):
        ProtMicrographs.__init__(self, **kwargs)
        self.stepsExecutionMode = STEPS_PARALLEL
    
    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputParticles', PointerParam, pointerClass='SetOfParticles', allowsNull=False,
                       label='Input Particles', important=True)
        form.addParam('mask', IntParam, default=36, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('clusters', IntParam, default=5, label='Number of clusters')
        # form.addParam('ctf', EnumParam, choices=['yes', 'no', 'flip'], label="CTF flag:", default=1,
        #               display=EnumParam.DISPLAY_HLIST)
        # form.addParam('ctfInfo', FileParam, label='CTF Information', help='Text file with CTF info(*.txt/*.asc)')
        # form.addParam('oritab', FileParam, label='Table of orientations', help='Supported formats *.txt and *.asc')
        # form.addParam('threads', IntParam, label='Number of threads', default=1)
        form.addParallelSection(threads=4, mpi=1)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        self._insertFunctionStep("convertInput")
        deps = []
        particleName = self._getExtraPath("particles.mrc")
        samplingRate = self.inputParticles.get().getSamplingRate()
        deps.append(self._insertFunctionStep('prime2DStep', particleName, samplingRate, prerequisites=[]))
        self._insertFunctionStep("createOutputStep", prerequisites=deps)
        #inputMV = self.inputMovies.get()
        #for movie in inputMV:
            # movieName = movie.getFileName()
            # SamplingRate = movie.getSamplingRate()
            #params = self.getP2DParams(movieName, SamplingRate)
            #self._insertFunctionStep('simple_distr_exec', params)
            #self.insertFunctionStep("prime2DStep", movie)
         #   self.prime2DStep(movie)
         #   self.createOutputStep(movie.getFileName())
        #self._insertFunctionStep("createOutputStep")
        
    #--------------------------- STEPS functions -------------------------------
    def convertInput(self):
        inputPart = self.inputParticles.get()
        inputPart.writeStack(self._getExtraPath("particles.mrc"))


    def prime2DStep(self,partFile,SamplingRate):
        partName = os.path.basename(partFile)
        partName = os.path.splitext(partName)[0]
        tmpDir = self._getTmpPath(partName)
        makePath(tmpDir)

        params = self.getP2DParams(partFile, SamplingRate)

        self.runJob("simple_distr_exec", params, cwd=os.path.abspath(tmpDir))

        #Move output files to ExtraPath and rename them properly
        folder = self._getExtraPath(partName)
        folder = os.path.abspath(folder)
        source_dir = os.path.abspath(tmpDir)
        files1 = glob.iglob(os.path.join(source_dir, "*.txt"))
        files2 = glob.iglob(os.path.join(source_dir, "*.mrc"))
        for file1, file2 in map(None, files1, files2):
            if (file1 != None):
                if os.path.isfile(file1):
                    oldName = os.path.basename(file1)
                    shutil.move(file1, folder + '_' + oldName)
            if (file2 != None):
                if os.path.isfile(file2):
                    oldName = os.path.basename(file2)
                    shutil.move(file2, folder + '_' + oldName)
        cleanPath(tmpDir)


    def getP2DParams(self, partF, SR):
        """Prepare the commmand line to call Prime2D program"""
        fn = os.path.abspath(partF)
        partitions = 1
        params = ' prg=prime2D stk=%s smpd=%f msk=%d ncls=%d ctf=no nparts=%d nthr=1' % (fn, SR, self.mask.get(), self.clusters.get(),
                                                                                         partitions)
        # if self.ctfInfo.get():
        #     params = params + ' deftab=%s' %(self.ctfInfo.get())
        #
        # if self.oritab.get():
        #     params = params + ' oritab=%s' %(self.oritab.get())

        return params

    def createOutputStep(self):
        """Move output files to extra Path and rename them properly"""
        # folder = os.path.basename(mvF)
        # folder = self._getExtraPath(folder)
        # folder = os.path.splitext(folder)[0]
        # folder = os.path.abspath(folder)
        # source_dir = os.getcwd()
        # files1 = glob.iglob(os.path.join(source_dir, "*.txt"))
        # files2 = glob.iglob(os.path.join(source_dir, "*.mrc"))
        # for file1, file2 in map(None, files1, files2):
        #     if (file1 != None):
        #         if os.path.isfile(file1):
        #             oldName = os.path.basename(file1)
        #             shutil.move(file1, folder + '_' + oldName)
        #     if (file2 != None):
        #         if os.path.isfile(file2):
        #             oldName = os.path.basename(file2)
        #             shutil.move(file2, folder + '_' + oldName)
        pass
    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2012']
        return cites

        
        