import remi.gui as gui
from functools import partial
from helper_functions import *
import numpy as np
from matplotlib_app import MatplotImage

class DiscussionHistory():
    page = None
    userProfile = None
    def __init__(self, display, profile):
        """
        This should work to make a container
        The display variable should be either "none" or "block" for whether the
        container should be visible or not initially
        """
        if(display=='none'):
            self.page = DEFAULT_HIDDEN_CONTAINER()
        if(display=="block"):
            self.page = DEFAULT_VISIBLE_CONTAINER()
        self.userProfile = profile
    def getContainer(self):
        return self.page

    def addContent(self):
        self.page.append(self.create_disc_hist_objects())

    def create_disc_hist_objects(self):
        retval = []
        title = gui.Label('Discussion History', width="100%", margin='auto',
                          style = {'text-align':'center', 'font-size':'20px',
                                   'margin-top':'5px', 'margin-bottom':'5px'})
        retval.append(title)

        ##create some plots of the prior discussion
        if(self.userProfile.date == 1):
            retval.append(gui.Label('No prior discussions yet', width="100%", style = {'text-align':'center', 'margin-top':'5px', 'margin-bottom':'5px'}))
            return retval

        #default if date is not one

        #should add in switching between discussions

        table = gui.Table(width="100%", height = "200px", style={'background-color':'light-blue'})
        tableCells = [ ("Discussion Number", "Instructional Goal", "Achieved") ]

        #pull in the all of the date-1 goal files.
        for i in range(1, self.userProfile.date):
             goalPath = findByDate(BASEPATH, self.userProfile.teacher, str(i), filetype='goal', classifier=self.userProfile.classifier)
             print(goalPath)
             goalData = readGoalFile(goalPath)
             #check the next transcript for if the goal is in the strengths
             strList = self.userProfile.data[i]['strengths']
             if(goalData['goalID'] in strList):
                 achievedMsg = "Yes"
             else:
                 achievedMsg = "No"
             tableCells.append((str(i), goalData['GoalText'], achievedMsg))
        
        #tableCells.append(("2", "Increase the number of explanations the students give", "No??"))

        table.append_from_list(tableCells, fill_title=True)

        #modify the inspect so that someone can click it
        # ti = table.children["1"].children["3"]
        # ti.set_text("")
        # tib = gui.Button("Click to Inspect")
        # ti.append(tib)

        # self.trackContainer = self.DEFAULT_VISIBLE_CONTAINER()
        # self.trackContainer.style['background-color'] = 'aqua'
        # self.trackContainer.style['padding'] = "5px"
        # if(self.date == 3):
        #     self.trackContainer.append(self.create_track_content(self.date-2, "Argumentation", "ArgMove" ,"explanation"))
        #     self.trackContainer.append(self.create_track_content(self.date-1, "Argumentation", "ArgMove" ,"explanation"))




        # tib.onclick.do(partial(self.track_container_clicked, "2"))


        # if(self.date==3):
        #     ti2 = table.children["2"].children["3"]
        #     ti2.set_text("")
        #     tib2 = gui.Button("Click to Inspect")
        #     ti2.append(tib2)
        #     tib2.onclick.do(partial(self.track_container_clicked, "3"))

        # #for i in table.children:
        # #    if(i != "0"):
        # #        ti = table.children[i].children
        # #        ti["3"].set_text("")
        # #
        # #        ti["3"].append()


        retval.append(table)
        # retval.append(self.trackContainer)
        #make a plot of the prior discussion
        graphics = gui.GridBox(width="100%")
        grid = [list(range(3))]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                grid[i][j] = 'pos%s%s'%(i,j)

        argLabels = list(self.userProfile.getCurrentTranscript()['graphData']['argMoveCount'].keys())
        argY = []
        argY_labels = []

        indices = np.arange(self.userProfile.date-1, max(-1, self.userProfile.date-6), -1)
        for x in indices:
            argY.insert(0, [self.userProfile.data[x]['graphData']['argMoveCount'][k] for k in argLabels])
            argY_labels.insert(0, "Discussion %d" %(x+1))
        argPlot = self.create_graph_object(argY, argLabels, argY_labels)
        graphics.append(argPlot, 'pos00')

        specLabels = list(self.userProfile.getCurrentTranscript()['graphData']['specifiCount'].keys())
        specY = []
        specY_labels = []

        indices = np.arange(self.userProfile.date-1, max(-1, self.userProfile.date-6), -1)
        for x in indices:
            specY.insert(0, [self.userProfile.data[x]['graphData']['specifiCount'][k] for k in specLabels])
            specY_labels.insert(0, "Discussion %d" %(x+1))
        specPlot = self.create_graph_object(specY, specLabels, specY_labels)
        graphics.append(specPlot, 'pos01')

        colLabels = list(self.userProfile.getCurrentTranscript()['graphData']['collabCount'].keys())
        colY = []
        colY_labels = []

        indices = np.arange(self.userProfile.date-1, max(-1, self.userProfile.date-6), -1)
        for x in indices:
            colY.insert(0, [self.userProfile.data[x]['graphData']['collabCount'][k] for k in colLabels])
            colY_labels.insert(0, "Discussion %d" %(x+1))
        colPlot = self.create_graph_object(colY, colLabels, colY_labels)
        graphics.append(colPlot, 'pos02')



        graphics.define_grid(grid)
        retval += [graphics]


        return retval
    def create_graph_object(self, y, labels, y_labels):
        """
        y will be an array for each set of values that needs to be presented
        labels will be the set of labels.
        """
        x = np.arange(len(labels))

        plot = MatplotImage()
        plot.style['margin'] = "auto"

        barWidth = .8
        width = barWidth/len(y)
        barOffset = (1-barWidth)/2
        start = -.5 + barOffset
        end = .5 - barOffset
        x_pos = np.arange(start+width/2, end, width)

        for i in range(len(y)):
            plot.ax.bar(x+x_pos[i], y[i], width, label=y_labels[i])

        plot.ax.set_xticks(x)
        plot.ax.set_xticklabels(labels)
        plot.ax.legend()
        plot.redraw()

        return plot



    def create_track_content(self, discIDX, goalType, goalCat, goal):
        #how many students improved their number of warrants.
        print("This function is for making the tables on tracking at student level")
        print("This function is currently unused")
        #loop through prior discussion
        students = {}
        for turn in self.data[discIDX-1]['turnList']:
            if(turn['Student'] != 'teacher'):
                if(turn['Student'] not in students):
                    students[turn['Student']] = [0,0]
                if(goalType == "Argumentation"):
                    for elem in turn['Argumentation']:
                        if(elem[goalCat] == goal):
                            students[turn['Student']][0] +=1

        for turn in self.data[discIDX]['turnList']:
            if(turn['Student'] != 'teacher'):
                if(turn['Student'] not in students):
                    students[turn['Student']] = [0,0]
                if(goalType == "Argumentation"):
                    for elem in turn['Argumentation']:
                        if(elem[goalCat] == goal):
                            students[turn['Student']][1] +=1

        #create a table of how many students improved their score
        tableElems = [["Number Improved", "Number did not Improve"],[0,0]]
        for k in students:
            if(students[k][0] < students[k][1]):
                students[k] = True
                tableElems[1][0] += 1
            else:
                students[k] = False
                tableElems[1][1] += 1
                tableElems[1][0] = str(tableElems[1][0])
                tableElems[1][1] = str(tableElems[1][1])
                table = gui.Table(width="25%", style={'background-color':'light-blue'})
                table.append_from_list(tableElems, fill_title=True)
                self.data[discIDX]['improvementDetail'] = students
                json.dump( self.data[discIDX], open(findByDate(BASEPATH, self.teacher, str(discIDX+1), classifier=self.userProfile.classifier), 'w', encoding="utf-8") )
                #ask about what the teacher did
        lbl = gui.Label("What did you do to achieve this goal?", width = "25%")
        improvement = gui.DropDown(width = "50%")
        #init with default values
        improvement.append("Activity")
        improvement.append("Mini-Lesson")
        improvement.append("More discussions")
        #when they select
        improvement.onchange.do(partial(self.improvementDropdown, discIDX))


        #checkBoxes = []
        #checkBoxes.append(gui.CheckBoxLabel(label="Activity"))
        #checkBoxes.append(gui.CheckBoxLabel(label="Mini-Lesson"))
        #checkBoxes.append(gui.CheckBoxLabel(label="More Discussions"))

        #create a table of the students and what they were improved by
        self.studentDetail = gui.TableWidget(width="100%")
        if('improvementAction' in self.data[discIDX]):
            improvement.select_by_value(self.data[discIDX]['improvementAction'])
        else:
            self.data[discIDX]['improvementAction'] = "None Set"
            self.fill_improvement_table(discIDX)
            #butt = gui.Button("refresh table")
            #butt.onclick.do(partial(self.update_improvement_table, discIDX))
        cont = DEFAULT_HIDDEN_CONTAINER()
        cont.append([table, lbl, improvement, self.studentDetail])
        cont.attributes['discID'] = str(discIDX+1)
        return cont

    def improvementDropdown(self, discIDX, widget, value):
        self.data[discIDX]['improvementAction'] = value
        self.update_improvement_table(discIDX, value)
        json.dump( self.data[discIDX], open(findByDate(BASEPATH, self.teacher, str(discIDX+1), classifier=self.userProfile.classifier), 'w', encoding="utf-8") )

    def update_improvement_table(self, discIDX, value):
        for rowKey in self.studentDetail.children:
            if(rowKey != "0"):
                for colKey in self.studentDetail.children[rowKey].children:
                    if colKey == str(discIDX):
                        if(self.data[discIDX]['improvementDetail'][self.studentDetail.children[rowKey].children["0"].get_text()] ):
                            self.studentDetail.children[rowKey].children[colKey].set_text(self.data[discIDX]['improvementAction'])

    def fill_improvement_table(self, discIDX):
        #potential issue the number of students is not maximum between two discussions

        tableElems = []
        titleRow = ["Student#"]
        for i in range(discIDX):
            titleRow.append("Discussion %s->%s" %(i+1, i+2))
            tableElems.append(titleRow)

        for k in self.data[discIDX]['improvementDetail']:
            toAppend = [k]
            for discID in range(1,discIDX+1):
                if(k in self.data[discID]['improvementDetail'] and self.data[discID]['improvementDetail'][k]):
                    toAppend.append(self.data[discID]['improvementAction'])
                else:
                    toAppend.append("")
                    tableElems.append(toAppend)
                    self.studentDetail.append_from_list(tableElems, fill_title=True)

    def track_container_clicked(self, buttonClicked, widget):
        """
        buttonClicked is a string for which of the buttons at the top was clicked
        NOTE: this is to be used in conjunction with functools partial to pass in the widget properly
        """
        ## loop through the container list and show the correct ones
        toLoop = self.trackContainer.children
        for key in toLoop:
            print(toLoop[key].attributes['discID'])
            if(toLoop[key].attributes['discID'] == buttonClicked):
                if(toLoop[key].style['display'] == 'none'):
                    toLoop[key].style['display'] = 'block'
                else:
                    toLoop[key].style['display'] = 'none'
            else:
                toLoop[key].style['display'] = 'none'

