from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import StringIO

from pytest import raises

from aspen import json


def test_json_basically_works(harness):
    expected = '''{
    "Greetings": "program!"
}'''
    actual = harness.simple( "[---] application/json\n{'Greetings': 'program!'}"
                           , filepath="foo.json.spt"
                            ).body
    assert actual == expected

def test_json_defaults_to_application_json_for_static_json(harness):
    actual = harness.simple( '{"Greetings": "program!"}'
                           , filepath="foo.json"
                            ).headers['Content-Type']
    assert actual == 'application/json'

def test_json_content_type_is_configurable_for_static_json(harness):
    harness.fs.project.mk(('configure-aspen.py', 'website.media_type_json = "floober/blah"'))
    expected = 'floober/blah'
    actual = harness.simple( '{"Greetings": "program!"}'
                           , filepath="foo.json"
                            ).headers['Content-Type']
    assert actual == expected

def test_json_content_type_is_configurable_from_the_command_line(harness):
    actual = harness.simple( '{"Greetings": "program!"}'
                           , filepath="foo.json"
                           , argv=['--media_type_json=floober/blah']
                            ).headers['Content-Type']
    assert actual == 'floober/blah'

def test_json_content_type_is_configurable_for_dynamic_json(harness):
    harness.fs.project.mk(('configure-aspen.py', 'website.media_type_json = "floober/blah"'))
    actual = harness.simple( "[---] floober/blah\n{'Greetings': 'program!'}"
                           , filepath="foo.json.spt"
                            ).headers['Content-Type']
    assert actual == 'floober/blah'

def test_json_content_type_is_per_file_configurable(harness):
    expected = 'floober/blah'
    actual = harness.simple('''
        response.headers['Content-type'] = 'floober/blah'
        [---] floober/blah
        {'Greetings': 'program!'}
    ''', filepath="foo.json.spt").headers['Content-Type']
    assert actual == expected

def test_json_handles_unicode(harness):
    expected = b'''{
    "Greetings": "\u00b5"
}'''
    actual = harness.simple('''
        [---] application/json
        {'Greetings': unichr(181)}
    ''', filepath="foo.json.spt").body
    assert actual == expected

def test_json_doesnt_handle_non_ascii_bytestrings(harness):
    raises( UnicodeDecodeError
          , harness.simple
          , "[---] application/json\n{'Greetings': chr(181)}"
          , filepath="foo.json.spt"
           )

def test_json_handles_time(harness):
    expected = '''{
    "seen": "19:30:00"
}'''
    actual = harness.simple('''
        import datetime
        [---------------] application/json
        {'seen': datetime.time(19, 30)}
    ''', filepath="foo.json.spt").body
    assert actual == expected

def test_json_handles_date(harness):
    expected = '''{
    "created": "2011-05-09"
}'''
    actual = harness.simple('''
        import datetime
        [---------------] application/json
        {'created': datetime.date(2011, 5, 9)}
    ''', filepath='foo.json.spt').body
    assert actual == expected

def test_json_handles_datetime(harness):
    expected = '''{
    "timestamp": "2011-05-09T00:00:00"
}'''
    actual = harness.simple("""
        import datetime
        [---------------] application/json
        {'timestamp': datetime.datetime(2011, 5, 9, 0, 0)}
    """, filepath="foo.json.spt").body
    assert actual == expected

def test_json_handles_complex(harness):
    expected = '''{
    "complex": [
        1.0,
        2.0
    ]
}'''
    actual = harness.simple( "[---] application/json\n{'complex': complex(1,2)}"
                           , filepath="foo.json.spt"
                            ).body
    # The json module puts trailing spaces after commas, but simplejson
    # does not. Normalize the actual input to work around that.
    actual = '\n'.join([line.rstrip() for line in actual.split('\n')])
    assert actual == expected

def test_json_raises_TypeError_on_unknown_types(harness):
    raises( TypeError
          , harness.simple
          , contents='class Foo: pass\n[---] application/json\nFoo()'
          , filepath='foo.json.spt'
           )

def test_aspen_json_load_loads():
    fp = StringIO.StringIO()
    fp.write('{"cheese": "puffs"}')
    fp.seek(0)
    actual = json.load(fp)
    assert actual == {'cheese': 'puffs'}

def test_aspen_json_dump_dumps():
    fp = StringIO.StringIO()
    json.dump({"cheese": "puffs"}, fp)
    fp.seek(0)
    actual = fp.read()
    assert actual == '''{
    "cheese": "puffs"
}'''

def test_aspen_json_loads_loads():
    actual = json.loads('{"cheese": "puffs"}')
    assert actual == {'cheese': 'puffs'}

def test_aspen_json_dumps_dumps():
    actual = json.dumps({'cheese': 'puffs'})
    assert actual == '''{
    "cheese": "puffs"
}'''
