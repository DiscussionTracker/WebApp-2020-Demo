import remi.gui as gui
from functools import partial
from helper_functions import *
from matplotlib_app import MatplotImage
import pandoc

class OverviewPage():
    page = None
    userProfile = None
    tableFunc = None
    def __init__(self, display, profile, tableFunc):
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
        self.tableFunc = tableFunc
    def getContainer(self):
        return self.page

    def addContent(self):
        disc_menu = gui.Menu(width='100%', height = '50px')
        mwidth = get_percent(4)
        mheight = '50px'
        dmList = [gui.MenuItem('Overview', width=mwidth, height=mheight),
                  gui.MenuItem('Annotated Transcript', width=mwidth, height=mheight),
                  gui.MenuItem('Collaboration Map', width=mwidth, height=mheight),
                  gui.MenuItem('Help', width=mwidth, height=mheight)]
        disc_menu.append(dmList)

        #creating the Current discussion menus
        #container to hold the 4 tabs here
        self.currDiscContentContainer = DEFAULT_VISIBLE_CONTAINER()
        currDiscStuff = self.create_curr_disc_objects()
        self.currDiscContentContainer.append(currDiscStuff)

        ### add in the function to show that menu item and hide the rest
        dmNameList = [ MENU_OVER_VIEW, MENU_ANOT_TRAN, MENU_COLB_MAP, MENU_HELP]

        for menuItem, name in zip(dmList, dmNameList):
            menuItem.onclick.do(partial(self.curr_disc_menu_clicked, name))

        self.page.append([disc_menu, self.currDiscContentContainer])
    def create_curr_disc_objects(self):
        """
        Since Current Discussion is a page with tabs of its own
        We made another function to create the information for currrent discussion page
        Returns a list of container objects
        """
        overviewContainer = DEFAULT_VISIBLE_CONTAINER()
        overviewContainer.attributes['dtname'] = MENU_OVER_VIEW
        overviewContainer.append(self.generateOverviewInfo())

        annotTransContainer = DEFAULT_HIDDEN_CONTAINER()
        #annotTransContainer.style['margin']= "20px"
        # annotTransContainer.style['padding-left'] = '15px'
        # annotTransContainer.style['padding-right'] = '15px'
        annotTransContainer.attributes['dtname'] = MENU_ANOT_TRAN
        annotTransContainer.append(self.generateAnnotatedTranscript())

        collabMapContainer = DEFAULT_HIDDEN_CONTAINER()
        collabMapContainer.attributes['dtname'] = MENU_COLB_MAP
        collabMapContainer.append(self.generateCollabContent())

        helpContainer = DEFAULT_HIDDEN_CONTAINER()
        helpContainer.attributes['dtname'] = MENU_HELP
        helpContainer.append(self.generateHelpContent())
        ##dummy text
        #overviewContainer.append( gui.Label('You are in overview', width=200, height=30, margin='10px'))
        #annotTransContainer.append( gui.Label('Annotated Transcript is not done yet', width=200, height=30, margin='10px'))
        #collabMapContainer.append( gui.Label('Collaboration Map is not done yet', width=200, height=30, margin='10px'))
        #helpContainer.append( gui.Label('Help is not done yet: Details on how to use discussion tracker since teachers will be on their own. What things mean...', width=200, height=30, margin='10px'))

        return [overviewContainer, annotTransContainer, collabMapContainer, helpContainer]
    def generateOverviewInfo(self):
        labelText = ["Teacher: %s" % (self.userProfile.data[int(self.userProfile.date)-1]['Teacher']),
                     "Date: %s" % (self.userProfile.data[int(self.userProfile.date)-1]['Date']),
                     "Topic: %s" % (self.userProfile.data[int(self.userProfile.date)-1]['Topic']),
                     "Number of Students: %s" % (self.userProfile.data[int(self.userProfile.date)-1]['NumStudents']),
                     "Students Speaking: %s" % (self.userProfile.data[int(self.userProfile.date)-1]['NumStudentSpeakers']),
                     "Number of Turns: %s" % (self.userProfile.data[int(self.userProfile.date)-1]['NumTurns']),
                     "Teacher Turns: %.4s%%" % (self.userProfile.data[int(self.userProfile.date)-1]['TeacherPercentage']*100),
                     "Avg Turns per Speaking Student: %.4s" % (self.userProfile.data[int(self.userProfile.date)-1]['AvgNumStudentTurns']),]
        retval = [gui.Label(x, width="100%", style={'text-align':'center', 'margin-top':'5px', 'margin-bottom':'5px'}) for x in labelText]
        for i in range(3):
            retval[i].style['font-size'] = '20px'


        graphics = gui.GridBox(width="100%")
        grid = [list(range(3)),list(range(3))]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                grid[i][j] = 'pos%s%s'%(i,j)


        graphics.append( gui.Label("Argumentation", style={'text-align':'center', 'font-size':'20px'}),'pos00')
        graphics.append( gui.Label("Specificity", style={'text-align':'center', 'font-size':'20px'}),'pos01')
        graphics.append( gui.Label("Collaboration", style={'text-align':'center', 'font-size':'20px'}),'pos02')

        argElems = list(self.userProfile.data[int(self.userProfile.date)-1]['graphData']['argMoveCount'].items())

        argElems[1], argElems[2] = argElems[2], argElems[1]

        labels, plot_data = zip(*argElems)
        #print(plot_data)
        argPlot = MatplotImage()
        argPlot.style['margin'] = 'auto'
        argPlot.ax.pie(plot_data, labels=labels, autopct='%1.1f%%' )
        #argPlot.ax.bar(range(len(labels)), plot_data, tick_label=labels)
        #argPlot.ax.legend(loc='lower center')
        argPlot.redraw()
        graphics.append(argPlot, 'pos10')

        labels, plot_data = zip(*self.userProfile.data[int(self.userProfile.date)-1]['graphData']['specifiCount'].items())
        specPlot = MatplotImage()
        specPlot.style['margin'] = 'auto'
        specPlot.ax.pie(plot_data, labels=labels, autopct='%1.1f%%' )
        #specPlot.ax.bar(range(len(labels)), plot_data, tick_label=labels )
        #specPlot.ax.legend(loc='lower center')
        specPlot.redraw()
        graphics.append(specPlot, 'pos11')

        labels, plot_data = zip(*self.userProfile.data[int(self.userProfile.date)-1]['graphData']['collabCount'].items())
        colPlot = MatplotImage()
        colPlot.style['margin'] = 'auto'
        colPlot.ax.pie(plot_data, labels=labels, autopct='%1.1f%%' )
        #colPlot.ax.bar(range(len(labels)), plot_data, tick_label=labels )

        #colPlot.ax.legend(loc='lower center')
        colPlot.redraw()
        graphics.append(colPlot, 'pos12')



        graphics.define_grid(grid)
        retval += [graphics]

        return retval

    def generateAnnotatedTranscript(self):
        retval = []

        #creating the table to see
        tList = self.userProfile.data[self.userProfile.date-1]['turnList']
        numRows = len(tList)+1
        for x in tList:
            numRows += len(x['Argumentation'])-1
        print("\t\t", numRows)
        table = gui.TableWidget(n_rows = numRows, n_columns = 6, width="90%")
        table.style['margin'] = "auto"
        #table.style['overflow'] = "hidden"
        table.item_at(0,0).set_text('Turn')
        table.item_at(0,0).attributes['annotTranscript'] = "0"
        table.item_at(0,1).set_text('Speaker')
        table.item_at(0,1).attributes['annotTranscript'] = "0"
        table.item_at(0,2).set_text('Talk')
        table.item_at(0,2).attributes['annotTranscript'] = "0"
        table.item_at(0,2).style['width'] = "60%"

        #table.item_at(0,3).set_text("ArgMove")
        table.item_at(0,3).attributes['annotTranscript'] = "0"
        aDropDown = gui.DropDown.new_from_list(['ArgMove','claim','evidence','explanation'])
        aDropDown.onchange.do(self.tableFunc)
        aDropDown.set_value("ArgMove")
        table.item_at(0,3).append(aDropDown)
        table.item_at(0,3).style['width'] = "10%"
        
        #table.item_at(0,4).set_text('Specificity')
        table.item_at(0,4).attributes['annotTranscript'] = "0"
        sDropDown = gui.DropDown.new_from_list(['Specificity', 'low', 'med', 'high'])
        sDropDown.onchange.do(self.tableFunc)
        sDropDown.set_value("Specificity")
        table.item_at(0,4).append(sDropDown)
        table.item_at(0,4).style['width'] = "10%"

        #table.item_at(0,5).set_text('Collaboration')
        table.item_at(0,5).attributes['annotTranscript'] = "0"
        cDropDown = gui.DropDown.new_from_list(['Collaboration', 'new','extension','challenge','agree'])
        cDropDown.onchange.do(self.tableFunc)
        cDropDown.set_value("Collaboration")
        table.item_at(0,5).append(cDropDown)
        table.item_at(0,5).style['width'] = "10%"

        rowIdx = 1
        turnIdx = 1
        for turn in tList:
            #add in the turnnum
            table.item_at(rowIdx,0).set_text(turn['TurnNum'])
            table.item_at(rowIdx,0).attributes['rowspan'] = len(turn['Argumentation'])
            table.item_at(rowIdx,0).attributes['tColor'] = turnIdx%2
            #speaker info
            table.item_at(rowIdx,1).set_text(turn['Student'])
            table.item_at(rowIdx,1).attributes['rowspan'] = len(turn['Argumentation'])
            table.item_at(rowIdx,1).attributes['tColor'] = turnIdx%2
            #collablabel
            table.item_at(rowIdx,5).set_text(turn['Collaboration'])
            table.item_at(rowIdx,5).attributes['rowspan'] = len(turn['Argumentation'])
            table.item_at(rowIdx,5).attributes['tColor'] = turnIdx%2
            table.item_at(rowIdx,5).attributes[turn['Collaboration']] = 0
            
            for idx, x in enumerate(turn['Argumentation']):
                table.item_at(rowIdx, 2).set_text(x['Text'])
                table.item_at(rowIdx, 2).style['text-align'] = 'left'
                table.item_at(rowIdx, 2).attributes['tColor'] = turnIdx%2
                table.item_at(rowIdx,3).set_text(x['ArgMove'])
                table.item_at(rowIdx,3).attributes['tColor'] = turnIdx%2
                table.item_at(rowIdx,3).attributes[x['ArgMove']] = 0
                table.item_at(rowIdx,4).set_text(x['Specificity'])
                table.item_at(rowIdx,4).attributes['tColor'] = turnIdx%2
                table.item_at(rowIdx,4).attributes[x['Specificity']] = 0
                # delete the table items so that the cells don't get shifted
                # setting to empty string because 'None' causes the text 'none'
                # to be printed for some reason
                if(idx != 0):
                    table.children[str(rowIdx)].children["0"] = ""
                    table.children[str(rowIdx)].children["1"] = ""
                    table.children[str(rowIdx)].children["5"] = ""
                rowIdx += 1
            turnIdx += 1

        #doing some table styling
        #for key in table.children:
        #    if(key != "0"):
        #        table.children[key].attributes['onMouseOver']="this.style.color=\'#0F0\'"
        #        table.children[key].attributes['onMouseOut']="this.style.color=\'#00F\'"

        retval.append(table)
        return retval

    def generateCollabContent(self):
        retval = DEFAULT_VISIBLE_CONTAINER()
        retval.add_child("myhtml", self.userProfile.getCurrentTranscript()['collabMap']['svg'])
        return retval
    def generateHelpContent(self):
        """
        I could make this a read in an markdown file and fill the markdown file with 
        """
        doc = pandoc.Document()
        doc.markdown = open("helpPageContent.md", 'rb').read()

        retval = DEFAULT_VISIBLE_CONTAINER()
        retval.style['margin-left'] = "2%"
        retval.style['margin-right'] = "2%"
        retval.add_child('text', doc.html.decode('utf-8'))

        return retval
    def curr_disc_menu_clicked(self, buttonClicked, widget):
        """
        Generic function to switch menus at current discussion
        buttonClicked is a string for which of the buttons at the top was clicked
        NOTE: this is to be used in conjunction with functools partial to pass in the widget properly
        """
        ## loop through the container list and show the correct ones
        toLoop = self.currDiscContentContainer.children
        for key in toLoop:
            if(toLoop[key].attributes['dtname'] == buttonClicked):
                toLoop[key].style['display'] = 'block'
            else:
                toLoop[key].style['display'] = 'none'
