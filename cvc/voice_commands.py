'''
##Customization
You can add as many new commands as you like:
just prefix their function names with the language they are spoken in, *i.e. "it_" for italian, "en_" for english, so for instance you'll create the method "en_smile()" and the voice command you'll have to say will be "smile"*.
Some commands support one argument, for example: if you say *"drive for 10 seconds"*, 10 will be passed to the method *"en_drive"*, any other words will be ignored.
'''
import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps, degrees
from termcolor import colored, cprint

speed = 50

def extract_float(cmd_args, index=0):
    if len(cmd_args) > index:
        try:
            float_val = float(cmd_args[index])
            return float_val
        except ValueError:
            pass
    return None


def extract_next_float(cmd_args, index=0):
    #Loop through arguments to find first float and position!

    for i in range(index, len(cmd_args)):
        try:
            float_val = float(cmd_args[i])
            return float_val#, i #can return position if needed
        except ValueError:
            pass
    return None#, None

class VoiceCommands():

    def __init__(self, robot):
        self.robot = robot

    ###### ACTIONS ######
    def en_blocks(self, robot, cmd_args):
        usage = "Do blocks"
        print("looking for my blocks...")
        lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

        cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)

        print("found %s cube(s)" % cubes)

        lookaround.stop()

        if len(cubes) == 0:
            robot.play_anim_trigger(cozmo.anim.Triggers.MajorFail).wait_for_completed()
        elif len(cubes) == 1:
            robot.run_timed_behavior(cozmo.behavior.BehaviorTypes.RollBlock, active_time=60)
        else:
            robot.run_timed_behavior(cozmo.behavior.BehaviorTypes.StackBlocks, active_time=120)

    def it_gioca(self, robot, cmd_args):
        self.en_blocks(robot,cmd_args)

    def en_dance(self, robot, cmd_args):
        usage = "Dance"
        print("dancing...")
        robot.play_anim("anim_speedtap_wingame_intensity02_01").wait_for_completed()
        return

    def it_balla(self, robot, cmd_args):
        self.en_dance(robot,cmd_args)

    def en_look(self, robot, cmd_args):
        usage = "Look for a face"
        any_face = None
        print("Looking for a face...")
        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        robot.move_lift(-3)
        look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)

        try:
            any_face = robot.world.wait_for_observed_face(timeout=30)

        except asyncio.TimeoutError:
            print("Didn't find anyone :-(")

        finally:
            # whether we find it or not, we want to stop the behavior
            look_around.stop()

        if any_face is None:
            robot.play_anim_trigger(cozmo.anim.Triggers.MajorFail).wait_for_completed()
            return

        print("Yay, found someone!")

        anim = robot.play_anim_trigger(cozmo.anim.Triggers.LookInPlaceForFacesBodyPause)
        anim.wait_for_completed()

    def it_guarda(self, robot, cmd_args):
        self.en_look(robot,cmd_args)

    def en_follow(self, robot, cmd_args):
        usage = "Follow a face"
        print("Following your face - any face...")
        # Move lift down and tilt the head up
        robot.move_lift(-3)
        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

        face_to_follow = None

        while True:
            turn_action = None
            if face_to_follow:
            # start turning towards the face
                turn_action = robot.turn_towards_face(face_to_follow)

            if not (face_to_follow and face_to_follow.is_visible):
                # find a visible face, timeout if nothing found after a short while
                try:
                    face_to_follow = robot.world.wait_for_observed_face(timeout=30)
                except asyncio.TimeoutError:
                    return "Didn't find a face - exiting!"

            if turn_action:
                # Complete the turn action if one was in progress
                turn_action.wait_for_completed()

            #time.sleep(.1)

    def it_segui(self, robot, cmd_args):
        self.en_follow(robot,cmd_args)

    def en_picture(self, robot, cmd_args):
        usage = "Take a picture"
        print("taking a picture...")
        pic_filename = "picture.png"
        robot.say_text("Say cheese!").wait_for_completed()
        latest_image = robot.world.latest_image
        if latest_image:
            latest_image.raw_image.convert('L').save(pic_filename)
            print ("picture saved as: " + pic_filename)
        else:
            print ("no picture saved")
        return

    def it_foto(self, robot, cmd_args):
        self.en_picture(robot,cmd_args)

    #NEW COMMANDS#
    def en_drive(self, robot, cmd_args):
        usage = "Drive forward/backwards X seconds"
        error_message = ""
        #print(cmd_args)
        drive_duration = extract_next_float(cmd_args)#[0]

        if drive_duration is not None:

            if "backward" in cmd_args or "backwards" in cmd_args:
                drive_speed = -speed
                drive_dir = "backwards"
            else:
                drive_speed = speed
                drive_dir = "forward"

            robot.drive_wheels(drive_speed, drive_speed, duration=drive_duration)
            time.sleep(drive_duration)

            return "I drove " + drive_dir + " for " + str(drive_duration) + " seconds!"

        return "Error: usage = " + usage + error_message

    def it_avanti(self, robot, cmd_args):
        cmd_args.append("forward")
        self.en_drive(robot,cmd_args)

    def it_indietro(self, robot, cmd_args):
        cmd_args.append("backward")
        self.en_drive(robot,cmd_args)

    def en_turn(self, robot, cmd_args):
        usage = "turn X degrees"

        drive_angle = extract_next_float(cmd_args)#[0]

        if drive_angle is not None:
            robot.turn_in_place(degrees(drive_angle)).wait_for_completed()
            return "I turned " + str(drive_angle) + " degrees!"

        return "Error: usage = " + usage

    def it_ruota(self, robot, cmd_args):
        self.en_turn(robot,cmd_args)

    def en_lift(self, robot, cmd_args):
        usage = "Lift X (min:0, max:1)"

        lift_height = extract_next_float(cmd_args)#[0]

        if lift_height is not None:
            robot.set_lift_height(height=lift_height).wait_for_completed()
            return "I moved lift to " + str(lift_height)

        return "Error: usage = " + usage

    def it_solleva(self, robot, cmd_args):
        self.en_lift(robot,cmd_args)

    def en_head(self, robot, cmd_args):
        usage = "Tilt head for X degrees (min:-25, max: 44)" #-25 (down) to 44.5 degrees (up)

        head_angle = extract_next_float(cmd_args)#[0]

        if head_angle is not None:
            head_angle_action = robot.set_head_angle(degrees(head_angle))
            clamped_head_angle = head_angle_action.angle.degrees
            head_angle_action.wait_for_completed()
            resultString = "I moved head to " + "{0:.1f}".format(clamped_head_angle)
            if abs(head_angle - clamped_head_angle) > 0.01:
                resultString += " (clamped to range)"
            return resultString

        return "Error: usage = " + usage

    def it_testa(self, robot, cmd_args):
        self.en_head(robot,cmd_args)

    def en_say(self, robot, cmd_args):
        usage = "Say X (where X is any text to say)"

        entire_message = None
        if len(cmd_args) > 0:
            try:
                entire_message = ""
                for s in cmd_args:
                    entire_message = entire_message + " " + str(s)
                entire_message = entire_message.strip()
            except:
                pass

        if (entire_message is not None) and (len(entire_message) > 0):
            robot.say_text(entire_message).wait_for_completed()
            return 'I said "' + entire_message + '"!'

        return "Error: usage = " + usage

    def it_dici(self, robot, cmd_args):
        self.en_say(robot,cmd_args)

    def it_bici(self, robot, cmd_args):
        self.en_say(robot,cmd_args)
