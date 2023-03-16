# Automated Testing for Blockonomics WordPress Plugin

Selenium Based Testing
- Tests for JS/No JS, Lite/Normal, BTC/BCH Modes
- Tests for: Display Errors, Copy To Clipboard Functionalities, Refresh Button, QR Code Rendering and URLs
- Automatically Switches the Modes by logging into WP Admin

## How to run?

### Setup WordPress and Plugin

- Install the plugin in any wordpress environment and set it up with API Keys and Callback
- Note the URL for Plugin Settings Page [Main Tab], you'll need it in next step.
- Goto Homepage of your wordpress environment, and do the checkout process until you reach the Blockonomics Checkout Page (after selecting crypto). Note this page URL, you'll need in next step.

### Setup Microsoft Edge and Edge Driver

- Download the relevant webdriver version for yoru MS Edge version from https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/. You can see the version by going to Menu -> Help & Feedback -> About
- Place the downloaded binary into same root as `main.py`

### Setup Python Environment

- Setup your python environment (Python 3.6+)
- Install the requirements using `pip install -r requirements.txt`
- Create a `.env` file or provide the environment variables. See `sample.env` for required variables and sample values. Copy the URLs from previous steps in respective variables.
- Run `python main.py`

That's all!
