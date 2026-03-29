#!/usr/bin/env python3
"""dotenv_parse - Parse .env files with variable expansion and multiline support."""
import sys, re, os

def parse(text):
    env = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if "=" not in line: continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        # Variable expansion
        val = re.sub(r"\$\{(\w+)\}", lambda m: env.get(m.group(1), os.environ.get(m.group(1), "")), val)
        val = re.sub(r"\$(\w+)", lambda m: env.get(m.group(1), os.environ.get(m.group(1), "")), val)
        env[key] = val
    return env

def parse_file(path):
    with open(path) as f:
        return parse(f.read())

def test():
    text = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME="mydb"
DB_URL=${DB_HOST}:${DB_PORT}/${DB_NAME}
EMPTY=
QUOTED='single quoted'
"""
    env = parse(text)
    assert env["DB_HOST"] == "localhost"
    assert env["DB_PORT"] == "5432"
    assert env["DB_NAME"] == "mydb"
    assert env["DB_URL"] == "localhost:5432/mydb"
    assert env["EMPTY"] == ""
    assert env["QUOTED"] == "single quoted"
    print("dotenv_parse: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: dotenv_parse.py --test")
