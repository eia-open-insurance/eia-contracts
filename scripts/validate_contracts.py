#!/usr/bin/env python3
"""Validate the EIA canonical API contracts.

Runs with the Python standard library only. It deliberately does not depend on
PyYAML, jsonschema, openapi-spec-validator, Node.js, or any other tool that a
contributor would have to install. The script provides:

1. A strict parser for the YAML subset used by this repository (block
   mappings, block sequences, quoted and plain scalars, flow lists and maps,
   folded and literal block scalars, comments). Constructs outside that subset
   are rejected with a line number instead of being guessed.
2. Structural checks for every OpenAPI 3.1 and AsyncAPI 3 document: the
   required paths and methods, operation metadata, response presence.
3. Cross-document checks: every JSON Reference resolves, the AsyncAPI catalog
   and the per-vertical event documents name the same events, and the JSON
   Schemas contain the canonical required members and validate their own
   examples.
4. A non-zero exit code and a printed failure list when any check fails.

Usage:
    python scripts/validate_contracts.py
    python scripts/validate_contracts.py --verbose

Exit codes:
    0  every check passed
    1  one or more checks failed
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENAPI_DIR = ROOT / "openapi"
ASYNCAPI_DIR = ROOT / "asyncapi"
SCHEMA_DIR = ROOT / "schemas"

VERTICAL_FILES = [
    "party",
    "policy",
    "contract",
    "direct-claims",
    "assumed-claims",
    "cession",
    "retrocession",
    "document",
    "payment",
    "notifications",
]

HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")

REQUIRED_OPENAPI_PATHS = {
    "party": [
        ("/api/v1/parties", "get"),
        ("/api/v1/parties", "post"),
        ("/api/v1/parties/{partyId}", "get"),
        ("/internal/v1/parties", "get"),
        ("/internal/v1/parties", "post"),
        ("/internal/v1/parties/{partyId}", "get"),
    ],
    "policy": [
        ("/api/v1/policies", "get"),
        ("/api/v1/policies", "post"),
        ("/api/v1/policies/{policyId}", "get"),
        ("/api/v1/policies/{policyId}/status", "patch"),
        ("/internal/v1/policies", "get"),
        ("/internal/v1/policies", "post"),
        ("/internal/v1/policies/{policyId}", "get"),
        ("/internal/v1/policies/{policyId}/status", "patch"),
    ],
    "contract": [
        ("/api/v1/contracts", "get"),
        ("/api/v1/contracts", "post"),
        ("/api/v1/contracts/{contractId}", "get"),
        ("/api/v1/contracts/{contractId}/status", "patch"),
        ("/internal/v1/contracts", "get"),
        ("/internal/v1/contracts", "post"),
        ("/internal/v1/contracts/{contractId}", "get"),
        ("/internal/v1/contracts/{contractId}/status", "patch"),
    ],
    "direct-claims": [
        ("/api/v1/claims", "get"),
        ("/api/v1/claims", "post"),
        ("/api/v1/claims/{claimId}", "get"),
        ("/api/v1/claims/{claimId}/status", "patch"),
        ("/internal/v1/claims", "get"),
        ("/internal/v1/claims", "post"),
        ("/internal/v1/claims/{claimId}", "get"),
        ("/internal/v1/claims/{claimId}/status", "patch"),
    ],
    "assumed-claims": [
        ("/api/v1/assumed-claims", "get"),
        ("/api/v1/assumed-claims", "post"),
        ("/api/v1/assumed-claims/{assumedClaimId}", "get"),
        ("/api/v1/assumed-claims/{assumedClaimId}/status", "post"),
        ("/api/v1/assumed-claims/claims", "get"),
        ("/api/v1/assumed-claims/claims", "post"),
        ("/api/v1/assumed-claims/claims/{assumedClaimId}", "get"),
        ("/api/v1/assumed-claims/claims/{assumedClaimId}/status", "post"),
        ("/internal/v1/assumed-claims", "get"),
        ("/internal/v1/assumed-claims", "post"),
        ("/internal/v1/assumed-claims/{assumedClaimId}", "get"),
        ("/internal/v1/assumed-claims/{assumedClaimId}/status", "post"),
    ],
    "cession": [
        ("/api/v1/cessions", "get"),
        ("/api/v1/cessions", "post"),
        ("/api/v1/cessions/{cessionId}", "get"),
        ("/api/v1/cessions/{cessionId}/transition", "post"),
        ("/internal/v1/cessions", "get"),
        ("/internal/v1/cessions", "post"),
        ("/internal/v1/cessions/{cessionId}", "get"),
        ("/internal/v1/cessions/{cessionId}/status", "put"),
    ],
    "retrocession": [
        ("/api/v1/retrocessions", "get"),
        ("/api/v1/retrocessions", "post"),
        ("/api/v1/retrocessions/{retrocessionId}", "get"),
        ("/api/v1/retrocessions/{retrocessionId}/transition", "post"),
        ("/internal/v1/retrocessions", "get"),
        ("/internal/v1/retrocessions", "post"),
        ("/internal/v1/retrocessions/{retrocessionId}", "get"),
        ("/internal/v1/retrocessions/{retrocessionId}/status", "put"),
    ],
    "document": [
        ("/api/v1/documents", "get"),
        ("/api/v1/documents", "post"),
        ("/api/v1/documents/{documentId}", "get"),
        ("/api/v1/documents/{documentId}/status", "post"),
        ("/internal/v1/documents", "get"),
        ("/internal/v1/documents", "post"),
        ("/internal/v1/documents/{documentId}", "get"),
        ("/internal/v1/documents/{documentId}/status", "post"),
    ],
    "payment": [
        ("/api/v1/payments", "get"),
        ("/api/v1/payments", "post"),
        ("/api/v1/payments/{paymentId}", "get"),
        ("/api/v1/payments/{paymentId}/submit", "post"),
        ("/api/v1/payments/{paymentId}/authorize", "post"),
        ("/api/v1/payments/{paymentId}/approve", "post"),
        ("/api/v1/payments/{paymentId}/issue", "post"),
        ("/internal/v1/payments", "get"),
        ("/internal/v1/payments", "post"),
        ("/internal/v1/payments/{paymentId}", "get"),
        ("/internal/v1/payments/{paymentId}/status", "patch"),
    ],
    "notifications": [
        ("/api/v1/notifications", "get"),
        ("/api/v1/notifications", "post"),
        ("/api/v1/notifications/{notificationId}", "get"),
        ("/api/v1/notifications/{notificationId}/send", "post"),
        ("/internal/v1/notifications", "get"),
        ("/internal/v1/notifications", "post"),
        ("/internal/v1/notifications/{notificationId}", "get"),
        ("/internal/v1/notifications/{notificationId}/send", "post"),
    ],
}

REQUIRED_COMPONENTS = {
    "schemas": [
        "Problem",
        "ProblemFieldError",
        "Money",
        "MoneyAmount",
        "CurrencyCode",
        "Percent",
        "AuditFields",
        "Page",
        "PageMeta",
        "PageLinks",
        "Link",
        "EntityRef",
        "VerticalId",
    ],
    "parameters": [
        "TenantHeader",
        "BookHeaderDirect",
        "BookHeaderAssumed",
        "TenantIdQuery",
        "PageParam",
        "PageSizeParam",
        "CorrelationId",
        "IdempotencyKey",
        "IfMatch",
    ],
    "headers": [
        "ETag",
        "IdempotentReplayed",
    ],
    "responses": [
        "BadRequest",
        "NotFound",
        "Conflict",
        "BadGateway",
        "ServiceUnavailable",
        "Problem",
    ],
}

REQUIRED_SCHEMA_FILES = [
    "error-envelope.schema.json",
    "money.schema.json",
    "event-envelope.schema.json",
]

EVENT_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
VALID_JSON_TYPES = {"null", "boolean", "object", "array", "number", "string", "integer"}


# ---------------------------------------------------------------------------
# Minimal YAML parser for the repository's YAML subset
# ---------------------------------------------------------------------------


class YamlError(ValueError):
    def __init__(self, source: Path, line: int, message: str):
        super().__init__(f"{source}:{line}: {message}")
        self.source = source
        self.line = line
        self.message = message


class _YamlParser:
    """Parse the YAML subset used by this repository.

    Supported: block mappings and sequences, plain and quoted scalars, flow
    lists and flow maps, literal and folded block scalars, full-line comments,
    and trailing comments on scalars. Anchors, aliases, tags, multiple
    documents, complex keys, and explicit indentation indicators are rejected.
    """

    def __init__(self, text: str, source: Path):
        self.lines = text.splitlines()
        self.source = source
        self.i = 0

    # -- helpers ---------------------------------------------------------

    def _error(self, line_index: int, message: str) -> YamlError:
        return YamlError(self.source, line_index + 1, message)

    def _indent_of(self, raw: str, line_index: int) -> int:
        stripped = raw.lstrip(" ")
        indent = len(raw) - len(stripped)
        if stripped.startswith("\t") or raw[:indent].find("\t") != -1:
            raise self._error(line_index, "tab character in indentation")
        return indent

    def _peek(self):
        """Return (indent, content, line_index) of the next content line."""
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            stripped = raw.strip()
            if stripped == "" or stripped.startswith("#"):
                self.i += 1
                continue
            if stripped in ("---", "..."):
                self.i += 1
                continue
            indent = self._indent_of(raw, self.i)
            return indent, raw[indent:], self.i
        return None

    # -- public ----------------------------------------------------------

    def parse(self):
        node = self._parse_node(0)
        extra = self._peek()
        if extra is not None:
            raise self._error(extra[2], "unexpected content after the document root")
        return node

    # -- structure -------------------------------------------------------

    def _parse_node(self, indent: int):
        peeked = self._peek()
        if peeked is None:
            return None
        current, content, line_index = peeked
        if current != indent:
            raise self._error(line_index, f"expected indentation {indent}, found {current}")
        if content == "-" or content.startswith("- "):
            return self._parse_sequence(indent)
        return self._parse_mapping(indent)

    def _parse_mapping(self, indent: int):
        result = {}
        while True:
            peeked = self._peek()
            if peeked is None:
                break
            current, content, line_index = peeked
            if current < indent:
                break
            if current > indent:
                raise self._error(line_index, f"unexpected indentation {current} inside a mapping")
            if content == "-" or content.startswith("- "):
                raise self._error(line_index, "sequence item where a mapping key was expected")
            key, rest = self._split_key(content, line_index)
            if key in result:
                raise self._error(line_index, f"duplicate key '{key}'")
            self.i = line_index + 1
            result[key] = self._parse_value(rest, indent, line_index)
        return result

    def _parse_sequence(self, indent: int):
        result = []
        while True:
            peeked = self._peek()
            if peeked is None:
                break
            current, content, line_index = peeked
            if current < indent:
                break
            if current > indent:
                raise self._error(line_index, f"unexpected indentation {current} inside a sequence")
            if not (content == "-" or content.startswith("- ")):
                break
            rest = content[1:]
            if rest.startswith(" "):
                rest = rest[1:]
            self.i = line_index + 1
            if rest.strip() == "":
                peeked_inner = self._peek()
                if peeked_inner is None or peeked_inner[0] <= indent:
                    result.append(None)
                else:
                    result.append(self._parse_node(peeked_inner[0]))
                continue
            key_split = self._try_split_key(rest)
            if key_split is not None:
                item = self._parse_inline_mapping_item(rest, indent, line_index)
                result.append(item)
            else:
                result.append(self._parse_scalar(rest, line_index))
        return result

    def _parse_inline_mapping_item(self, first_content: str, dash_indent: int, line_index: int):
        """Parse a sequence item that starts with a mapping entry on the dash line."""
        first_key, first_rest = self._split_key(first_content, line_index)
        # The mapping's indentation is the column of the first key.
        prefix = len(first_content) - len(first_content.lstrip(" "))
        item_indent = dash_indent + 2 + prefix
        item = {first_key: self._parse_value(first_rest, item_indent, line_index)}
        while True:
            peeked = self._peek()
            if peeked is None:
                break
            current, content, next_line = peeked
            if current < item_indent:
                break
            if current > item_indent:
                raise self._error(next_line, f"unexpected indentation {current} in a sequence item")
            if content == "-" or content.startswith("- "):
                break
            key, rest = self._split_key(content, next_line)
            if key in item:
                raise self._error(next_line, f"duplicate key '{key}' in a sequence item")
            self.i = next_line + 1
            item[key] = self._parse_value(rest, item_indent, next_line)
        return item

    def _parse_value(self, rest: str, parent_indent: int, line_index: int):
        text = rest.strip()
        if text == "":
            peeked = self._peek()
            if peeked is None or peeked[0] <= parent_indent:
                return None
            return self._parse_node(peeked[0])
        if text[0] in ("|", ">"):
            style = text[0]
            chomp = text[1:]
            if chomp not in ("", "-", "+"):
                raise self._error(line_index, f"unsupported block scalar header '{text}'")
            return self._read_block_scalar(parent_indent, style, chomp, line_index)
        return self._parse_scalar(text, line_index)

    # -- scalars ---------------------------------------------------------

    def _read_block_scalar(self, parent_indent: int, style: str, chomp: str, line_index: int) -> str:
        block = []
        block_indent = None
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            if raw.strip() == "":
                block.append("")
                self.i += 1
                continue
            indent = self._indent_of(raw, self.i)
            if indent <= parent_indent:
                break
            if block_indent is None:
                block_indent = indent
            if indent < block_indent:
                break
            block.append(raw[block_indent:])
            self.i += 1
        if style == "|":
            text = "\n".join(block)
        else:
            parts = []
            previous_blank = False
            for line in block:
                if line == "":
                    parts.append("\n")
                    previous_blank = True
                else:
                    if parts and not previous_blank:
                        parts.append(" ")
                    parts.append(line)
                    previous_blank = False
            text = "".join(parts)
        if chomp == "-":
            return text.rstrip("\n")
        if chomp == "+":
            return text + "\n"
        return text.rstrip("\n") + "\n"

    def _parse_scalar(self, text: str, line_index: int):
        value = _strip_trailing_comment(text).strip()
        if value == "":
            return ""
        if value[0] == "'":
            return _parse_single_quoted(value, self.source, line_index)
        if value[0] == '"':
            return _parse_double_quoted(value, self.source, line_index)
        if value[0] == "[":
            return _parse_flow_sequence(value, self.source, line_index)
        if value[0] == "{":
            return _parse_flow_map(value, self.source, line_index)
        if value in ("null", "Null", "NULL", "~"):
            return None
        if value in ("true", "True", "TRUE"):
            return True
        if value in ("false", "False", "FALSE"):
            return False
        if re.fullmatch(r"[+-]?[0-9]+", value):
            return int(value)
        if value[0] in ("&", "*", "!", "@", "`"):
            raise YamlError(self.source, line_index + 1, f"unsupported YAML construct '{value[0]}'")
        return value

    # -- keys ------------------------------------------------------------

    def _try_split_key(self, content: str):
        try:
            return _split_key_text(content, self.source, 0)
        except YamlError:
            return None

    def _split_key(self, content: str, line_index: int):
        return _split_key_text(content, self.source, line_index)


def _strip_trailing_comment(text: str) -> str:
    quote = None
    depth = 0
    i = 0
    while i < len(text):
        char = text[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(text) and text[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == "#" and depth == 0 and (i == 0 or text[i - 1] in " \t"):
                return text[:i]
        i += 1
    return text


def _split_key_text(content: str, source: Path, line_index: int):
    quote = None
    depth = 0
    i = 0
    while i < len(content):
        char = content[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(content) and content[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == ":" and depth == 0:
                next_char = content[i + 1] if i + 1 < len(content) else ""
                if next_char in ("", " ", "\t"):
                    raw_key = content[:i].strip()
                    if raw_key == "":
                        raise YamlError(source, line_index + 1, "empty mapping key")
                    key = _unquote_key(raw_key, source, line_index)
                    return key, content[i + 1:]
        i += 1
    raise YamlError(source, line_index + 1, f"expected 'key: value', found '{content.strip()}'")


def _unquote_key(raw: str, source: Path, line_index: int) -> str:
    if raw[0] == "'":
        return _parse_single_quoted(raw, source, line_index)
    if raw[0] == '"':
        return _parse_double_quoted(raw, source, line_index)
    return raw


def _require_consumed(text: str, position: int, source: Path, line_index: int):
    if text[position:].strip() != "":
        raise YamlError(source, line_index + 1, f"unexpected trailing text '{text[position:].strip()}'")


def _parse_single_quoted(text: str, source: Path, line_index: int) -> str:
    result = []
    i = 1
    while i < len(text):
        if text[i] == "'":
            if i + 1 < len(text) and text[i + 1] == "'":
                result.append("'")
                i += 2
                continue
            _require_consumed(text, i + 1, source, line_index)
            return "".join(result)
        result.append(text[i])
        i += 1
    raise YamlError(source, line_index + 1, "unterminated single-quoted scalar")


def _parse_double_quoted(text: str, source: Path, line_index: int) -> str:
    escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0"}
    result = []
    i = 1
    while i < len(text):
        char = text[i]
        if char == "\\":
            if i + 1 >= len(text):
                raise YamlError(source, line_index + 1, "dangling escape in double-quoted scalar")
            escape = text[i + 1]
            result.append(escapes.get(escape, escape))
            i += 2
            continue
        if char == '"':
            _require_consumed(text, i + 1, source, line_index)
            return "".join(result)
        result.append(char)
        i += 1
    raise YamlError(source, line_index + 1, "unterminated double-quoted scalar")


def _split_flow_items(inner: str) -> list[str]:
    items = []
    start = 0
    depth = 0
    quote = None
    i = 0
    while i < len(inner):
        char = inner[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(inner) and inner[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == "," and depth == 0:
                items.append(inner[start:i])
                start = i + 1
        i += 1
    items.append(inner[start:])
    return [item for item in items if item.strip() != ""]


def _parse_flow_sequence(text: str, source: Path, line_index: int):
    close = _matching_flow(text, 0, "[", "]", source, line_index)
    inner = text[1:close]
    _require_consumed(text, close + 1, source, line_index)
    if inner.strip() == "":
        return []
    result = []
    for item in _split_flow_items(inner):
        value = _strip_trailing_comment(item).strip()
        if value[:1] == "'":
            result.append(_parse_single_quoted(value, source, line_index))
        elif value[:1] == '"':
            result.append(_parse_double_quoted(value, source, line_index))
        elif value[:1] == "[":
            result.append(_parse_flow_sequence(value, source, line_index))
        elif value[:1] == "{":
            result.append(_parse_flow_map(value, source, line_index))
        elif value in ("true", "false"):
            result.append(value == "true")
        elif value in ("null", "~"):
            result.append(None)
        elif re.fullmatch(r"[+-]?[0-9]+", value):
            result.append(int(value))
        else:
            result.append(value)
    return result


def _parse_flow_map(text: str, source: Path, line_index: int):
    close = _matching_flow(text, 0, "{", "}", source, line_index)
    inner = text[1:close]
    _require_consumed(text, close + 1, source, line_index)
    if inner.strip() == "":
        return {}
    result = {}
    for item in _split_flow_items(inner):
        key, rest = _split_key_text(item.strip(), source, line_index)
        value = rest.strip()
        if value[:1] == "'":
            result[key] = _parse_single_quoted(value, source, line_index)
        elif value[:1] == '"':
            result[key] = _parse_double_quoted(value, source, line_index)
        elif value == "":
            result[key] = None
        else:
            result[key] = value
    return result


def _matching_flow(text: str, start: int, open_char: str, close_char: str, source: Path, line_index: int) -> int:
    depth = 0
    quote = None
    i = start
    while i < len(text):
        char = text[i]
        if quote == "'":
            if char == "'":
                if i + 1 < len(text) and text[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif quote == '"':
            if char == "\\":
                i += 2
                continue
            if char == '"':
                quote = None
        else:
            if char in ("'", '"'):
                quote = char
            elif char == open_char:
                depth += 1
            elif char == close_char:
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    raise YamlError(source, line_index + 1, f"unterminated flow collection starting with '{open_char}'")


def parse_yaml(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"cannot read {path}: {error}")
    return _YamlParser(text, path).parse()


# ---------------------------------------------------------------------------
# JSON Reference resolution
# ---------------------------------------------------------------------------


class ContractSet:
    def __init__(self):
        self.cache = {}
        self.failures = []
        self.checks = 0

    def fail(self, message: str):
        self.failures.append(message)

    def check(self, condition: bool, message: str):
        self.checks += 1
        if not condition:
            self.fail(message)
        return condition

    def load(self, path: Path):
        path = path.resolve()
        if path in self.cache:
            return self.cache[path]
        if not str(path).startswith(str(ROOT)):
            raise SystemExit(f"reference escapes the repository: {path}")
        if path.suffix.lower() == ".json":
            with path.open(encoding="utf-8") as handle:
                value = json.load(handle)
        else:
            value = parse_yaml(path)
        self.cache[path] = value
        return value

    def resolve(self, document, reference: str):
        if reference.startswith("#"):
            file_part = ""
            pointer = reference[2:] if reference.startswith("#/") else reference[1:]
            target = document
            target_path = None
        else:
            file_part, _, pointer = reference.partition("#")
            pointer = pointer[1:] if pointer.startswith("/") else pointer
            target_path = (self.current_file.parent / file_part).resolve()
            if not target_path.exists():
                raise KeyError(f"missing referenced file {file_part}")
            target = self.load(target_path)
        value = target
        if pointer:
            for raw_token in pointer.split("/"):
                token = raw_token.replace("~1", "/").replace("~0", "~")
                if isinstance(value, list):
                    value = value[int(token)]
                elif isinstance(value, dict):
                    value = value[token]
                else:
                    raise KeyError(f"cannot descend into {type(value).__name__} at '{token}'")
        return value, target_path

    def walk_refs(self, node, document_path: Path, trail: str):
        self.current_file = document_path
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str):
                    try:
                        target, target_path = self.resolve(self.load(document_path), value)
                    except (KeyError, IndexError, ValueError, json.JSONDecodeError, YamlError) as error:
                        self.fail(f"{document_path.relative_to(ROOT).as_posix()} {trail}: unresolved $ref '{value}': {error}")
                        continue
                    if target is None:
                        self.fail(f"{document_path.relative_to(ROOT).as_posix()} {trail}: $ref '{value}' resolves to null")
                else:
                    self.walk_refs(value, document_path, f"{trail}/{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                self.walk_refs(value, document_path, f"{trail}/{index}")

    def check_schema_object(self, schema, relative, trail: str = "$"):
        """Check schema hygiene on an already-parsed schema object."""
        if not isinstance(schema, dict):
            return
        declared = schema.get("type")
        if declared is not None:
            values = declared if isinstance(declared, list) else [declared]
            self.check(
                all(value in VALID_JSON_TYPES for value in values),
                f"{relative} {trail}: invalid schema type {declared}",
            )
        if "required" in schema:
            required = schema["required"]
            self.check(isinstance(required, list), f"{relative} {trail}: required must be a list")
            properties = schema.get("properties")
            if isinstance(required, list) and isinstance(properties, dict):
                for field in required:
                    self.check(
                        field in properties,
                        f"{relative} {trail}: required '{field}' has no property definition",
                    )
        if "properties" in schema:
            self.check(isinstance(schema["properties"], dict), f"{relative} {trail}: properties must be a mapping")
            for name, sub in (schema["properties"] or {}).items():
                self.check_schema_object(sub, relative, f"{trail}.properties.{name}")
        if "enum" in schema:
            self.check(
                isinstance(schema["enum"], list) and bool(schema["enum"]),
                f"{relative} {trail}: enum must be a non-empty list",
            )
        for keyword in ("allOf", "oneOf", "anyOf"):
            for index, sub in enumerate(schema.get(keyword) or []):
                self.check_schema_object(sub, relative, f"{trail}.{keyword}[{index}]")
        if isinstance(schema.get("items"), dict):
            self.check_schema_object(schema["items"], relative, f"{trail}.items")
        for keyword in ("$defs", "definitions"):
            for name, sub in (schema.get(keyword) or {}).items():
                self.check_schema_object(sub, relative, f"{trail}.{keyword}.{name}")

    def check_openapi_schemas(self, document, relative):
        schemas = (document.get("components") or {}).get("schemas") or {}
        for name, schema in schemas.items():
            self.check_schema_object(schema, str(relative), f"components.schemas.{name}")



# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_openapi(contracts: ContractSet, verbose: bool):
    print("\nOpenAPI 3.1 documents")
    expected = {"components"} | set(VERTICAL_FILES)
    present = {path.stem for path in OPENAPI_DIR.glob("*.yaml")}
    contracts.check(
        present == expected,
        f"openapi/ must contain exactly {sorted(expected)}; found {sorted(present)}",
    )

    components = contracts.load(OPENAPI_DIR / "components.yaml")
    contracts.check(components.get("openapi") == "3.1.0", "components.yaml: openapi must be 3.1.0")
    info = components.get("info") or {}
    contracts.check(bool(info.get("title")), "components.yaml: info.title is required")
    contracts.check(bool(info.get("version")), "components.yaml: info.version is required")
    contracts.check(
        components.get("jsonSchemaDialect") == "https://json-schema.org/draft/2020-12/schema",
        "components.yaml: jsonSchemaDialect must be the JSON Schema 2020-12 dialect",
    )
    component_sections = components.get("components") or {}
    for section, names in REQUIRED_COMPONENTS.items():
        actual = component_sections.get(section) or {}
        for name in names:
            contracts.check(name in actual, f"components.yaml: missing components.{section}.{name}")

    operation_ids = {}
    for vertical in VERTICAL_FILES:
        path = OPENAPI_DIR / f"{vertical}.yaml"
        if not path.exists():
            contracts.check(False, f"missing openapi/{vertical}.yaml")
            continue
        document = contracts.load(path)
        relative = path.relative_to(ROOT).as_posix()
        contracts.check(document.get("openapi") == "3.1.0", f"{relative}: openapi must be 3.1.0")
        doc_info = document.get("info") or {}
        contracts.check(bool(doc_info.get("title")), f"{relative}: info.title is required")
        contracts.check(
            isinstance(doc_info.get("version"), str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", doc_info["version"]),
            f"{relative}: info.version must be SemVer",
        )
        contracts.check(
            document.get("jsonSchemaDialect") == "https://json-schema.org/draft/2020-12/schema",
            f"{relative}: jsonSchemaDialect must be the JSON Schema 2020-12 dialect",
        )
        contracts.check(
            (document.get("x-vertical") == vertical),
            f"{relative}: x-vertical must be '{vertical}'",
        )
        contracts.check(
            isinstance(document.get("security"), list) and bool(document.get("security")),
            f"{relative}: a document-level security requirement is required",
        )
        security_schemes = (document.get("components") or {}).get("securitySchemes") or {}
        contracts.check(
            "sessionCookie" in security_schemes,
            f"{relative}: components.securitySchemes.sessionCookie is required",
        )

        paths = document.get("paths") or {}
        contracts.check(isinstance(paths, dict) and bool(paths), f"{relative}: paths must be a non-empty mapping")
        local_operation_ids = set()
        operation_count = 0
        for path_key, path_item in paths.items():
            contracts.check(
                path_key.startswith("/api/v1/") or path_key.startswith("/internal/v1/"),
                f"{relative}: path '{path_key}' must start with /api/v1/ or /internal/v1/",
            )
            contracts.check(isinstance(path_item, dict), f"{relative}: path '{path_key}' must be a mapping")
            if not isinstance(path_item, dict):
                continue
            is_internal = path_key.startswith("/internal/v1/")
            for method, operation in path_item.items():
                if method not in HTTP_METHODS:
                    continue
                operation_count += 1
                where = f"{relative}: {method.upper()} {path_key}"
                contracts.check(isinstance(operation, dict), f"{where}: operation must be a mapping")
                if not isinstance(operation, dict):
                    continue
                operation_id = operation.get("operationId")
                contracts.check(bool(operation_id), f"{where}: operationId is required")
                if operation_id:
                    contracts.check(operation_id not in local_operation_ids, f"{where}: duplicate operationId '{operation_id}'")
                    contracts.check(
                        operation_id not in operation_ids,
                        f"{where}: operationId '{operation_id}' is already used in {operation_ids.get(operation_id)}",
                    )
                    local_operation_ids.add(operation_id)
                    operation_ids[operation_id] = relative
                contracts.check(bool(operation.get("summary")), f"{where}: summary is required")
                contracts.check(bool(operation.get("tags")), f"{where}: tags are required")
                if is_internal:
                    contracts.check(operation.get("security") == [], f"{where}: internal operations must declare security: []")
                    contracts.check(operation.get("x-internal-api") is True, f"{where}: internal operations must be marked x-internal-api: true")
                responses = operation.get("responses")
                contracts.check(isinstance(responses, dict) and bool(responses), f"{where}: responses are required")
                if isinstance(responses, dict):
                    success = [code for code in responses if str(code).startswith("2")]
                    contracts.check(bool(success), f"{where}: a 2xx response is required")
                    for code, response in responses.items():
                        if isinstance(response, dict) and "$ref" not in response:
                            contracts.check(bool(response.get("description")), f"{where}: response {code} needs a description")
                request_body = operation.get("requestBody")
                if request_body is not None:
                    contracts.check(isinstance(request_body, dict), f"{where}: requestBody must be a mapping")
                    content = (request_body or {}).get("content") or {}
                    contracts.check("application/json" in content, f"{where}: requestBody must declare application/json")
                    if "application/json" in content:
                        schema = (content["application/json"] or {}).get("schema")
                        contracts.check(isinstance(schema, dict), f"{where}: requestBody schema is required")

        for required_path, required_method in REQUIRED_OPENAPI_PATHS[vertical]:
            path_item = paths.get(required_path) if isinstance(paths, dict) else None
            contracts.check(
                isinstance(path_item, dict) and required_method in path_item,
                f"{relative}: required operation {required_method.upper()} {required_path} is missing",
            )
        contracts.check_openapi_schemas(document, relative)
        if verbose:
            print(f"  OK {relative}  paths={len(paths)} operations={operation_count}")
        else:
            print(f"  OK {relative}  {len(paths)} paths, {operation_count} operations")
    contracts.check_openapi_schemas(components, Path("openapi/components.yaml"))



def check_asyncapi(contracts: ContractSet, verbose: bool):
    print("\nAsyncAPI 3 documents")
    expected = {"event-catalog"} | set(VERTICAL_FILES)
    present = {path.stem for path in ASYNCAPI_DIR.glob("*.yaml")}
    contracts.check(
        present == expected,
        f"asyncapi/ must contain exactly {sorted(expected)}; found {sorted(present)}",
    )

    catalog_path = ASYNCAPI_DIR / "event-catalog.yaml"
    catalog = contracts.load(catalog_path)
    contracts.check(catalog.get("asyncapi") == "3.0.0", "event-catalog.yaml: asyncapi must be 3.0.0")
    contracts.check(bool((catalog.get("info") or {}).get("version")), "event-catalog.yaml: info.version is required")
    catalog_entries = catalog.get("x-event-catalog") or {}
    contracts.check(isinstance(catalog_entries, dict), "event-catalog.yaml: x-event-catalog must be a mapping")
    contracts.check(
        set(catalog_entries) == set(VERTICAL_FILES),
        f"event-catalog.yaml: x-event-catalog must list exactly {sorted(VERTICAL_FILES)}",
    )

    published_by_vertical = {}
    for vertical in VERTICAL_FILES:
        path = ASYNCAPI_DIR / f"{vertical}.yaml"
        if not path.exists():
            contracts.check(False, f"missing asyncapi/{vertical}.yaml")
            continue
        document = contracts.load(path)
        relative = path.relative_to(ROOT).as_posix()
        contracts.check(document.get("asyncapi") == "3.0.0", f"{relative}: asyncapi must be 3.0.0")
        contracts.check(bool((document.get("info") or {}).get("version")), f"{relative}: info.version is required")
        channels = document.get("channels") or {}
        operations = document.get("operations") or {}
        contracts.check(isinstance(channels, dict) and bool(channels), f"{relative}: channels must be non-empty")
        contracts.check(isinstance(operations, dict) and bool(operations), f"{relative}: operations must be non-empty")

        addresses = set()
        for channel_key, channel in channels.items():
            where = f"{relative}: channel {channel_key}"
            contracts.check(isinstance(channel, dict), f"{where} must be a mapping")
            if not isinstance(channel, dict):
                continue
            address = channel.get("address")
            contracts.check(bool(address), f"{where} needs an address")
            if address:
                addresses.add(address)
                contracts.check(bool(EVENT_NAME_RE.fullmatch(address)), f"{where} address '{address}' is not a valid event name")
                contracts.check(channel.get("x-event-type") == address, f"{where} x-event-type must equal the address")
            contracts.check(channel.get("x-status") == "planned", f"{where} must be marked x-status: planned")
            messages = channel.get("messages") or {}
            contracts.check("DomainEvent" in messages, f"{where} must reference the DomainEvent message")

        for operation_key, operation in operations.items():
            where = f"{relative}: operation {operation_key}"
            contracts.check(isinstance(operation, dict), f"{where} must be a mapping")
            if not isinstance(operation, dict):
                continue
            contracts.check(operation.get("action") == "send", f"{where} action must be send for a publisher document")
            channel_ref = (operation.get("channel") or {}).get("$ref")
            contracts.check(
                isinstance(channel_ref, str) and channel_ref.startswith("#/channels/"),
                f"{where} must reference a local channel",
            )
            if isinstance(channel_ref, str) and channel_ref.startswith("#/channels/"):
                key = channel_ref.split("/")[-1].replace("~1", "/")
                contracts.check(key in channels, f"{where} references unknown channel '{key}'")

        entry = catalog_entries.get(vertical) or {}
        published = entry.get("published") or []
        contracts.check(isinstance(published, list) and bool(published), f"event-catalog.yaml: {vertical}.published must be non-empty")
        contracts.check(
            len(published) == len(set(published)),
            f"event-catalog.yaml: {vertical}.published contains duplicate event names",
        )
        contracts.check(
            set(published) == addresses,
            f"{relative}: channels {sorted(addresses)} do not match catalog published {sorted(published)}",
        )
        for event in published:
            contracts.check(bool(EVENT_NAME_RE.fullmatch(event)), f"event-catalog.yaml: {event} is not a valid event name")
        published_by_vertical[vertical] = set(published)
        if verbose:
            print(f"  OK {relative}  channels={len(channels)} operations={len(operations)}")
        else:
            print(f"  OK {relative}  {len(channels)} event channels")

    all_events = set()
    for names in published_by_vertical.values():
        overlap = all_events & names
        contracts.check(not overlap, f"event names published by more than one vertical: {sorted(overlap)}")
        all_events |= names

    for vertical, entry in catalog_entries.items():
        if not isinstance(entry, dict):
            contracts.check(False, f"event-catalog.yaml: {vertical} entry must be a mapping")
            continue
        consumed = entry.get("consumed") or []
        contracts.check(isinstance(consumed, list), f"event-catalog.yaml: {vertical}.consumed must be a list")
        for event in consumed:
            contracts.check(
                event in all_events,
                f"event-catalog.yaml: {vertical} consumes '{event}' but no vertical publishes it",
            )
    print(f"  OK catalog: {len(all_events)} unique published events across {len(published_by_vertical)} verticals")


def check_json_schemas(contracts: ContractSet, verbose: bool):
    print("\nJSON Schema 2020-12 documents")
    present = {path.name for path in SCHEMA_DIR.glob("*.schema.json")}
    for name in REQUIRED_SCHEMA_FILES:
        contracts.check(name in present, f"schemas/: missing {name}")

    schemas = {}
    for name in REQUIRED_SCHEMA_FILES:
        path = SCHEMA_DIR / name
        if not path.exists():
            continue
        try:
            document = contracts.load(path)
        except json.JSONDecodeError as error:
            contracts.check(False, f"schemas/{name}: invalid JSON: {error}")
            continue
        relative = path.relative_to(ROOT).as_posix()
        contracts.check(isinstance(document, dict), f"{relative}: root must be an object")
        contracts.check(
            document.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
            f"{relative}: $schema must be the 2020-12 dialect",
        )
        contracts.check(bool(document.get("$id")), f"{relative}: $id is required")
        contracts.check_schema_object(document, str(relative))
        schemas[name] = document
        if verbose:
            print(f"  OK {relative}")

    error_schema = schemas.get("error-envelope.schema.json")
    if error_schema:
        required = set(error_schema.get("required") or [])
        for field in ("type", "title", "status", "detail", "instance", "code", "category", "retryable"):
            contracts.check(field in required, f"schemas/error-envelope.schema.json: '{field}' must be required")
        properties = error_schema.get("properties") or {}
        contracts.check(
            (properties.get("code") or {}).get("pattern") == "^EIA-[A-Z]{3}-[0-9]{4}$",
            "schemas/error-envelope.schema.json: code must use the EIA-XXX-NNNN pattern",
        )
        categories = set((properties.get("category") or {}).get("enum") or [])
        contracts.check(len(categories) >= 10, "schemas/error-envelope.schema.json: category enum is incomplete")
        for index, example in enumerate(error_schema.get("examples") or []):
            problems = _validate_instance(example, error_schema, error_schema)
            contracts.check(not problems, f"schemas/error-envelope.schema.json: example {index} invalid: {problems}")

    money_schema = schemas.get("money.schema.json")
    if money_schema:
        required = set(money_schema.get("required") or [])
        contracts.check({"amount", "currency"} <= required, "schemas/money.schema.json: amount and currency must be required")
        definitions = money_schema.get("$defs") or {}
        amount = definitions.get("MoneyAmount") or {}
        contracts.check(amount.get("type") == "string", "schemas/money.schema.json: MoneyAmount.type must be string")
        contracts.check(bool(amount.get("pattern")), "schemas/money.schema.json: MoneyAmount.pattern is required")
        currency = definitions.get("CurrencyCode") or {}
        contracts.check(currency.get("pattern") == "^[A-Z]{3}$", "schemas/money.schema.json: CurrencyCode.pattern must be ^[A-Z]{3}$")
        for index, example in enumerate(money_schema.get("examples") or []):
            problems = _validate_instance(example, money_schema, money_schema)
            contracts.check(not problems, f"schemas/money.schema.json: example {index} invalid: {problems}")

    event_schema = schemas.get("event-envelope.schema.json")
    if event_schema:
        required = set(event_schema.get("required") or [])
        for field in ("eventId", "eventType", "eventVersion", "occurredAt", "recordedAt", "tenantId", "vertical", "aggregateType", "aggregateId", "aggregateVersion", "subject", "data"):
            contracts.check(field in required, f"schemas/event-envelope.schema.json: '{field}' must be required")
        properties = event_schema.get("properties") or {}
        contracts.check(
            (properties.get("book") or {}).get("enum") == ["DIRECT", "ASSUMED"],
            "schemas/event-envelope.schema.json: book must be the DIRECT/ASSUMED enum",
        )
        verticals = set((properties.get("vertical") or {}).get("enum") or [])
        contracts.check(len(verticals) == 10, "schemas/event-envelope.schema.json: vertical must enumerate the ten verticals")


def _validate_instance(instance, schema, root, path="$"):
    """Validate a small subset of JSON Schema for the schema's own examples."""
    problems = []
    if "$ref" in schema:
        target = _local_ref(root, schema["$ref"])
        if target is None:
            return [f"{path}: unresolved $ref {schema['$ref']}"]
        return _validate_instance(instance, target, root, path)
    declared = schema.get("type")
    if declared is not None:
        types = declared if isinstance(declared, list) else [declared]
        if not any(_matches_type(instance, item) for item in types):
            problems.append(f"{path}: expected type {types}, found {type(instance).__name__}")
    enum = schema.get("enum")
    if enum is not None and instance not in enum:
        problems.append(f"{path}: value {instance!r} is not in enum")
    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, instance) is None:
            problems.append(f"{path}: '{instance}' does not match {pattern}")
        minimum = schema.get("minLength")
        if minimum is not None and len(instance) < minimum:
            problems.append(f"{path}: shorter than minLength")
        maximum = schema.get("maxLength")
        if maximum is not None and len(instance) > maximum:
            problems.append(f"{path}: longer than maxLength")
    if isinstance(instance, int):
        minimum = schema.get("minimum")
        if minimum is not None and instance < minimum:
            problems.append(f"{path}: below minimum")
        maximum = schema.get("maximum")
        if maximum is not None and instance > maximum:
            problems.append(f"{path}: above maximum")
    if isinstance(instance, dict):
        for field in schema.get("required") or []:
            if field not in instance:
                problems.append(f"{path}: missing required '{field}'")
        properties = schema.get("properties") or {}
        for field, value in instance.items():
            if field in properties:
                problems.extend(_validate_instance(value, properties[field], root, f"{path}.{field}"))
            elif schema.get("additionalProperties") is False:
                problems.append(f"{path}: unexpected '{field}'")
    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for index, value in enumerate(instance):
                problems.extend(_validate_instance(value, items, root, f"{path}[{index}]"))
    return problems


def _matches_type(value, declared_type):
    if declared_type == "null":
        return value is None
    if declared_type == "string":
        return isinstance(value, str)
    if declared_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if declared_type == "boolean":
        return isinstance(value, bool)
    if declared_type == "object":
        return isinstance(value, dict)
    if declared_type == "array":
        return isinstance(value, list)
    return True


def _local_ref(root, reference):
    if not reference.startswith("#/"):
        return None
    value = root
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value:
            return None
        value = value[token]
    return value


def check_references(contracts: ContractSet):
    print("\nJSON Reference resolution")
    documents = []
    for directory in (OPENAPI_DIR, ASYNCAPI_DIR):
        documents.extend(sorted(directory.glob("*.yaml")))
    for path in documents:
        contracts.current_file = path
        contracts.walk_refs(contracts.load(path), path, "")
    print(f"  OK walked {len(documents)} YAML documents")


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv[1:]
    unknown = [arg for arg in argv[1:] if arg not in ("--verbose",)]
    if unknown:
        print(f"unknown arguments: {unknown}")
        return 2
    for directory in (OPENAPI_DIR, ASYNCAPI_DIR, SCHEMA_DIR):
        if not directory.is_dir():
            print(f"missing directory: {directory}")
            return 2

    print("EIA canonical contract validation")
    print(f"repository: {ROOT}")
    print(f"python: {sys.version.split()[0]} (standard library only)")

    contracts = ContractSet()
    sections = [
        ("OpenAPI 3.1 documents", lambda: check_openapi(contracts, verbose)),
        ("AsyncAPI 3 documents", lambda: check_asyncapi(contracts, verbose)),
        ("JSON Schema 2020-12 documents", lambda: check_json_schemas(contracts, verbose)),
        ("JSON Reference resolution", lambda: check_references(contracts)),
    ]
    for label, section in sections:
        try:
            section()
        except YamlError as error:
            contracts.check(False, f"{label}: YAML parse error: {error}")
        except json.JSONDecodeError as error:
            contracts.check(False, f"{label}: JSON parse error: {error}")

    print("\nResult")
    if contracts.failures:
        print(f"  FAIL {len(contracts.failures)} of {contracts.checks} checks failed")
        for failure in contracts.failures:
            print(f"   - {failure}")
        return 1
    print(f"  PASS {contracts.checks} checks, 0 failures")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
