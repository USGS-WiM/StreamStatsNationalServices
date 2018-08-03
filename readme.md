![WiM](wimlogo.png)

# StreamStats National Services

StreamStats supporting national REST web services

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Installing
### Dependancies
[ python WIMLib package](https://pypi.org/project/WIMLib/): `pip install WIMLib`

#### ArcGIS 10.x
* You will be using ESRI's ArcGIS ArcPy library for geoprocessing. If you have not installed ArcGIS before, you can skip to the next section.
* If you already have ArcGIS installed on your machine, then you might need to reinstall it. If you are reinstalling, delete C:\Python27 and C:\Program Files (x86)\ArcGIS to remove the files from your machine. Once that is done, download ArGIS from your favorite repository or have an IT administrator add it to your machine. During installation, if you are prompted to overwrite a file, choose the option to overwrite as it will help you clean up your installation (i.e. miscellaneous parts that ESRI has a tendency of leaving out and about on your computer).
* Following installation, verify that you have Python up and working correctly. Open ArcMap or ArcCatalog to verify the installation worked as expected. 

#### Set Python as a System Variable
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

#### Pip and Related Packages
* Go [here](https://pip.pypa.io/en/stable/installing/), open the get-pip.py file and save it to your computer. Personally, I open a copy of Notepad++ and save the file.
* Open the Command Prompt, navigate to where get-pip.py is and execute the command `python get-pip.py` this will download and install Pip.
* Install requests, cirtifi, and virtualenv by executing `pip install requests` `pip install cirtifi` `pip install virtualenv`

#### Visual Studio Code
* Install Visual Studio Code (VS Code) from [here](https://code.visualstudio.com/).
* < INSERT USEFUL DEPENDENCIES TO INSTALL HERE >

#### GitHub
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

# netCDF
* For Windows
* Download and install HD5 1.8.18 from [here]
(https://support.hdfgroup.org/HDF5/).
* Make an environmental variable HDF5_DIR that's value is the installation directory of HDF5.
* Download and install netCDF 4.4.1.1 from [here]
(https://www.unidata.ucar.edu/downloads/netcdf/index.jsp
* Make an environmental variable NETCDF4_DIR that's value is the installation directory of netCDF4.
* Download and pip install the appropriate netCDF4 wheel file from [here] (http://www.lfd.uci.edu/~gohlke/pythonlibs/)

* For Linux
* Use the distribution's respective package manager to install HDF5 and netCDF4.  Then use pip to install netCDF4 for Python.

## Built With

* [Dotnetcore 2.0](https://github.com/dotnet/core) - ASP.Net core Framework

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the process for submitting pull requests to us. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on adhering by the [USGS Code of Scientific Conduct](https://www2.usgs.gov/fsp/fsp_code_of_scientific_conduct.asp).

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](../../tags). 

Advance the version when adding features, fixing bugs or making minor enhancement. Follow semver principles. To add tag in git, type git tag v{major}.{minor}.{patch}. Example: git tag v2.0.5

To push tags to remote origin: `git push origin --tags`

*Note that your alias for the remote origin may differ.

## Authors

* **[Jeremy Newson](https://www.usgs.gov/staff-profiles/jeremy-k-newson)**  - *Lead Developer* - [USGS Web Informatics & Mapping](https://wim.usgs.gov/)
* **[John Wall](https://www.usgs.gov/staff-profiles/john-wall)**  - *Developer* - [USGS South Atlantic Water Science Center](https://www.usgs.gov/centers/sa-water)

See also the list of [contributors](../../graphs/contributors) who participated in this project.

## License

This project is licensed under the Creative Commons CC0 1.0 Universal License - see the [LICENSE.md](LICENSE.md) file for details

## Suggested Citation

In the spirit of open source, please cite any re-use of the source code stored in this repository. Below is the suggested citation:

`This project contains code produced by the Web Informatics and Mapping (WIM) team at the United States Geological Survey (USGS). As a work of the United States Government, this project is in the public domain within the United States. https://wim.usgs.gov`

## Acknowledgments

* [Network-Linked Data Index](https://cida.usgs.gov/nldi/about)
* [GeoJson.Net](https://github.com/GeoJSON-Net/GeoJSON.Net)

## About WIM

* This project authored by the [USGS WIM team](https://wim.usgs.gov)
* WIM is a team of developers and technologists who build and manage tools, software, web services, and databases to support USGS science and other federal government cooperators.
* WiM is a part of the [Upper Midwest Water Science Center](https://www.usgs.gov/centers/wisconsin-water-science-center).
