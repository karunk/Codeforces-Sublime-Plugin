# Codeforces Sublime Plugin

This plugin makes it easy to test your solutions against the standard input / output provided by codeforces as well as submit the solutions direct from sublime text.

- To Do: -
  - ~~Create python snippets for running the executable code against the test cases provided~~
  - ~~Create python snippets for checking extra test cases~~
  - ~~Display output in another sublime text window or the console~~
  - ~~Submitting the solution~~
  - ~~Getting the result of the solution~~
  -  Explore the codeforces API

## Description
Using this plugin you can directly submit your solution, check if your solution gives correct outputs for the standard test cases, check the status of your submitted solution as well as fetch question details just by the touch of a (few) buttons

#### SETTING UP THE PLUGIN
Download this repository as a zip file, and simply place the extracted folder in the Packages Directory.
(Sublime Text - > Browse Packages or Preferences -> Browse Packages)

After the restart, press `ctrl+shift+s` to open the plugin settings file. Enter your codeforces username and password along with the complete directory path where you would like to store your solutions and your preferred language. Make sure everything is in quotes.

##### INITIALIZING A CONTEST
To get started press `FN+i`, you will get the input box at the bottom of the screen. Enter the codeforces contest ID. (Note that the contest ID is  different from contest number in codeforces. For round #348 it was 669. See the url.)

It will take a few seconds to initialize. After that, press `Fn+ctrl+d` to create the contest directory and open the corresponding files for each problem where you will write the solution.

##### QUESTION DETAILS
Question details can only be seen after you have initialized a contest and created directories (above two steps). Press `Fn+ctrl+q` while any of the solution tabs is open. Doing this will open a new tab with the corresponding question details.

##### STANDARD TESTING
After you have written your code, compile or build it using sublime's build command (`command+b`). Then press `fn+ctrl+s` to test your solution against standard test cases.

##### CUSTOM TESTING
Press `fn+ctrl+i` to open the input window while making sure your active window is the solution which is to be tested and that you have already complied/built the solution. Enter your custom input and press `fn+ctrl+c` to get the corresponding output.

##### SUBMITTING A SOLUTION
While making sure your active window is the solution which you want to submit, press `fn+s`

#### JUDGE RESULT
While making sure your active window is the solution whose judge result you want to know press `fn+ctrl+r`

In case you forget the key combinations, you can always use the menu (tools -> codeforces plugin)

### Version
1.0
