# mqtt_as.py Asynchronous version of umqtt.robust
# (C) Copyright Peter Hinch 2017-2023.
# Released under the MIT licence.

# Pyboard D support added also RP2/default
# Various improvements contributed by Kevin Köck.

import gc
import time
from sys import platform

import aioespnow
import network
import uasyncio as asyncio
import usocket as socket
import ustruct as struct
from machine import unique_id
from micropython import const
from ubinascii import hexlify
from uerrno import EINPROGRESS, ETIMEDOUT
from utime import ticks_diff, ticks_ms

gc.collect()

VERSION = (0, 7, 1)

# Default short delay for good SynCom throughput (avoid sleep(0) with SynCom).
_DEFAULT_MS = const(20)
_SOCKET_POLL_DELAY = const(5)  # 100ms added greatly to publish latency

# Legitimate errors while waiting on a socket. See uasyncio __init__.py
# open_connection().
ESP32 = platform == "esp32"
RP2 = platform == "rp2"

if ESP32:
    BUSY_ERRORS = [
        EINPROGRESS,
        ETIMEDOUT,
        118,  # Weird ESP32 error
        119,
    ]
elif RP2:
    BUSY_ERRORS = [EINPROGRESS, ETIMEDOUT, -110]
else:
    BUSY_ERRORS = [EINPROGRESS, ETIMEDOUT]

ESP8266 = platform == "esp8266"
PYBOARD = platform == "pyboard"


# Default "do little" coroutine for optional user replacement
async def eliza(*_):
    """Example: set_wifi_handler(coro) - see test program."""
    await asyncio.sleep_ms(_DEFAULT_MS)


class MsgQueue:
    def __init__(self, size):
        self._q = [0 for _ in range(max(size, 4))]
        self._size = size
        self._wi = 0
        self._ri = 0
        self._evt = asyncio.Event()
        self.discards = 0

    def put(self, *v):
        self._q[self._wi] = v
        self._evt.set()
        self._wi = (self._wi + 1) % self._size
        if self._wi == self._ri:  # Would indicate empty
            self._ri = (self._ri + 1) % self._size
            self.discards += 1

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._ri == self._wi:  # Empty
            self._evt.clear()
            await self._evt.wait()
        r = self._q[self._ri]
        self._ri = (self._ri + 1) % self._size
        return r


config = {
    "client_id": hexlify(unique_id()),
    "server": None,
    "port": 0,
    "user": "",
    "password": "",
    "keepalive": 60,
    "ping_interval": 0,
    "ssl": False,
    "ssl_params": {},
    "response_time": 10,
    "clean_init": True,
    "clean": True,
    "max_repubs": 4,
    "will": None,
    "subs_cb": lambda *_: None,
    "wifi_coro": eliza,
    "connect_coro": eliza,
    "ssid": None,
    "wifi_pw": None,
    "queue_len": 0,
    "gateway": False,
}


class MQTTException(Exception):
    pass


def pid_gen():
    """Generator for packet IDs."""
    pid = 0
    while True:
        pid = pid + 1 if pid < 65535 else 1
        yield pid


def qos_check(qos):
    if qos not in {0, 1}:
        raise ValueError("Only qos 0 and 1 are supported.")


class MQTT_base:
    """Handles core MQTT protocol, WiFi and broker connectivity is handled by
    MQTTClient subclass."""

    REPUB_COUNT = 0  # For debug or tests
    DEBUG = False

    def __init__(self, config):
        self._events = config["queue_len"] > 0
        self._client_id = config["client_id"]
        self._user = config["user"]
        self._pswd = config["password"]
        self._keepalive = config["keepalive"]
        if self._keepalive >= 65536:
            raise ValueError("Invalid keepalive time")

        self._response_time = config["response_time"] * 1000
        self._max_repubs = config["max_repubs"]
        self._clean_init = config["clean_init"]
        self._clean = config["clean"]

        will = config["will"]
        if will is None:
            self._lw_topic = False
        else:
            self._set_last_will(*will)

        # WiFi config
        self._ssid = config["ssid"]
        self._wifi_pw = config["wifi_pw"]
        self._ssl = config["ssl"]
        self._ssl_params = config["ssl_params"]

        # Callbacks and coroutines
        if self._events:
            self.up = asyncio.Event()
            self.down = asyncio.Event()
            self.queue = MsgQueue(config["queue_len"])
        else:
            self._cb = config["subs_cb"]
            self._wifi_handler = config["wifi_coro"]
            self._connect_handler = config["connect_coro"]

        # Network settings
        self.port = config["port"] or (8883 if self._ssl else 1883)
        self.server = config["server"]
        if self.server is None:
            raise ValueError("No server specified.")

        self._sock = None
        self._sta_if = network.WLAN(network.STA_IF)
        self._sta_if.active(True)

        if config["gateway"]:  # Called from gateway (hence ESP32).

            while not (sta := self._sta_if).active():
                time.sleep(0.1)
            sta.config(pm=sta.PM_NONE)  # No power management
            sta.active(True)
            self._espnow = aioespnow.AIOESPNow()
            self._espnow.active(True)

        self.newpid = pid_gen()
        self.rcv_pids = set()  # PUBACK and SUBACK pids awaiting ACK response
        self.last_rx = ticks_ms()
        self.lock = asyncio.Lock()

    def _set_last_will(self, topic, msg, retain=False, qos=0):
        qos_check(qos)
        if not topic:
            raise ValueError("Empty topic.")
        self._lw_topic = topic
        self._lw_msg = msg
        self._lw_qos = qos
        self._lw_retain = retain

    def dprint(self, msg, *args):
        if self.DEBUG:
            print(msg % args)

    def _timeout(self, t):
        return ticks_diff(ticks_ms(), t) > self._response_time

    async def _as_read(self, n, sock=None):
        """Asynchronous read of n bytes from socket."""
        if sock is None:
            sock = self._sock
        data = bytearray(n)
        buff = memoryview(data)
        size = 0
        t = ticks_ms()

        while size < n:
            if self._timeout(t) or not self.isconnected():
                raise OSError(-1, "Timeout on socket read")
            try:
                msg_size = sock.readinto(buff[size:], n - size)
            except OSError as e:
                msg_size = None
                if e.args[0] not in BUSY_ERRORS:
                    raise
            if msg_size == 0:
                raise OSError(-1, "Connection closed by host")
            if msg_size is not None:
                size += msg_size
                t = ticks_ms()
                self.last_rx = ticks_ms()
            await asyncio.sleep_ms(_SOCKET_POLL_DELAY)
        return data

    async def _as_write(self, bytes_wr, length=0, sock=None):
        """Asynchronous write of up to 'length' bytes to socket."""
        if sock is None:
            sock = self._sock

        bytes_wr = memoryview(bytes_wr)
        if length:
            bytes_wr = bytes_wr[:length]

        t = ticks_ms()
        while bytes_wr:
            if self._timeout(t) or not self.isconnected():
                raise OSError(-1, "Timeout on socket write")
            try:
                n = sock.write(bytes_wr)
            except OSError as e:
                n = 0
                if e.args[0] not in BUSY_ERRORS:
                    raise
            if n:
                t = ticks_ms()
                bytes_wr = bytes_wr[n:]
            await asyncio.sleep_ms(_SOCKET_POLL_DELAY)

    async def _send_str(self, s):
        await self._as_write(struct.pack("!H", len(s)))
        await self._as_write(s)

    async def _recv_len(self):
        """Receive length from MQTT variable-length integer."""
        n = 0
        shift = 0
        while True:
            res = await self._as_read(1)
            b = res[0]
            n |= (b & 0x7F) << shift
            if not b & 0x80:
                return n
            shift += 7

    async def _connect(self, clean):
        self._sock = socket.socket()
        self._sock.setblocking(False)
        try:
            self._sock.connect(self._addr)
        except OSError as e:
            if e.args[0] not in BUSY_ERRORS:
                raise

        await asyncio.sleep_ms(_DEFAULT_MS)
        self.dprint("Connecting to broker.")

        if self._ssl:
            import ssl

            self._sock = ssl.wrap_socket(self._sock, **self._ssl_params)

        premsg = bytearray(b"\x10\0\0\0\0\0")
        msg = bytearray(b"\x04MQTT\x04\0\0\0")  # Protocol 3.1.1

        sz = 10 + 2 + len(self._client_id)
        msg[6] = clean << 1

        if self._user:
            sz += 2 + len(self._user) + 2 + len(self._pswd)
            msg[6] |= 0xC0

        if self._keepalive:
            msg[7] |= self._keepalive >> 8
            msg[8] |= self._keepalive & 0x00FF

        if self._lw_topic:
            sz += 2 + len(self._lw_topic) + 2 + len(self._lw_msg)
            msg[6] |= 0x4 | (self._lw_qos & 0x1) << 3
            msg[6] |= (self._lw_qos & 0x2) << 3
            msg[6] |= self._lw_retain << 5

        i = 1
        while sz > 0x7F:
            premsg[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz
        await self._as_write(premsg, i + 2)
        await self._as_write(msg)
        await self._send_str(self._client_id)

        if self._lw_topic:
            await self._send_str(self._lw_topic)
            await self._send_str(self._lw_msg)
        if self._user:
            await self._send_str(self._user)
            await self._send_str(self._pswd)

        resp = await self._as_read(4)
        self.dprint("Connected to broker.")  # Got CONNACK
        # Bad CONNACK e.g. authentication fail
        if resp[3] != 0 or resp[0] != 0x20 or resp[1] != 0x02:
            code = f"0x{(resp[0] << 8) + resp[1]:04x} {resp[3]}"
            raise OSError(-1, f"Connect fail: {code} (README 7)")

    async def _ping(self):
        async with self.lock:
            await self._as_write(b"\xc0\0")

    async def wan_ok(
        self,
        packet=(
            b"$\x1a\x01\x00\x00\x01\x00\x00\x00"
            b"\x00\x00\x00\x03www\x06google\x03com\x00"
            b"\x00\x01\x00\x01"
        ),
    ):
        """Check internet connectivity by sending DNS lookup to 8.8.8.8."""
        if not self.isconnected():  # WiFi down
            return False
        length = 32
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(False)
        s.connect(("8.8.8.8", 53))
        await asyncio.sleep(1)
        try:
            await self._as_write(packet, sock=s)
            await asyncio.sleep(2)
            res = await self._as_read(length, s)
            if len(res) == length:
                return True
        except OSError:
            return False
        finally:
            s.close()
        return False

    async def broker_up(self):
        """Test if broker is responding."""
        if not self.isconnected():
            return False
        tlast = self.last_rx
        if ticks_diff(ticks_ms(), tlast) < 1000:
            return True
        try:
            await self._ping()
        except OSError:
            return False
        t = ticks_ms()
        while not self._timeout(t):
            await asyncio.sleep_ms(100)
            if ticks_diff(self.last_rx, tlast) > 0:
                return True
        return False

    async def disconnect(self):
        """Disconnect from broker, keep socket open for 100ms."""
        if self._sock is not None:
            await self._kill_tasks(False)
            try:
                async with self.lock:
                    self._sock.write(b"\xe0\0")
                    await asyncio.sleep_ms(100)
            except OSError:
                pass
            self._close()
        self._has_connected = False

    def _close(self):
        if self._sock is not None:
            self._sock.close()

    def close(self):
        """API close. See:
        https://github.com/peterhinch/micropython-mqtt/issues/60"""
        self._close()
        try:
            self._sta_if.disconnect()
        except OSError:
            self.dprint("Wi-Fi not started, unable to disconnect interface")
        self._sta_if.active(False)

    async def _await_pid(self, pid):
        """Wait for PID to appear in self.rcv_pids, or time out."""
        t = ticks_ms()
        while pid in self.rcv_pids:
            if self._timeout(t) or not self.isconnected():
                break
            await asyncio.sleep_ms(100)
        else:
            return True
        return False

    async def publish(self, topic, msg, retain, qos):
        """Publish message with optional QoS 1. Retry if no PUBACK."""
        pid = next(self.newpid)
        if qos:
            self.rcv_pids.add(pid)
        async with self.lock:
            await self._publish(topic, msg, retain, qos, 0, pid)
        if qos == 0:
            return

        count = 0
        while True:
            if await self._await_pid(pid):
                return
            if count >= self._max_repubs or not self.isconnected():
                raise OSError(-1)
            async with self.lock:
                await self._publish(topic, msg, retain, qos, 1, pid)
            count += 1
            self.REPUB_COUNT += 1

    async def _publish(self, topic, msg, retain, qos, dup, pid):
        """Core publish method. Called by publish() with or without DUP."""
        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain | dup << 3
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        if sz >= 2097152:
            raise MQTTException("Strings too long.")
        i = 1
        while sz > 0x7F:
            pkt[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        await self._as_write(pkt, i + 1)
        await self._send_str(topic)
        if qos > 0:
            struct.pack_into("!H", pkt, 0, pid)
            await self._as_write(pkt, 2)
        await self._as_write(msg)

    async def subscribe(self, topic, qos):
        """Subscribe with optional QoS."""
        pkt = bytearray(b"\x82\0\0\0")
        pid = next(self.newpid)
        self.rcv_pids.add(pid)
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, pid)
        async with self.lock:
            await self._as_write(pkt)
            await self._send_str(topic)
            await self._as_write(qos.to_bytes(1, "little"))
        if not await self._await_pid(pid):
            raise OSError(-1)

    async def unsubscribe(self, topic):
        """Unsubscribe from topic."""
        pkt = bytearray(b"\xa2\0\0\0")
        pid = next(self.newpid)
        self.rcv_pids.add(pid)
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic), pid)
        async with self.lock:
            await self._as_write(pkt)
            await self._send_str(topic)
        if not await self._await_pid(pid):
            raise OSError(-1)

    async def wait_msg(self):
        """Wait for one incoming MQTT message."""
        try:
            res = self._sock.read(1)  # Throws OSError on WiFi fail
        except OSError as e:
            if e.args[0] in BUSY_ERRORS:
                await asyncio.sleep_ms(0)
                return
            raise
        if res is None:
            return
        if res == b"":
            raise OSError(-1, "Empty response")

        if res == b"\xd0":  # PINGRESP
            await self._as_read(1)
            return
        op = res[0]

        if op == 0x40:  # PUBACK
            sz = await self._as_read(1)
            if sz != b"\x02":
                raise OSError(-1, "Invalid PUBACK packet")
            rcv_pid = await self._as_read(2)
            pid = rcv_pid[0] << 8 | rcv_pid[1]
            if pid in self.rcv_pids:
                self.rcv_pids.discard(pid)
            else:
                raise OSError(-1, "Invalid pid in PUBACK packet")

        if op == 0x90:  # SUBACK
            resp = await self._as_read(4)
            if resp[3] == 0x80:
                raise OSError(-1, "Invalid SUBACK packet")
            pid = resp[2] | (resp[1] << 8)
            if pid in self.rcv_pids:
                self.rcv_pids.discard(pid)
            else:
                raise OSError(-1, "Invalid pid in SUBACK packet")

        if op == 0xB0:  # UNSUBACK
            resp = await self._as_read(3)
            pid = resp[2] | (resp[1] << 8)
            if pid in self.rcv_pids:
                self.rcv_pids.discard(pid)
            else:
                raise OSError(-1)

        # If not Publish, bail out
        if op & 0xF0 != 0x30:
            return

        sz = await self._recv_len()
        topic_len = await self._as_read(2)
        t_len = (topic_len[0] << 8) | topic_len[1]
        topic = await self._as_read(t_len)
        sz -= t_len + 2
        pid = None
        if op & 6:  # QoS
            pid_bytes = await self._as_read(2)
            pid = pid_bytes[0] << 8 | pid_bytes[1]
            sz -= 2
        msg = await self._as_read(sz)
        retained = bool(op & 0x01)

        if self._events:
            self.queue.put(topic, msg, retained)
        else:
            self._cb(topic, msg, retained)

        # QoS 1
        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")
            struct.pack_into("!H", pkt, 2, pid)
            await self._as_write(pkt)
        elif op & 6 == 4:  # qos 2 not supported
            raise OSError(-1, "QoS 2 not supported")


class MQTTClient(MQTT_base):
    """Handles issues relating to WiFi connectivity & broker re-connects."""

    def __init__(self, config):
        super().__init__(config)
        self._isconnected = False
        keepalive_ms = 1000 * self._keepalive
        self._ping_interval = keepalive_ms // 4 if keepalive_ms else 20000
        p_i = config["ping_interval"] * 1000
        if p_i and p_i < self._ping_interval:
            self._ping_interval = p_i
        self._in_connect = False
        self._has_connected = False
        self._tasks = []

        if ESP8266:
            import esp

            esp.sleep_type(0)  # Improve connection integrity at cost of power

    async def wifi_connect(self, quick=False):
        """Connect to WiFi, optionally skipping reliability checks."""
        s = self._sta_if
        if ESP8266:
            if s.isconnected():
                return
            s.active(True)
            s.connect()
            for _ in range(60):
                if s.status() != network.STAT_CONNECTING:
                    break
                await asyncio.sleep(1)
            if s.status() == network.STAT_CONNECTING:
                s.disconnect()
                await asyncio.sleep(1)
            if not s.isconnected() and self._ssid and self._wifi_pw:
                s.connect(self._ssid, self._wifi_pw)
                while s.status() == network.STAT_CONNECTING:
                    await asyncio.sleep(1)
        else:
            s.active(True)
            if RP2:  # Disable auto-sleep
                s.config(pm=0xA11140)
            s.connect(self._ssid, self._wifi_pw)
            for _ in range(60):
                await asyncio.sleep(1)
                if s.isconnected():
                    break
                if ESP32:
                    if s.status() != network.STAT_CONNECTING:
                        break
                elif PYBOARD:
                    if not 1 <= s.status() <= 2:
                        break
                elif RP2:
                    if not 1 <= s.status() <= 2:
                        break
            else:
                s.disconnect()
                await asyncio.sleep(1)

        if not s.isconnected():
            raise OSError("Wi-Fi connect timed out")

        if not quick:
            self.dprint("Checking WiFi integrity.")
            for _ in range(5):
                if not s.isconnected():
                    raise OSError("Connection Unstable")
                await asyncio.sleep(1)
            self.dprint("Got reliable connection")

    async def connect(self, *, quick=False):
        """Connect to MQTT broker, optionally skipping reliability checks."""
        if not self._has_connected:
            await self.wifi_connect(quick)
            self._addr = socket.getaddrinfo(self.server, self.port)[0][-1]

        self._in_connect = True
        try:
            if not self._has_connected and self._clean_init and not self._clean:
                await self._connect(True)
                try:
                    async with self.lock:
                        self._sock.write(b"\xe0\0")
                except OSError:
                    pass
                self.dprint("Waiting for disconnect")
                await asyncio.sleep(2)
                self.dprint("About to reconnect with unclean session.")

            await self._connect(self._clean)

        except Exception:
            self._close()
            self._in_connect = False
            raise

        self.rcv_pids.clear()
        self._isconnected = True
        self._in_connect = False

        if not self._events:
            asyncio.create_task(self._wifi_handler(True))
        if not self._has_connected:
            self._has_connected = True
            asyncio.create_task(self._keep_connected())

        asyncio.create_task(self._handle_msg())
        self._tasks.append(asyncio.create_task(self._keep_alive()))
        if self.DEBUG:
            self._tasks.append(asyncio.create_task(self._memory()))

        if self._events:
            self.up.set()
        else:
            asyncio.create_task(self._connect_handler(self))

    async def _handle_msg(self):
        """Continuously read incoming messages until connectivity fails."""
        try:
            while self.isconnected():
                async with self.lock:
                    await self.wait_msg()
                await asyncio.sleep_ms(_DEFAULT_MS)
        except OSError:
            pass
        self._reconnect()

    async def _keep_alive(self):
        """Send periodic PINGREQs to keep broker connection alive."""
        while self.isconnected():
            pings_due = ticks_diff(ticks_ms(), self.last_rx) // self._ping_interval
            if pings_due >= 4:
                self.dprint("Reconnect: broker fail.")
                break
            await asyncio.sleep_ms(self._ping_interval)
            try:
                await self._ping()
            except OSError:
                break
        self._reconnect()

    async def _kill_tasks(self, kill_skt):
        """Cancel running tasks and optionally close the socket."""
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()
        await asyncio.sleep_ms(0)
        if kill_skt:
            self._close()

    async def _memory(self):
        """Debug task to show RAM usage periodically."""
        while True:
            await asyncio.sleep(20)
            gc.collect()
            self.dprint("RAM free %d alloc %d", gc.mem_free(), gc.mem_alloc())

    def isconnected(self):
        """Check if WiFi and broker connection is alive."""
        if self._in_connect:
            return True
        if self._isconnected and not self._sta_if.isconnected():
            self._reconnect()
        return self._isconnected

    def _reconnect(self):
        """Schedule reconnection if not already in progress."""
        if self._isconnected:
            self._isconnected = False
            asyncio.create_task(self._kill_tasks(True))
            if self._events:
                self.down.set()
            else:
                asyncio.create_task(self._wifi_handler(False))

    async def _connection(self):
        """Await broker connection."""
        while not self._isconnected:
            await asyncio.sleep(1)

    async def _keep_connected(self):
        """Maintains WiFi & broker connectivity, reconnect if link goes down."""
        while self._has_connected:
            if self.isconnected():
                await asyncio.sleep(1)
                gc.collect()
            else:
                try:
                    self._sta_if.disconnect()
                except OSError:
                    self.dprint("Wi-Fi not started, unable to disconnect interface")
                await asyncio.sleep(1)
                try:
                    await self.wifi_connect()
                except OSError:
                    continue
                if not self._has_connected:
                    self.dprint("Disconnected, exiting _keep_connected")
                    break
                try:
                    await self.connect()
                    self.dprint("Reconnect OK!")
                except OSError as e:
                    self.dprint("Error in reconnect. %s", e)
                    self._close()
                    self._in_connect = False
                    self._isconnected = False
        self.dprint("Disconnected, exited _keep_connected")

    async def subscribe(self, topic, qos=0):
        """Subscribe with QoS 0 or 1."""
        qos_check(qos)
        while True:
            await self._connection()
            try:
                return await super().subscribe(topic, qos)
            except OSError:
                pass
            self._reconnect()

    async def unsubscribe(self, topic):
        """Unsubscribe from topic."""
        while True:
            await self._connection()
            try:
                return await super().unsubscribe(topic)
            except OSError:
                pass
            self._reconnect()

    async def publish(self, topic, msg, retain=False, qos=0):
        """Publish with optional retain/QoS."""
        qos_check(qos)
        while True:
            await self._connection()
            try:
                return await super().publish(topic, msg, retain, qos)
            except OSError:
                pass
            self._reconnect()
