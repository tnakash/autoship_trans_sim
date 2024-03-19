## Introduction
This is the Autonomous Ship Transition Simulator for UTokyo-MIT GTL2022 Project. (https://gtl.edu.k.u-tokyo.ac.jp)
## Getting Started
This is an example of how you may give instructions on setting up your project locally. To get a local copy up and running follow these simple example steps.

1. install python ^3.9 environment and poetry.
2. Clone this folder and type this command
```
poetry install
```
## Usage
#### 1. Run webtool (for interactive scenario setting)
if you want to run main.py and use web GUI tool, run shell command from the poetry first.
```
poetry shell
```
After that, run streamlit by the following command
```
streamlit run main.py
```

#### 2. Run from command line (for multiple scenario)
You can get several results by running the following command.
By this command you can get the trade space analysis results.
```
poetry run python multiple_run.py
```

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

## License
Distributed under the MIT License. See LICENSE.txt for more information.

## Memo
Each Technology should be written as Class (240123).

## Contact
Takuya Nakashima