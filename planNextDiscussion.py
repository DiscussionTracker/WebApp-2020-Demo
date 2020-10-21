import remi.gui as gui
from functools import partial
from helper_functions import *
from matplotlib_app import MatplotImage
from radioButtonExample import RadioButtonWithLabel, RadioButton

class PlanNextDiscussion():

    strengths_text = {'Strengths':
                      ['Students spoke more than 75% of the time',
                       'Most claims were supported with evidence',
                       'Most student ideas were built on and extended by another classmate',
                       'Most of the evidence was explained ',
                       'Most students spoke at least once',
                       'Students were specific in their talk',
                       'Student probed and challenged each other’s ideas more than average '],
                      'Weaknesses':
                      ['Teacher talked more than 25% of the time',
                       'Less than 50% of claims were supported with evidence',
                       'Students built on/ extended less than 50% of each other’s ideas',
                       'Less than 50% of the evidence provided was explained',
                       'Less than 2/3 of the students contributed to the discussion',
                       'Less than 70% of claims, evidence and explanations were specific',
                       'Students probed or challenged less than 10% of each other’s ideas.'],
                      'Goals':
                      ['Students will do more of the talking (and the teacher will do less) in the next discussion.',
                       'Students will use more evidence to back up their claims in the next discussion.',
                       'Students will build more on each other’s ideas in the next discussion.',
                       'Students will provide more explanations for evidence and their arguments in the next discussion.',
                       'More students will speak in the next discussion.',
                       'Students will be more specific in the next discussion',
                       'Students will probe or challenge one another’s ideas more in the next discussion.']}
    # structure of links is: [teacher talk, minilesson, activity]
    resources_links = {
        0:['https://drive.google.com/open?id=1xWQFkbkuQ3HYy9Nk0BbCU51rSKZDPsST', 'https://drive.google.com/open?id=1IP6sHQuKmVSKcrOAbJq2zKb-Y7xAe7Mo', 'https://drive.google.com/open?id=1_veOgBcIUuuz0Xi0g--96VOMAPCeVzVf'],
        1:['https://drive.google.com/open?id=1Ei-WIEUmUj-n0ZOV9zIscvfayhV9NGjG', 'https://drive.google.com/open?id=1t_I-jsuxFHvKxnzl7xU96oMyj4GsHGcz', 'https://drive.google.com/open?id=1sR5v9k3gDLh5pcyRhUgnvIRPwH58oolj'],
        2:['https://drive.google.com/open?id=1duss3UfbV73c2-8-uKt3HWlRai6mnfqB', 'https://drive.google.com/open?id=1szyNdxKpUjZpDASvfgEwmO3F017lUTdZ', 'https://drive.google.com/open?id=1wAjGdYmKUi0riiuUca-KiDf4U5PpkGSj'],
        3:['https://drive.google.com/open?id=172JrQRvD0fKhRkWBOb4dCANG23W6lMcV', 'https://drive.google.com/open?id=1b-oQK53_7Z18_63jbt75xEMJdPQe-LNv', 'https://drive.google.com/open?id=104n0W2TcxoHxFSKaJ-gZZxWFaVi4lDSO'],
        4:['https://drive.google.com/open?id=1dZBgyQGthppkLDGDGAT3Ob_5e7Bf0gpf', 'https://drive.google.com/open?id=1Kt8FXlA5M4zcnitGp7ZL98wYOWUPJ-9t', 'https://drive.google.com/open?id=198xg_JFRQvmOKC5HXla9-ORTjx16MWW7'],
        5:['https://drive.google.com/open?id=1umP05r4d9QPCwT3R-qryT7j_ToBONTn0', 'https://drive.google.com/open?id=1OzJnz7Z2KjUH_ofsBmDlvVgOs_sAgyPe', 'https://drive.google.com/open?id=1_8iVyK1IXdNRYyaBVgRdLYTJ-jMsaTFR'],
        6:['https://drive.google.com/open?id=1OamQPNZC2tu6SrbnwdVWSxerpKhw7upw', 'https://drive.google.com/open?id=1N9PEkYNsIYpz8EY7mvA3p6VM2WtOxjsP', 'https://drive.google.com/open?id=166YlEi8kGh17_tPS13_CXiWGmSNvK-Qm']
    }

    page = None
    userProfile = None
    onload_functions = []
    onload_functions_js = []
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
    def getOnloadFunctions(self):
        return self.onload_functions
    def getOnloadFunctionsJS(self):
        return self.onload_functions_js
    def addContent(self):
        #strength and weakness box
        swBox = DEFAULT_VISIBLE_CONTAINER()
        #swBox.attributes['width'] = '95%'
        swBox.style['width'] = '95%'
        swBox.style['margin'] = '10px auto'
        swBox.style['float'] = 'none'
        swBox.style['background-color'] = 'cyan'

        #Text one
        lblOne = gui.Label('1. Strengths and Weaknesses of the Discussion: ', margin='1%')
        lblOne.style['background-color'] = 'white'
        swBox.append(lblOne)

        #grid of strenghts and weaknesses
        swGrid = gui.GridBox(width = "98%", margin="10px 1% 20px")
        swGrid.style['float'] = 'none'
        grid = [['pos00','pos01']]
        swGrid.define_grid(grid)
        strength = gui.Container(width = "100%", style={'background-color':'palegreen','padding':"10px 0px 10px"})
        weakness = gui.Container(width = "100%",  style={'background-color':'lightgoldenrodyellow',  'padding':"10px 0px 10px"})

        strength.append(gui.Label("Strengths:"))
        strength.append(gui.Label("-%s"%(self.strengths_text['Strengths'][self.userProfile.data[int(self.userProfile.date-1)]['strengths'][0]]), style={'padding-left':'2%'}))
        strength.append(gui.Label("-%s"%(self.strengths_text['Strengths'][self.userProfile.data[int(self.userProfile.date-1)]['strengths'][1]]), style={'padding-left':'2%'}))
        weakness.append(gui.Label("Weaknesses:"))
        weakness.append(gui.Label("-%s"%(self.strengths_text['Weaknesses'][self.userProfile.data[int(self.userProfile.date-1)]['weaknesses'][0]]), style={'padding-left':'2%'}))
        weakness.append(gui.Label("-%s"%(self.strengths_text['Weaknesses'][self.userProfile.data[int(self.userProfile.date-1)]['weaknesses'][1]]), style={'padding-left':'2%'}))

        swGrid.append(strength, 'pos00')
        swGrid.append(weakness, 'pos01')
        swBox.append(swGrid)

        #creating the goal setting box
        gsBox = DEFAULT_VISIBLE_CONTAINER()
        gsBox.style['width'] = '95%'
        gsBox.style['margin'] = '10px auto'
        gsBox.style['float'] = 'none'
        gsBox.style['background-color'] = 'cyan'
        lblTwo = gui.Label("2. Select a Goal for Improving the Next Student Discussion:", margin="1%", style={'background-color':'white'})
        gsBox.append(lblTwo)

        radioBox = gui.VBox(width = '98%', margin="10px 1% 20px")
        radioBox.style['display'] = 'block'
        self.gsRadio1 = RadioButtonWithLabel(self.strengths_text['Goals'][self.userProfile.getCurrentTranscript()['weaknesses'][0]], False, 'groupGoal', margin="5px 0px", style = {'padding-left':'1px'})
        self.gsRadio2 = RadioButtonWithLabel(self.strengths_text['Goals'][self.userProfile.getCurrentTranscript()['weaknesses'][1]], False, 'groupGoal', margin="5px 0px", style = {'padding-left':'1px'})
        #adding a custom field to know what shit is happening
        self.gsRadio1.idx = self.userProfile.data[int(self.userProfile.date-1)]['weaknesses'][0]
        self.gsRadio2.idx = self.userProfile.data[int(self.userProfile.date-1)]['weaknesses'][1]
        #enabling the action
        self.gsRadio1.onchange.do(self.radio_changed)
        self.gsRadio2.onchange.do(self.radio_changed)
        #selecting option
        self.selectButton()
        radioBox.append([self.gsRadio1, self.gsRadio2])
        #register the javascript code for selecting the button so it occurs on load to
        self.onload_functions_js.append( ('activate_radio_button', partial(self.selectButtonJS)) )
        #self.onload_functions.append(('activate_radio_button', partial(self.selectButton)))
        gsBox.append(radioBox)

        #creating the box for the instructional resources
        isBox = DEFAULT_VISIBLE_CONTAINER()
        isBox.style['display'] = 'none'
        isBox.style['width'] = '95%'
        isBox.style['margin'] = '10px auto'
        isBox.style['float'] = 'none'
        isBox.style['background-color'] = 'cyan'
        lblThree = gui.Label('3. Look at these instructional resources and incorporate them in your lessons before your next discussion:', margin='1%', style={'background-color':'white'})
        isBox.append(lblThree)

        linkBox = gui.VBox(width="98%", margin = "10px 1% 20px", style={"background-color":'white'})
        linkBox.style['display'] = 'block'
        tTalk = gui.Label("Teacher Talk", margin="1px")
        tTalk.attributes['href'] = "/"
        tTalk.type = "a"
        mLess = gui.Label("Minilesson", margin="1px")
        mLess.attributes['href'] = "/"
        mLess.type = "a"
        acivi = gui.Label("Activity", margin="1px")
        acivi.attributes['href'] = "/"
        acivi.type = "a"
        linkBox.append(tTalk)
        linkBox.append(gui.Label(" "))
        linkBox.append(mLess)
        linkBox.append(gui.Label(" "))
        linkBox.append(acivi)
        self.isLinkKey = isBox.append(linkBox)
        self.page.append(swBox)
        self.page.append(gsBox)
        self.isKey = self.page.append(isBox)

        #activate the isBox if appropriate
        self.activateIS()


    def selectButton(self):
        #setting the one to true if there already exists a goal
        goalIdx = self.getGoalFileInfo()
        if(goalIdx >= 0):
            index = self.userProfile.getCurrentTranscript()['weaknesses'].index(goalIdx)
            if(index == 1):
                print("Selecting box 2")
                self.gsRadio2.set_value(True)
            if(index == 0):
                print("Selecting box 1")
                self.gsRadio1.set_value(True)

    def selectButtonJS(self):
        """
        This function return a string of JS code that needs to be executed
        This one will happen when the page loads (onload)
        """
        baseJS = "document.getElementsByName('groupGoal')[%s].checked = true;console.log(\"selectButtonJS from planNextDiscussion\")"

        goalIdx = self.getGoalFileInfo()
        if(goalIdx >= 0):
            index = self.userProfile.getCurrentTranscript()['weaknesses'].index(goalIdx)
            baseJS = baseJS % (str(index))
        else:
            #if no goal is set send a comment out piece of code so that it doesn't execute
            baseJS = "//" + baseJS

        #print(baseJS)
        #baseJS = "console.log('%s')" %(baseJS)
        return baseJS
    def activateIS(self):
        #figure out if one of the boxes are true
        #shortcut to the box containing the links
        linkBox = self.page.children[self.isKey].children[self.isLinkKey]
        if(self.gsRadio1.get_value() or self.gsRadio2.get_value()):
            self.page.children[self.isKey].style['display'] = 'block'
            if(self.gsRadio2.get_value()):
                goalIdx = self.gsRadio2.idx
            else:
                goalIdx = self.gsRadio1.idx
            for child in linkBox.children:
                if(linkBox.children[child].get_text() == "Teacher Talk"):
                    linkBox.children[child].attributes['href'] = self.resources_links[goalIdx][0]
                if(linkBox.children[child].get_text() == "Minilesson"):
                    linkBox.children[child].attributes['href'] = self.resources_links[goalIdx][1]
                if(linkBox.children[child].get_text() == "Activity"):
                    linkBox.children[child].attributes['href'] = self.resources_links[goalIdx][2]
            #if(self.gsRadio1.get_value):
            #    self.page.children[self.isKey].append()
        else:
            self.page.children[self.isKey].style['display'] = 'none'
    def getGoalFileInfo(self):
        """
        returns idx from goal file or a negative number
        """
        sidx = self.userProfile.getCurrentTranscript()['TranscriptName'].find(".")+1
        classifier = ".classifier" if self.userProfile.classifier else ""
        goalFileName = self.userProfile.getCurrentTranscript()['TranscriptName'] + classifier +".goal"
        goalFileName = os.path.join(BASEPATH,
                                    self.userProfile.getCurrentTranscript()['TranscriptName'][:sidx-1],
                                    goalFileName)
        if(os.path.exists(goalFileName)):
            with open(goalFileName, 'r') as f:
                return int(f.readline().strip())
        else:
            return -1


    def radio_changed(self, emitter, value):
        #Note I need to save the the goal selected
        #save the latest one selected in the transcript folder
        sidx = self.userProfile.getCurrentTranscript()['TranscriptName'].find(".")+1
        classifier = ".classifier" if self.userProfile.classifier else ""
        goalFileName = self.userProfile.getCurrentTranscript()['TranscriptName'] + classifier +".goal"
        goalFileName = os.path.join(BASEPATH,
                                    self.userProfile.getCurrentTranscript()['TranscriptName'][:sidx-1],
                                    goalFileName)
        with open(goalFileName, 'w') as f:
            lines = [str(emitter.idx),
                     "#some identifying info in case the numbers change or more is added",
                     "#Goal: " + self.strengths_text['Goals'][emitter.idx],
                     "#Strength: " + self.strengths_text['Strengths'][emitter.idx],
                     "#Weakness: " + self.strengths_text['Weaknesses'][emitter.idx]
            ]
            lines = [x + "\n" for x in lines]
            f.writelines(lines)
        self.activateIS()
        print('Goal Set: ' + str(emitter.idx))
