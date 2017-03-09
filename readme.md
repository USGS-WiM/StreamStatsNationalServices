# ArcGIS 10.x
* You will be using ESRI's ArcGIS ArcPy library for geoprocessing. If you have not installed ArcGIS before, you can skip to the next section.
* If you already have ArcGIS installed on your machine, then you might need to reinstall it. If you are reinstalling, delete C:\Python27 and C:\Program Files (x86)\ArcGIS to remove the files from your machine. Once that is done, download ArGIS from your favorite repository or have an IT administrator add it to your machine. During installation, if you are prompted to overwrite a file, choose the option to overwrite as it will help you clean up your installation (i.e. miscellaneous parts that ESRI has a tendency of leaving out and about on your computer).
* Following installation, verify that you have Python up and working correctly. Open ArcMap or ArcCatalog to verify the installation worked as expected. 

# Set Python as a System Variable
* Go to the Start Menu
* Right click on _Computer_
* Select _Properties_
* Select _Advanced Systems Settings_
* Click _Environment Variables_
* Under _System Variables_, find _Path_ and press _Edit_
* Add `C:\Python27\ArcGIS10.3` or whatever your relevant path is.
* Click _OK_
* Click _OK_, again
* Open the Command Prompt and type `python` which should turn your Command Prompt into a Python Command Prompt allowing you to use Python commands. It is useful to also obtain the version using `python --version` from the command line. If you're using ArcGIS 10.3.1 you should have Python 2.7.8.

# Pip and Related Packages
* Go [here](https://pip.pypa.io/en/stable/installing/), open the get-pip.py file and save it to your computer. Personally, I open a copy of Notepad++ and save the file.
* Open the Command Prompt, navigate to where get-pip.py is and execute the command `python get-pip.py` this will download and install Pip.
* Install requests, cirtifi, and virtualenv by executing `pip install requests` `pip install cirtifi` `pip install virtualenv`

# Visual Studio Code
* Install Visual Studio Code (VS Code) from [here](https://code.visualstudio.com/).
* < INSERT USEFUL DEPENDENCIES TO INSTALL HERE >

# GitHub
* Install Git from [here](https://git-scm.com/downloads).
* Be sure to have a Git Hub account. As soon as you have one, be sure to send a link to your profile to your administrator and let them know the affiliated email for your account.

# Set up for WiM
* Create a directory for your work. Personally, I would recommend something like `C:\gis\usgs\ss`
* Next, open a Command Prompt window and `cd` to this newly created directory.
* In the Command Prompt, clone your required code from Git Hub using `git clone https://github.com/USGS-WiM/StreamStatsNationalServices.git` where the address is to your Git repository code (main branch).
* Open VS Code
* Within VS Code, navigate to File => Open Folder...
* Navigate to your working directory. For the sake of this example, that would be `C:\gis\usgs\ss`
* Click on the VS Code Explorer (stack of two papers) and your folder schema for the cloned code should be shown
* Next, open _config.json_ and change the paths within the JSON file to the relevant paths for your local machine. For example, the NLDIService should be changed to `C:/gis/usgs/ss/ss_apps/gages_iii` here it is worth noting that your backslashes need to be facing the correct direction this is because VS Code provides a false sense of security with "\" slashes resulting in errors.
* Following the saving of _config.json_, open _delineateWrapper.py_ and press the Debugging button found on the left-hand side of VS Code. Make sure that Python is selected from the drop down next to the green arrow and begin debugging. Note that there is a small tab at the top of your VS Code now that has a series of action buttons. You should find the Step Over button (F10) and step through your code to identify errors.

# Commander
* Download and install cmdr (Commander) from [here](http://cmder.net/).

# NodeJS
* Download and install Nodejs from [here](https://nodejs.org/en/).

# Getting Familiar with Git
* This section assumes you are working with _StreamStatsNationalServices_
* Once you have cloned _StreamStatsNationalServices_, navigate to within it
* Verify that you are up-to-date using `git checkout staging`
* If you are behind by a commit, issue a pull command with `git pull origin staging`
* After you have made some changes to your code, issue a submit command by 