from dungeoneer.game_assets import load_sound_file, sfx_file


def sfx_from_name(name):
    class NullSfx:
        def play(self, *args, **kwargs):
            del args
            del kwargs
            del self

    if not name:
        return NullSfx()
    return load_sound_file(sfx_file(name))


class SfxEvents:
    def __init__(self, *, create=None, pickup=None, destroy=None, activate=None):
        self._events = locals()

    @property
    def create(self):
        return sfx_from_name(self._events["create"])

    @property
    def pickup(self):
        return sfx_from_name(self._events["pickup"])

    @property
    def destroy(self):
        return sfx_from_name(self._events["destroy"])

    @property
    def activate(self):
        return sfx_from_name(self._events["activate"])
