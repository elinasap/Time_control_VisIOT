from flask import Flask, render_template
from influxdb_client import InfluxDBClient
from datetime import datetime
import plotly.graph_objs as go

app = Flask(__name__)

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "LFTefMVg8dhz22I2V2sUtjnX9i_1WcqdKM9Bjumc8fcmf1gxLJ2B6sSzSD3TbxqnXSTYfHSEV0GBAswkoyDXjw=="
INFLUXDB_ORG = "myorg"

BUCKET1 = "try5"
BUCKET2 = "try6"
BUCKET3 = "try7"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()


def get_press_times(bucket):
    query = f'''
        from(bucket: "{bucket}")
        |> range(start: -10m)
        |> filter(fn: (r) => r["_measurement"] == "button_press")
        |> sort(columns: ["_time"])
    '''
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    times = []
    for table in result:
        for record in table.records:
            times.append(record.get_time())
    return times


def check_false_start(t1, t2, starts):
    if not starts:
        return []
    start_time = min(starts)
    false_starters = []
    if any(t < start_time for t in t1):
        false_starters.append("Спортсмен 1")
    if any(t < start_time for t in t2):
        false_starters.append("Спортсмен 2")
    return false_starters


def get_winner_and_time(t1, t2):
    if len(t1) >= 5 or len(t2) >= 5:
        if len(t1) >= 5 and (len(t2) < 5 or t1[4] < t2[4]):
            return "Спортсмен 1", t1[4]
        elif len(t2) >= 5:
            return "Спортсмен 2", t2[4]
    return None, None


def calculate_speeds(times):
    speeds = []
    for i in range(1, min(len(times), 5)):  # от 1 до 4 интервалов
        delta = (times[i] - times[i - 1]).total_seconds()
        if delta > 0:
            speed = 50 / delta  # 50 метров
            speeds.append(round(speed, 2))
        else:
            speeds.append(0)
    return speeds


@app.route("/")
def index():
    times1 = get_press_times(BUCKET1)
    times2 = get_press_times(BUCKET2)
    times3 = get_press_times(BUCKET3)

    false_starters = check_false_start(times1, times2, times3)
    winner, finish_time = get_winner_and_time(times1, times2)

    speeds1 = calculate_speeds(times1)
    speeds2 = calculate_speeds(times2)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=times1,
        y=[1] * len(times1),
        mode="markers",
        name="Спортсмен 1",
        marker=dict(color="blue", size=10)
    ))

    fig.add_trace(go.Scatter(
        x=times2,
        y=[2] * len(times2),
        mode="markers",
        name="Спортсмен 2",
        marker=dict(color="red", size=10)
    ))

    fig.add_trace(go.Scatter(
        x=times3,
        y=[3] * len(times3),
        mode="markers",
        name="СТАРТ",
        marker=dict(color="green", size=10)
    ))

    fig.update_layout(
        title="График нажатий кнопок",
        xaxis_title="Время",
        yaxis=dict(
            tickvals=[1, 2, 3],
            ticktext=["Спортсмен 1", "Спортсмен 2", "СТАРТ"]
        ),
        height=500
    )

    graph_html = fig.to_html(full_html=False)

    return render_template("index.html",
                           graph=graph_html,
                           false_starters=false_starters,
                           winner=winner,
                           finish_time=finish_time,
                           speeds1=speeds1,
                           speeds2=speeds2)


if __name__ == "__main__":
    app.run(debug=True)
