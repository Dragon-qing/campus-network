import asyncio
import aioconsole

async def main(main_loop):
    t = main_loop.create_task(aioconsole.ainput(">>"))
    try:
        await asyncio.wait_for(t, timeout=3)
        value = t.result()
    except asyncio.TimeoutError as _:
        value = "default value"
    print()
    print(value)
    return value

if __name__ == '__main__':
    l = asyncio.get_event_loop()
    value = l.run_until_complete(main(l))
    print(123)
    l.close()

