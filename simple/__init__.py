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
import pyworkflow.em
import pyworkflow.utils as pwutils

#from .base import *
from .constants import SIMPLE_HOME



_logo = "simple_logo.png"
_references = ['Elmlund2012']
_currentVersion = '2.5'

class Plugin(pyworkflow.em.Plugin):
    _homeVar = SIMPLE_HOME
    _pathVars = [SIMPLE_HOME]
    _supportedVersions = []

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(SIMPLE_HOME, 'simple-%s'%_currentVersion)

    @classmethod
    def getEnviron(cls):
        """ Create the needed environment for Spring programs. """
        environ = pwutils.Environ(os.environ)
        pos = pwutils.Environ.BEGIN
        environ.update({
            'PATH': Plugin.getHome(),
            'LD_LIBRARY_PATH': str.join(cls.getHome(), 'simple')
                               +':'+cls.getHome(),
        }, position=pos)

        return environ
    
    @classmethod
    def validateInstallation(cls):
        '''This function will be used to check if package is properly
        installed.'''
        missingPaths = ['%s: %s' % (cls._homeVar, cls.getHome())] \
            if not os.path.exists(Plugin._homeVar) else []

    '''
    @classmethod
    def defineBinaries(cls, env):
        Defined required binaries in the given Environment.
        scons = env.addPipModule('scons', '2.3.6', target='scons-2.3.6',
                                 default=True, ignoreDefaultDeps=True)

        installCmd = "src/xmipp/xmipp config ; src/xmipp/xmipp check_config ;" \
                     "src/xmipp/xmipp compile %d ; src/xmipp/xmipp install %s" \
                      % (env.getProcessors(), cls.getHome())

        target = "%s/bin/xmipp_reconstruct_significant" % cls.getHome()

        env.addPackage('xmippSrc', version=_currentVersion,
                       tar='xmippSrc-%s.tgz'%_currentVersion,
                       commands=[(installCmd, target)],
                       default=True,
                       deps=[scons])
            # Old dependencies now are checked inside xmipp script:
            #   fftw3, scikit, nma, tiff, sqlite, opencv, sh_alignment, hdf5

        env.addPackage('xmippBin', version=_currentVersion,
                       tar='xmipp-%s.tgz'%_currentVersion)
    '''
    @classmethod
    def defineBinaries(cls,env):
        '''Defined required binaries in the given Environment'''
        pass 

pyworkflow.em.Domain.registerPlugin(__name__)
