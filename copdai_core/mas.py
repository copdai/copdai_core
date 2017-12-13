from copdai_core.commun import ReturnCodes
from enum import Enum, unique
import sys
import os
import signal
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
from pathlib import Path
from uuid import getnode, uuid4
from abc import ABC, abstractmethod

# Setting logging system for development environment
home = str(Path.home())
log = logging.getLogger(__name__)
# numeric_level = getattr(logging, loglevel.upper(), None)
# if not isinstance(numeric_level, int):
# raise ValueError('Invalid log level: %s' % loglevel)
log.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s:(%(threadName)-10s) %(message)s')
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(format)
log.addHandler(sh)
fh = handlers.RotatingFileHandler("%s%scopdai_core.log" % (home, os.pathsep), maxBytes=(1048576 * 5), backupCount=7)
fh.setFormatter(format)
log.addHandler(fh)

@unique
class AgentState(Enum):
    """Normal agent life cycle FIPA specification"""

    UNKNOWN = 0
    INITIATED = 1
    ACTIVE = 2
    SUSPENDED = 3
    WAITING = 4
    TRANSIT = 5


class AbstractAgent(ABC):
    """
    An Agent is the fundamental actor on an AP which
    combines one or more service capabilities into a
    unified and integrated execution model that may
    include access to external software, human users and
    communications facilities.
    An agent may have certain resource brokering capabilities
    for accessing software (see [FIPA00079]).
    """

    __slots__ = ['_state', '_platform_id', '_pid', '_aid', '_run']

    def __init__(self, platform_id=None, name=None):
        super().__init__()
        # The platform ID in normal case will be the MAC address of current machine
        if platform_id is None:
            self._platform_id = getnode()
        else:
            self._platform_id = platform_id

        self._pid = os.getpid()
        self._run = False
        # A globally unique name for the agent
        # the name will be composed from an ID + filename + platform ID
        if name is None:
            self._aid = '%s#%s@%s' % (
                str(uuid4()),
                __name__,
                ''.join(("%012X" % self._platform_id)[i:i + 2] for i in range(0, 12, 2))
            )
        else:
            self.name = '%s#%s@%s' % (
                name,
                __name__,
                ''.join(("%012X" % self._platform_id)[i:i + 2] for i in range(0, 12, 2))
            )

        # register to handle TERM signal
        # The graceful termination of an agent. This can be ignored by the agent.
        signal.signal(signal.SIGTERM, self.signal_term)
        # register to handle KILL signal
        # The forceful termination of an agent. This can only be initiated by the AMS and cannot be ignored by the agent
        signal.signal(signal.SIGKILL, self.signal_kill)
        # register to handle STOP signal
        # Puts an agent in a suspended state. This can be initiated by the agent or the AMS.
        signal.signal(signal.SIGSTOP, self.signal_stop)
        # register to handle CONT signal
        # Brings the agent from a suspended state. This can only be initiated by the AMS.
        signal.signal(signal.SIGCONT, self.signal_cont)
        # register to handle USR1 signal
        # Brings the agent from a waiting state. This can only be initiated by the AMS.
        signal.signal(signal.SIGUSR1, self.signal_usr1)

        self._state = AgentState.INITIATED

    def continue_handling_signal(self, target_agent_state):
        if target_agent_state == self._state:
            log.debug('Agent already in %s state' % target_agent_state.name)
            return False
        elif target_agent_state == AgentState.SUSPENDED and self._state == AgentState.ACTIVE:
            return True
        elif target_agent_state == AgentState.WAITING and self._state == AgentState.ACTIVE:
            return True
        elif target_agent_state == AgentState.TRANSIT and self._state == AgentState.ACTIVE:
            return True
        elif target_agent_state == AgentState.ACTIVE and (self._state == AgentState.WAITING or self._state == AgentState.SUSPENDED or self._state == AgentState.INITIATED or self._state == AgentState.TRANSIT):
            return True
        log.debug('Cannot go to %s state, current state is : %s' % (target_agent_state.name, self._state.name))
        return False

    @abstractmethod
    def run(self):
        log.debug('starting execution of agent ...')

    def _start(self):
        if self._run :
            self.run()
        signal.pause()

    def signal_usr1(self, signum, frame):
        """
        Callback invoked when a USR1 signal is received
        :param frame:
        :return:
        """
        log.debug("Agent Received USR1 signal from")
        self.wakeup()

    def signal_term(self, signum, frame):
        log.debug("receiving signal TERM")
        self.quit()

    def signal_kill(self, signum, frame):
        log.debug("receiving signal KILL")
        self.destroy()

    def signal_stop(self, signum, frame):
        log.debug("receiving signal STOP")
        if self.continue_handling_signal(AgentState.SUSPENDED):
            self.suspend()

    def signal_cont(self, signum, frame):
        log.debug("receiving signal CONT")
        if self.continue_handling_signal(AgentState.ACTIVE):
            self.resume()


    def resume(self):
        """
        Brings the agent from a suspended state. This can only be initiated by the AMS.
        :return:
        """
        log.debug("Resuming agent")
        self._state = AgentState.ACTIVE
        return ReturnCodes.SUCCESS

    def invoke(self):
        """
        The invocation of a new agent.
        :return:
        """
        log.debug("Agent go to active state")
        self._state = AgentState.ACTIVE
        return ReturnCodes.SUCCESS

    def suspend(self):
        """
        Puts an agent in a suspended state. This can be initiated by the agent or the AMS.
        :return:
        """
        log.debug("Agent go to suspend state")
        self._state = AgentState.SUSPENDED
        return ReturnCodes.SUCCESS

    def wait(self):
        """
        Puts an agent in a waiting state. This can only be initiated by an agent.
        :return:
        """
        if self.continue_handling_signal(AgentState.WAITING):
            log.debug("Agent go to wait state")
            self._state = AgentState.WAITING
            self._run = False

        return ReturnCodes.SUCCESS

    def wakeup(self):
        """
        Brings the agent from a waiting state. This can only be initiated by the AMS.
        :return:
        """
        log.debug("Agent go to active state")
        self._state = AgentState.ACTIVE
        return ReturnCodes.SUCCESS

    def move(self):
        """
        The following transition are only used by mobile agents:
        Puts the agent in a transitory state. This can only be initiated by the agent.
        :return:
        """
        log.debug("Agent go to transit state")
        self._state = AgentState.TRANSIT
        return ReturnCodes.SUCCESS

    def execute(self):
        """
        The following transition are only used by mobile agents:
        Brings the agent from a transitory state. This can only be initiated by the AMS.
        :return:
        """
        log.debug("Agent go to active state")
        self._state = AgentState.ACTIVE
        return ReturnCodes.SUCCESS


    def destroy(self):
        """
        The forceful termination of an agent. This can only be initiated by the AMS and cannot be ignored by the agent
        :return:
        """
        log.debug("Agent Destroyed")
        self._state = AgentState.UNKNOWN
        return ReturnCodes.SUCCESS

    def quit(self):
        """
        The graceful termination of an agent. This can be ignored by the agent.
        :return:
        """
        log.debug("Agent Quit")
        self._state = AgentState.UNKNOWN
        return ReturnCodes.SUCCESS



class AgentPlatform(object):
    """
    Agents exist physically on an AP and utilise the facilities offered
    by the AP for realising their functionalities.
    """

    def __init__(self, uid):
        self.uid = uid


class AgentManagementSystem(AbstractAgent):
    """
    An Agent Management System (AMS) is a mandatory component of
    the AP.
    The AMS exerts supervisory control over access to and use
    of the AP.
    Only one AMS will exist in a single AP.
    The AMS maintains a directory of AIDs which contain transport
    addresses (amongst other things) for agents registered with the
    AP.
    """


    def __init__(self):
        # The platform ID in normal case will be the MAC address of current machine
        super().__init__()
        self._aid = "ams@%s" % ''.join(("%012X" % self._platform_id)[i:i + 2] for i in range(0, 12, 2))


    # PART1 :  Management Functions Supported by the Agent Management System
    def register(self):
        return ReturnCodes.SUCCESS

    def deregister(self):
        return ReturnCodes.SUCCESS

    def modify(self):
        return ReturnCodes.SUCCESS

    def search(self):
        return ReturnCodes.SUCCESS

    def get_description(self):
        """
        An agent can make a query in order to request the platform profile of an AP from an AMS.
        :return: platform ID
        """
        return ''.join(("%012X" % self._platform_id)[i:i + 2] for i in range(0, 12, 2))

    # END PART1

    # PART2 : AMS can instruct the underlying AP to perform the following operations
    def invoke(self, aid):
        log.debug("Agent go to active state")
        return ReturnCodes.SUCCESS

    def suspend(self, aid):
        log.debug("Agent go to suspend state")
        return ReturnCodes.SUCCESS

    def terminate(self, aid):
        log.debug("Agent go to unkowen  state")
        return ReturnCodes.SUCCESS

    def resume(self, aid):
        log.debug("Agent go to active  state")
        return ReturnCodes.SUCCESS

    def create(self, agent_path_file_name):
        """
        The creation or installation of a new agent
        :param agent_path_file_name:
        :return:
        """
        log.debug("Creating agent")
        return ReturnCodes.SUCCESS

    def execute(self, aid):
        log.debug("Agent go to active state")
        return ReturnCodes.SUCCESS

    def manage_resource(self):
        return ReturnCodes.SUCCESS

    # END PART2

    def quit(self):
        return ReturnCodes.SUCCESS


class DirectoryFacilitator(object):
    """
    A Directory Facilitator (DF) is a mandatory component of the AP.
    The DF provides yellow pages services to other agents.
    Agents may register their services with the DF or query
    the DF to find out what services are offered by other agents.
    Multiple DFs may exist within an AP and may be federated.
    """

    def register(self):
        return ReturnCodes.SUCCESS

    def deregister(self):
        return ReturnCodes.SUCCESS

    def modify(self):
        return ReturnCodes.SUCCESS

    def search(self):
        return ReturnCodes.SUCCESS


class MessageTransportService(object):
    """
    An Message Transport Service (MTS) is the default
    communication method between agents on different APs
    (see [FIPA00067]).
    """

    def deliverMessage(self, agent):
        """
        The MTS delivers messages to the agent as normal if it is in state
        active, if it is in state (Initiated/Waiting/Suspended) The MTS either
        buffers messages until the agent returns to the active state
        or forwards messages to a new location (if a forward is set for the agent)..
        :param agent:
        :return:
        """
        return ReturnCodes.SUCCESS

    def bufferMessage(self):
        return ReturnCodes.SUCCESS

"""
One or more transport-descriptions, each of which is a self describing structure containing a transport-type, 
a transport-specific-address and zero or more transport-specific-properties used to communicate with the agent
#self.locator = locator
"""