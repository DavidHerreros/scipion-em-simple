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

import os
#import pyworkflow.em as em
from pyworkflow import VERSION_1_1
import pyworkflow.protocol.params as param
from pyworkflow.protocol.params import IntParam, PointerParam, EnumParam, FileParam, StringParam
#from subprocess import call
from pyworkflow.em.protocol.protocol_micrographs import ProtMicrographs


class ProtRecVol(ProtMicrographs):
    """
    Reconstructing volumes from MRC and SPIDER stacks
    
    To find more information about Simple.RecVol go to:
    https://simplecryoem.com/tutorials.html
    """
    _label = 'RecVol'
    
    def __init__(self,**kwargs):
        ProtMicrographs.__init__(self, **kwargs)
    
    #--------------------------- DEFINE param functions -------------------------------

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputMovies', PointerParam, pointerClass='SetOfMovies', allowsNull=False,
                       label='Input Movies', important=True)
        form.addParam('mask', IntParam, default=80, label='Mask radius', help='Mask radius (in Pixels).')
        form.addParam('ctf', EnumParam, choices=['yes', 'no', 'flip'], label="CTF flag:", default=1,
                      display=EnumParam.DISPLAY_HLIST)
        form.addParam('symmetry', StringParam, important=True, label='Point-group symmetry')
        form.addParam('ctfInfo', FileParam, label='CTF Information', help='Text file with CTF info(*.txt/*.asc)')
        form.addParam('oritab', FileParam, label='Table of orientations', help='Supported formats *.txt and *.asc')
        form.addParam('threads', IntParam, label='Number of threads', default=1)
                
    #--------------------------- INSERT steps functions -------------------------------
    
    def _insertAllSteps(self):
        inputMV = self.inputMovies.get()
        for movie in inputMV:
            # movieName = movie.getFileName()
            # SamplingRate = movie.getSamplingRate()
            # params = self.getRVParams(movieName, SamplingRate)
            # self._insertRunJobStep('simple_distr_exec', params)
            #self._insertFunctionStep("recVolStep", movie)
            self.recVolStep(movie)
        self._insertFunctionStep("createOutputStep")
        
    #--------------------------- STEPS functions -------------------------------

    def recVolStep(self, movie):
        movieName = movie.getFileName()
        SamplingRate = movie.getSamplingRate()
        params = self.getRVParams(movieName, SamplingRate)

        self.runJob("simple_distr_exec", params)
      
    def getRVParams(self, mvN, SR):
        """Prepare the commmand line to call Recvol program"""
        fn = os.path.abspath(mvN)
        partitions = 1
        params = ' prg=recvol stk=%s smpd=%f oritab=%s msk=%d ctf=%s pgrp=%s nparts=%d nthr=%d' % (fn, SR, self.oritab.get(),
                                                                                                   self.mask.get(),
                                                                                                   self.getEnumText('ctf'),
                                                                                                   self.symmetry.get(), partitions,
                                                                                                   self.threads.get())
        if self.ctfInfo.get():
            params = params + ' deftab=%s' %(self.ctfInfo.get())

        return params

    def createOutputStep(self):
        pass
        
    #------------------------------- INFO functions ---------------------------------
    def _citations(self):
        cites = ['Elmlund2012']
        return cites

        
        