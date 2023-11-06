from unittest.mock import AsyncMock, Mock

from pytest_mock import MockerFixture

from main import db


class CustomException(Exception):
    pass


async def test_db(mocker: MockerFixture):
    mock_scoped_session = Mock()
    mock_scoped_session_remove = AsyncMock()
    mock_scoped_session.remove = mock_scoped_session_remove

    mocker.patch.object(db, "scoped_session", mock_scoped_session)

    assert not mock_scoped_session.called

    # Main function works normally
    async with db.scope():
        assert mock_scoped_session.call_count == 1
        assert not mock_scoped_session_remove.called

    assert mock_scoped_session.call_count == 1

    # Main function raises an error, session should be cleaned up
    try:
        async with db.scope():
            assert mock_scoped_session.call_count == 2
            assert mock_scoped_session_remove.call_count == 1

            raise CustomException
    except CustomException:
        pass

    assert mock_scoped_session_remove.call_count == 2
