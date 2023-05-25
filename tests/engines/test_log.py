from main.engines.items import add_item, count_items


async def test_log():
    assert (await count_items()) == 0

    await add_item()

    assert (await count_items()) == 1
