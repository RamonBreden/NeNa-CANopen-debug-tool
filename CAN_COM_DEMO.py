import time
import numpy as np

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
        # Check if the variables have a value
        if bustype is None:
            raise ValueError('bustype variable has no value')
        if channel is None:
            raise ValueError('channel variable has no value')
        if bitrate is None:
            raise ValueError('bitrate variable has no value')

    def scan_bus(self):
        """This function scans for nodes on the network and returns all
        found node ID's in a list.

        :return: 
            A list with connected nodes
        """

        # Add all nodes on the bus to this list
        node_list = [40, 41]

        return node_list

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
        wnode = node_id
        # Calculate the length of the write value in if writen as byte
        byte_length = write_val.bit_length() // 8 + (write_val.bit_length() % 8 > 0)
        # Convert int to bytes
        write_byte = write_val.to_bytes(byte_length, "little")
        # Send bytes to node
        print("Written ", write_byte, "to node ", wnode, "to object id ", ob_id, "with a subindex of", sub_idx)

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

        # twee verschillende datastreams
        if node_id == 40 and ob_id == 6045 and sub_idx == 0:
            return np.random.normal(size=300)
        elif node_id == 40 and ob_id == 6046 and sub_idx == 0:
            return np.random.normal(size=200)
        else:
            return "Invalid Input"