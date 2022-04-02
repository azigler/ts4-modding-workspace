import sims4.commands
import zone
from ui.ui_dialog_notification import UiDialogNotification
from sims4.localization import LocalizationHelperTuning
from injector import inject_to
from functools import wraps

@sims4.commands.Command('hello_world', command_type=sims4.commands.CommandType.Live)
def myfirstscript(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("Hello world!")
 
# CREDIT: LOT51
@inject_to(zone.Zone, 'on_loading_screen_animation_finished')
def lot51_on_loading_screen_lifted(original, self,  *args, **kwargs):
    result = original(self, *args, **kwargs)
    try:
        title = LocalizationHelperTuning.get_raw_text("Injection was successful!")
        text = LocalizationHelperTuning.get_raw_text("Hello world!")
        dialog =  UiDialogNotification.TunableFactory().default(
            None,
            title=lambda *args, **kwargs: title,
            text=lambda *args, **kwargs: text,
        )

        dialog.show_dialog()
    except BaseException as e:
        pass
    return result