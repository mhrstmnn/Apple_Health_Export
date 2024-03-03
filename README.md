# Parser and Converter for Apple Health Export

Scripts to parse and convert health data after exporting it from Apple's Health app

## Requirements

- A somewhat modern version of [Python](https://www.python.org)
- If you want to use it in the CSV script: [jq](https://jqlang.github.io/jq/)
- Shell scripts were written for the [Zsh](https://www.zsh.org)

## Installation

- Clone this repository from GitHub
- Then run: `./pip_install.sh`

## Usage

- First export all of your health data from Apple's Health app
- Then unpack the exported ZIP archive
- Copy the `Export.xml` file to the `data` directory
- Run one of the two scripts that start with `parse_and_convert`

## Helpful

- [Parsing Apple Health data](https://gist.github.com/hoffa/936db2bb85e134709cd263dd358ca309)
- [How to parse XML file exported from Apple iOS Health App […]](https://blog.gwlab.page/how-to-parse-xml-file-exported-from-apple-ios-health-app-and-make-a-sleep-schedule-plot-using-60c652697c81)

## Contribute

If you find a bug, feel free to create an issue or a pull request
