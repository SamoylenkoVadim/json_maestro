import async_timeout
import asyncio
import simplejson as json
from traceback import format_exc
from time import monotonic

import fl.logging_utils.logger_constants as log_const
from fl.configs.configs import configs
from prometheus_async.aio import time
from fl.monitoring.monitoring import monitoring
from fl.logging_utils.logger_utils import system_log
from fl.configs.ssl import ssl_context
from fl.monitoring.monitoring_objects import GEO_REQ_TIME


@time(GEO_REQ_TIME)
async def send_geo_request(message):
    geo_config = configs["ab_config"].get("geo_service")
    try:
        location = message.payload["meta"]["location"]
        lat = location["lat"]
        lon = location["lon"]
        timeout = geo_config.get("timeout", 100)/1000
        base_url = geo_config.get("url")
        url = base_url.format(lat, lon)
    except Exception as e:
        system_log("Error in creating geo request: %(EXCEPTION)s",
                   message_obj=message,
                   params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                           "EXCEPTION": format_exc()},
                   level="ERROR")
        return None, 520

    try:
        async with async_timeout.timeout(timeout):
            message.geo_session.message = message
            monitoring.got_counter("fl_geo_request")
            system_log("Send request to geo: url - %(url)s.",
                       message_obj=message,
                       level="INFO",
                       params={"url": url, "base_url": base_url})
            request_id = str(message.message_id)
            verify_ssl = geo_config.get("verify_ssl", True)

            start_time = monotonic()
            async with message.geo_session.get(url=url, headers={"XRequestId": request_id}, verify_ssl=verify_ssl,
                                   ssl_context=ssl_context("geoservice_cert.pem", "geoservice_key.pem")) as resp:
                resp_text = await resp.text()
                response_time = (monotonic() - start_time) * 1000
                status = resp.status
                monitoring.got_counter("fl_geo_response")
                system_log(
                    "Get response from geo: status - %(status)s, response text - %(text)s, XRequestId: %(request)s.",
                    message_obj=message,
                    level="INFO",
                    params={"status": status,
                            "text": resp_text,
                            "request": request_id,
                            "process_time": response_time,
                            "url": url,
                            "base_url": base_url})
                return resp_text, status
    except asyncio.TimeoutError:
        monitoring.got_counter("fl_geo_timeout")
        system_log("Timeout while awaiting for message: url - %(url)s.",
                   message_obj=message,
                   params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                           "url": url,
                           "base_url": base_url
                           },
                   level="ERROR")
        return None, asyncio.TimeoutError
    except Exception as e:
        system_log("Error in send_geo_request: %(EXCEPTION)s, url - %(url)s",
                   message_obj=message,
                   params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                           "EXCEPTION": format_exc(),
                           "url": url,
                           "base_url": base_url
                           },
                   level="ERROR")
        return None, 520


def begin_geo_interaction(model, message):
    return asyncio.get_event_loop().create_task(send_geo_request(message)) if model.is_geo(message) else None


async def end_geo_interaction(task, message):
    if task:
        get_response, status = await task
        if status == 200:
            try:
                return json.loads(get_response)
            except:
                monitoring.got_counter("fl_geo_exception")
                system_log("Error in creating json in end_geo_interaction: %(EXCEPTION)s,"
                           " geo_response: %(geo_response)s",
                           message_obj=message,
                           params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                                   "EXCEPTION": format_exc(),
                                   "geo_response": get_response},
                           level="ERROR")
        elif status == 520:
            monitoring.got_counter("fl_geo_exception")
        else:
            monitoring.got_counter("fl_geo_exception")
            system_log("Status code received: %(STATUS_CODE)s",
                       message_obj=message,
                       params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                               "STATUS_CODE": status
                               },
                       level="ERROR")
    return {}
