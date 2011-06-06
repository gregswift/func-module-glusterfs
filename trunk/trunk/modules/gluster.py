#
# Copyright 2011
# Greg Swift <gregswift@gmail.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import stat

import func_module
import func.minion.codes as codes

try:
    import subprocess
except ImportError:
    from func.minion import sub_process as subprocess

GLUSTER_BIN = '/usr/sbin/gluster'
CONFIG_PATH = '/etc/glusterd'
VOLUME_CONFIG_PATH = os.path.join(CONFIG_PATH, 'vols/')
ERROR_SUBCOMMAND = 'gluster %s subcommand (%s) does not exist'
DEBUG = False

class GlusterModule(func_module.FuncModule):
    version = "0.0.1"
    api_version = "3.2.0"
    description = "GlusterFS related information and tasks"

    def handle_command(self, command, subcommand, value=None):
        """
        Internal function to generate the cli command to run
        Then run it and return stdout/err
        """
        # splitting the command variable out into a list does not seem to function
        # in the tests I have run
        command = '%s %s %s' % (GLUSTER_BIN, command, subcommand)
        if (value):
            command += ' %s' % (value)
        if DEBUG: print "Command: %s" % command
        cmdref = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True,
                                   close_fds=True)
        (stdout, stderr) = cmdref.communicate()
        return (stdout, stderr)

    def peer(self, subcommand, name=None):
        """
        Returns output of the internal method mapping to the peer subcommand
        """
        command = 'peer'
        if DEBUG: print "Calling _%s_%s('%s')" % (command, subcommand, name)
        method = getattr(self, '_%s_%s' % (command, subcommand))
        if not method:
            raise codes.FuncException(ERROR_SUBCOMMAND % (command, subcommand))
        return method(name)

    def _peer_status(self, value=None):
        """
        Returns the status of each of the gluster peers for a node
        The option 'value' is due to reducing extranaeous config.  status does not accept a value
        """
        command = 'peer'
        subcommand = 'status'
        peers = {}
        peer = {}
        (stdout, stderr) = self.handle_command(command, subcommand)
        for line in stdout.split('\n'):
            if not line or line[:6].lower() == 'number':
                continue
            if line[:8].lower() == 'hostname':
                if peer:
                    peers[hostname] = peer
                    peer = {}
                hostname = line.split()[-1]
                if DEBUG: print "Hostname: %s" % hostname
            else:
                line = line.split(':')
                line[-1] = line[-1].strip()
                peer[line[0]] = line[-1]
        if peer:
            peers[hostname] = peer
        return peers

    def volume(self, subcommand, name=None):
        """
        Returns output of the internal method mapping to the volume subcommand
        """
        command = 'volume'
        if DEBUG: print "Calling _%s_%s('%s')" % (command, subcommand, name)
        method = getattr(self, '_%s_%s' % (command, subcommand))
        if not command:
            raise codes.FuncException(ERROR_SUBCOMMAND % (command, subcommand))
        return method(name)

    def _volume_info(self, volume_name=None):
        """
        Returns the gluster volume info output
        """
        command = 'volume'
        subcommand = 'info'
        volumes = {}
        volume = {}
        options = False
        (stdout, stderr) = self.handle_command(command, subcommand, volume_name)
        for line in stdout.split('\n'):
            if not line:
                continue
            if line[:6] == 'Volume':
                if volume:
                    volumes[name] = volume
                    volume = {}
                    options = False
                name = line.split()[-1]
                if DEBUG: print "Name: %s" % name
            else:
                if line[:6] == 'Bricks':
                    volume['Bricks'] = {}
                    continue
                elif line == 'Options Reconfigured:':
                    volume['Options Reconfigured'] = {}
                    options = True
                    continue
                else:
                    line = line.split(':')
                    line[-1] = line[-1].strip()
                    if options:
                        volume['Options Reconfigured'][line[0]] = line[-1]
                    elif line[0][:5] == 'Brick':
                        volume['Bricks'][line[0]] = line[-1]
                    else:
                        volume[line[0]] = line[-1]
        if volume:
            volumes[name] = volume
        return volumes

    def _volume_cksum(self, volume_name):
        """
        Returns the gluster cksum for a volume
        """
        if not volume_name:
            raise codes.FuncException('Must provide a volume name')
        cksum_path = os.path.join(VOLUME_CONFIG_PATH, volume_name, 'cksum')
        if DEBUG: print "cksum file path: %s" % cksum_path
        if os.access(cksum_path, os.R_OK):
            return open(cksum_path, 'r').readlines()[0].strip().split('=')[-1]
        raise codes.FuncException('Unable to access %s' % cksum_path)

    def _volume_process(self, volume_name):
        """
        Returns info about the glusterfsd process for a volume
        """
        if not volume_name:
            raise codes.FuncException('Must provide a volume name')
        pids = {}
        pid_path = os.path.join(VOLUME_CONFIG_PATH, volume_name, 'run')
        for pidfile in os.listdir(pid_path):
            full_path = os.path.join(pid_path, pidfile)
            if not os.access(full_path, os.R_OK):
                raise codes.FuncException('Unable to access %s' % full_path)
            pid = open(full_path, 'r').readlines()[0].strip()
            if not pid:
                raise codes.FuncException('No pid found in %s' % full_path)
            if DEBUG: print "Found PID: %s" % pid
            pids[pid] = {'pidfile': full_path,
                         'ctime': os.stat(full_path)[stat.ST_CTIME]}
            proc_path = '/proc/%s' % pid
            cmdline = open(os.path.join(proc_path, 'cmdline')).readlines()[0]
            pids[pid]['cmdline'] = cmdline.replace('\x00', ' ')
        return pids

    def _do_volume_function(self, subcommand, volume_name, force=False):
        """
        Handles gluster volume start/stop functions
        """
        if not volume_name:
            raise codes.FuncException('Must provide a volume name')
        command = 'volume'
        subcommand += ' --mode=script'
        if force is True:
            volume_name += ' force'
        (stdout, stderr) = self.handle_command(command, subcommand, volume_name)
        return stdout.split('\n')[0]

    def _volume_start(self, volume_name):
        """
        Forces the start of a gluster volume
        """
        return self._do_volume_function('start', volume_name)

    def _volume_forcestart(self, volume_name):
        """
        Forces the start of a gluster volume
        """
        return self._do_volume_function('start',volume_name, 'True')

    def _volume_stop(self, volume_name):
        """
        Forces the start of a gluster volume
        """
        return self._do_volume_function('stop', volume_name)

    def _volume_forcestop(self, volume_name):
        """
        Forces the start of a gluster volume
        """
        return self._do_volume_function('stop', volume_name, 'True')

    def register_method_args(self):
        """
        The argument export method
        """
        return {
                'peer':{
                    'args':{
                        'subcommand': {
                            'type':'string',
                            'optional':False,
                            'description':'Which peer subcommand you want to run',
                            },
                        'hostname': {
                            'type':'string',
                            'optional':True,
                            'description':'The specific peer to work with',
                            }
                        },
                    'description':'Run Gluster peer commands'
                    },
                'volume':{
                    'args':{
                        'subcommand': {
                            'type':'string',
                            'optional':False,
                            'description':'Which volume subcommand you want to run',
                            },
                        'volume_name': {
                            'type':'string',
                            'optional':True,
                            'description':'The specific volume to get information from',
                            }
                        },
                    'description':'Run Gluster volume subcommands, some are actions, some gather information'
                    }
                }

if __name__ == '__main__':
    from sys import argv
    try:
        command = argv[1]
    except:
        command = 'peer'
    try:
        subcommand = argv[2]
    except:
        if command == 'volume':
            subcommand = 'info'
        elif command == 'peer':
            subcommand = 'status'
        else:
            subcommand = None
    try:
        value = argv[3]
    except:
        value = None
    DEBUG = True
    print "Command: %s" % command
    print "Subcommand: %s" % subcommand
    if value is not None:
        print "Value: %s" % value
    g = GlusterModule()
    method = getattr(g, command)
    print method(subcommand, value)
