# Lab 2 - Using telemetry data programatically

The second part of the lab consist of developing a series of scripts to interact and manipulate the collected and enriched telemetry data in a CLI application.

For this reason we have the example CLI app [`sauron.py`](sauron.py) that has commands for each task of this section to give example of how these tasks can be completed.

The python script `sauron.py` uses [`typer`](https://typer.tiangolo.com/) with [`rich`](https://rich.readthedocs.io/en/stable/introduction.html#quick-start) as dependency to create a beautiful CLI app. It also comes with a python client to interact with Prometheus and Nautobot. In order to install them:

```shell
# Install dependencies
pip install -r requeriments.txt
```

## Tasks

### 1- Prints interfaces High on bandwidth usage on a network device based on a specific threshold

<details><summary>Solution</summary>
<p>

See command `get_links_high_on_in_bw` in `sauron.py`. Here is a snippet:

```python
@app.command()
def get_links_high_on_in_bw(
    device: Optional[str] = typer.Option("", help="Network device or regular expression for multiple devices"),
    device_role: Optional[str] = typer.Option("", help="Role fo the device(s) in the network topology"),
    threshold: float = typer.Option(1000.0, help="Bandwidth threshold on bits per second"),
):
    typer.echo("Getting links with Bandwidth higher than threshold")
    # Prepare the labels to help filtering out the latest metrics
    query = f'rate(interface_in_octets{{device=~"{device}"}}[2m])*8 > {threshold}'

    # Get a list of all the latest metrics that matches the name and label set
    prom = PrometheusConnect(url=prom_url["url"], disable_ssl=True)
    results = prom.custom_query(query=query)
    if not results:
        typer.echo(message="No results returned :(")
        raise typer.Exit(1)

    # Print out the results
    for metric in results:
        _role = metric["metric"]["device_role"]
        _device = metric["metric"]["device"]
        _interface = metric["metric"]["interface"]
        _traffic = sizeof_fmt(float(metric["value"][-1]))
        typer.echo(message=f"Role: {device_role} - device: {_device} - interface: {_interface} => Traffic IN: {_traffic}")
    return
```

Try it out!

```shell
python sauron.py --prometheus-host http://localhost:9091 get-links-high-on-in-bw --device netpanda-jcy-bb-01
```

</p>
</details>

## 2- Allow to show more network devices by using filters like `device_role` or `region`

<details><summary>Solution</summary>
<p>

For this query, we added a `device_role` parameter which creates a slightly different query that can bring the information of multiple devices as well.

```python
@app.command()
def get_links_high_on_in_bw(
    device: Optional[str] = typer.Option("", help="Network device or regular expression for multiple devices"),
    device_role: Optional[str] = typer.Option("", help="Role fo the device(s) in the network topology"),
    threshold: float = typer.Option(1000.0, help="Bandwidth threshold on bits per second"),
):
    typer.echo("Getting links with Bandwidth higher than threshold")
    # Prepare the labels to help filtering out the latest metrics
    query = ""
    if device:
        query = f'rate(interface_in_octets{{device=~"{device}"}}[2m])*8 > {threshold}'
    if device_role:
        query = f'rate(interface_in_octets{{device_role="{device_role}"}}[2m])*8 > {threshold}'
    if not query:
        typer.echo(message="No query generated :(")
        raise typer.Exit(1)

    # Get a list of all the latest metrics that matches the name and label set
    prom = PrometheusConnect(url=prom_url["url"], disable_ssl=True)
    results = prom.custom_query(query=query)
    if not results:
        typer.echo(message="No results returned :(")
        raise typer.Exit(1)

    # Print out the results
    for metric in results:
        _role = metric["metric"]["device_role"]
        _device = metric["metric"]["device"]
        _interface = metric["metric"]["interface"]
        _traffic = sizeof_fmt(float(metric["value"][-1]))
        typer.echo(message=f"Role: {device_role} - device: {_device} - interface: {_interface} => Traffic IN: {_traffic}")
    return
```

Try it out!

```shell
python sauron.py --prometheus-host http://localhost:9091 get-links-high-on-in-bw --device-role backbone
```

</p>
</details>

## 3- Retrieve BGP state for `device` or BGP neighbor

<details><summary>Solution</summary>
<p>

Similar to the previous one.

```python
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
    prom = PrometheusConnect(url=prom_url["url"], disable_ssl=True)
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
```

Try it out!

```shell
python sauron.py --prometheus-host http://localhost:9091 get-bgp-state --device netpanda-jcy-rtr-02
```

</p>
</details>

