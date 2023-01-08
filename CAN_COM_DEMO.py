import time

class CAN_COM():
    """This class enables communication with a CAN bus using a CAN to USB adapter.
    """

    # Heb hier de init verwijderd, misschien dat dat problemen gaat geven

    def scan_bus(self):
        """This function scans for nodes on the network and returns all
        found node ID's in a list.

        :return: 
            A list with connected nodes
        """
        
        # Even wachten
        time.sleep(0.5)

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
        # Deze moet ik nog fixen!
        # Connect to node
        rnode= self.network.add_node(node_id, "PD4E_test.eds", False)
        # Read byte array from node
        read_byte = rnode.sdo.upload(ob_id, sub_idx)
        # Convert byte array to integer
        conv_int = int.from_bytes(read_byte, "little")
        return conv_int