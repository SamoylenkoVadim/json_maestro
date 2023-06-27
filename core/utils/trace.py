import aiohttp
import asyncio
from fl.logging_utils.logger_utils import trace_log


async def on_request_start(session, trace_config_ctx, params):
    trace_config_ctx.start = asyncio.get_event_loop().time() * 1000
    trace_log("REQUEST START TIME %(start_time)s",
              message_obj=session.message,
              params={"start_time": trace_config_ctx.start})


async def on_request_end(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("REQUEST TOOK time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_request_chunk_sent(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("REQUEST CHUNK SETN TOOK time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_response_chunk_received(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("RESPONSE CHUNK SETN TOOK time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_connection_queued_start(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("CONNECTION QUEUED START TIME time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_connection_queued_end(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("CONNECTION QUEUED END TIME time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_connection_create_start(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("CONNECTION CREATE START TIME time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_connection_create_end(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("CONNECTION CREATE END TIME time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_dns_resolvehost_start(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("CONNECTION DNS RESOLVE START TIME time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


async def on_dns_resolvehost_end(session, trace_config_ctx, params):
    elapsed = asyncio.get_event_loop().time() * 1000 - trace_config_ctx.start
    trace_log("CONNECTION DNS RESOLVE END TIME time - %(time)s elapsed - %(elapsed)s",
              message_obj=session.message,
              params={"time": asyncio.get_event_loop().time() * 1000,
                      "elapsed": elapsed})


trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)
trace_config.on_dns_resolvehost_start.append(on_dns_resolvehost_start)
trace_config.on_dns_resolvehost_end.append(on_dns_resolvehost_end)
trace_config.on_connection_create_start.append(on_connection_create_start)
trace_config.on_connection_create_end.append(on_connection_create_end)
trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
trace_config.on_response_chunk_received.append(on_response_chunk_received)
