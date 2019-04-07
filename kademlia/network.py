import hashlib, random, asyncio, uvloop
from aiorpc import register, serve, RPCClient

from kademlia.node import Node

class Network:
    def __init__(self, ip, port, nodes, k = 20, alpha = 3, id = None):
        self.k = k
        self.alpha = alpha
        self.node = Node(hashlib.sha1(str(random.getrandbits(255)).encode('utf8')).digest(), ip, port, k)
        loop = uvloop.new_event_loop()                          #TODO: decide movement to userspace
        asyncio.set_event_loop(loop)
        self.server = self.server_init(loop)
        loop.run_until_complete(self.bootstrap(nodes))
        loop.run_forever()

    def server_init(self, loop):
        register("ping", self.ping)
        register("find_value", self.find_value)
        register("find_node", self.find_node)
        register("store", self.store)
        return asyncio.start_server(serve, '127.0.0.1', 60000, loop=loop)

    async def client(self, addr, func, *args):
        async with RPCClient(addr[0], addr[1]) as client:       #TODO: test and fix problem with context managed RPCClient
            ret = await client.call(func.func_name, *args)
        return ret


    async def bootstrap(self, nodes):
        nodes = await asyncio.gather(*list(map(lambda addr: await self.client(self.ping, self.node.id, addr), nodes)))
        return await self.client(self.find, nodes)

    async def ping(self, id, ip, port):
        return self.node.id


    async def find_node(self, id):
        pass


    async def find_value(self, key):
        pass


    async def store(self, key, value):
        self.node.store(key, value)
        return True

    async def find(self, nodes):
        pass

    async def get(self, key):
        key = hashlib.sha1(key).digest()
        value =  self.node.retrieve(key)
        if value is None:
            value = self.client(self.find_value, key)
        return value