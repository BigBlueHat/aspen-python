from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pytest import raises

from aspen.sockets import FFFD
from aspen.sockets.packet import Packet
from aspen.sockets.message import Message


def test_packet_Packetable_with_unframed_bytes():
    expected = [Message.from_bytes(b'1:::')]
    actual = list(Packet(b'1:::'))
    assert actual == expected

def test_packet_Packetable_with_framed_bytes():
    expected = [Message.from_bytes(b'1:::')]
    actual = list(Packet(FFFD + b'4' + FFFD + b'1:::'))
    assert actual == expected

def test_packet_Packetable_with_multiple_frames():
    expected = [Message.from_bytes(x) for x in (b'0:::', b'1:::')]
    actual = list(Packet(FFFD+b'4'+FFFD+b'0:::'+FFFD+b'4'+FFFD+b'1:::'))
    assert actual == expected

def test_packet_with_odd_frames_raises_SyntaxError():
    Packet_ = lambda s: list(Packet(s)) # raises chokes on generator
    raises(SyntaxError, Packet_, FFFD+b'4'+FFFD+b'0:::'+FFFD)

def test_packet_with_odd_frames_tells_you_that():
    Packet_ = lambda s: list(Packet(s)) # raises chokes on generator
    packet = FFFD+b'4'+FFFD+b'0:::'+FFFD
    exc = raises(SyntaxError, Packet_, packet).value
    expected = b"There are an odd number of frames in this packet: %s" % packet
    actual = exc.args[0]
    assert actual == expected



