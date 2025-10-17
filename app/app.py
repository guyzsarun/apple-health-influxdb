import influxdb_client
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from influxdb_client.client.write_api import SYNCHRONOUS
from fastapi import FastAPI, HTTPException, Request
from opentelemetry import trace

from config import settings
from utils import *


DATAPOINTS_CHUNK = settings.DATAPOINTS_CHUNK

logger = setup_logger("apple-health")
tracer = trace.get_tracer(__name__)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

client = influxdb_client.InfluxDBClient(
    url=settings.INFLUX_URL,
    token=settings.INFLUX_TOKEN,
    org=settings.INFLUX_ORG
)


def write_to_influx(data: list, bucket: str = "metrics"):
    with tracer.start_as_current_span("write_influx"):
        logger.info(f"DB Write Started")
        try:
            for i in range(0, len(data), DATAPOINTS_CHUNK):
                logger.info("DB Writing chunk {}".format(i))
                write_api = client.write_api(write_options=SYNCHRONOUS)
                write_api.write(bucket=bucket, org=settings.INFLUX_ORG, record=data[i : i + DATAPOINTS_CHUNK])
        except Exception as e:
            logger.exception("Caught Exception. See stacktrace for details.", e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

        logger.info(f"DB Metrics Write Complete")


def ingest_metrics(metrics: list):
    with tracer.start_as_current_span("ingest_metrics"):
        logger.info("Ingesting Metrics")
        transformed_data = []

        for metric in metrics:
            for datapoint in metric["data"]:
                data, _ = split_fields(datapoint)

                point = {
                    "measurement": metric["name"],
                    "time": datapoint["date"],
                    "fields": data,
                }
                transformed_data.append(point)

        logger.info(f"Data Transformation Complete")
        logger.info(f"Number of data points to write: {len(transformed_data)}")

        write_to_influx(transformed_data)

@app.post("/")
def collect(healthkit_data: dict, request: Request):
    logger.info("Request received")
    try:
        ingest_metrics(healthkit_data.get("data", {}).get("metrics", []))
    except Exception as e:
        logger.exception("Caught Exception. See stacktrace for details.", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7788)