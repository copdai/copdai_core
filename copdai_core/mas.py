from copdai_core.commun import ReturnCodes
from enum import Enum, unique

@unique
class AgentState(Enum):

    """Normal agent life cycle FIPA specification"""

    UNKNOWN = 0
    INITIATED = 1
    ACTIVE = 2
    SUSPENDED = 3
    WAITING = 4
    TRANSIT = 5

class Agent(object):
    """
    An Agent is the fundamental actor on an AP which
    combines one or more service capabilities into a
    unified and integrated execution model that may
    include access to external software, human users and
    communications facilities.
    An agent may have certain resource brokering capabilities
    for accessing software (see [FIPA00079]).
    """

    def __init__(self):
        self.state = AgentState.UNKNOWN

    def invoke(self):
        print("Agent go to active state")
        self.state = AgentState.ACTIVE
        return ReturnCodes.SUCCESS

    def suspend(self):
        print("Agent go to suspend state")
        self.state = AgentState.SUSPENDED
        return ReturnCodes.SUCCESS

    def wait(self):
        print("Agent go to wait state")
        self.state = AgentState.WAITING
        return ReturnCodes.SUCCESS

    def wakeup(self):
        print("Agent go to active state")
        self.state = AgentState.ACTIVE
        return ReturnCodes.SUCCESS

    def move(self):
        print("Agent go to transit state")
        self.state = AgentState.TRANSIT
        return ReturnCodes.SUCCESS

    def execute(self):
        print("Agent go to active state")
        self.state = AgentState.ACTIVE
        return ReturnCodes.SUCCESS

    #TODO state destroy and create


class AgentPlatform(object):
    """
    Agents exist physically on an AP and utilise the facilities offered
    by the AP for realising their functionalities.
    """

    def __init__(self, uid):
        self.uid = uid

class AgentManagementSystem(object):
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
        return ReturnCodes.SUCCESS

    # END PART1

    # PART2 : AMS can instruct the underlying AP to perform the following operations
    def invoke(self):
        print("Agent go to active state")
        return ReturnCodes.SUCCESS

    def suspend(self):
        print("Agent go to suspend state")
        return ReturnCodes.SUCCESS

    def terminate(self):
        print("Agent go to unkowen  state")
        return ReturnCodes.SUCCESS

    def resume(self):
        print("Agent go to active  state")
        return ReturnCodes.SUCCESS

    def create(self):
        print("Creating agent")
        return ReturnCodes.SUCCESS

    def execute(self):
        print("Agent go to active state")
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