#!/usr/bin/env python3
"""dotenv_parse - Parse and manage .env files."""
import sys, re, os

def parse(text):
    env = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
        if m:
            key = m.group(1)
            value = m.group(2).strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            value = re.sub(r"\\n", "\n", value)
            env[key] = value
    return env

def serialize(env):
    lines = []
    for k, v in sorted(env.items()):
        if " " in v or "\n" in v or '"' in v:
            v = '"' + v.replace("\n", "\\n").replace('"', '\\"') + '"'
        lines.append(f"{k}={v}")
    return "\n".join(lines)

def merge(base, override):
    result = dict(base)
    result.update(override)
    return result

def interpolate(env):
    result = dict(env)
    for k, v in result.items():
        def replacer(m):
            ref = m.group(1)
            return result.get(ref, m.group(0))
        result[k] = re.sub(r"\$\{([^}]+)\}", replacer, v)
    return result

def test():
    text = """
# Comment
DB_HOST=localhost
DB_PORT=5432
DB_NAME="my database"
SECRET='s3cr3t'
MULTILINE="line1\\nline2"
"""
    env = parse(text)
    assert env["DB_HOST"] == "localhost"
    assert env["DB_PORT"] == "5432"
    assert env["DB_NAME"] == "my database"
    assert env["SECRET"] == "s3cr3t"
    s = serialize(env)
    assert "DB_HOST=localhost" in s
    merged = merge({"A": "1"}, {"A": "2", "B": "3"})
    assert merged == {"A": "2", "B": "3"}
    # interpolation
    env2 = interpolate({"HOST": "localhost", "URL": "http://${HOST}:8080"})
    assert env2["URL"] == "http://localhost:8080"
    print("OK: dotenv_parse")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: dotenv_parse.py test")
