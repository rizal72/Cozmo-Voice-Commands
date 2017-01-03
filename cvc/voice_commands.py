'''
##Customization
You can add as many new commands as you like:
just prefix their function names with the language they are spoken in, *i.e. "it_" for italian, "en_" for english, so for instance you'll create the method "en_smile()" and the voice command you'll have to say will be "smile"*.
Some commands support one argument, for example: if you say *"drive for 10 seconds"*, 10 will be passed to the method *"en_drive"*, any other words will be ignored.
'''
import asyncio
import time

import cozmo
from cozmo.util import distance_mm, speed_mmps, degrees
from termcolor import colored, cprint

speed = 75
log = False

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
            if "zero" in cmd_args:
                return 0
            if "one" in cmd_args or "uno" in cmd_args:
                return 1
    return None#, None

class VoiceCommands():

    def __init__(self, robot):
        self.robot = robot

    ###### BLOCKS ######
    def en_blocks(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo plays with his blocks."
        if robot is None:
            return usage
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

    def it_gioca(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo gioca con i suoi cubi."
        if robot is None:
            return usage
        self.en_blocks(robot, cmd_args)

    def fr_joue(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo joue avec ses blocs."
        if robot is None:
            return usage
        self.en_blocks(robot, cmd_args)

###### DANCE ######

    def en_dance(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo dances."
        if robot is None:
            return usage
        print("dancing...")
        robot.play_anim("anim_speedtap_wingame_intensity02_01").wait_for_completed()
        return

    def it_balla(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo balla."
        if robot is None:
            return usage
        self.en_dance(robot, cmd_args)

    def fr_danse(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo danse."
        if robot is None:
            return usage
        self.en_dance(robot, cmd_args)

###### LOOK ######

    def en_look(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo looks for a face."
        if robot is None:
            return usage
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

    def it_guarda(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo cerca una faccia."
        if robot is None:
            return usage
        self.en_look(robot, cmd_args)

    def fr_regarde(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo regarde un visage."
        if robot is None:
            return usage
        self.en_look(robot, cmd_args)

###### FOLLOW ######

    def en_follow(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo follows a face."
        if robot is None:
            return usage
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

    def it_segui(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo segue una faccia."
        if robot is None:
            return usage
        self.en_follow(robot, cmd_args)

    def fr_suit(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo suit un visage."
        if robot is None:
            return usage
        self.en_follow(robot, cmd_args)

###### PICTURE ######

    def en_picture(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo takes a picture, then it saves it in the folder where you launched CvC."
        if robot is None:
            return usage
        robot.camera.image_stream_enabled = True
        print("taking a picture...")
        pic_filename = "cozmo_pic_" + str(int(time.time())) + ".png"
        robot.say_text("Say cheese!").wait_for_completed()
        latest_image = robot.world.latest_image
        if latest_image:
            latest_image.raw_image.convert('L').save(pic_filename)
            print ("picture saved as: " + pic_filename)
        else:
            print ("no picture saved")
        robot.camera.image_stream_enabled = False
        return

    def it_foto(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo scatta una foto, poi la salva nella cartella in cui ci si trova durante l'esecuzione di CvC."
        if robot is None:
            return usage
        self.en_picture(robot, cmd_args)

    def fr_photo(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo prend une photo, puis la sauvegarde dans le repertoire où a été lancé CvC."
        if robot is None:
            return usage
        self.en_picture(robot, cmd_args)

###### DRIVE ######

    def en_drive(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo drives forward/backwards for X seconds (i.e. 'Cozmo, drive backwards for 3 seconds')."
        if robot is None:
            return usage

        error_message = ""
        if log:
            print(cmd_args)

        #check if the user said "drive to charger" and redirect the command to en_charger()
        if "charger" in cmd_args:
            en_charger(robot, cmd_args)
            return

        drive_duration = extract_next_float(cmd_args)#[0]

        if drive_duration is not None:

            if "backward" in cmd_args or "backwards" in cmd_args:
                drive_speed = speed
                drive_duration = -drive_duration
                drive_dir = "backwards"
            else:
                drive_speed = speed
                drive_dir = "forward"

            #robot.drive_wheels(drive_speed, drive_speed, duration=drive_duration)
            robot.drive_straight(distance_mm(drive_duration*drive_speed), speed_mmps(drive_speed), should_play_anim=True).wait_for_completed()
            #time.sleep(drive_duration)

            return "I drove " + drive_dir + " for " + str(drive_duration) + " seconds!"

        return "Error: usage = " + usage + error_message

    def it_avanti(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo si muove in avanti per X secondi (es. 'Cozmo, vai avanti per 3 secondi')."
        if robot is None:
            return usage
        cmd_args.append("forward")
        self.en_drive(robot, cmd_args)

    def fr_avance(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo avance pendant X secondes (ex. 'Cozmo, avance pendant 3 secondes')."
        if robot is None:
            return usage
        cmd_args.append("forward")
        self.en_drive(robot, cmd_args)

    def it_indietro(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo si muove all'indietro per X secondi (es. 'Cozmo, vai indietro per 3 secondi')"
        if robot is None:
            return usage
        cmd_args.append("backward")
        self.en_drive(robot, cmd_args)

    def fr_recule(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo recule pendant X secondes (ex. 'Cozmo, recule pendant 3 secondes')."
        if robot is None:
            return usage
        cmd_args.append("backward")
        self.en_drive(robot, cmd_args)

###### TURN ######

    def en_turn(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo turns X degrees."
        if robot is None:
            return usage
        drive_angle = extract_next_float(cmd_args)#[0]

        if drive_angle is not None:
            robot.turn_in_place(degrees(drive_angle)).wait_for_completed()
            return "I turned " + str(drive_angle) + " degrees!"

        return "Error: usage = " + usage

    def it_ruota(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo ruota di X gradi."
        if robot is None:
            return usage
        self.en_turn(robot, cmd_args)

    def fr_tourne(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo tourne de X degrés."
        if robot is None:
            return usage
        self.en_turn(robot, cmd_args)

###### LIFT ######

    def en_lift(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo lifts his lift of X (min:0, max:1 - i.e. 'Cozmo, lift your lift of 0.5')."
        if robot is None:
            return usage
        lift_height = extract_next_float(cmd_args)#[0]

        if lift_height is not None:
            robot.set_lift_height(height=lift_height).wait_for_completed()
            return "I moved lift to " + str(lift_height)

        return "Error: usage = " + usage

    def it_solleva(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo solleva il suo braccio di X (min:0, max:1 - es. 'Cozmo, solleva il tuo braccio di 0.5')."
        if robot is None:
            return usage
        self.en_lift(robot, cmd_args)

    def fr_souleve(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo soulève son bras de X (min:0, max:1 - ex. 'Cozmo, soulève ton bras de 0.5')."
        if robot is None:
            return usage
        self.en_lift(robot, cmd_args)

###### HEAD ######

    def en_head(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo tilts his head of X (min:0, max:1)." #-25 (down) to 44.5 degrees (up)
        if robot is None:
            return usage

        head_angle_01 = extract_next_float(cmd_args)#[0]

        if head_angle_01 is not None:
            #FORMULA: Result = ((Input - InputLow) / (InputHigh - InputLow)) * (OutputHigh - OutputLow) + OutputLow;
            head_angle = head_angle_01 * (44 + 25) - 25;
            print("head angle = ", head_angle)
            head_angle_action = robot.set_head_angle(degrees(head_angle))
            clamped_head_angle = head_angle_action.angle.degrees
            head_angle_action.wait_for_completed()
            resultString = "I moved head to " + "{0:.1f}".format(clamped_head_angle)
            if abs(head_angle - clamped_head_angle) > 0.01:
                resultString += " (clamped to range)"
            return resultString

        return "Error: usage = " + usage

    def it_testa(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo muove la sua testa di X (min:0, max:1)."
        if robot is None:
            return usage
        self.en_head(robot, cmd_args)

    def fr_hoche(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo hoche sa tête de X (min:0, max:1)."
        if robot is None:
            return usage
        self.en_head(robot, cmd_args)

###### SAY ######

    def en_say(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo says X (where X is any text)."
        if robot is None:
            return usage
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

    def it_dici(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo dice X (dove X è un testo qualunque)."
        if robot is None:
            return usage
        self.en_say(robot, cmd_args)

    def fr_dit(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo dit X (où X est n'importe quel texte)."
        if robot is None:
            return usage
        self.en_say(robot, cmd_args)

    def it_bici(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "alternativo a 'dici', Cozmo dice X (dove X è un testo qualunque)."
        if robot is None:
            return usage
        self.en_say(robot, cmd_args)

###### CHARGER ######

    def en_charger(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo tries to park on is charger, in 3 tries."
        if robot is None:
            return usage

        trial = 1
        # If the robot was on the charger, drive them forward and clear of the charger
        if robot.is_on_charger:
            # drive off the charger
            if log:
                print("I am on the charger. Driving off the charger...")
            robot.drive_off_charger_contacts().wait_for_completed()
            robot.drive_straight(distance_mm(70), speed_mmps(50)).wait_for_completed()
            # Start moving the lift down
            robot.move_lift(-3)
            # turn around to look at the charger
            robot.turn_in_place(degrees(180),in_parallel=True)#.wait_for_completed()
            # Tilt the head to be level
            robot.set_head_angle(degrees(0), in_parallel=True)#.wait_for_completed()
            # wait half a second to ensure Cozmo has seen the charger
            time.sleep(0.5)
            # drive backwards away from the charger
            robot.drive_straight(distance_mm(-60), speed_mmps(50)).wait_for_completed()

        # try to find the charger
        charger = None

        # see if Cozmo already knows where the charger is
        if robot.world.charger:
            if robot.world.charger.pose.origin_id == robot.pose.origin_id:
                if log:
                    print("Cozmo already knows where the charger is!")
                charger = robot.world.charger
            else:
                # Cozmo knows about the charger, but the pose is not based on the
                # same origin as the robot (e.g. the robot was moved since seeing
                # the charger) so try to look for the charger first
                pass

        if not charger:
            # Tell Cozmo to look around for the charger
            if log:
                print("looking for the charger now...")
            look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
            try:
                charger = robot.world.wait_for_observed_charger(timeout=60)
                print("Found charger: %s" % charger)
            except asyncio.TimeoutError:
                print("Didn't see the charger")
            finally:
                # whether we find it or not, we want to stop the behavior
                look_around.stop()

        if charger:
            # lift his arms to manouver
            robot.set_lift_height(0.8,0.8,0.8,0.1)#.wait_for_completed()
            # Attempt to drive near to the charger, and then stop.
            if log:
                print("Trial number %s" % trial)
                print("Going for the charger!!!")
            action = robot.go_to_pose(charger.pose, in_parallel=True)
            action.wait_for_completed()
            if log:
                print("Completed action: result = %s" % action)
            robot.drive_straight(distance_mm(-30), speed_mmps(50)).wait_for_completed()
            if log:
                print("Done.")

            # Turn 180 (and 10) degrees, then goes backwards at full speed
            if log:
                print("Now the grand finalle: turn around and park!")
                print("Turning...")
            #this value needs to be tweaked (90 or 95)
            robot.turn_in_place(degrees(90)).wait_for_completed()
            robot.turn_in_place(degrees(90)).wait_for_completed()
            time.sleep( 1 )
            if log:
                print("Get out of the way: here I go!")
            robot.drive_straight(distance_mm(-130), speed_mmps(150)).wait_for_completed()
            if log:
                print("checking if I did it...")
            if robot.is_on_charger:
                print("I did it! Yay!")
            else:
                print("I did not manage to dock in the charger =(")
                print("Trying again...")
                robot.world.charger = None
                if log:
                    print("let me go a little bit further to be easier to see...")
                robot.drive_straight(distance_mm(90), speed_mmps(50)).wait_for_completed()
                trial += 1
                if trial < 4:
                    self.en_charger(robot)
                else:
                    print("tired of trying. Giving up =(")

    def it_base(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo cerca di ritornare nella sua base, in 3 tentativi."
        if robot is None:
            return usage
        self.en_charger(robot, cmd_args)

    def fr_chargeur(self, robot:cozmo.robot.Robot = None, cmd_args = None):
        usage = "Cozmo tente de retourner à son chargeur, en 3 tentatives."
        if robot is None:
            return usage
        self.en_charger(robot, cmd_args)
