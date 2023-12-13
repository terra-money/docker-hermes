#! /usr/bin/env python3

import toml, json, subprocess, sys
from datetime import datetime, time

HERMES = "/usr/local/bin/hermes"
HERMES_CONFIG = "/hermes/config.toml"


def hermes(command):
    process = subprocess.run(
        [HERMES, "--config", HERMES_CONFIG, "--json"] + command.split(" "),
        stdout=subprocess.PIPE,
        text=True,
    )
    output_lines = process.stdout.splitlines()

    for line in output_lines:
        line_json = json.loads(line)
        if "result" in line_json:
            return line_json
    else:
        return None


def get_connection(chain_id, port, channel):
    output = hermes(
        f"query channel end --chain {chain_id} --port {port} --channel {channel}"
    )

    if output["status"] == "success":
        return output["result"]["connection_hops"][0]
    else:
        return None


def get_client_id(chain_id, connection):
    output = hermes(
        f"query connection end --chain {chain_id} --connection {connection}"
    )

    if output["status"] == "success":
        return output["result"]["client_id"]
    else:
        return None


def get_clients_from_config():
    config = toml.load(HERMES_CONFIG)
    clients = []

    for chain in config["chains"]:
        chain_id = chain["id"]
        whitelist = chain["packet_filter"]["list"]

        for position in whitelist:
            port = position[0]
            channel = position[1]

            connection = get_connection(chain_id, port, channel)
            if connection:
                client = get_client_id(chain_id, connection)
                if client:
                    clients.append((chain_id, client))

    return clients


def update_clients():
    clients = get_clients_from_config()
    for client in clients:
        chain_id = client[0]
        client_id = client[1]

        output = hermes(f"update client --host-chain {chain_id} --client {client_id}")
        result = output["result"]

        if output["status"] == "success":
            write_stderr(f"Success: {client_id} ({chain_id})\n")
        else:
            write_stderr(f"Failed: {result}\n")


def is_update_time():
    current_time = datetime.utcnow().time()

    update_start_time = time(0, 0)
    update_end_time = time(1, 0)

    return update_start_time <= current_time < update_end_time


def write_stdout(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()


def main():
    while True:
        write_stdout("READY\n")
        sys.stdin.readline()

        if is_update_time():
            update_clients()

        write_stdout("RESULT 2\nOK")


if __name__ == "__main__":
    main()
