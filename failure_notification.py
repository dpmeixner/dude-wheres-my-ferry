from pushbullet import Pushbullet
import secrets
pb = Pushbullet(pb_key)
push = pb.push_note("Error", "Script failed to run")