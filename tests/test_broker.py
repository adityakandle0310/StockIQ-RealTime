import asyncio
import contextlib

from app.broker import InMemoryBroker


def test_publish_reaches_all_subscribers():
    async def scenario():
        broker = InMemoryBroker()
        received = {"a": [], "b": []}

        async def listen(name, count):
            stream = broker.subscribe("ticks")
            async with contextlib.aclosing(stream):
                async for message in stream:
                    received[name].append(message)
                    if len(received[name]) == count:
                        return

        tasks = [asyncio.create_task(listen("a", 2)), asyncio.create_task(listen("b", 2))]
        await asyncio.sleep(0)  # let both subscribe
        await broker.publish("ticks", "one")
        await broker.publish("ticks", "two")
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=2)
        return received

    assert asyncio.run(scenario()) == {"a": ["one", "two"], "b": ["one", "two"]}


def test_channels_are_isolated():
    async def scenario():
        broker = InMemoryBroker()
        got = []

        async def listen():
            stream = broker.subscribe("alerts")
            async with contextlib.aclosing(stream):
                async for message in stream:
                    got.append(message)
                    return

        task = asyncio.create_task(listen())
        await asyncio.sleep(0)
        await broker.publish("ticks", "ignored")
        await broker.publish("alerts", "wanted")
        await asyncio.wait_for(task, timeout=2)
        return got

    assert asyncio.run(scenario()) == ["wanted"]


def test_subscriber_is_removed_after_close():
    async def scenario():
        broker = InMemoryBroker()
        stream = broker.subscribe("ticks")
        task = asyncio.create_task(stream.__anext__())
        await asyncio.sleep(0)
        assert broker.subscriber_count("ticks") == 1
        await broker.publish("ticks", "x")
        await task
        await stream.aclose()
        return broker.subscriber_count("ticks")

    assert asyncio.run(scenario()) == 0


def test_slow_subscriber_drops_oldest_instead_of_blocking():
    async def scenario():
        broker = InMemoryBroker(max_queue=2)
        stream = broker.subscribe("ticks")
        first = asyncio.create_task(stream.__anext__())
        await asyncio.sleep(0)
        for message in ("1", "2", "3", "4"):
            await broker.publish("ticks", message)
        results = [await first, await stream.__anext__()]
        await stream.aclose()
        return results

    # the queue holds at most 2, so only the two newest messages survive
    assert asyncio.run(scenario()) == ["3", "4"]