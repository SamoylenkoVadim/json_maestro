import aiohttp
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
from fl.monitoring.monitoring_objects import UFS_REQ_TIME
from fl.utils.trace import trace_config


def get_url(url, url_path):
    if url.endswith('/'):
        url = url[:-1]
    if "https" not in url:
        if "http" in url:
            url = url.replace("http", "https")
        else:
            url = "https://" + url
    return url+url_path


@time(UFS_REQ_TIME)
async def send_ufs_request(message):
    ufs_config = configs["ab_config"].get("ufs_launcher")
    payload = message.payload
    try:
        ufs_info = payload["meta"]["ufsInfo"]
        cookies = {
            "UFS-SESSION": ufs_info["ufsSession"]["UFS-SESSION"],
            "UFS-TOKEN": ufs_info["ufsSession"]["UFS-TOKEN"]
        }
        application_platform = "iPhone" if message.device["platformType"].lower() == "ios" else "аndroid"
        data = {
          "applicationPlatform": application_platform,
          "applicationVersion": message.device["additionalInfo"]["sdk_version"]
        }
        timeout = ufs_config.get("timeout", 100)/1000
        url = get_url(ufs_info.get("host"), ufs_config.get("url_path", "/sm-uko/v1/va/configuration"))
    except Exception as e:
        system_log("Error in creating ufs request: %(EXCEPTION)s",
                   message_obj=message,
                   params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                           "EXCEPTION": format_exc()},
                   level="ERROR")
        return None, 520, None

    try:
        async with async_timeout.timeout(timeout):
            message.ufs_session.message = message
            monitoring.got_counter("fl_ufs_request")
            system_log("Send request to UFS: cookies - %(cookies)s, url - %(url)s, data - %(data)s.",
                       message_obj=message,
                       level="INFO",
                       params={"data": data, "cookies": cookies, "url": url})
            start_time = monotonic()
            async with message.ufs_session.post(url=url, json=data, verify_ssl=False, cookies=cookies) as resp:
                resp_text = await resp.text()
                response_time = (monotonic() - start_time) * 1000
                status = resp.status
                monitoring.got_counter("fl_ufs_response")
                system_log("Get response from UFS: status - %(status)s, response text - %(text)s",
                           message_obj=message,
                           level="INFO",
                           params={"status": status, "text": resp_text, "process_time": response_time, "url": url})
                return resp_text, status, resp.cookies
    except asyncio.TimeoutError:
        system_log("Timeout while awaiting for message: cookies - %(cookies)s, url - %(url)s, data - %(data)s.",
                   message_obj=message,
                   params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                           "data": data,
                           "cookies": cookies,
                           "url": url
                           },
                   level="ERROR")
        return None, asyncio.TimeoutError, cookies
    except Exception as e:
        system_log("Error in send_ufs_request: %(EXCEPTION)s, cookies - %(cookies)s, url - %(url)s, data - %(data)s.",
                   message_obj=message,
                   params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                           "EXCEPTION": format_exc(),
                           "data": data,
                           "cookies": cookies,
                           "url": url
                           },
                   level="ERROR")
        return None, 520, cookies


def begin_ufs_interaction(model, message):
    return asyncio.get_event_loop().create_task(send_ufs_request(message)) if model.is_efs(message) else None


async def end_ufs_interaction(task, message):
    if task:
        ufs_response, status, cookies = await task
        if status == 200:
            try:
                response = json.loads(ufs_response)
                if not response["success"]:
                    monitoring.got_counter("fl_ufs_unsuccess_in_response")
                return response
            except:
                monitoring.got_counter("fl_ufs_exception")
                system_log("Error in creating json in end_ufs_interaction: %(EXCEPTION)s, ufs_response: "
                           "%(ufs_response)s",
                           message_obj=message,
                           params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                                   "EXCEPTION": format_exc(),
                                   "ufs_response": ufs_response},
                           level="ERROR")
        elif status == asyncio.TimeoutError:
            monitoring.got_counter("fl_ufs_timeout")
        elif status == 520:
            monitoring.got_counter("fl_ufs_exception")
        else:
            monitoring.got_counter("fl_ufs_exception")
            system_log("Status code received: %(STATUS_CODE)s, cookies - %(cookies)s, url - %(url)s",
                       message_obj=message,
                       params={log_const.KEY_NAME: log_const.EXCEPTION_VALUE,
                               "STATUS_CODE": status,
                               "cookies": cookies,
                               "url": message.payload.get("ufsInfo",{}).get("host")
                               },
                       level="ERROR")
    return {}
