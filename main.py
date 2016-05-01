import sublime, sublime_plugin
import threading
from subprocess import Popen, PIPE
import subprocess
import os.path
import re
import ast
import json 
import urllib.request
import signal
import sys
import filecmp

sys.path.append(os.path.join(os.path.dirname(__file__), "requests-2.9.1"))
sys.path.append(os.path.join(os.path.dirname(__file__), "beautifulsoup4-4.4.1"))
import requests
from bs4 import BeautifulSoup as bs

def QuoteFunc(s):
	return '"' + s + '"'

class Command(object):
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None

	def run(self, timeout):
		def target():
			print('Thread started')
			self.process = subprocess.Popen(self.cmd, shell=True, preexec_fn=os.setsid)
			self.process.communicate()
			print('Thread finished')

		thread = threading.Thread(target=target)
		thread.start()

		thread.join(timeout)
		if thread.is_alive():
			print('Terminating process')
			os.killpg(self.process.pid, signal.SIGTERM)
			thread.join()
		print(self.process.returncode)


class InitializeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.window().show_input_panel("Codeforces Contest Serial Number:", '', self.on_done, None, None)
		
	def on_done(self, user_input):

		ContestNumber = user_input
		r = requests.get("http://codeforces.com/contest/" + str(ContestNumber))
		data = r.text
		soup = bs(data)
		refined_soup = soup.findAll('a', href=re.compile('^/contest/'+str(ContestNumber)+'/problem'))
		ordered_soup = []
		for i in refined_soup:																																												
			ordered_soup.append(str(i.text).strip())
		questions = {}
		for i in range(0,len(ordered_soup)):
			if len(ordered_soup[i]) == 1:																																																																		
				questions[ordered_soup[i]] = ordered_soup[i+1] 

		#print(questions)
		QuestionNamesAndDirectories = {}
		for i in questions:
			QuestionNamesAndDirectories[i] = {}
			QuestionNamesAndDirectories[i]['name'] = questions[i]
		inputString = []
		outputString = []
		r = requests.get("http://codeforces.com/contest/"+str(ContestNumber)+"/")
		data = r.text
		soup = bs(data)


		myTable= soup.findAll('table',class_="problems")
		myT=myTable[0].findAll('tr')

		myDict = {}
		for i in range(1,len(myT)):
			myID=myT[i].findAll('td',class_="id")[0].text.strip()
			#print (myID)
			ri = requests.get("http://codeforces.com/contest/"+str(ContestNumber)+"/problem/"+myID)
			datai = ri.text
			soupi = bs(datai)

			innerDict = {}

			rawInputSoup = soupi.findAll('div', class_="input")
			inputString = []
			for input_ in rawInputSoup:
				refinedInput = input_.findAll('pre')

				refindInputString = ''
				for items in refinedInput[0].contents:
					if str(items) != '<br/>':
						refindInputString+=str(items)
					elif str(items) == '<br/>':
						refindInputString+='\n'
				inputString.append(refindInputString)

			innerDict['input']=inputString

			rawOutputSoup = soupi.findAll('div', class_="output")
			outputString = []
			for output_ in rawOutputSoup:
				refinedOutput = output_.findAll('pre')

				refindOutputString = ''
				for items in refinedOutput[0].contents:
					if str(items) != '<br/>':
						refindOutputString+=str(items)
					elif str(items) == '<br/>':
						refindOutputString+='\n'
				outputString.append(refindOutputString)

			innerDict['output']=outputString
			myDict[myID]=innerDict
			superDict = {}
			superDict['questions'] = QuestionNamesAndDirectories
			superDict['io'] = myDict
			superDict['contest_number'] = ContestNumber
			
			with open(os.path.dirname(os.path.realpath(__file__))+'/data.json', 'w') as fp:
				json.dump(superDict, fp, indent = 4)

class DirectoriesCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		UserSettings = sublime.load_settings("UserSettings.sublime-settings")
		CodeforcesSettings = sublime.load_settings("CodeforcesSettings.sublime-settings")
		Directory = UserSettings.get('Directory')
		LangPref = UserSettings.get('Lang_pref')
		LangExt = CodeforcesSettings.get('Lang_ext')
		Extension = LangExt[LangPref]


		json1_file = open(os.path.dirname(os.path.realpath(__file__))+'/data.json', 'r')
		json1_str = json1_file.read()
		json1_data = json.loads(json1_str)
		superDict = json1_data
		json1_file.close()
		
		QuestionNames = superDict['questions']
		IO = superDict['io']
		ContestNumber = superDict['contest_number']

		Directory+=('/'+str(ContestNumber))
		os.makedirs(Directory)	#have to handle cases when this folder already exists
		for i in QuestionNames:
			dir_ = Directory+'/'+str(i)
			os.makedirs(dir_)
			sublime.active_window().open_file(dir_+'/'+QuestionNames[i]['name']+'.'+Extension)
			superDict['questions'][i]['path_to_solution'] = dir_+'/'+QuestionNames[i]['name']+'.'+Extension
		for ques_no in IO:
			dest = Directory+'/'+str(ques_no)
			for i in range(0, len(IO[ques_no]['input'])):
				input_no = 'input'+str(i+1)
				output_no = 'output'+str(i+1)

				target = open(dest+'/'+input_no, 'w')
				target.write(IO[ques_no]['input'][i])
				target.close()
			
				target = open(dest+'/'+output_no, 'w')
				target.write(IO[ques_no]['output'][i])
				target.close()
		
		with open(os.path.dirname(os.path.realpath(__file__))+'/data.json', 'w') as fp:
			 json.dump(superDict, fp, indent = 4)
					

		
class StandardTestCommand(sublime_plugin.WindowCommand):
	def run(self):
		'''
		CurrentWindowFileName = self.window.active_view().file_name()
		head, tail = os.path.split(CurrentWindowFileName)
		tail = tail.split('.')[0]
		ExecutableFile = head+'/'+tail
		InputFile = head+'/input1'
		TempOutputFile = head+'/output_temp'


		ExecutableFile = '"' + ExecutableFile + '"'
		InputFile 	   = '"' + InputFile 	  + '"'
		TempOutputFile = '"' + TempOutputFile + '"'
		cmd = ExecutableFile+"<"+InputFile+">"+TempOutputFile
		#print(cmd)
		command = Command(cmd)
		command.run(timeout = 3)

		'''
		CurrentWindowFileName = self.window.active_view().file_name()
		print(CurrentWindowFileName)
		try:
			QuestionNumber = CurrentWindowFileName.split('/')[-2]
			print(QuestionNumber)
		except:
			sublime.error_message("Standard Test can only be run from the solution file as an active tab!")
			return

		try:
			json1_file = open(os.path.dirname(os.path.realpath(__file__))+'/data.json', 'r')
			json1_str = json1_file.read()
			json1_data = json.loads(json1_str)
			superDict = json1_data
			json1_file.close()
		except:
			sublime.error_message("Question data is not ready! Have you initialized the contest?")
			return
		
		if QuestionNumber not in superDict['questions']:
			sublime.error_message("Your active tab is not a contest solution file! Make sure you have initialized the contest and are using the appropriate solution files.")
		else:
			head, tail = os.path.split(CurrentWindowFileName)
			tail = tail.split('.')[0]
			ExecutableFile = head + '/' + tail
			if os.path.isfile(head+'/'+tail) == False:
				sublime.error_message("You have not created the executable! Use Sublime Text to build the executable.")
			else:
				cnt = 1
				correct_cnt = 0
				ResultFilePointer = open(head+'/ResultFile', 'w')
				ResultFilePointer.write("STANDARD TESTING FOR "+str(QuestionNumber)+"  -  "+str(ExecutableFile.split('/')[-1]+"\n\n\n"))

				while(os.path.isfile(head+'/input'+str(cnt))):
					ResultFilePointer.write("Input #"+str(cnt)+"\n")

					InputFile = head+'/input'+str(cnt)
					TempOutputFile = head+'/output'+str(cnt)+'_temp'
					OrigOutputFile = head+'/output'+str(cnt)

					cmd = QuoteFunc(ExecutableFile)+"<"+ QuoteFunc(InputFile) +">"+ QuoteFunc(TempOutputFile)
					print(cmd)
					command = Command(cmd)
					command.run(timeout = 3)

					#Reading all 3 file contents
					with open(InputFile, 'r') as InputFilePointer:
						InputFileData = InputFilePointer.read()
					ResultFilePointer.write(InputFileData.rstrip())
					ResultFilePointer.write("\n")
					
					ResultFilePointer.write("Your Output : -")
					ResultFilePointer.write("\n")
					with open(TempOutputFile, 'r') as TempOutputFilePointer:
						TempOutputFileData = TempOutputFilePointer.read()  
					ResultFilePointer.write(TempOutputFileData.rstrip())
					ResultFilePointer.write("\n")

					ResultFilePointer.write("Required Output : -")
					ResultFilePointer.write("\n")				
					with open(OrigOutputFile, 'r') as OrigOutputFilePointer:
						OrigOutputFileData = OrigOutputFilePointer.read() 
					ResultFilePointer.write(OrigOutputFileData.rstrip())
					ResultFilePointer.write("\n")


					ResultFilePointer.write("Result for case#" + str(cnt) + " ---- > ")
					if TempOutputFileData.rstrip() == OrigOutputFileData.rstrip():
						correct_cnt+=1
						ResultFilePointer.write("OUTPUT MATCH!\n")
					else:
						ResultFilePointer.write("INCORRECT OUTPUT!!\n")
					cnt+=1
					ResultFilePointer.write("\n")

				if cnt == correct_cnt:
					ResultFilePointer.write("All standatd test casses passed! You can submit your solution now.\n")
				else:
					ResultFilePointer.write("Standard Tests failed!\n")
					
				ResultFilePointer.close()
				self.window.open_file(head+'/ResultFile')
				v = sublime.active_window().active_view()
				v.add_regions("OUTPUT", [sublime.Region(0,v.size())], "somescope","", sublime.DRAW_SOLID_UNDERLINE|sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE)



class InputFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		CurrentWindowFileName = self.window.active_view().file_name().split('/')[-1].split('.')[0]
		inputFile = CurrentWindowFileName+"_input.in"
		print(CurrentWindowFileName)
		self.window.open_file(inputFile)

class OutputFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		CurrentWindowFileName = self.window.active_view().file_name().split('/')[-1].split('.')[0]
		outputFile = CurrentWindowFileName+"_output.out"
		print(CurrentWindowFileName)
		self.window.open_file(outputFile)

class CustomCasesCommand(sublime_plugin.WindowCommand):
	def run(self):
		head, tail = os.path.split(self.window.active_view().file_name())
		CurrentWindowFileName = self.window.active_view().file_name().split('/')[-1].split('.')[0]
		CurrentWindowFileType = self.window.active_view().file_name().split('/')[-1].split('.')[-1]
		
		if os.path.isfile(CurrentWindowFileName) == False:
			sublime.error_message("You have not complied your solution! Build the executable using sublime text")
			return

		inputFile = CurrentWindowFileName+"_input.in"
		outputFile = CurrentWindowFileName+"_output.out"

		if os.path.isfile(inputFile) == False:
			print(os.path.isfile(inputFile), inputFile)
			sublime.error_message("Initialize the input first! Enter your custom testcases here")
			self.window.open_file(inputFile)
			return


		cmd = QuoteFunc(head + '/' + tail.split('.')[0])+"<"+QuoteFunc(head + '/' + inputFile)+">"+QuoteFunc(head + '/' + outputFile)
		command = Command(cmd)
		command.run(timeout = 3)
		self.window.open_file(outputFile)


class SubmitCommand(sublime_plugin.WindowCommand):
	def run(self):
		try:
			json1_file = open(os.path.dirname(os.path.realpath(__file__))+'/data.json', 'r')
			json1_str = json1_file.read()
			json1_data = json.loads(json1_str)
			superDict = json1_data
			json1_file.close()
		except:
			sublime.error_message("Question data is not ready! Have you initialized the contest?")
			return
		if superDict == {} or "contest_number" not in superDict or "questions" not in superDict or "io" not in superDict:
			sublime.error_message("Question data is not ready! Have you initialized the contest?")
			return

		CurrentWindowFileName = self.window.active_view().file_name()
		IsActiveWindowPathCorrect = False
		for quesno in superDict['questions']:
			if CurrentWindowFileName == superDict['questions'][quesno]["path_to_solution"]:
				IsActiveWindowPathCorrect = True
				break

		if IsActiveWindowPathCorrect == False:
			sublime.error_message("You can only submit solutions to the contest! This is not a solutions file according to the plugin.")
			return

		
		UserSettings 	   = sublime.load_settings("UserSettings.sublime-settings")
		CodeforcesLangDict = sublime.load_settings("CodeforcesSettings.sublime-settings")
		LangPref = UserSettings.get("Lang_pref")
		LangCode = CodeforcesLangDict.get(LangPref)
		Username = UserSettings.get("Login_Settings")['username']
		Password = UserSettings.get("Login_Settings")['password']
		ContestId = superDict["contest_number"]
		ProblemId = CurrentWindowFileName.split('/')[-2]

		
		base = "http://codeforces.com"
		cf_enter = "{base}/{login}".format(base=base, login="enter")
		cliente = requests.session()
		r = cliente.get(cf_enter)
		html = r.content
		soup = bs(html)
		head = soup.head
		meta = head.findChildren('meta')
		csrf_token = [
			m for m in meta if 'name' in m.attrs and m['name'] == 'X-Csrf-Token']
		csrf_token = csrf_token[0]["content"]
				
		print(csrf_token) # it's working, :)

		user =  Username
		password = Password

		login_data = {
			'csrf_token': csrf_token,
			'action': 'enter',
			'handle': user,
			'password': password,
		}

		headers = {
			'Referer': cf_enter,
			'User-agent': 'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'
		}

		r = cliente.post(cf_enter, data=login_data, headers=headers)
		if r.status_code != 200:
			print('fail to connect')

		type_contest = "contest"
		contest_id = str(ContestId)
		url_submit = "{base}/{type}/{id}/submit".format(
			base=base, type=type_contest, id=contest_id)
		print(url_submit)

		# url_submit = url_submit +'?csrf_token={0}'.format(csrf_token)
		r = cliente.get(url_submit, headers=headers)
		if r.status_code != 200:
			print('fail to connect', url_submit)
		else:
			print('[200] ', url_submit)

		parts = {
			"csrf_token":            csrf_token,
			"action":                "submitSolutionFormSubmitted",
			"contestId": 			 str(ContestId),
			"submittedProblemIndex": str(ProblemId),
			"source":                open(CurrentWindowFileName, "rb"),
			"programTypeId":         str(LangCode),
			"sourceFile":            "",
			"_tta":                  "834",
			'handle': user,
			'password': password
		}

		r = cliente.post(url_submit, files=parts, headers=headers)
		

		# programtypeId 1 GNU C++
		# programtypeId 7 Python 2.7
		# programtypeId 10 GNU C
		













