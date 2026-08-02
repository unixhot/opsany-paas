"""
The MIT License (MIT)

Copyright (c)   2014 rescale
                2014 - 2016 Mohab Usama
"""

"""
Guacamole.Status.Code = {
    /**
     * The operation succeeded.
     *
     * @type {!number}
     */
    "SUCCESS": 0x0000, 0
    /**
     * The requested operation is unsupported.
     *
     * @type {!number}
     */
    "UNSUPPORTED": 0x0100, 256
    /**
     * The operation could not be performed due to an internal failure.
     *
     * @type {!number}
     */
    "SERVER_ERROR": 0x0200, 512
    /**
     * The operation could not be performed as the server is busy.
     *
     * @type {!number}
     */
    "SERVER_BUSY": 0x0201, 513
    /**
     * The operation could not be performed because the upstream server is not
     * responding.
     *
     * @type {!number}
     */
    "UPSTREAM_TIMEOUT": 0x0202, 514
    /**
     * The operation was unsuccessful due to an error or otherwise unexpected
     * condition of the upstream server.
     *
     * @type {!number}
     */
    "UPSTREAM_ERROR": 0x0203, 515
    /**
     * The operation could not be performed as the requested resource does not
     * exist.
     *
     * @type {!number}
     */
    "RESOURCE_NOT_FOUND": 0x0204, 516
    /**
     * The operation could not be performed as the requested resource is
     * already in use.
     *
     * @type {!number}
     */
    "RESOURCE_CONFLICT": 0x0205,517
    /**
     * The operation could not be performed as the requested resource is now
     * closed.
     *
     * @type {!number}
     */
    "RESOURCE_CLOSED": 0x0206, 518
    /**
     * The operation could not be performed because the upstream server does
     * not appear to exist.
     *
     * @type {!number}
     */
    "UPSTREAM_NOT_FOUND": 0x0207, 519
    /**
     * The operation could not be performed because the upstream server is not
     * available to service the request.
     *
     * @type {!number}
     */
    "UPSTREAM_UNAVAILABLE": 0x0208, 520
    /**
     * The session within the upstream server has ended because it conflicted
     * with another session.
     *
     * @type {!number}
     */
    "SESSION_CONFLICT": 0x0209, 521
    /**
     * The session within the upstream server has ended because it appeared to
     * be inactive.
     *
     * @type {!number}
     */
    "SESSION_TIMEOUT": 0x020A, 522
    /**
     * The session within the upstream server has been forcibly terminated.
     *
     * @type {!number}
     */
    "SESSION_CLOSED": 0x020B, 523
    /**
     * The operation could not be performed because bad parameters were given.
     *
     * @type {!number}
     */
    "CLIENT_BAD_REQUEST": 0x0300, 768
    /**
     * Permission was denied to perform the operation, as the user is not yet
     * authorized (not yet logged in, for example).
     *
     * @type {!number}
     */
    "CLIENT_UNAUTHORIZED": 0x0301, 769
    /**
     * Permission was denied to perform the operation, and this permission will
     * not be granted even if the user is authorized.
     *
     * @type {!number}
     */
    "CLIENT_FORBIDDEN": 0x0303, 771
    /**
     * The client took too long to respond.
     *
     * @type {!number}
     */
    "CLIENT_TIMEOUT": 0x0308, 776
    /**
     * The client sent too much data.
     *
     * @type {!number}
     */
    "CLIENT_OVERRUN": 0x030D, 781
    /**
     * The client sent data of an unsupported or unexpected type.
     *
     * @type {!number}
     */
    "CLIENT_BAD_TYPE": 0x030F, 783
    /**
     * The operation failed because the current client is already using too
     * many resources.
     *
     * @type {!number}
     */
    "CLIENT_TOO_MANY": 0x031D 797
};

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
            # 设置非阻塞超时，避免 recv() 永久阻塞
            self._client.settimeout(self.timeout)

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
                try:
                    buf = self.client.recv(BUF_LEN)
                except socket.error:
                    # 另一个线程关闭了 socket（比如 disconnect），不打印噪音日志
                    self.close()
                    return None
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
