#! /usr/bin/env python3

import toml, json, subprocess

HERMES = "hermes"
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
            print(f"Success: {client_id} ({chain_id})")
        else:
            print(f"Failed: {result}")


update_clients()
