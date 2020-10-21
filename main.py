import remi.gui as gui
from remi import start, App
import remi.server as server
from helper_functions import *
from functools import partial
from pprint import pprint
import convert_transcript
import json
import os
from matplotlib_app import MatplotImage
import argparse
import re
import hashlib

#import over the classes that represent each page
from discussionHistory import DiscussionHistory
from planNextDiscussion import PlanNextDiscussion
from overviewPage import OverviewPage

class Profile():

    def __init__(self, teacher, date, data):
        self.date = date
        self.teacher = teacher
        self.data = data
        self.demo = False
        self.classifier = False
    def getCurrentTranscript(self):
        return self.data[self.date-1]


class DTApp(App):


    onload_functions = {}
    onload_functions_js = {}

    def __init__(self, *args):
        res_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res')
        self.re_static_file = re.compile(r"^([\/]*[\w\d]+:[-_. $@?#£'%=()\/\[\]!+°§^,\w\d]+)(\?hash=[\w\d]+)")
        super(DTApp, self).__init__(*args, static_file_path={'res':res_path})

    def _instance(self):
        super(DTApp, self)._instance()
        # this process will check for if the css file is updated and hash it each time.
        # we do this so the browser knows to ask for the css file again whenever we update the file
        # note that this breaks the regular expression for the static files 
        stylesheet = self.page.children['head'].children['internal_css']
        # get the hash value of the stylesheet by reading in the file
        hasher = hashlib.md5()
        with open(os.path.join(self._app_args.get("static_file_path")['res'], 'style.css'), 'rb') as filef:
            buf = filef.read()
            hasher.update(buf)

        if(hasher.hexdigest() not in stylesheet):
            stylesheet = re.sub(r".css.*?'", ".css?hash=%s'"%(hasher.hexdigest()), stylesheet)
            self.page.children['head'].children['internal_css'] = stylesheet

        for child in self.collectHeadJS():
            self.page.children['head'].add_child(child[0], child[1])

    def do_GET(self):
        """
        This is a copy and paste from the server.py file in remi so I can
        add a script tag where I want to add it
        """
        # check here request header to identify the type of req, if http or ws
        # if this is a ws req, instance a ws handler, add it to App's ws list, return
        if "Upgrade" in self.headers:
            if self.headers['Upgrade'].lower() == 'websocket':
                #passing arguments to websocket handler, otherwise it will lost the last message, 
                # and will be unable to handshake
                ws = server.WebSocketsHandler(self.headers, self.request, self.client_address, self.server)
                return

        """Handler for the GET requests."""
        do_process = False
        if self.server.auth is None:
            do_process = True
        else:
            if not ('Authorization' in self.headers) or self.headers['Authorization'] is None:
                self._log.info("Authenticating")
                self.do_AUTHHEAD()
                self.wfile.write(encode_text('no auth header received'))
            elif self.headers['Authorization'] == 'Basic ' + self.server.auth.decode():
                do_process = True
            else:
                self.do_AUTHHEAD()
                self.wfile.write(encode_text(self.headers['Authorization']))
                self.wfile.write(encode_text('not authenticated'))

        if do_process:
            path = str(server.unquote(self.path))
            # noinspection PyBroadException
            try:
                self._instance()
                # build the page (call main()) in user code, if not built yet
                with self.update_lock:
                    # build the root page once if necessary
                    if not 'root' in self.page.children['body'].children.keys():
                        self._log.info('built UI (path=%s)' % path)
                        self.set_root_widget(self.main(*self.server.userdata))
                    if not 'script' in self.page.children['body'].children.keys():
                        self._log.info("Rav Msg: Adding in script tag")
                        self.page.children['body'].add_child(
                            "script", "<script>%s</script>" % (self.collectBodyJS())
                        )
                self._process_all(path)
            except:
                self._log.error('error processing GET request', exc_info=True)

    def main(self):

        self.mainContainer = gui.Container(width='95%', margin='0px auto',
                                      style={'display': 'block', 'overflow': 'hidden'})

        #variable for controlling whether classifier information is shown or gold info
        self.classifier = False
        self.date = 2

        self.loginBox = gui.VBox( width="50%", margin="10px auto 20px", )
        self.loginBox.css_background_color = 'cyan'
        self.loginBox.style['padding'] = "2%"

        heading = gui.Label("Discussion Tracker App", margin = "5px  auto")
        userBox = gui.Input(width = 200, height = 15, margin = "5px  auto")
        userBox.attributes['placeholder'] = "username"
        userBox.set_on_key_up_listener(self.formEnterUp)
        passBox = gui.Input(input_type='password', width = 200, height = 15, margin = "5px  auto")
        passBox.attributes['placeholder'] = "password"
        passBox.set_on_key_up_listener(self.formEnterUp)

        button = gui.Button("Login", margin = "5px  auto")
        button.onclick.do(self.addContent)

        self.loginBox.append( {'head':heading, 'user':userBox, 'pass':passBox, 'button':button})

        self.mainContainer.append(self.loginBox)

        #print(self.session)
        return self.mainContainer

    def collectHeadJS(self):
        """
        This function will collect all of the JS source files from
        the res folder
        """
        retval = []
        #create Jquery tag
        tag = gui.Tag(_type='script')
        tag.attributes['src'] = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"
        retval.append(('jquery', tag))

        jsFiles = ["svg-pan-zoom.min.js"]#, "waitSVG.js"]
        for js in jsFiles:
            fh = open("res/"+js, "r")
            tag = gui.Tag(_type='script')
            tag.add_child("javascript", fh.read())
            fh.close()
            key = js[:js.rfind(".")]
            retval.append((key,tag))

        return retval

    def collectBodyJS(self):
        """
        This will return a JS string of JS to run in the script tag in the body
        """
        retval = ""
        jsFiles = ['waitSVG.js']
        for js in jsFiles:
            fh = open("res/" + js, "r")
            retval += fh.read() + "\n"
            fh.close()
        return retval

    def formEnterUp(self, widget, key, keycode, ctrl, shift, alt):
        if(keycode == '13'):
            self.addContent(widget)

    def addContent(self, widget):
        box = widget.get_parent()
        userText = box.children['user'].get_value()
        passText = box.children['pass'].get_value()

        #print(userText, passText)

        #set the profile
        #assume processed data
        #and set the date to be 1 or 2

        if(userText == "demo" and passText == "dtapp_demo_password"):
            #load in the demo user

            data = []
            self.userProfile = Profile("T124D", self.date, None)
            self.userProfile.classifier = self.classifier
            self.userProfile.demo = True
            for i in range(1,self.userProfile.date+1):
                path = findByDate(BASEPATH, self.userProfile.teacher, str(i), classifier=self.classifier)
                data.append(json.load(open(path, 'r', encoding="utf-8")))

            self.userProfile.data = data

            #fill in the main content with this user profile
            self.mainContainer.empty()
            self.mainContainer.append(self.hidemain())
            #reset the text boxes so it is not filled in on log out
            self.loginBox.children['user'].set_value('')
            self.loginBox.children['pass'].set_value('')
        else:
            box.append(gui.Label("Incorrect username or password"))


    def logout(self, widget):
        self.mainContainer.empty()
        self.mainContainer.append(self.loginBox)

    def hidemain(self):

        ## the containers the hold the stuff we want to see
        #mainContainer = gui.Container(width='95%', margin='0px auto',
        #                              style={'display': 'block', 'overflow': 'hidden'})

        self.contentContainer = DEFAULT_VISIBLE_CONTAINER()


        ## Core Menu Items
        menu = gui.Menu(width='100%', height='50px')
        mwidth = get_percent(4)
        mheight = 50
        m1 = gui.MenuItem('Current Discussion', width=mwidth, height=mheight)
        m2 = gui.MenuItem('Discussion History', width=mwidth, height=mheight)
        m3 = gui.MenuItem('Plan Next Discussion', width=mwidth, height=mheight)
        m4 = gui.MenuItem('Logout', width=mwidth, height=mheight)
        menu.append([m1, m2, m3, m4])

        m1.onclick.do(partial(self.top_menu_clicked, MENU_CURR_DISC))
        m2.onclick.do(partial(self.top_menu_clicked, MENU_DISC_HIST))
        m3.onclick.do(partial(self.top_menu_clicked, MENU_PLAN_NEXT))
        m4.onclick.do(self.logout)
        #adding in the menu bar and addint it to
        menubar = gui.MenuBar(width='100%', height='30px')
        menubar.append(menu)
        #mainContainer.append([menubar, self.contentContainer])

        self.create_top_menu_objects()

        if(self.userProfile.demo):
            classifierSwitchMsg = "Switch to Classifier Labels" if not self.classifier else "Switch to Gold Labels"
            self.classifierSwitch = gui.Button(classifierSwitchMsg, margin = "5px auto")
            self.classifierSwitch.onclick.do(self.switchClassifierGold)
        # returning the root widget
        #return mainContainer
        return [menubar, self.contentContainer, self.classifierSwitch]

    def switchClassifierGold(self, widget):
        self.classifier = not self.classifier

        data = []
        self.userProfile = Profile("T124D", self.date, None)
        self.userProfile.classifier = self.classifier
        self.userProfile.demo = True
        for i in range(1,self.userProfile.date+1):
            path = findByDate(BASEPATH, self.userProfile.teacher, str(i), classifier=self.classifier)
            data.append(json.load(open(path, 'r', encoding="utf-8")))

        self.userProfile.data = data

        #fill in the main content with this user profile
        self.mainContainer.empty()
        self.mainContainer.append(self.hidemain())

    def create_top_menu_objects(self):
        """
        This will create for the top menu and display control things to be used by
        other functions test message
        """

        ## creating the container for the current discussion
        currDiscContainer = OverviewPage(display='block', profile=self.userProfile, tableFunc=partial(self.tableChangeColor))
        currDiscContainer.addContent()
        currDiscContainer.getContainer().attributes['dtname'] = MENU_CURR_DISC

        #creating a container for discussion history
        discHistContainer = DiscussionHistory(display='none', profile=self.userProfile)
        discHistContainer.addContent()
        discHistContainer.getContainer().attributes['dtname'] = MENU_DISC_HIST

        # discHistContainer.append(self.create_disc_hist_objects())
        print(self.userProfile)
        #creating a container for plan next
        planNextContainer = PlanNextDiscussion(display='none', profile=self.userProfile)
        planNextContainer.addContent()
        planNextContainer.getContainer().attributes['dtname'] = MENU_PLAN_NEXT
        #collect onload functions and register them
        for func in planNextContainer.getOnloadFunctions():
            self.registerOnload(*func)
        for func in planNextContainer.getOnloadFunctionsJS():
            self.registerOnloadJS(*func)

        ## container list so that we can access all of them
        ## adding all the containers to the list

        containerList = [currDiscContainer.getContainer(),
                         discHistContainer.getContainer(),
                         planNextContainer.getContainer()]
        ## adding the containers to the content container
        self.contentContainer.append(containerList)



    def flip_container(self, toFlip, widget):
        if(toFlip.style['display'] == 'block'):
            toFlip.style['display'] = 'none'
        else:
            toFlip.style['display'] = 'block'

    def top_menu_clicked(self, buttonClicked, widget):
        """
        Generic function to switch menus at the top level
        buttonClicked is a string for which of the buttons at the top was clicked
        NOTE: this is to be used in conjunction with functools partial to pass in the widget properly
        """
        ## loop through the container list and show the correct ones
        toLoop = self.contentContainer.children
        for key in toLoop:
            if(toLoop[key].attributes['dtname'] == buttonClicked):
                toLoop[key].style['display'] = 'block'
            else:
                toLoop[key].style['display'] = 'none'


    def tableChangeColor(self, widget, attr):
        """
        This function is used in the annotated transcript section to flip the colors of all
        cells in the table
        """
        if(attr not in ['ArgMove', 'Collaboration', 'Specificity']):
            self.execute_javascript("""
            elemList = document.querySelectorAll("[%s]");
            var x;
            for(x in elemList){
            if(elemList[x].getAttribute('%s') == "0"){
            elemList[x].setAttribute('%s', "1")
            }
            else{
            elemList[x].setAttribute("%s", "0")
            }
            }
            """ %(attr, attr, attr, attr))
        widget.set_value('')
    def registerOnload(self, name, func):
        """
        This function will register the given function to a
        dictionary so that it is run when the page loads
        """
        self.onload_functions[name] = func
    def registerOnloadJS(self, name, func):
        """
        This function will register the given function to a
        dictionary so that it is run when the page loads
        these are javascript functions that need to be handled differently
        """
        self.onload_functions_js[name] = func
    def onload(self, emitter):
        for funcKey in self.onload_functions:
            self.onload_functions[funcKey]()
        for funcKey in self.onload_functions_js:
            js_str = self.onload_functions_js[funcKey]()
            self.execute_javascript(js_str)
    # def onpageshow(self, width, height, emitter):
    #     print(width)
    #     print(height)
    #     print(emitter)
    #     print("page shown")
    #     return (width, height)

if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    parser = argparse.ArgumentParser()
    # parser.add_argument("date", help ="This is the internal date for running the simulation the running order should be 1->2->3", choices=("1", "2", "3"))
    parser.add_argument("launchMode", help="This is determines what mode to launch the server in, either dev mode or production ... more could be added if needed", choices=['dev', 'production'])
    parser.add_argument("--port", help="specify the port number to launch on, only used in dev mode", default=8081)
    parser.add_argument("--skip", help="flag for specifying whether to skip the classifier if we get an error", action="store_true")
    args = parser.parse_args()

    if(args.skip):
        convert_transcript.skipClassifier = True
    #process all the transcripts waiting to be processed
    convert_transcript.batchProcessTranscripts(BASEPATH, METAPATH, True)
    if(args.launchMode == 'dev'):
       start(DTApp, debug=True, address='0.0.0.0', port=args.port, start_browser=False, multiple_instance=True)
    if(args.launchMode == 'production'):
       start(DTApp, debug=True, address='0.0.0.0', port=80, start_browser=False, multiple_instance=True)
