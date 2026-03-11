import os

import vcr
from vcr.record_mode import RecordMode

from tests import _serializers

upbeat_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    filter_headers=[("Authorization", "REDACTED")],
    filter_query_parameters=["access_key"],
    decode_compressed_response=True,
    record_mode=RecordMode(os.environ.get("VCR_RECORD_MODE", "none")),
    before_record_response=_serializers.pretty_json_body,
)
upbeat_vcr.register_serializer("pretty-yaml", _serializers)
upbeat_vcr.serializer = "pretty-yaml"
