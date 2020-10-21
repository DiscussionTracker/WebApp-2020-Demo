import os
from functools import partial
import remi.gui as gui
#trying out defining constants in this place

#some constants
#Top menu names
MENU_CURR_DISC = "menu_curr_disc"
MENU_DISC_HIST = "menu_disc_hist"
MENU_PLAN_NEXT = "menu_plan_next"
#Current discussion menu names
MENU_OVER_VIEW = "overview"
MENU_ANOT_TRAN = "annotTrans"
MENU_COLB_MAP = "collabMap"
MENU_HELP = "help"

DEFAULT_HIDDEN_CONTAINER = partial(gui.Container, width='100%',
                                   layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
                                   margin='0px', style={'display': 'none', 'overflow': 'auto'})
DEFAULT_VISIBLE_CONTAINER = partial(gui.Container, width='100%',
                                    layout_orientation=gui.Container.LAYOUT_HORIZONTAL,
                                    margin='0px', style={'display': 'block', 'overflow': 'auto'})
DUMMYLABEL = partial(gui.Label, 'dummy text', width=200, height=30, margin='10px')
BASEPATH = "transcripts"
METAPATH = "metadata"

def get_percent(num_items):
    """
   Returns a string for the percent 1 item should take up if there are "num_items" items
   ex: num_items=4 returns '25%'
    """
    return "%.5s%%" % ((1/num_items*100))


def readGoalFile(goalPath):
    retval = {}
    with open(goalPath, 'r') as f:
        retval['goalID'] = int(f.readline().strip())
        f.readline() #kill an extra line
        retval['GoalText'] = f.readline().split(" ", 1)[1].strip()
        retval['StrengthText'] = f.readline().split(" ", 1)[1].strip()
        retval['WeaknessText'] = f.readline().split(" ", 1)[1].strip()

    return retval
def findByDate(basepath, teacher, date, filetype='json', classifier = False, verbose=False):
    if(verbose):
        print(basepath, teacher, date, filetype, classifier, verbose)
    for x in os.listdir(os.path.join(basepath, teacher)):
        split = x.split(".")
        if(verbose):
            print("Checking: " + str(x))
            print(split)
        if(date == split[2] and split[-1] == filetype):
            if(verbose):
                print("Found: " + str(x))
            if(classifier and "classifier" == split[-2]):
                return os.path.join(basepath, teacher, x)
            if(not classifier and "classifier" != split[-2]):
                return os.path.join(basepath, teacher, x)
if __name__ == "__main__":
    print(get_percent(4))
    print(findByDate(BASEPATH, "T124D", "1", classifier=True))
