import pyinotify
from pathlib import Path


class Socket(pyinotify.ProcessEvent):

    """ Socket simulation uses a directory scanner for new incoming data simulation on files """

    def __init__(self):

        # The file used to scan and get new data
        self.file = None

        # A queue for new incoming data
        self.msg_queue = []

        # The socket begins the scanning for its file for new incoming data.
        self.listening = False

        # Used when text written into the file its new.
        # Allows the data flow blocking if not changed.
        self.is_ignored = True

        # watch_manager : It is the scanner for file changes.
        # Used when a new change is detected.
        # watch_manager along self.notifier detect changes,
        # update the queue, and set the new state.

        self.__init_scope()

        #
        watch_manager = pyinotify.WatchManager()
        watch_manager.add_watch(self.sockets_scope, pyinotify.IN_MODIFY)
        self.notifier = pyinotify.ThreadedNotifier(watch_manager, self)

    def __init_scope(self):
        """Initialize directories for scope of the sockets"""

        SOCKET_DIR = "active"
        self.sockets_scope = Path.joinpath(Path.cwd(), Path(SOCKET_DIR))

        if not Path.exists(self.sockets_scope):
            print("[Warn] Not found. Creating .active directory ...")
            Path.mkdir(self.sockets_scope)

    def bind(self, address, port):
        """ Asociate the addres and port with the socket. """

        self.address = "{}:{}".format(address, port)

        try:
            self.filepath = Path.joinpath(self.sockets_scope, self.address)
            self.file = open(self.filepath, 'x')
        except Exception as e:
            print("[Error] Socket in use {}".format(self.address))
            self.file = None

    def listen(self):
        """ The socket is now capable of detect changes of its respective file."""
        if self.file:
            self.listening = True
            self.notifier.start()
            print("[Info] Listening on {}".format(self.address))

    def accept(self):
        pass

    def close(self):
        """ Close the connection and removes the socket file. """
        if self.file:
            self.file.close()

        self.filepath.unlink()

    def send(self, data):
        with open(self.filepath, 'w') as file:
            file.write(data)

    def recv(self):

        # Guarrantee the queue has new data,
        # if it is not the case it will be blocked until new data is detected
        if self.listening:

            while self.is_ignored:
                # Blocking loop
                pass

            data = self.msg_queue[0]
            self.msg_queue = self.msg_queue[1:]

            self.is_ignored = True
            return data

        else:
            raise Exception('[Error] The socket is not listening')
            exit()

    def connect(self, address, port):
        """ Asociate the addres for use in remote mode. (read only) """
        address = "{}:{}".format(address, port)
        try:
        	self.filepath = Path.joinpath(self.sockets_scope, address)
        	self.file = open(self.filepath, 'r')
        	self.address = address
        except Exception as e:
            print("[Error] Could not connect to {}".format(address))

    def process_IN_MODIFY(self, event):
        if self.address == event.pathname.split('/')[-1]:

            with open(self.filepath, 'r') as file:
                data = file.read()
                self.msg_queue.append(data)

            # Unlock the receiver socket method
            self.is_ignored = False
