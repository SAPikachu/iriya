iriya
========

Check whether all characters in ASS file exist in specified fonts.


Installation
------------

This tool works only on Windows. Python 3.3 or later is required.

Using `pip <http://www.pip-installer.org/en/latest/>`_ to install is recommended::

    pip install https://github.com/SAPikachu/iriya/archive/master.zip

Alternatively, you can also clone this repository, and run::

    setup.py install

You need to manually install `pysubs <https://github.com/tigr42/pysubs>`_ if you use this method though.


Usage
-----

Run it like this:

    py -3 -miriya <your ass file> [more ass files...]

If there is no output, your ASS file is good.
It will output details if there is any character that doesn't exist in specified fonts.


Known issues
------------

It is slow when checking very big ASS files (on my machine, it need ~4 seconds to check a 3.5 MB ASS file)


Why is this tool called "iriya"?
--------------------------------

She's moe, no? (
