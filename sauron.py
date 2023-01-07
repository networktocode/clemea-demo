import time
import signal
from typing import List
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from prometheus_api_client import PrometheusConnect
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, TaskID

import typer

app = typer.Typer()
prom = PrometheusConnect(url="http://netpanda-dev:9091", disable_ssl=True)

BGP_STATES = {
    6: "Established",
    5: "OpenConfirmed",
    4: "OpenSent",
    3: "Active",
    2: "Connect",
    1: "Idle",
}


@app.command()
def get_bgp_state(
    neighbor: str = typer.Option("", help="BGP neighbor"),
    device: str = typer.Option("", help="Network device"),
):
    # Prepare the labels to help filtering out the latest metrics
    labelset = {}
    if neighbor:
        labelset.update(neighbor_address=neighbor)
    if device:
        labelset.update(device=device)

    # Get a list of all the latest metrics that matches the name and label set
    results = prom.get_current_metric_value(metric_name="bgp_session_state", label_config=labelset)
    if not results:
        typer.echo(message="No results returned :(")
        raise typer.Exit(1)

    # Print out the results
    for metric in results:
        _device = metric["metric"]["device"]
        _neighbor = metric["metric"]["neighbor_address"]
        state_code = int(metric["value"][-1])
        typer.echo(message=f"BGP State for device: {_device} - neighbor {_neighbor} => {BGP_STATES[state_code]}")


########################################################################################################################


def sizeof_fmt(num, suffix="bps"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1000.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1000.0
    return f"{num:.1f}Yi{suffix}"


progress = Progress(
    TextColumn("[bold blue]{task.fields[interface_id]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    "Traffic: {task.fields[traffic]}",
    "•",
    TimeRemainingColumn(),
)


done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


def get_interface_traffic(task_id: TaskID, interface: str, device: str):
    # progress.console.log(f"Requesting {device}: {interface}")
    query = f'rate(interface_in_octets{{device="{device}", interface="{interface}"}}[2m])*8'
    progress.update(task_id, total=100)
    progress.start_task(task_id)
    for i in range(100):
        result = prom.custom_query(query=query)
        traffic = float(result[0]["value"][-1])
        progress.console.log(f"{device}: {interface} ==> {sizeof_fmt(traffic)}")
        progress.update(task_id, traffic=sizeof_fmt(traffic), advance=1)
        time.sleep(2)
        if done_event.is_set():
            return
    # progress.console.log("Interface traffic watch completed")


@app.command()
def watch_interface_traffic(
    interface: List[str] = typer.Option(..., help="List of interfaces to watch traffic"),
    device: str = typer.Option(..., help="Network device"),
):
    with progress:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for intf in interface:
                task_id = progress.add_task("interface", interface_id=f"{device}: {intf}", start=False, traffic=sizeof_fmt(0))
                pool.submit(get_interface_traffic, task_id, intf, device)


if __name__ == "__main__":
    app()
