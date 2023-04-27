
import websockets
import asyncio
import multiprocessing
import json
import logging
import socket


class WebSocketProcess(multiprocessing.Process):
    def __init__(self, mpid, pipe, ip, port):
        multiprocessing.Process.__init__(self)
        self.logger = logging.getLogger(__name__)
        # Process ID
        self.mpid = mpid
        # Communication port to allow for communication with other WebSocketProcess
        self.pipe = pipe
        # WebSocket port (e.g. 5555)
        self.port = port
        # Bind to specified IP address, if provided, otherwise bind to any address
        self.ip = ip
        # Get nice name (e.g. "SensorStream")
        self.name = self.__class__.__name__

    
    def server(self):
        ADDR =(self.ip, self.port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(ADDR)
        self.logger.info('entered')
        asyncio.get_event_loop().run_until_complete(self.main(server))
        asyncio.get_event_loop().run_forever()

    def run(self):

        self.logger.info("Starting " + self.name + " process at " + str(self.ip) + ":" + str(self.port))
        # Start the WebSocket server, run the main() function
        
        try:
            # task1 = asyncio.get_event_loop().create_task(self.awaiting())
            proc = multiprocessing.Process(target=self.server)
            proc.start()
            
            asyncio.run(self.awaiting())
            proc.join()
        except multiprocessing.ProcessError:
            proc.terminate()
            #task1.cancel()
            self.logger.info("Exiting " + self.name + " process")
        
    async def awaiting(self):
        pass
  
