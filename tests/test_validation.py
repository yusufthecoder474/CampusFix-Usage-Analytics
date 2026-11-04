import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from etl import validate

BASE = {
 'event_id': 'd97d9e4e-5a13-4d37-a26d-b94ad8a50d55',
 'event_name': 'issue_created',
 'event_timestamp': '2026-11-04T12:00:00+00:00',
 'user_id': 'user_1', 'session_id': 'session_1',
 'schema_version': '1.0', 'properties': {}
}

def test_valid_event():
    assert validate(BASE).year == 2026

@pytest.mark.parametrize('field', list(BASE))
def test_missing_field(field):
    event = dict(BASE)
    del event[field]
    with pytest.raises(ValueError):
        validate(event)

def test_unknown_event():
    with pytest.raises(ValueError):
        validate({**BASE, 'event_name': 'unknown'})

def test_invalid_uuid():
    with pytest.raises(ValueError):
        validate({**BASE, 'event_id': 'invalid'})

def test_timestamp_without_timezone():
    with pytest.raises(ValueError):
        validate({**BASE, 'event_timestamp': '2026-11-04T12:00:00'})
