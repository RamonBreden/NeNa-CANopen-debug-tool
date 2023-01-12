#----------------------------------------------------------------------------------#
# Connecting, reading and writing from and to a CAN bus using the CANopen protocol #
#----------------------------------------------------------------------------------#
# Authors: Ramon Breden - Willem van Rossum                                        #
# Email: name.name@email.com - name.name@email.com                                 #
# Date: 21 December 2022                                                           #
# Version: 0.1 (IN DEVELOPMENT)                                                    #
#----------------------------------------------------------------------------------#
# Language: Python                                                                 #
# Required library: CANopen for Python                                             #
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
            A list with connected nodes
        """

        # This will attempt to read an SDO from nodes 1 - 127
        self.network.scanner.search()
        # We may need to wait a short while here to allow all nodes to respond
        time.sleep(0.05)

        # Add all nodes on the bus to this list
        node_list = []
        for node_id in self.network.scanner.nodes:
            node_list.append(node_id)

        return node_list

    def end_program(self):
        """This function terminates the established connection.
        (Disconnecting is not necessary, although it's best practice ;) )
        """
        self.network.disconnect()

    def upload(self, node_id, ob_id, sub_idx, write_val):
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

        # Connect to node
        wnode = self.network.add_node(node_id, "PD4E_test.eds", False)
        # Calculate the length of the write value in if writen as byte
        byte_length = write_val.bit_length() // 8 + (write_val.bit_length() % 8 > 0)
        # Convert int to bytes
        write_byte = write_val.to_bytes(byte_length, "little")
        # Send bytes to node
        wnode.sdo.download(ob_id, sub_idx, write_byte)

    #def rnode(self, node_id):
    #    # Connect to node
    #    rnode= self.network.add_node(node_id, "PD4E_test.eds", False)
        
    #    return rnode

    def download(self, node_id, ob_id, sub_idx):
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
        rnode= self.network.add_node(node_id, "PD4E_test.eds", False)
        # Read byte array from node
        read_byte = rnode.sdo.upload(ob_id, sub_idx)
        # Convert byte array to integer
        conv_int = int.from_bytes(read_byte, "little")

        return conv_int

    def disconnect(self):
        self.network.disconnect()


# TEST OF FUNCTIONS - REMOVE FOR FINAL APPLICATION
#p = CAN_COM('pcan', 'PCAN_USBBUS1', 250000)
#print(p.scan_bus())
#p.upload(41, 0x320E, 6, 800)

#time.sleep(1)

#print(p.download(41, 0x320E, 6))
#p.end_program()