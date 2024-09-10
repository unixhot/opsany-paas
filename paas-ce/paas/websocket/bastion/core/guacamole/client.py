"""
The MIT License (MIT)

Copyright (c)   2014 rescale
                2014 - 2016 Mohab Usama
"""

import socket
import logging

from bastion.core.guacamole.exceptions import GuacamoleError

from bastion.core.guacamole.instruction import INST_TERM
from bastion.core.guacamole.instruction import GuacamoleInstruction as Instruction

# supported protocols
PROTOCOLS = ('vnc', 'rdp', 'ssh', 'telnet')

PROTOCOL_NAME = 'guacamole'

BUF_LEN = 4096

guac_logger = logging.getLogger('django.server')
guac_logger.setLevel(logging.INFO)


class GuacamoleClient(object):
    """Guacamole Client class."""

    def __init__(self, host, port, timeout=20, debug=False, logger=None):
        """
        Guacamole Client class. This class can handle communication with guacd
        server.

        :param host: guacd server host.

        :param port: guacd server port.

        :param timeout: socket connection timeout.

        :param debug: if True, default logger will switch to Debug level.
        """
        self.host = host
        self.port = port
        self.timeout = timeout

        self._client = None

        # handshake established?
        self.connected = False

        # Receiving buffer
        self._buffer = bytearray()

        # Client ID
        self._id = None

        self.logger = guac_logger
        if logger:
            self.logger = logger

        if debug:
            self.logger.setLevel(logging.debug)


    @property
    def client(self):
        """
        Socket connection.
        """
        if not self._client:
            self._client = socket.create_connection(
                (self.host, self.port), self.timeout)

        return self._client

    @property
    def id(self):
        """Return client id"""
        return self._id

    def close(self):
        """
        Terminate connection with Guacamole guacd server.
        """
        self.client.close()
        self._client = None
        self.connected = False
        self.logger.debug('Connection closed.')

    def receive(self):
        """
        Receive instructions from Guacamole guacd server.
        """
        start = 0

        while True:
            idx = self._buffer.find(INST_TERM.encode(), start)
            if idx != -1:
                # instruction was fully received!
                line = self._buffer[:idx + 1].decode()
                self._buffer = self._buffer[idx + 1:]
                self.logger.debug('Received instruction: %s' % line)
                return line
            else:
                start = len(self._buffer)
                # we are still waiting for instruction termination
                buf = self.client.recv(BUF_LEN)
                if not buf:
                    # No data recieved, connection lost?!
                    self.close()
                    return None
                self._buffer.extend(buf)

    def send(self, data):
        """
        Send encoded instructions to Guacamole guacd server.
        """
        if not isinstance(data, bytes):
            data = data.encode()
        self.client.sendall(data)

    def read_instruction(self):
        """
        Read and decode instruction.
        """
        return Instruction.load(self.receive())

    def send_instruction(self, instruction):
        """
        Send instruction after encoding.
        """
        return self.send(instruction.encode())

    def handshake(self, protocol='vnc', width=1920, height=1080, dpi=96,
                  audio=None, video=None, image=None, **kwargs):
        """
        Establish connection with Guacamole guacd server via handshake.

        """
        if protocol not in PROTOCOLS and 'connectionid' not in kwargs:
            raise GuacamoleError('Cannot start Handshake. '
                                 'Missing protocol or connectionid.')

        if audio is None:
            audio = list()

        if video is None:
            video = list()

        if image is None:
            image = list()

        if 'connectionid' in kwargs:
            self.send_instruction(Instruction('select',
                                              kwargs.get('connectionid')))
        else:
            self.send_instruction(Instruction('select', protocol))

        instruction = self.read_instruction()

        if not instruction:
            self.close()
            raise GuacamoleError(
                'Cannot establish Handshake. Connection Lost!')

        if instruction.opcode != 'args':
            self.close()
            raise GuacamoleError(
                'Cannot establish Handshake. Expected opcode `args`, '
                'received `%s` instead.' % instruction.opcode)

        self.send_instruction(Instruction('size', width, height, dpi))

        self.send_instruction(Instruction('audio', *audio))

        self.send_instruction(Instruction('video', *video))

        self.send_instruction(Instruction('image', *image))

        # 4. Send `connect` instruction with proper values
        connection_args = [
            kwargs.get(arg.replace('-', '_'), '') for arg in instruction.args
        ]

        self.send_instruction(Instruction('connect', *connection_args))

        # 5. Receive ``ready`` instruction, with client ID.
        instruction = self.read_instruction()

        if instruction.opcode != 'ready':
            self.logger.warning(
                'Expected `ready` instruction, received: %s instead')

        if instruction.args:
            self._id = instruction.args[0]

        self.connected = True
