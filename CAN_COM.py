#----------------------------------------------------------------------------------#
# Connecting, reading and writing from and to a CAN bus using the CANopen protocol #
#----------------------------------------------------------------------------------#
# Authors: Ramon Breden - Willem van Rossum                                        #
# Date: 14 January 2023                                                            #
# Version: 0.1 (IN DEVELOPMENT)                                                    #
#----------------------------------------------------------------------------------#
# Language: Python                                                                 #
# Required libraries: canopen, time                                                #
#----------------------------------------------------------------------------------#

# IMPORTS
import canopen  # https://canopen.readthedocs.io/en/latest/
import time

class CAN_COM():
    """This class enables communication with a CAN bus using a CAN to USB adapter.
    """

    def __init__(self, bustype, channel, bitrate) -> None:
        """This function initializes a connection to a CAN bus 
        through a CAN to USB adapter.

        :param bustype:
            Type of bus to connect with, use 'pcan' for the PEAK adapter.
        :param channel:
            Channel to communicate over, use 'PCAN_USBBUS1' for the PEAK adapter.
        :param bitrate:
            Bitrate of the CAN bus in kbit/s. use 250000 for the NeNa system.
        """

        # Connect to the CAN network
        self.network = canopen.Network()
        self.network.connect(bustype=bustype, channel=channel, bitrate=bitrate)

    def scan_bus(self):
        """This function scans for nodes on the network and returns all
        found node ID's in a list.

        :return: 
            A list with responded nodes and a list with connected nodes
        """

        # This will attempt to read an SDO from nodes 1 - 127
        self.network.scanner.search()
        # We may need to wait a short while here to allow all nodes to respond
        time.sleep(0.05)

        # Add all responed nodes to a list and connect to all nodes 
        node_list = []
        node_added_list = []
        for node_id in self.network.scanner.nodes:
            node_added_list.append(self.network.add_node(node_id, "PD4E_test.eds", False))
            node_list.append(node_id)

        return node_list, node_added_list

    def upload(self, node_id, ob_id, sub_idx, write_val, node_added_list):
        """ This function writes an integer value to an object ID
        :param node_id:
            The node identifier (40 = right motor, 41 = left motor).
        :param ob_id:
            The object name in hex format: (0x....). See device documentation.
        :param sub_idx:
            The sub index of the object, if object has no sub indexes use 0.
        :param write_val:
            The value that should be written to the object ID (integer).
        """

        # Node selection to pull from node_added_list
        if node_id == 40:
            i = 0
        elif node_id == 41:
            i = 1

        wnode = node_added_list[i]
        # Calculate the length of the write value in if writen as byte
        byte_length = write_val.bit_length() // 8 + (write_val.bit_length() % 8 > 0)
        # Convert int to bytes
        write_byte = write_val.to_bytes(byte_length, "little")
        # Send bytes to node
        wnode.sdo.download(ob_id, sub_idx, write_byte)

    def download(self, node_id, ob_id, sub_idx, node_added_list):
        """ This function reads a byte array from an object ID 
        and converts it to an integer.
        :param node_id:
            The node identifier (40 = right motor, 41 = left motor).
        :param ob_id:
            The object name in hex format: (0x....). See device documentation.
        :param sub_idx:
            The sub index of the object, if object has no sub indexes use 0.
        :param write_val:
            The value that should be written to the object ID (integer).
        """

        # Node selection to pull from node_added_list
        if node_id == 40:
            i = 0
        elif node_id == 41:
            i = 1

        rnode= node_added_list[i]
        # Read byte array from node
        read_byte = rnode.sdo.upload(ob_id, sub_idx)
        # Convert byte array to integer
        conv_int = int.from_bytes(read_byte, "little")

        return conv_int

    def disconnect(self):
        """ This function disconnects the established connection.
        """
        self.network.disconnect()