from cli_app.utils.emoji import Emoji


def test_emoji_members_are_strings() -> None:
    for member in Emoji:
        assert isinstance(member, str)


def test_emoji_rocket() -> None:
    assert Emoji.ROCKET == "🚀"


def test_emoji_stop_sign() -> None:
    assert Emoji.STOP_SIGN == "🛑"


def test_emoji_sunglasses() -> None:
    assert Emoji.SUNGLASSES == "😎"


def test_emoji_pray() -> None:
    assert Emoji.PRAY == "🙏"


def test_emoji_expected_members() -> None:
    names = {e.name for e in Emoji}
    assert names == {"ROCKET", "STOP_SIGN", "SUNGLASSES", "PRAY"}
